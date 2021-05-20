"""
Run this file to the app against a subset of comments to evaluate performance,
THIS REQUIRES ACCESS TO THE DB WITH THE COMMENTS
"""
import sys
import os
import numpy as np
sys.path.append(os.path.abspath("../.."))
from src.dev.analysis import data
import matplotlib.pyplot as plt
from src.hardrules import HardRules
from sklearn.metrics import ConfusionMatrixDisplay


def evaluate(most_recent=50000):
    """
    Produce confusion matrices for automated rules run against a subset of comments
    
    Returns
        results (dict): confusion matrices for all the automated rules
    """

    # Take the most recent comments to evaluate
    sample = data[["Comment_Title", "Comment_Text", "Rejection_Reason"]].tail(most_recent)
    start_index = sample.index[1]

    # This is pretty inefficient/slow as HardRules is not designed for batch requests + iterrows is pants
    for idx, row in sample.iterrows():
        applied_rules = HardRules(comment=row["Comment_Text"], title=row["Comment_Title"]).apply()

        # Fill in results
        for rule_index, rule in applied_rules.items():
            sample.loc[idx, rule["Rule"]] = rule["Code"]
        
        # Add classifier outputs
        sample.loc[idx, "pid_classifier"] = applied_rules[5]["Details"]["Classifier output"]["result"]

        # To show progress
        print(f"{idx - start_index}/{most_recent} reviews processed")
    
    def conf_matrix(rule: str, Rejection_Reasons: list, df=sample):
        """Construct confusion matrix from custom subset

        Args
            rule (str): Title of rule to evaluate
            Rejection_Reason (list): string equivalent(s) of the rule in rejection reason
            df (pd.DataFrame): Dataframe with results from HardRules as defined above

        Returns
            confusion matrices (dict): Confusion matrix of results of rules
        """
        # Only evaluate against passed comments or ones that have been failed for this rule since
        # comments can only be failed for one reason.
        subset = df.loc[
            df["Rejection_Reason"].isin(Rejection_Reasons) | df["Rejection_Reason"].isna()
        ]

        # Pid doesn't pass anything atm so can't have 0 results
        if rule == "Personal_Information_Detection":
            TP = len(subset.loc[
                subset["Rejection_Reason"].isin(Rejection_Reasons) & (subset[rule] == 1)
            ])
            TN = len(subset.loc[
                subset["Rejection_Reason"].isna() & (subset[rule] == 2)
            ])
            FP = len(subset.loc[
                subset["Rejection_Reason"].isna() & (subset[rule] == 1)
            ])
            FN = len(subset.loc[
                subset["Rejection_Reason"].isin(Rejection_Reasons) & (subset[rule] == 2)
            ])
        else:
            TP = len(subset.loc[
                subset["Rejection_Reason"].isin(Rejection_Reasons) & 
                ((subset[rule] == 1) | (subset[rule] == 2))
            ])
            TN = len(subset.loc[
                subset["Rejection_Reason"].isna() & (subset[rule] == 0)
            ])
            FP = len(subset.loc[
                subset["Rejection_Reason"].isna() & ((subset[rule] == 1) | (subset[rule] == 2))
            ])
            FN = len(subset.loc[
                subset["Rejection_Reason"].isin(Rejection_Reasons) & (subset[rule] == 0)
            ])

        return np.array([[TN, FP], [FN, TP]])

    results = {
        "All_Caps" : conf_matrix("All_Caps", ["All caps comment"]),
        "Language_Detection" : conf_matrix("Language_Detection", ["Foreign Language"]),
        # "URL_Rule" : "There is no rejection reason corresponding to this so a confusion matrix can't be made",
        # # The profanity list used by the app and moderators is different
        # "Profanity_Detection" : conf_matrix("Profanity_Detection", ["Offensive Language"]), 
        "Personal_Information_Detection" : conf_matrix(
            "Personal_Information_Detection",
            ["Feedback on individuals", "Personal details", "Names in review"]
        ),
    }

    return results

if __name__=="__main__":
    results = evaluate()

    for rule, confmat in results.items():
        ConfusionMatrixDisplay(confmat, display_labels=["NO_PID", "PID"]) \
            .plot(cmap=plt.cm.Blues).figure_.savefig(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{rule}.png")
            )


