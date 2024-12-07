# Data

The ``./data/`` directory contains three subdirectories:

### ``gold_labels/``

The important file here is ``initial_publication_labels.csv``, which contains the gold MCQ quality labels for each of initial set of MCQs for the set of 5 quality criteria. The file contains one column for the questionID, followed by columns for each each criterion containing the categorical rating for the criterion for the MCQ. 

There is also a directory called ``interrater_agreement`` which was used for computing interrater agreement between raters who generated the set of gold labels.

### ``mcqs/``

This directories stores MCQs to be evaluated. By default, there is a subdirectory, ``initial_publication_mcqs`` containing the initial set of MCQs at the time of releasing this repository.

MCQ files have the following form:
``mcq_questionID.json``
```json
{
    "question": "In Python, what does the equal '=' sign mean in the statement 'x = 5'?",
    "choices": [
        {
            "choice": "It means that 5 is equal to x.",
            "correct": "false"
        },
        {
            "choice": "It means that the variable x is assigning the value 5.",
            "correct": "false"
        },
        {
            "choice": "It means that the variable x is storing the value 5.",
            "correct": "true"
        }
    ]
}
```

### ``model_labels/``

This is the output directory for model evaluations. Every experiment should have its own subdirectory. For each experiment, a subdirectory will contain a ``responses/`` folder containing logs of the LLM's raw responses, as well as ``evaluation.csv`` which has columns for:

- QuestionID
- Each criteria and its gold label
- Each criteria and the model's predicted label

The initial subdirectories in ``model_labels`` (``claude-3-opus-20240229/``, ``gpt-4-0613/``, and ``llama-3``) contain a ``predictions_scores.json`` file which was computed via a separate script at ``./src/analysis/predictions.py``.