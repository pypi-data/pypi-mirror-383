"""
Browser streaming tool  based on StreamingBaseTool
This is the  version of BrowserStreamingTool that uses the improved streaming architecture.
"""

import datetime
import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any, ClassVar

from langcrew.tools.astream_tool import (
    EventType,
    ExternalCompletionBaseTool,
    HitlGetHandoverInfoTool,
)
from langcrew.web import LangGraphAdapter
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from langcrew_tools.cloud_phone.context import summarize_history_messages_direct

try:
    from typing import override
except ImportError:
    from typing_extensions import override

from agentbox import AsyncSandbox
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langcrew.utils.runnable_config_utils import RunnableStateManager
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field, PrivateAttr

from langcrew_tools.cloud_phone.langchain_tools import get_cloudphone_tools

from .virtual_phone_hook import CloudPhoneMessageHandler

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
# Virtual Cell Phone(Cloud phone)


## Overview
You can control an Android device to achieve a specified goal the user is asking for.
You receive screenshots and clickable elements list before each operation. Use these together for precise control.

## Context Information
- **Current Time**: {current_time}
- **Time Zone**: UTC

## langguage
- The default working language is chinese
- All thinking and responses MUST be conducted in the working language
- Natural language arguments in function calling should use the working language
- DO NOT switch the working language midway unless explicitly requested by the user

## Core Principles
- **Auto-Provided Data**: Screenshots and clickable elements are provided automatically. Only call `phone_take_screenshot()` and `phone_get_clickables()` if not received in current request
- **Context Analysis**: Calculate center coordinates from bounds: (x,y) = ((left+right)/2, (top+bottom)/2)
- If user requests to stop the task immediately, please use agent_end_task to end the task
- **Visual Information Utilization**: Make full use of visual information, carefully analyze all elements on the screen, especially obvious close buttons or other operable elements.
- **Handle Ineffective Clicks**: After discovering that repeated clicking on search boxes is ineffective, analyze whether there are popups/recommendation lists on the interface, look for close buttons, or try using the back key to exit the current interface level, then continue the task.
- **Modal Layer Handling**: Modal layers are likely to cause ineffective clicks. Need to analyze whether there are popups/recommendation lists on the interface, look for close buttons, or try using the back key to exit the current interface level, then continue the task. (e.g., 下载应用时，请先点击右上角关闭按钮、请务必先关闭推荐应用的弹窗， 弹窗里应用无法正常下载，不要使用一键下载！！)
## Please make full use of visual analysis
1. Analyze the current page image and clickable elements
2. Determine if this is the target page
3. Compare the differences between current page and previous page clickable elements
4. If elements are completely identical, the click operation may not have taken effect
5. If 2 screens have the same elements, think about not falling into repetitive operations and getting stuck in error loops
6. Consider closing popups or finding other solutions
7. For gaining focus or clearing textbox text, it's normal that the 2 screens may not change, you can continue with the next operation
8. 仔细分析并充分考虑系统提示词，不要只操作而忽略系统提示词的提示！！！
                
## Core Analysis & Planning Process
1. **Screen State Analysis**: Examine all UI elements in current screenshot
2. **Step-by-Step Planning**: Break down task into sequential actions
3. **Tool Selection**: Choose appropriate tool for each step
4. **Result Validation**: Verify action outcomes match expectations
5. **Error Recovery**: Re-execute if results are inconsistent

## Navigation & Search
- **Search Issues**: If results don't appear, click search button again
- **No Search Button**: Try return/back to regain focus, then re-enter
- **Alternative Search**: Use enter tool as equivalent to search trigger
- **App Management**: Use list_packages to get app names, then start_app to open

## Input & Text Handling
- **Input Focus**: tap input box only once before using input_text tool, After clicking, you can get the focus (the selected focus may not be displayed in the clickable elements), simply enter the text
- **Pre-existing Content**: Input boxes may contain previous/placeholder text (normal)
- **Keyboard Blocking**: Use back button or scroll if keyboard obscures view

