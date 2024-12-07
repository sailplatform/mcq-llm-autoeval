"""
utils.py

This file has two major sections:

FILE READ/WRITE HELPERS:
  This section implements various helper functions for reading and writing
  .json, .yaml, and .txt files.
  The following functions are implemented:
    - read_json: Loading .json.
    - write_json: Saving .json.
    - read_yaml: Loading .yaml.
    - read_file: Loading .txt.

MODEL-RUNNING FUNCTIONS:
  This section implements functions required for running a model and generating
  criterion evaluations for questions.
  The following functions are implemented:
    - get_model: Fetches the model constructor for the experiment.
    - run_model: Performs experiment and generates output.
    - eval: Helper used by run_model to compute model's criterion rating 
            for question.
"""

###############################################################################

import json
import yaml
import importlib
import inspect
from models.model_abstract import Model
import pandas as pd
import os
from tqdm import tqdm
from typing import *

###############################################################################

###########################
# FILE READ/WRITE HELPERS #
###########################

def read_json(path: str):
    """
    Generates data structure of json file at path.
    Useful for reading mcq files.

    Args:
        path (str): Path to json file.

    Returns:
        _type_: Output. Type can vary based on json.
    """
    with open(path, 'r') as file:
        return json.load(file)
    
def write_json(path: str, 
               contents) -> None:
    """
    Writes contents to a json file at path.
    Useful for saving model outputs.

    Args:
        path (str): Path to json file.
        contents (_type_): Data to be written to json file.
    """
    with open(path, 'w', encoding="utf-8") as outfile:
          json.dump(contents, outfile, indent=4)
    
def read_yaml(path: str):
    """
    Generates data structure of yaml file at path.
    Useful for reading model config files.

    Args:
        path (str): Path to yaml file.

    Returns:
        _type_: Output. Type can vary based on yaml.
    """
    with open(path, 'r') as file:
        return yaml.safe_load(file)
    
def read_file(path: str) -> str:
    """
    Reads the data from a file at path. Typically used for .txt files.

    Args:
        path (str): Path to file.

    Returns:
        str: Contents from file.
    """
    with open(path, 'r') as file:
        return file.read()
    
###############################################################################

###########################
# MODEL-RUNNING FUNCTIONS #
###########################
        
def get_model(model_module_name: str) -> Type[Model]:
    """
    Given a model module name, returns the constructor for a model
    that inherets from abstract parent class Model.

    Args:
        model_module_name (str): Model module. Ex: models.model_gpt.

    Raises:
        NotImplementedError: If the model module contains no class inheriting
                             from Model

    Returns:
        Type[Model]: Constructor for a model inheriting from the abstract
                     parent class Model.
    """

    # Dynamically import the model module at runtime.
    model_module = importlib.import_module(model_module_name)

    # Loop through classes in module. Return subclass of Model once found.
    for name, obj in inspect.getmembers(model_module):
        if (inspect.isclass(obj) and issubclass(obj, Model)):
            return obj
        
    # No subclass of model found in model module.
    raise NotImplementedError(f"Module {model_module_name} doesn't implement Model subclass.")

