import asyncio
import logging
import threading
import json
import re
from langchain.tools import BaseTool, Tool
import requests

class AssistantTool(BaseTool):
    def __extract_and_validate_json(self, json_data): 
        try:
            match = re.search(r"```json\s*([\s\S]*?)\s*```", json_data)
            if not match:
                json_string = json_data
            else:
                json_string = match.group(1).strip()
            
            data = json.loads(json_string)
            return data
        except json.JSONDecodeError as e:
            return {"error" : "Provided data is not a valid Json, try again."}
        except Exception as e:
            return {"error" : "Unexpected error, try one more time"}
    
    def __init__(self, name, api_url, schema, description, headers=None, callback = None):
        super().__init__(name = name, description = description)
        self.metadata = {"api_url": api_url,"headers": headers or {},"schema":schema, "callback": callback}

    def _run(self, data):
        body = self.__extract_and_validate_json(data)
        if "error" in body:
            return body
        try:
            if self.metadata["callback"]:
                self.tool_start_callback()
            
            api_url = self.metadata["api_url"]
            headers:dict[str,str] = self.metadata["headers"]
            response = requests.post(api_url, json=body, headers=headers, verify=False)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            
            return response.json()
        except requests.exceptions.RequestException as e:
            return  "An unexpected error happend, try one more time"
    
    def tool_start_callback(self):
        if self.metadata["callback"]:
            callback = self.metadata["callback"]
            try:
                asyncio.get_running_loop()  # Check if there's a running loop
                logging.debug("Try calling tool_start_callback on running loop")
                asyncio.create_task( callback(self.name, self.description) ) 
            except RuntimeError:
                try:
                    logging.debug("No running event loop found. try calling tool_start_callback asyncio.run().")
                    asyncio.run(callback(self.name, self.description))
                except:
                    logging.debug("Something wend wrong")

class ToolManager:
    def __init__(self, tool_call_notification_callable = None):
        self.tool_call_notification_callable = tool_call_notification_callable

    def create_tool(self, tool_details:dict = None):
        tool_name = tool_details['name']
        api_url = tool_details['api_url']
        schema = tool_details['schema']
        description = tool_details['description']
        headers = tool_details.get('headers', {})

        return AssistantTool(name=tool_name, 
                             api_url=api_url, 
                             schema=schema, 
                             description=description, 
                             headers=headers, 
                             callback=self.tool_call_notification_callable)
    
   