## Shopping & E-commerce
- **Add to Cart Process**: 
- First click opens cart view (doesn't add item)
- Second click on cart page actually adds item
- **Navigation**: Use "Next" to return to search results
- **Modal Handling**: Close via back button, outside click, or close button
- **Payment**: Do not add any payment information

### Opening Apps
- The virtual phone may have multiple screens - If the app is not found, use horizontal left or right swipes to navigate between them when searching for apps.
- Don't keep scrolling left, you can try scrolling right to find the app
- Apps can be opened either by tapping their icon on screen (`phone_tap`) or by launching directly with the package name (`phone_list_packages` + `phone_start_app`).
- The 应用列表 in the clickable element is not clickable now. Click on the screen app to open it
- Calculator（计算器） is a built-in application on mobile phones, which can be opened using ` phone_ist_mackages `+` phone_start_app `

## Error Handling Strategies
- If unresolved, try alternative methods or tools, but NEVER repeat the same action
- **Stuck State**: Try back button, retry, or home button
- **Loading Issues**: Use wait action or retry
- **Content Discovery**: Swipe up for more content, swipe down for history
- **Task Completion**: If unable to complete (e.g., app not installed), call complete tool directly
- If all attempts fail, explain the failure to the user and request further guidance (use `message_notify_user` tool)
- If I'm repeating the same tool more than 3 times without success, try alternatives or notify user and end task

### Common Scenarios
- **Page scrolling**: Use `phone_swipe()` for vertical scrolling
- **Text input**: First phone_tap_coordinates input() field, then `phone_input_text()`
- **Index tap** (preferred): `phone_tap(index)` - Based on elements list, more accurate
- **Coordinate tap** (backup): `phone_tap_coordinates(x, y)` - Requires coordinate calculation
- **Clear text** : `phone_clear_text(x, y, num_chars, brief)` - Clear text from an input field by tapping and deleting characters, then input correct text
- For downloads use `phone_wait` to verify completion before proceeding
- When downloading an application, please turn off the recommended application pop-up layer
- Do not click repeatedly, use phone_tap_coordinates instead
- Mobile browser search requires simple and efficient access to answers, controlled frequency, and no redundant operations
- When logging into the application, it is likely necessary to first check the 'Agree to User Agreement' option

## Special Tools & Scenarios 
`ask_user(question, suggested_user_action="take_over_phone")` - if need user to take over the phone (eg: login, input verification code)

## Note
The response style should be concise, clear, and not overly designed.

In the cloud phone environment, you may use the file management tools as your memory to store important intermediate results and avoid loss, and retrieve them later as necessary. However, avoid using other sandbox tools (like command execution) unless explicitly permitted. Browser tools should only be used for phone-related tasks in this environment.

Do not fall into error loops. If repeatedly executing tools still cannot complete the task, please explain the situation and report task failure.
"""


class CloudPhoneStreamingToolInput(BaseModel):
    """Input for CloudPhoneStreamingTool."""

    instruction: str = Field(..., description="The instruction to use cloud phone")


class CloudPhoneStreamingTool(ExternalCompletionBaseTool, HitlGetHandoverInfoTool):
    """Cloud phone tool  for cloud phone interaction based on StreamingBaseTool."""

    name: ClassVar[str] = "cloud-phone"
    args_schema: type[BaseModel] = CloudPhoneStreamingToolInput
    description: ClassVar[str] = (
        "Use this tool to interact with cloud phones. Input should be a natural language description of what you want to do with the cloud phone, such as 'Open WeChat and send a message', 'Take a screenshot of the home screen', or 'Navigate to a specific app and perform actions'."
        "The sandbox environment cannot be operated in the cloud phone. You can first obtain a screenshot URL and then save it to the sandbox environment"
        "Provide high-level, comprehensive task descriptions rather than breaking them into small steps"
        "The tool can handle complex, multi-step operations within a single call"
        "If the user wants to take over the cloud phone directly, please use this tool first, and then request the user to take over through `user_input`"
    )

    sandbox_source: Callable[[], Awaitable[AsyncSandbox]] | None = Field(
        default=None, description="AsyncSandbox"
    )
    base_model: BaseChatModel | None = Field(default=None, description="Base model")
    recursion_limit: int = Field(default=120, description="Recursion limit")
    model_name: str | None = Field(default=None, description="Model name")
    session_id: str = Field(default="", description="Session id")

    _cloudphone_handler_with_model: CloudPhoneMessageHandler | None = PrivateAttr(
        default=None
    )
    config: RunnableConfig | None = None
    adapter: LangGraphAdapter | None = None
    graph: CompiledStateGraph | None = None

    def __init__(
        self,
        model_name: str,
        base_model: BaseChatModel,
        sandbox_source: Callable[[], Awaitable[AsyncSandbox]],
        session_id: str,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.sandbox_source = sandbox_source
        self.base_model = base_model
        self.model_name = model_name
        self.session_id = session_id

    @override
    async def _arun_custom_event(self, instruction: str, **kwargs: Any) -> Any:
        """
        work for _arun
        """
        final_config = {
            "configurable": {"thread_id": self.session_id + "_cloudphone"},
            "recursion_limit": self.recursion_limit,
        }
        self.config = final_config
        RunnableStateManager.init_state(self.config)
        self._cloudphone_handler_with_model = CloudPhoneMessageHandler(
            model_name=self.model_name
        )
        system_prompt = SYSTEM_PROMPT.format(
            current_time=datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
        )
        tools = await self._initialize_tools()
        # =====langgraph beign======
        checkpointer = InMemorySaver()
        graph = create_react_agent(
            model=self.base_model,
            tools=tools,
            prompt=system_prompt,
            pre_model_hook=self.pre_model_hook,
            post_model_hook=self.post_model_hook,
            checkpointer=checkpointer,
        )
        self.graph = graph
        logger.info(f"run graph with instruction: {instruction}")
        messages = [HumanMessage(content=instruction)]
        inputs = {"messages": messages}
        pre_event = None
        async for event in graph.astream_events(inputs, config=self.config):
            pre_event = event
        return self._extract_content_from_event(pre_event)

        # =====langgraph end=====

        #  TODO crew tool_stop_result方法中无法获取历史消息，等支持后打开
        # agent = Agent(
        #     llm=self.base_model,
        #     tools=tools,
        #     prompt=system_prompt,
        #     pre_model_hook=self.pre_model_hook,
        #     post_model_hook=self.post_model_hook,
        #     executor_type = "react",
        #     memory=MemoryConfig(),
        # )
        # crew = RunnableCrew(
        #     agents=[agent],
        #     session_id=self._session_id,
        # )
        # logger.info(f"run graph with instruction: {instruction}")
        # messages = [HumanMessage(content=instruction)]
        # inputs = {"messages": messages}
        # self.adapter = LangGraphAdapter(crew=crew)
        # content = "EMPTY_CONTENT"
        # pre_event = None
        # async for event in self.adapter.executor.astream_events(inputs, config=self.config):
        #    pre_event = event
        # if pre_event:
        #     result = self.get_last_event_content(pre_event)
        #     content = result.get("data", {}).get("output", "")
        # return content

    # Get the last message content as the result
    def _extract_content_from_event(self, event: dict[str, Any]) -> str:
        content = "EMPTY_CONTENT"
        if event:
            messages = event.get("data", {}).get("output", {}).get("messages", [])
            if not messages:
                logger.warning(f"No valid AI message found in the event: {event}")
                return content
            last_message = messages[-1]
            if isinstance(last_message, ToolMessage):
                args = {}
                if len(messages) >= 2 and isinstance(messages[-2], AIMessage):
                    tool_calls = getattr(messages[-2], "tool_calls", [])
                    if tool_calls:
                        args = tool_calls[0].get("args", {})

                content = (
                    f"{json.dumps(args, ensure_ascii=False)}\n{last_message.content}"
                )
            else:
                content = last_message.content
            if isinstance(content, dict | list):
                content = json.dumps(content, ensure_ascii=False)
        logger.info(f"agent_as_tool content: {content}")
        return content

    async def pre_model_hook(self, state: dict[str, Any]) -> dict[str, Any]:
         await self._cloudphone_handler_with_model.pre_hook(self.base_model, state)

    async def post_model_hook(self, state: dict[str, Any]) -> dict[str, Any]:
        messages = state.get("messages", [])
        await self._cloudphone_handler_with_model.post_hook(messages)

    @override
    async def handle_external_completion(
        self, event_type: EventType, message: str | None = None
    ):
        # state =  await self.adapter.executor.agents[0].executor.graph.aget_state(self.config)
        state = await self.graph.aget_state(self.config)
        if "messages" in state.values:
            retrieved_messages = state.values["messages"]
            summary = await summarize_history_messages_direct(
                self.base_model, retrieved_messages
            )
            logger.info(f"summary: {summary}")
            if event_type == EventType.STOP:
                return f"Tool execution history summary:\n {summary}\n User requested to stop the task, task ended"
            elif event_type == EventType.NEW_MESSAGE:
                return f"Tool execution history summary:\n {summary}\n User added new instruction: {message}"
        else:
            return message

    @override
    async def get_handover_info(self) -> dict | None:
        return {"scene": "phone"}

    async def _initialize_tools(self) -> list[Any]:
        tools = get_cloudphone_tools(self.sandbox_source, self.config)
        return tools
