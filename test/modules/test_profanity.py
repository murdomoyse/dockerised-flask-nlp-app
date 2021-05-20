import pytest
from src.pipeline import nlp
from modules.profanity import profanity_rule


@pytest.mark.parametrize(
    "submission_words, expected",
    [
        (
            [
                word.text
                for word in nlp(
                    """
                This is a good practice with attentive staff who always make me feel massively good
                """
                )
            ],
            (0, []),
        ),
        (
            [
                word.text
                for word in nlp(
                    """
                load of rubbish don't go there at the risk of getting gerrymandering
                """
                )
            ],
            (1, ["gerrymandering"]),
        ),
    ],
)
def test_profanity_BAU(submission_words, expected):
    assert profanity_rule(submission_words) == expected