def run_model(Model_Class: Type[Model], 
              in_directory: str, 
              out_directory: str,
              gold_path: str, 
              criteria_string: str,
              force_eval: bool) -> None:
    """
    Main method for running an experiment. Given a model, a directory of mcqs,
    an output directory, and criteria, this method will use the model to
    generate evaluations for any question-criteria pair which have a
    corresponding label in the human-generated gold labels.

    Progress is saved after each evaluation. Running this method will not
    generate any evaluations if they already exist in the output directory.
    In other words, progress is saved if a run is interrupted.

    Args:
        Model_Class (Type[Model]): Constructor for model to use for experiment.
        in_directory (str): Path to directory containing multiple-choice questions (mcqs)
        out_directory (str): Path to directory to store results from experiment. If path
                             doesn't exist, it will be created at runtime.
        gold_path (str): Path to gold labels CSV.
        criteria_string (str): String to decide what criteria to evaluate. For example,
                               "1245" would evaluate criteria 1, 2, 4, and 5.
        force_eval (bool): When True, all selected criteria will be evaluated 
                           for every question. Otherwise, for each question, 
                           only criteria with a corresponding gold label will
                           be evaluated.

    Side Effects:
        If out_directory does not exist, it will be created.
        Results csv is stored in "out_directory/evaluation.csv".
        Full message logs are stored in "out_directory/responses/criteria_*/".
    """

    # Parse criteria string to generate list of criteria to evaluate
    criteria = sorted(list({c for c in criteria_string if c.isdigit()}))
    if len(criteria) == 0:
        return
    
    # Initialize evaluations dataframe 
    try: # (Try loading from in-progress csv from out_directory)
        df = pd.read_csv(os.path.join(out_directory, "evaluation.csv"), dtype=str)
    except:
        df = pd.read_csv(gold_path, dtype=str)
        # Initialize auto columns
        auto_cols = [f"auto {i}" for i in range(1, 6)]
        for col in auto_cols:
            df[col] = None

    # Iterate over questions and generate responses for each criterion
    for questionID in tqdm(df['questionID']):
        for crit in criteria:

            # Evaluate if:
            # - questionID corresponds to a question.json file, and
            # - questionID has not been auto evaluated for this criterion, and
            # - questionID has corresponding gold label, OR force_eval enabled.
            in_file_path = os.path.join(in_directory, f"{questionID}.json")
            if (os.path.isfile(in_file_path) and 
                pd.isna(df.loc[df["questionID"]==questionID,f"auto {crit}"].iloc[0]) and
                ((not pd.isna(df.loc[df["questionID"]==questionID,f"criteria {crit}"].iloc[0])) 
                  or force_eval)):
    
                # Get mcq
                mcq = read_json(in_file_path)
                
                # Get model's evaluation for this mcq and criterion
                model_output, mcq_eval = None, None
                for _ in range(5):
                    model_output, mcq_eval = eval(Model_Class, mcq, crit)
                    
                    # Make sure model's rating is indeed a number
                    if mcq_eval.isdigit():
                        break
                if mcq_eval == None:
                    print(f"Model failed to produce proper output on question {questionID} criterion {crit} after 5 attempts. Skipping...")
                    continue

                # Update evaluations dataframe
                df.loc[df["questionID"]==questionID,f"auto {crit}"] = mcq_eval
                
                # Create output response directory if it doesn't exist
                out_response_path = os.path.join(out_directory, f"responses/criteria_{crit}")
                if not os.path.exists(out_response_path):
                    os.makedirs(out_response_path)

                # Create response file (full message log)
                write_json(os.path.join(out_response_path, f"{questionID}.json"), model_output)

                # Update evaluation results csv
                df.to_csv(os.path.join(out_directory, "evaluation.csv"))

# Generates response for criteria
def eval(Model_Class: Type[Model], 
         mcq, 
         crit: str) -> Tuple[list, str]:
    """
    Given a model, mcq, and criteria, this function computes the model's
    evaluation of the mcq for this criteria.

    Args:
        Model_Class (Type[Model]): Constructor for model used for evaluation.
        mcq (_type_): Multiple-choice question data. Type is normally a dict,
                      but this is not strictly required.
        crit (str): Criterion being evaluated

    Returns:
        Tuple[list, str]: Message log (list) and criterion rating (string)
    """

    # Initialize model with system prompt
    prompts_directory = f"./config/prompts/criteria_{crit}"
    system_prompt = read_file(f"{prompts_directory}/system_{crit}.txt")
    model = Model_Class(system_prompt)
    
    # Get model's reasoning to the first user prompt
    user_question_prompt = read_file(f"{prompts_directory}/question_{crit}.txt")
    user_question_prompt = user_question_prompt.replace("{QUESTION}", json.dumps(mcq, sort_keys=False, indent=4))
    model.get_response(user_question_prompt)
    
    # Get model's answer for final criterion rating
    principle = read_file(f"{prompts_directory}/principle_{crit}.txt")
    rating = model.get_response(principle)
    _, messages = model.get_chat_log()
    messages.insert(0, {"role": "system", "content": system_prompt})

    return messages, rating.strip()

###############################################################################
