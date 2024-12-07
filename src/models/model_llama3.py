"""
model_llama3.py

This file implements the class "Meta Llama3 8B Instruct" which inherits from abstract
parent class "Model".
"""

###############################################################################

from models.model_abstract import Model
import requests, time
from utils import read_json, read_yaml
import copy
from typing import *

class Llama3(Model):
    """
    Sublass of "Model" implementing necessary functions for prompting Llama3.
    """
    
    def __init__(self, system_prompt: str) -> None:
        """ 
        Initializes a model with: 
          - System prompt. 
          - Messages list containing message log between user and assistant.
          - Client running the language model and handling API key.

        Args:
            system_prompt (str): System prompt for the model instance.
        """
        super().__init__(system_prompt)

        self.API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
       
        self.API_TOKEN = read_json("./api_keys.json")["llama3_hgface_api"]
        
        self.headers = {"Authorization": f"Bearer {self.API_TOKEN}"}

        self._model_params = read_yaml("./config/model_params/llama3_params.yaml")

    def get_chat_log(self) -> Tuple[str, list]:
        """
        Returns the system prompt and messages list.

        Returns:
            str: System prompt
            list: Message list history between user and assistant.
        """
        return self._system_prompt, self._messages

    def get_response(self, new_message: str, wait_time: int = 4) -> str:
        """ 
        Given a new message, 
         - Updates the messages list with the user's new message and the 
           assistant's response. 
         - Returns the assistant's response.

        Args:
            new_message (str): Message sent by the user.
            wait_time (int): Cooldown before prompting model again.

        Returns:
            str: Assistant's response to the user's message.
        """

        try:
            # Update message input with user message
            messages_input = copy.deepcopy(self._messages)
            messages_input.insert(0, {"role": "system", "content": self._system_prompt})
            messages_input.append({"role": "user", "content": new_message})

            # Parse the messages log to generate llama 3 query
            query_input = ""
            for message in messages_input:
                if message["role"] == "system":
                    query_input += f"<|begin_of_text|><|start_header_id|>system<|end_header_id|> {message["content"]} "
                elif message["role"] == "user":
                    query_input += f"<|eot_id|><|start_header_id|>user<|end_header_id|> {message["content"]} "
                elif message["role"] == "assistant":
                    query_input += f"<|eot_id|><|start_header_id|>assistant<|end_header_id|> {message["content"]} "
            query_input += "<|eot_id|><|start_header_id|>assistant<|end_header_id|>"

            query = {
                    "inputs": query_input,
                    "parameters" : {"temperature": self._model_params["temperature"]+1e-3, 
                                    "top_p": self._model_params["top_p"]-1e-3, 
                                    "max_length": self._model_params["completion_len"]}}

            # Get completion
            completion = requests.post(self.API_URL, headers=self.headers, json=query).json()
            
            # Extract llama's response
            response = completion[0]['generated_text'][len(query['inputs'])+2:]
            
            # Update the message log (without system prompt)
            self._messages = messages_input[1:] + [{"role": "assistant", 
                                                "content": response}]
            return response

        except:
            print(f"Hugging Face inference API for Llama3 rate limit exceeded. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
            return self.get_response(new_message, min(wait_time*2, 60))
        