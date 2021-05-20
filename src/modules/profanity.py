from typing import Tuple, List
from config import profanity


def profanity_rule(submission_words, profanity_list=profanity) -> Tuple[int, List[str]]:
    """Check comment and title for profanity

    Args:
        submission_words (list) : list of strings to check for profanity
        profanity (list) : list of strings of profane words to check for in submission
    """
    result = [
        profane_word
        for profane_word in profanity_list
        if profane_word in submission_words
    ]
    profane_count = len(result)

    if profane_count > 0:
        return 1, result

    if profane_count == 0:
        return 0, result
