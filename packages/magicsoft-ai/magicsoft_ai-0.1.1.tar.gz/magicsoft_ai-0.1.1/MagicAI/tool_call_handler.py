
from typing import Any
from langchain.callbacks.base import AsyncCallbackHandler
from langchain_core.agents import AgentAction
import logging
import re
import asyncio
class ToolCallHandler(AsyncCallbackHandler):
    def __init__(self, tool_start_callable = None):
        super().__init__()
        self.tool_start_callable = tool_start_callable
    
    async def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        logging.debug(f"starting agent actions tool : {action.tool}")
        text = action.log
        regex = r"Message: (.*?)[\n]*Action: (.*?)[\n]*Action Input: ([\s\S]*)"
        match = re.search(regex, text, re.DOTALL)
        message = None
        if match:
            message = match.group(1)

        if self.tool_start_callable and action.tool and message:
            self.invoke_tool_start_callable(action.tool, message)

    def invoke_tool_start_callable(self, tool, message):
        try:
            asyncio.get_running_loop()  # Check if there's a running loop
            logging.info("Existing event loop found. Using asyncio.create_task().")
            asyncio.create_task(self.tool_start_callable(tool, message)) 
        except RuntimeError:
            try:
                logging.info("No running event loop found. Using asyncio.run().")
                asyncio.run(self.tool_start_callable(tool, message))
            except:
                logging.info("Something wend wrong")