from pipeline import nlp, matcher
from helpers.common_functions import result_code_mappers
from modules.profanity import profanity_rule
from modules.pid import personal_information_rule
from typing import Dict, Union
import numpy as np
import logging

log = logging.getLogger(__name__)

class HardRules:
    """Class to enforce hard moderation rules on user generated comments"""

    def __init__(self, comment: str, title: str):
        """Instantiate HardRules object.

        Args:
          comment (str): The comment to be validated
          title (str): Comment title to be validated

        Returns:
          HardRules object
        """
        self.comment = nlp(comment)
        self.title = nlp(title)
        log.debug("SpaCy objects created")

        self.words = [word.text for word in self.comment] \
             + [word.text for word in self.title]

    def apply(self) -> Dict[int, Dict[str, Union[int, str, Dict[str, str]]]]:
        """Validate all of the hard rules

        Returns:
          results (dict): results for each rule applied to the comment. 0 for pass, 1 for
                          fail, 2 for flag for review
        """

        self.profanity_rule_results = profanity_rule(self.words)
        log.debug("profanity rule applied")
        self.pid_rule_results = personal_information_rule(self.comment, self.title)
        log.debug("PID rule applied")

        self.results = {
            1: {
                "Rule": "Profanity_Detection",
                "Code": self.profanity_rule_results[0],
                "Reason": result_code_mappers(self.profanity_rule_results[0]),
                "Details": {"Profane words": self.profanity_rule_results[1]},
            },
            2: {
                "Rule": "Personal_Information_Detection",
                "Code": self.pid_rule_results[0],
                "Reason": result_code_mappers(self.pid_rule_results[0]),
                "Details": {
                    "Matched comment entities": str(self.pid_rule_results[1]),
                    "Matched title entities": str(self.pid_rule_results[2]),
                    "Entity confidences": str(self.pid_rule_results[3]),
                    "Comment patterns": str(self.pid_rule_results[4]),
                    "Title patterns": str(self.pid_rule_results[5]),
                },
            },
        }
        return self.results
