# Source

The ``./src/`` directory contains the main scripts. This is a summary of the important files:

### ``main.py``

Top-level file for running LLM MCQ-evaluation experiments.

### ``utils.py``

Implements utility functions in order for experiments in ``main`` to run.

### ``models/``

This directory contains the implementations of LLMs for running experiments. **The ``model_abstract.py`` file outlines the format for how to implement new models.** Implementing a new model requires implementing a ``get_response()`` function for prompting the model and getting a response string.

### ``analysis/``

This directory serves two purposes.

- **1** Computing the prediction scores (accuracy, f1 score) of model experiments.
- **2** Computing interrater agreement between raters who generated the intiial gold labels.

See embedded docstrings for more details.