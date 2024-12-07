"""
model_gpt.py

This file implements the class "GPT" which inherits from abstract
parent class "Model".
"""

###############################################################################

from models.model_abstract import Model
import openai
import time
from utils import read_json, read_yaml
import copy
from typing import *

class GPT(Model):
    """
    Sublass of "Model" implementing necessary functions for prompting GPT.
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

        self._client = openai.OpenAI(
            api_key = read_json("./api_keys.json")["openai_api_key"]
        )
        self._model_params = read_yaml("./config/model_params/gpt_params.yaml")

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

            # Get completion
            completion = self._client.chat.completions.create(
                model             = self._model_params["model"],
                messages          = messages_input,
                temperature       = self._model_params["temperature"],
                max_tokens        = self._model_params["completion_len"],
                top_p             = self._model_params["top_p"],
                frequency_penalty = self._model_params["frequency_penalty"],
                presence_penalty  = self._model_params["presence_penalty"]
            )

            # Extract GPT's response
            response = completion.choices[0].message.content
            
            # Update the message log (without system prompt)
            self._messages = messages_input[1:] + [{"role": "assistant", 
                                                "content": response}]

            return response
        
        except openai.RateLimitError:
            print(f"GPT rate limit exceeded. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
            return self.get_response(new_message, min(wait_time*2, 60))
