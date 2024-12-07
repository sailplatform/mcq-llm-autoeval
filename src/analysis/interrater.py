"""
interrater.py

This file implements the necessary code to calculate interrater agreement
between raters for the initial publication labels.
Interrater agreement is computed using Krippendorff's Alpha.
Results are saved in "./data/gold_labels/interrater_agreement/scores.json".

This file is structured as follows:
  Helper Functions:
    - read_csv: Given a path, returns a 2D list of a CSV file's contents.
    - get_ratings: Returns a dictionary of rater ratings.

  Interrater Agreement Functions:
    - compute_krippendorff_alpha: Computes krippendorff's alpha across all
                                  raters for each criterion. 
    - main: Executes interrater agreement functions and compiles results into
            output file.

USAGE:
  From the mcq-eval/ directory, run 
    "python src/analysis/interrater.py --help" 
  for a list of optional parameters.
  By default, rater ratings come from
    "./data/gold_labels/interrater_agreement/rater_ratings.csv"
  and results are stored in
    "./data/gold_labels/interrater_agreement/scores.json"
"""

###############################################################################

import typer
import numpy as np
import csv
import krippendorff
import json

###############################################################################

####################
# HELPER FUNCTIONS #
####################

def read_csv(path: str) -> list:
    """
    Given a file path to a CSV, returns a 2D list of its contents

    Args:
        path (str): Path to CSV file

    Returns:
        list: 2D list of CSV contents
    """
    # Initialize results list
    result = []
    with open(path, newline='') as csvfile:
        csvreader = csv.reader(csvfile)

        # Add each row one at a time into results list
        for row in csvreader:
            result.append(row)
    return result


def get_ratings(ratings_path: str) -> dict:
    """
    Returns a dictionary of rater ratings given path to ratings CSV.
    Missing values are represented using np.nan.

    Args:
        ratings_path (str): Path to CSV file of rater ratings.
    
    Returns:
        dict: Dictionary of ratings in the following format:
                {
                    "criteria 1":
                        {
                        "rater 1": [#, #, #, #, ...],
                        "rater 2": [#, #, #, #, ...],
                        ...
                        },
                    "criteria 2":
                        ...
                }
    """
    # Read off raw data and initialize useful locals
    ratings_sheet = read_csv(ratings_path)
    criteria = [1,2,3,4,5]
    raters = [1,2,3]

    # Initialize ratings dictionary
    ratings = {f"criteria {i}": 
                {f"rater {j}": [] for j in raters} 
              for i in criteria}
    
    # Iterate through each row and add data to ratings dictionary
    for row in ratings_sheet[2:]:
        for crit in criteria:
            for rater in raters:

                # Compute index in row corresponding to criterion and rater
                rating_index = 4*(crit-1) + rater

                # Empty cells are represented by np.nan
                rating = row[rating_index] if row[rating_index] != '' else np.nan
                
                # Add data to ratings dictionary
                ratings[f"criteria {crit}"][f"rater {rater}"].append(rating)
    
    return ratings

###############################################################################

##################################
# INTERRATER AGREEMENT FUNCTIONS #
##################################

def compute_krippendorff_alpha(ratings_path: str) -> dict:
    """
    Computes krippendorff's alpha across all raters for each criterion. 

    Args:
        ratings_path (str): Path to CSV file of rater ratings.

    Returns:
        dict: Dictionary mapping criteria to krppendorff's alpha.
    """
    # Fetch annotator ratings
    full_ratings = get_ratings(ratings_path)

    # Initialize results dictionary
    results = {}

    # Iterate over each criterion to compute krippendorff's alpha
    for crit in range(1, 6):

        # Build up 2D list where rows represent raters, columns are questions
        ratings_formatted = []
        for _, ratings in full_ratings[f"criteria {crit}"].items():
            ratings_formatted.append(ratings)
        
        # Compute krippendorff's alpha and add to results dictionary
        alpha = krippendorff.alpha(reliability_data=ratings_formatted, level_of_measurement="nominal")
        results[f"criteria {crit}"] = alpha

    return results

###############################################################################

#################
# MAIN FUNCTION #
#################

app = typer.Typer()
    
@app.command()
def main(ratings_path: str = "./data/gold_labels/interrater_agreement/rater_ratings.csv",
         output_path: str = "./data/gold_labels/interrater_agreement/scores.json") -> None:
    """
    Executes interrater agreement functions using rater ratings at ratings_path
    and compiles results into output file at output_path.

    USAGE:
    From the mcq-eval/ directory, run 
        "python src/analysis/interrater.py --help" 
    for a list of optional parameters.
    By default, rater ratings come from
        "./data/gold_labels/interrater_agreement/rater_ratings.csv"
    and results are stored in
        "./data/gold_labels/interrater_agreement/scores.json"
    """
    # Compute krippendorff's alpha for each criterion
    krippendorff_results = compute_krippendorff_alpha(ratings_path)

    # Write results to output file
    results = {"krippendorff": krippendorff_results}
    with open(output_path, 'w', encoding="utf-8") as outfile:
        json.dump(results, outfile, indent=4)

if __name__ == "__main__":
    app()