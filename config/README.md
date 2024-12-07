# Config

The ``./config/`` directory contains two subdirectories:

### ``model_params/`` 

Contains configuration files for LLMs for their parameters such as ``temperature``, ``completion_len``, etc.

### ``prompts/`` 

Contains prompts used for LLMs to generate evaluations for MCQ quality criteria. All prompts have the following form:

- **System** - This explains to the LLM the structure of MCQs and its task in this program.

- **Question** - This presents a question to the LLM and prompts it to reason about how the question fares against the quality criterion. This prompt contains the string "{QUESTION}" which is replaced with the current question being evaluated.

- **Principle** - Once the LLM has reasoned about the question, this prompt asks the LLM to give a single categorical rating for where the MCQ falls with respects to the specific quality criterion. For example, "Does the question provide enough information to arrive at an answer: Yes/No."
All three prompts in combination make up a quality criterion.
