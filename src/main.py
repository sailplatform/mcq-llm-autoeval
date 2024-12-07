"""
main.py

This file implements the main function, which provides a command-line
interface for running the code.

USAGE:
From the mcq-eval/ directory, run "python src/main.py --help" for a
list of required arguments and optional parameters.

Example usage:
  "python src/main.py models.model_gpt data/model_labels/gpt-4-0613 --force-eval"
    This will run the GPT model on ALL criteria for all questions and save the
    results to data/model_labels/gpt-4-0613

  "python src/main.py models.model_claude data/temp --criteria 145 --mcqs data/my_mcqs"
    This will run the Claude model on all questions stored in data/my_mcqs for
    criteria 1, 4, and 5 that have a corresponding gold label, and save the results 
    to data/temp.
"""

###############################################################################

import typer
from models.model_abstract import Model
import utils
import os

app = typer.Typer()

@app.command()
def main(model_module_name: str,
         output_path: str, 
         mcqs: str = "./data/mcqs/initial_publication_mcqs",
         gold_path: str = "./data/gold_labels/initial_publication_labels.csv",
         criteria: str = "12345",
         force_eval: bool = False) -> None:
    """
    SUMMARY:
    Main function for running evaluation experiment. Given a
    model and output directory, the model will be run to generate
    ratings for every criterion-question pair that has a corresponding
    gold label (unless run with --force-eval).
    The input directory of multiple-choice questions (mcqs) can optionally
    be changed, and so can the set of criteria to evaluate.

    The experiment output will be saved to output_path.
      - Full ratings sheet saved to "output_path/evaluation.csv".
      - Full message logs saved to "output_path/responses/criteria_*/".

    Args:
        model_module_name (str): Name of module containing model to use for
                                 experiment. Ex: models.model_gpt.
        output_path (str): Path to output directory where results are saved.
        mcqs (str, optional): Path to input directory containing mcqs. 
                              Defaults to "./data/mcqs".
        gold_path (str, optional): Path to gold labels CSV. Defaults to
                                   "./data/gold_labels/initial_publication_labels.csv".
        criteria (str, optional): Set of criteria to evaluate, represented as a
                                  string. Defaults to "12345", which 
                                  corresponds to criteria 1, 2, 3, 4, and 5.
        force_eval (bool, optional): If enabled, all selected criteria will be
                                     evaluated for every question. Otherwise,
                                     for each question, only criteria with a
                                     corresponding gold label will be 
                                     evaluated. Defaults to False.

    Raises:
        FileNotFoundError: If the mcqs path does not exist.
    """
    
    # Check if mcq path exists.
    if not os.path.exists(mcqs):
        raise FileNotFoundError(f"mcq path '{mcqs}' does not exist.")

    # Fetch model constructor and run experiment.
    Model_Class = utils.get_model(model_module_name)
    utils.run_model(Model_Class, mcqs, output_path, gold_path, criteria, force_eval)

if __name__ == "__main__":
    app()
