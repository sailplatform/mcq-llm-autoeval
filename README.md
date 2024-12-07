# Benchmarking Large Language Models on Multiple-Choice Question Quality

## Table of Contents
- [Overview](#overview)
- [File Structure](#file-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

## Overview

This codebase implements an intuitive pipeline for utilizing Large Language Models (LLMs) to evaluate the quality of Multiple Choice Questions (MCQs) by rating them against a set of quality criteria.

At the time of creating this project, there does not exist an easy-to-use repository for automatically evaluating the quality of MCQs without human input. There has been recent literature exploring the capabilities of LLMs to automatically generate MCQs, but such systems still need human evaluators to guage the performance of the system. 

## Attribution

Aninditha Ramesh, Arav Agarwal, Jacob Arthur Doughty, Ketan Ramaneti, Jaromir Savelka, and Majd Sakr. 2024. A Benchmark for Testing the Capabilities of LLMs in Assessing the Quality of Multiple-choice Questions in Introductory Programming Education. In Proceedings of the 2024 on ACM Virtual Global Computing Education Conference V. 1 (SIGCSE Virtual 2024). Association for Computing Machinery, New York, NY, USA, 193–199. https://doi.org/10.1145/3649165.3690123

```
@inproceedings{10.1145/3649165.3690123,
author = {Ramesh, Aninditha and Agarwal, Arav and Doughty, Jacob Arthur and Ramaneti, Ketan and Savelka, Jaromir and Sakr, Majd},
title = {A Benchmark for Testing the Capabilities of LLMs in Assessing the Quality of Multiple-choice Questions in Introductory Programming Education},
year = {2024},
isbn = {9798400705984},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3649165.3690123},
doi = {10.1145/3649165.3690123},
abstract = {There has been a growing interest in utilizing large language models (LLMs) for numerous educational applications. Recent studies have focused on the use of LLMs for generating various educational artifacts for programming education, such as programming exercises, model solutions, or multiple-choice questions (MCQs). The ability to efficiently and reliably assess the quality of such artifacts, both automatically and human generated, has become of paramount importance. Hence, there is a pressing need to develop and make available robust benchmarks. In this paper, we investigate an example use case of assessing the quality of programming MCQs. To that end, we carefully curated a data set of 192 MCQs annotated with quality scores based on a rubric that evaluates crucial aspects such as, e.g., their clarity, the presence of a single correct answer, and the quality of distractors. The results show that the task presents a considerable challenge even to the state-of-the-art LLMs and, hence, further research is needed. To further such research efforts in this important area we release the dataset as well as the extensible evaluation pipeline to the public.},
booktitle = {Proceedings of the 2024 on ACM Virtual Global Computing Education Conference V. 1},
pages = {193–199},
numpages = {7},
keywords = {assessments, automated evaluation, claude, computing education, gpt-4, large language models, llama, llms, mcqs, multiple choice questions},
location = {Virtual Event, NC, USA},
series = {SIGCSE Virtual 2024}
}
```

## File Structure

This repository is divided into three separate folders containing separate but important parts of the pipeline:


```
├── config
├── data
└── src
```

* `src` contains the source code enabling automatic MCQ evaluation. `src/models` implements an abstract interface for working with arbitrary LLMs, whereas `src/analysis` contains scripts for assessing both interrater reliability as well as f1 and accuracy metrics for hte current dataset.
* `data` contains the data utilized to evaluate each model on MCQ quality. `data/gold_labels` contains the human-generated and verified quality scores for each of the questions considered. `data/mcqs` contains the set of questions evaluate. `data/model_labels` contains the evaluation output of running the pipeline across existing LLMs reported in the paper for `llama-3`, `gpt-4-0613`, and `claude-3-opus-20240229`. Each of these folders contains `prediction_scores.json`, the quality metrics per criterion, `evaluation.csv`, a condensed CSV of the model's outputs, and `responses`, which contains not only the evaluation output but also the raw rationale from relevant models.
* `config` contains configuration parameters for the generation output of each model, as well as the prompts utilized to judge each question based on the criteria reported in the paper.


## Installation

In order to install the dependencies for this project, create a Python vitual environment and use the following while inside the cloned repository:

```
pip install -r requirements.txt
```



## Usage

The main MCQ Evaluation pipline can be run from ``main.py``.
Use ``python src/main.py --help`` for a list of required and optional parameters. For convenience, they are also summarized below:
- ``model_module_name`` (REQUIRED): The module that implements the LLM to run the evaluation experiment.
- ``output_path`` (REQUIRED): The path to the directory where experiment results will be saved.
- ``mcqs`` (optional): The path to the directory containing the MCQs to be evaluated. Defaults to ``"./data/mcqs"``.
- ``criteria`` (optional): String representing what criteria to evaluate. Defaults to "12345" corresponding to running an evaluation on criteria 1 through 5.
- ``force_eval`` (optional): By default, LLMs will only produce a criterion rating for question-criterion pairs that have a corresponding gold label. This behavior can be overwridden using the --force-eval flag, in which case, all questions will be evaluated for all criteria.

#### Placing API Keys


To use the GPT, Claude, and LLama models, create ``api_keys.json`` at the root of the repository containing the following keys:
```json
{
    "openai_api_key" : "your_key_here",
    "anthropic_api_key": "your_key_here",
    "llama3_hgface_api": "your_key_here"
}
```

#### Example Usage

To run the GPT model on all question-criterion pairs with a corresponding gold label and save the results to ``data/model_labels/gpt-4-0613``:

```
python src/main.py models.model_gpt data/model_labels/gpt-4-0613
```

To run the Claude model for criteria 1, 4, and 5 for questions-criterion pairs with a corresponding gold label. Questions from the ``data/my_mcqs`` directory will be used, and results will be saved to ``data/temp``. **NOTE:** ``data/my_mcqs`` does not exist by default. **Note:** This will not work as-is. 


```
python src/main.py models.model_claude data/temp --criteria 145 --mcqs data/my_mcqs
```

To run the Llama 3 model for ALL criteria for all questoins, regardless of whether a gold label exists or not:

```
python src/main.py models.model_llama3 data/model_labels/llama-3_ALL --force-eval
```


## Contributing

### Adding an Evaluation Criteria

There are currently five MCQ quality criteria for this pipeline. These criteria assess:
- Is there enough information to answer the MCQ?
- Does the MCQ have a correct answer in the options, and does the answer key indicate it as the correct answer?
- Are each of the options unique?
- Is the MCQ free from obviously-wrong options?
- If code is present in the MCQ, is it logically and syntactically correct?


In order to add a criteria, you must simply create a folder under `prompts` with a separate text file for the following:

- The system prompt: This explains to the LLM the structure of MCQs and its task in this program.
- The question to be asked: This presents a question to the LLM and prompts it to reason about how the question fares against the quality criterion. This prompt must contain the string "{QUESTION}" which is replaced with the current question being evaluated. M
- The rating scale / "principle": Once the LLM has reasoned about the question, this prompt asks the LLM to give a single categorical rating for where the MCQ falls with respects to the specific quality criterion. For example, "Does the question provide enough information to arrive at an answer: Yes/No."


Afterwards, be sure to update the ``criteria`` default value in the ``main()`` function in ``src/main.py``, as well as the default value of the ``num_criteria`` parameter in the ``main()`` function in ``src/analysis/predictions.py``.


### Adding more Questions

This codebase currently contains 192 multiple choice questions, but more can easily be added. To add a question:

1. Add appropriate question JSON files to the `data/mcqs` folder, following the below format:

```json
{
    "question": "QUESTION STEM HERE",
    "choices": [
        {
            "choice": "CHOICE TEXT (most often 'A')",
            "correct": "true/false"
        },
        {
            "choice": "CHOICE TEXT (most often 'B')",
            "correct": "true/false"
        },
        {
            "choice": "CHOICE TEXT (most often 'C')",
            "correct": "true/false"
        }
    ]
}
```


2. Provide any relevant gold labels to `data/gold_labels`. Do so by creating a new CSV file in ``data/gold_labels/``. The CSV file should have the following columns:
``questionID``, ``criteria 1``, ``criteria 2``, ... ``criteria n``
where ``n`` is the number of criteria.
