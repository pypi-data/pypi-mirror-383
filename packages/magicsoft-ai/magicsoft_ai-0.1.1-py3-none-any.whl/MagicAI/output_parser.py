
import re
from typing import Union
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.exceptions import OutputParserException
from langchain.agents import AgentOutputParser

class MagicAgentOutputParser(AgentOutputParser):
    """Output parser for the conversational agent."""

    """Prefix to use before AI output."""
    ai_prefix: str = "AI: "
   

    action: str = "Do I need to use a tool? Yes"

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        """Parse the output from the agent into
        an AgentAction or AgentFinish object.

        Args:
            text: The text to parse.

        Returns:
            An AgentAction or AgentFinish object.
        """
        if f"{self.ai_prefix}" in text:
             return AgentFinish({"output": text.split(f"{self.ai_prefix}")[-1].strip()}, text)
        
        elif f"{self.action}" in text :
            regex = r"Action: (.*?)[\n]*Action Input: ([\s\S]*)"
            match = re.search(regex, text, re.DOTALL)
            if not match:
                raise OutputParserException(f"Could not parse LLM output: `{text}`")
            action = match.group(1)
            action_input = match.group(2)
            return AgentAction(action.strip(), action_input.strip(" ").strip('"'), text)
        
        return AgentFinish({"output": text.split(f"{self.ai_prefix}")[-1].strip()}, text)
       

    @property
    def _type(self) -> str:
        return "conversational"
