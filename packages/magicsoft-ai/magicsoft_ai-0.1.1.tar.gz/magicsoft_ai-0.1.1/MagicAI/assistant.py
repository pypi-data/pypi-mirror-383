import asyncio
import json
import logging
import re
import time
from datetime import datetime, timezone
from loguru import logger

from langchain.agents import AgentExecutor, ConversationalAgent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain

from MagicAI.prompt import get_main_prompt
from MagicAI.tool_manager import ToolManager
from MagicAI.time_monitor import TimeMonitorAgent
from MagicAI.tool_call_handler import ToolCallHandler
from MagicAI.token_count_handler import TokenCountingCallbackHandler
from MagicAI.output_parser import MagicAgentOutputParser


class AIAgent:
    DEFAULT_IDLE_TIME = 60
    DEFAULT_MAX_DURATION = 30 * 60  # 30 minutes in seconds
    DEFAULT_TEMPERATURE = 0
    DEFAULT_IDLE_MESSAGE = "I am still here, do you have any questions"
    MAX_IDLE_COUNT = 3

    def __init__(self, config, agent_callback = None, 
                 idel_time_reached_callable = None, 
                 session_ending_callable = None,
                 tool_call_start_callable = None,
                 session_end_auto_detect = True):
    
        self.agent_name = config['agent_name']
        
        self.avatar = config["avatar"]
        self.do_not_talk_about  = config["do_not_talk_about"]
        self.agent_task_prompt = config['agent_task_prompt']
        self.agent_goal = config.get('agent_goal',"")
        self.initial_prompt = config["initial_prompt"]
        self.session_id = config['session_id']
        self.task_variables = config['task_variables']

        self.idle_time = config.get('idle_time', self.DEFAULT_IDLE_TIME)
        self.idle_message = config.get('idel_remind',self.DEFAULT_IDLE_MESSAGE)
        self.idle_time_reached_count = self.MAX_IDLE_COUNT
        self.temperature = config.get('temperature', self.DEFAULT_TEMPERATURE)
        self.max_duration = config.get('max_duration', self.DEFAULT_MAX_DURATION) 
        

        self.voice = config.get('voice', None)
        self.agent_callback = agent_callback
        self.idle_time_reached_callable = idel_time_reached_callable
        self.session_ending_callable = session_ending_callable
        self.tool_call_start_callable = tool_call_start_callable
        self.session_end_auto_detect = session_end_auto_detect
       
        self.conversation_history = []

        # Default to 30 minutes if not provided
        self.start_time = time.time()
        self.elapsed_time = 0
      
        self.active = False

        self.idle_time_monitor = None
        if self.idle_time_reached_callable:
            self.idle_time_monitor = TimeMonitorAgent(self.idle_time, self.idle_time_reached)
        self.token_counter = TokenCountingCallbackHandler()
        self.tts_usage = 0
        
        self.tool_dict = config.get('tools_dict',[])
        self.set_tools(self.tool_dict)

        self.set_llm(config.get('llm',"gemini-2.0-flash"), api_key=config.get("llm_api",""))
    
        # Define a prompt template
        self.prompt_template = self._build_prompt_template()

        # Create an LLMChain 
        self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
            
        # Create a ConversationalAgent with the LLMChain and default MRKL output parser
        self.agent = ConversationalAgent(llm_chain=self.llm_chain, 
                                         tools=self.tools, 
                                         allowed_tools=self.tool_names,
                                         output_parser=MagicAgentOutputParser())
        
        
        tool_call_callback = ToolCallHandler(self.handle_toolcall_start)
        # Create an AgentExecutor using from_agent_and_tools method
        self.executor = AgentExecutor.from_agent_and_tools(agent=self.agent, tools=self.tools, verbose=True, callbacks=[tool_call_callback])


    def to_dict(self) -> dict:
        """
        Serialize the AIAgent instance to a dictionary.
        Handles non-serializable objects by storing only necessary configuration.
        
        Returns:
            dict: Serialized representation of the AIAgent instance
        """
        try:
            serialized = {
                "agent_name": self.agent_name,
                "avatar": self.avatar,
                "do_not_talk_about": self.do_not_talk_about,
                "agent_task_prompt": self.agent_task_prompt,
                "initial_prompt": self.initial_prompt,
                "session_id": self.session_id,
                "task_variables": self.task_variables,
                "idle_time": self.idle_time,
                "idle_message": self.idle_message,
                "idle_time_reached_count": self.idle_time_reached_count,
                "temperature": self.temperature,
                "max_duration": self.max_duration,
                "voice": self.voice,
                "conversation_history": self.conversation_history,
                "start_time": self.start_time,
                "elapsed_time": self.elapsed_time,
                "active": self.active,
                "tts_usage": self.tts_usage,
                "tool_dict": self.tool_dict,
                # Store LLM configuration
                "llm_config": {
                    "model": getattr(self, "model", None),
                    "api_key": getattr(self, "api_key", None)
                }
            }
            return serialized
        except Exception as e:
            logger.error(f"Error serializing AIAgent: {e}")
            raise

    def to_json(self) -> str:
        """
        Serialize the AIAgent instance to a JSON string.
        
        Returns:
            str: JSON string representation of the AIAgent instance
        
        Raises:
            RuntimeError: If serialization fails
        """
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            logger.error(f"Error converting AIAgent to JSON: {e}")
            raise RuntimeError(f"Failed to serialize AIAgent to JSON: {e}")

    @classmethod
    def from_dict(cls, data: dict) -> 'AIAgent':
        """
        Create a new AIAgent instance from a dictionary.
        
        Args:
            data (dict): Dictionary containing AIAgent configuration
            
        Returns:
            AIAgent: New AIAgent instance
            
        Raises:
            ValueError: If required configuration is missing
        """
        try:
            # Extract LLM configuration
            llm_config = data.pop("llm_config", {})
            
            # Create basic configuration
            config = {
                "agent_name": data["agent_name"],
                "avatar": data["avatar"],
                "do_not_talk_about": data["do_not_talk_about"],
                "agent_task_prompt": data["agent_task_prompt"],
                "initial_prompt": data["initial_prompt"],
                "session_id": data["session_id"],
                "task_variables": data["task_variables"],
                "idle_time": data.get("idle_time"),
                "idel_remind": data.get("idle_message"),
                "temperature": data.get("temperature"),
                "tools_dict": data.get("tool_dict", []),
                "llm": llm_config.get("model"),
                "llm_api": llm_config.get("api_key")
            }
            
            # Create new instance
            instance = cls(config)
            
            # Restore additional state
            instance.conversation_history = data.get("conversation_history", [])
            instance.start_time = data.get("start_time", time.time())
            instance.elapsed_time = data.get("elapsed_time", 0)
            instance.active = data.get("active", False)
            instance.tts_usage = data.get("tts_usage", 0)
            
            return instance
            
        except KeyError as e:
            raise ValueError(f"Missing required configuration field: {e}")
        except Exception as e:
            logger.error(f"Error deserializing AIAgent: {e}")
            raise

    @classmethod
    def from_json(cls, json_str: str) -> 'AIAgent':
        """
        Create a new AIAgent instance from a JSON string.
        
        Args:
            json_str (str): JSON string containing AIAgent configuration
            
        Returns:
            AIAgent: New AIAgent instance
            
        Raises:
            ValueError: If JSON string is invalid
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}")
        except Exception as e:
            logger.error(f"Error creating AIAgent from JSON: {e}")
            raise

    def set_tts_usage(self, value: int):
        self.tts_usage += value

    def set_llm(self,model:str, api_key: str):
        """
        Set the language model (LLM) based on the provided model name.

        This method initializes the appropriate language model (Deepseek or Gemini) 
        based on the prefix of the provided model name. It also handles the retrieval 
        of the necessary API key from environment variables.

        Args:
            model (str): The name of the model to be set. The model name should start 
                            with either 'deepseek' or 'gemini' to determine which LLM to initialize.

        Raises:
            RuntimeError: If there is an error during the initialization of the LLM.
        """
      
        try:

            if not model or not api_key:
                raise ValueError("Model name and API key are required")
            
            self.model:str = model
            self.api_key = api_key 
            
            if self.model.startswith("deepseek"):
                # Initialize the language model (Deepseek)
                self.llm = ChatDeepSeek(    model = self.model,
                                            temperature=self.temperature,
                                            callbacks=[self.token_counter],
                                            max_tokens=None,
                                            timeout=None,
                                            max_retries=2, 
                                            api_key=self.api_key)

            elif self.model.startswith("gemini"):  
                # Initialize the language model (Gemini)
                self.llm = ChatGoogleGenerativeAI(  model = self.model, 
                                                    callbacks=[self.token_counter],
                                                    temperature=self.temperature,
                                                    max_tokens=None,
                                                    timeout=None,
                                                    max_retries=2,
                                                    google_api_key=self.api_key)
            else:
                raise ValueError(f"Unsupported model type: {model}")

            logger.info(f"Successfully initialized {model}")

        except Exception as e:
            raise RuntimeError(f"Failed to create LLM: {e}")

    def set_tools(self,tools_dict):
        """
        Sets the tools for the assistant using the provided dictionary of tools.

        Args:
            tools_dict (dict): A dictionary where keys are tool names and values are tool configurations.

        Side Effects:
            Initializes a ToolManager instance with a tool call notification dictionary.
            Creates tool instances using the ToolManager and stores them in self.tools.
            Extracts and stores the names of the tools in self.tool_names.
        """
        tool_manager = ToolManager()
        self.tools = [tool_manager.create_tool(tool_item) for tool_item in tools_dict]
        self.tool_names = [tool.name for tool in self.tools]
    
           
    def _build_prompt_template(self):
        """
        Constructs a prompt template for the assistant with specific guidelines and tool usage instructions.
        The prompt template includes:
        - The assistant's name and task.
        - Guidelines for the assistant's responses, including avoiding special characters and managing conversation duration.
        - Instructions for using tools, if available, and the format for tool usage.
        - Instructions for ending the conversation based on user input.
        Returns:
            PromptTemplate: A configured prompt template with placeholders for dynamic variables.
        """
        
        tool_prompt =  """
            TOOLS:
            ------
            No tools provided.
            """
          
        if self.tools:
            tool_prompt = """
            TOOLS:
            ------
            You have access to the following tools,
            {tool_details}
            """
       
        # Define the outer prompt template
        outer_template = get_main_prompt(self.agent_task_prompt, tool_prompt)
            
        
        tool_details = "\n".join([f"({idx}) toolname:{tool.name} - {tool.description}. Input data json schema:{tool.metadata['schema']}" for idx,tool in enumerate(self.tools)])
        tool_names  = ",".join([f"{tool.name}" for tool in self.tools])

        partial_variable = {"agent_name": self.agent_name, 
                            "do_not_talk_about": self.do_not_talk_about,
                            "tool_details" : tool_details,
                            "tool_names": tool_names}
        
        partial_variable.update(self.task_variables)

        final_prompt = PromptTemplate(
            template = outer_template,
            input_variables=[
                "agent_name", 
                "current_date_time", 
                "day_of_week",
                "do_not_talk_about" , 
                "tool_details", 
                "tool_names", 
                "input", 
                "history", 
                "elapsed_time", 
                "total_duration"] + list(self.task_variables.keys()),
            partial_variables=partial_variable
        )
      
        return final_prompt
    
    async def start(self, test=False):
        """
        Starts the conversation by initializing the conversation history and setting the active status to True.
        Then, it proceeds to the first step of the conversation.

        Args:
            test (bool): A flag indicating whether the method is being called in a test context. Default is False.

        Returns:
            The output of the first step of the conversation.
        """
        self.conversation_history = []
        self.active = True
        return await self.step(None)
    
    async def step(self, input, test=False):
        """
        Executes a single step in the conversation.

        Args:
            input (str): The input string for the conversation step.
            test (bool): A flag indicating whether the method is being called in a test context. Default is False.

        Returns:
            str: The agent's response after processing the input.

        Workflow:
            1. Stops the ideal time monitor if it is active.
            2. Sets the initial prompt if the input is None and the conversation history is empty.
            3. Formats the input for the conversation.
            4. Sends the formatted input to the agent and returns the output.
            5. Handles any exceptions that occur during agent execution.
        """
        if self.idle_time_monitor:
            self.idle_time_monitor.stop()

        if not input and len(self.conversation_history) == 0:
            input = self.initial_prompt

        input = self.get_formatted_input(input)
        
        try:
            output = await self.send(input)  
            return output
        
        except Exception as e:
            raise RuntimeError(f"An error occurred during agent execution: {e}")

    async def send(self, input):
        """
        Asynchronously sends input to the executor and processes the result.

        Args:
            input (str): The input string to be sent to the executor.

        Returns:
            str: The agent's response after processing the input.

        Workflow:
            1. Sends the input to the executor's `ainvoke` method.
            2. Extracts the user input and agent output from the result.
            3. Handles the end session if the agent's response starts with "END".
            4. Starts the ideal time monitor if it is available.
            5. Appends the conversation history with the user and agent messages.
            6. Persists the conversation history if the `agent_callback` is provided.
        """
       
        user_message:str = input["input"] 
        user = {"date_time": datetime.now(timezone.utc), "type": "User", "message": user_message} 
        result = await self.executor.ainvoke(input=input, config=None, **self.task_variables, include_run_info=True)
        agent_message, end_session = self.handle_end_session(str(result["output"]).replace("`",""))
        agent = {"date_time": datetime.now(timezone.utc), "type": "AI", "message": agent_message} 
        
        if self.idle_time_monitor and not end_session:
            self.idle_time_monitor.start()

        self.conversation_history.append(f"User: {user_message}\nAI: {agent_message}")
        
        if (self.agent_callback):
            usage = self.token_counter.get_token_counts()
            input = {"messages" : [user,agent], 
                     "usage": usage}
            await self.agent_callback(self.session_id, input)
        
        return agent_message
    
 
    def get_formatted_input(self, input:str, system = False):
        self.elapsed_time = (time.time() - self.start_time) / 60  # Convert to minutes
        if system:
            input = f"system: {input} "
        

        history = "\n".join(self.conversation_history) 
        current_date = datetime.now(timezone.utc)
       
        input = {"input": input, 
                "history":history,
                "current_date_time": current_date.isoformat(),
                "day_of_week" :current_date.strftime("%A"),
                "elapsed_time":self.elapsed_time, 
                "total_duration":self.max_duration}
                
        return input 

    def handle_end_session(self, agent:str):
        """
        Handles the end of a session by performing necessary cleanup and logging.

        Args:
            agent (str): The agent string containing information about the session end.

        Returns:
            str: The agent name after processing the input string.

        Actions:
            - Sets the active status to False.
            - Splits the agent string to extract the reason and agent name.
            - Calls end_session with the reason and elapsed time.
            - Stops the ideal time monitor if it is active.
        """       
      
        # Regex pattern:
        # END-          - Matches the literal string "END-"
        # ([a-zA-Z0-9_]+) - Captures one or more alphanumeric characters or underscores (the reason)
        # -END          - Matches the literal string "-END"
        pattern = r"END-([a-zA-Z0-9_]+)-END"
        extracted_reason = "Unknown" # Initialize as Unknown
       
        # Try to find a single match
        match = re.search(pattern, agent)
        end_session  = False
        if match:
            end_session = True
            extracted_reason = match.group(1) # Extract the captured 'reason'
            # Replace all occurrences of the pattern with an empty string
            modified_text = re.sub(pattern, "", agent)    
            self.invoke_end_session(extracted_reason)
            agent = modified_text      

        return agent, end_session

    async def handle_toolcall_start(self, name, message=None):
        if self.tool_call_start_callable:
            logger.debug("calling tool_starting...")
            if message:
                await self.tool_call_start_callable(self.session_id, {"tool" : name, "tool_message": message})

    def invoke_end_session(self, data):
        reason = {"reason": data, "elapsed_time": self.elapsed_time, "stt_usage": 0, "tts_usage": self.tts_usage}
        try:
            asyncio.get_running_loop()  # Check if there's a running loop
            logging.info("Existing event loop found. Using asyncio.create_task().")
            asyncio.create_task(self.end_session(reason)) 
        except RuntimeError:
            try:
                logging.info("No running event loop found. Using asyncio.run().")
                asyncio.run(self.end_session(reason))
            except:
                logging.info("Something wend wrong")

       
    async def end_session(self, data: None):
        """
        Ends the current session by stopping the ideal time monitor if it is active,
        setting the active status to False, and calling the session ending callback
        with the session ID and provided payload.

        Args:
            data (None): The payload data to be passed to the session ending callback.
        """
        payload = data
        if (self.session_ending_callable):
          await self.session_ending_callable(self.session_id, payload) 

        await self.cleanup()

    async def cleanup(self):
        """Clean up resources."""
        self.active = False
        if self.idle_time_monitor:
            self.idle_time_monitor.stop()
            self.idle_time_monitor = None
        
        self.conversation_history.clear()
        
    def idle_time_reached(self, count):
        """
        Handles the event when the ideal time is reached. 

        This method is called from the time monitor class when the ideal time is reached. It appends a message to the 
        conversation history, calls the idle_time_reached_callable with the session ID and ideal message, stops the 
        current time monitor, and starts a new time monitor. If the count exceeds the idle_time_reached_count, it ends 
        the session with a reason indicating that the user has been idle for a long time.
        
        Args:
            count (int): The current count of the time monitor.
        """
        if count <= self.idle_time_reached_count:
            self.conversation_history.append(f"AI: {self.idle_message}")
            self.idle_time_reached_callable(self.session_id, self.idle_message)
            if self.idle_time_monitor:
                self.idle_time_monitor.stop()
                self.idle_time_monitor = None
                self.idle_time_monitor = TimeMonitorAgent(self.idle_time, self.idle_time_reached, count)
                self.idle_time_monitor.start()
        else:
            self.active = False
            self.invoke_end_session("User idle for long time")
