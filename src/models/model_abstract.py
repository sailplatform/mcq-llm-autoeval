"""
model_abstract.py

This file implements the abstract parent class "Model" that all other models
inherit from.

To add a new model
  - Create a new class inheriting from Model.
  - Implement get_response to prompt the language model and get a resopnse.
  - Update self._client and self._model_params in __init__ to handle importing
      API key and model parameters.
"""

###############################################################################

from typing import *

class Model:
    """
    Abstract parent class for models to inherit from.
    """

    def __init__(self, system_prompt: str) -> None:
        """ 
        Initializes a model with: 
          - System prompt. 
          - Messages list containing message log between user and assistant.
          - Client running the language model and handling API key.
          - Model Parameters

        Args:
            system_prompt (str): System prompt for the model instance.
        """
        self._client = None # Replace this line with LLM Client.
        self._model_params = None # Replace this line with model params.

        self._system_prompt = system_prompt
        self._messages = []


    def get_chat_log(self) -> Tuple[str, list]:
        """
        Returns the system prompt and messages list.

        Returns:
            str: System prompt
            list: Message list history between user and assistant.
        """
        return (self._system_prompt, self._messages)

    # Abstract
    def get_response(self, new_message: str) -> str:
        """ 
        Abstract method. Must be implemented in model subclass.

        Given a new message, 
         - Updates the messages list with the user's new message and the 
           assistant's response. 
         - Returns the assistant's response.

        NOTE: Don't forget to properly incorporate self._system_prompt
        when prompting the model, but do not add it to self._messages.

        Args:
            new_message (str): Message sent by the user.

        Returns:
            str: Assistant's response to the user's message.
        """
        raise NotImplementedError("Subclasses must implement get_response()")
