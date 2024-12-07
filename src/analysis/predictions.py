"""
predictions.py

This file implements the code to compute the accuracy scores and
f1 scores of predicted labels against gold labels.

USAGE:
  From the mcq-eval/ directory, run 
    "python src/analysis/predictions.py --help" 
  for a list of required parameters. Required parameters are:
    - evaluation_path: Path to model predictions csv for criteria labels.
    - results_path: Where to save the prediction accuracy and f1 scores.

  Example:
    "python 
     src/analysis/predictions.py 
     data/model_labels/gpt-4-0613/evaluation.csv 
     data/model_labels/gpt-4-0613/prediction_scores.json
    "
    Would computethe accuracy and f1 scores of GPT's label predictions
    at "data/model_labels/gpt-4-0613/evaluation.csv " and store the results in
    "data/model_labels/gpt-4-0613/prediction_scores.json".
"""

###############################################################################

import typer
import pandas as pd
import json
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score

###############################################################################

####################
# HELPER FUNCTIONS #
####################

def compute_scores(evaluation_path: str, 
                   num_criteria: int) -> dict:
    """
    Given prediction labels at evaluation_path, computes accuracy scores and
    f1 scores and returns results.

    Args:
        evaluation_path (str): Path to evaluations csv file containing model's
                              criteria label predictions.
        num_criteria (int): Number of criteria.

    Returns:
        dict: Dictionary containing accuracy and f1 scores for every
              criterion.
    """

    # Initialize dataframe from evaluation csv
    df = pd.read_csv(evaluation_path)

    # Initialize results dictionary
    criteria = range(1, num_criteria + 1)
    results = {f"criteria {crit}": 
                   {"accuracy": None, 
                    "f1": None} 
                for crit in criteria}
    
    # Iterate over each criterion
    for crit in criteria:

        # Get gold labels and predicted labels
        crit_df = df[[f"criteria {crit}", f"auto {crit}"]].dropna()
        gold = crit_df[f"criteria {crit}"]
        prediction = crit_df[f"auto {crit}"]

        # Compute accuracy score and f1 scores
        accuracy = accuracy_score(gold, prediction)
        f1 = f1_score(gold, prediction, average=None).tolist()

        # Update results
        results[f"criteria {crit}"]["accuracy"] = accuracy
        results[f"criteria {crit}"]["f1"] = f1

    return results

###############################################################################

#################
# Main function #
#################

app = typer.Typer()

@app.command()
def main(evaluation_path: str,
         results_path: str,
         num_criteria: int = 5
         ) -> None:
    """
    Given prediction labels at evaluation_path, computes accuracy scores and
    f1 scores and saves the results at results_path.

    USAGE:
      From the mcq-eval/ directory, run 
        "python src/analysis/predictions.py --help" 
      for a list of required parameters. Required parameters are:
        - evaluation_path: Path to model predictions csv for criteria labels.
        - results_path: Where to save the prediction accuracy and f1 scores.

      Example:
        "python 
        src/analysis/predictions.py 
        data/model_labels/gpt-4-0613/evaluation.csv 
        data/model_labels/gpt-4-0613/prediction_scores.json
        "
        Would computethe accuracy and f1 scores of GPT's label predictions
        at "data/model_labels/gpt-4-0613/evaluation.csv " and store the results in
        "data/model_labels/gpt-4-0613/prediction_scores.json".

    Args:
        evaluation_path (str): Path to evaluations csv file.
        results_path (str): Path to save the accuracy and f1 scores.
        num_criteria (int, optional): Number of criteria
    """
    
    # Calculate accuracy score and f1 scores
    results = compute_scores(evaluation_path, num_criteria)

    # Save the results
    with open(results_path, 'w', encoding="utf-8") as outfile:
        json.dump(results, outfile, indent=4)

if __name__ == "__main__":
    app()
