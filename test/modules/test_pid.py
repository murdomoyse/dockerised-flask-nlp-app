import pytest
from src.pipeline import nlp
from modules.pid import personal_information_rule
import json


with open("test/test-comments.json") as fh:
    test_comments = json.load(fh)


@pytest.mark.parametrize(
    "comment, title, expected",
    [
        (
            test_comments["ground"]["Comment"],
            test_comments["ground"]["Title"],
            (2, [], [], [], [])
        ),
        (
            test_comments["named_person"]["Comment"],
            test_comments["named_person"]["Title"],
            (1, [("Dr Smith", "PERSON")], [], [("Dr Smith", "Title matched"), ("Smith", "Token in names list")], [])
        ),
        (
            test_comments["named_nationality"]["Comment"],
            test_comments["named_nationality"]["Title"],
            (1, [("Brazilian", "NORP")], [], [], [])
        ),
        (
            test_comments["named_religion"]["Comment"],
            test_comments["named_religion"]["Title"],
            (1, [("hindu", "NORP")], [], [], [])
        ),
        (
            test_comments["ner_exception_list_comment"]["Comment"],
            test_comments["ner_exception_list_comment"]["Title"],
            (2, [], [], [], [])
        ),
        (
            test_comments["social_media"]["Comment"],
            test_comments["social_media"]["Title"],
            (1, [], [], [("@Anthony", "Social Media"), ("@StPaul", "Social Media")], [("@God", "Social Media")])
        )
    ],
)
def test_pid_BAU(comment, title, expected):
    # confidence scores are not tested
    result = personal_information_rule(comment=nlp(comment), title=nlp(title))
    assert (result[0], result[1], result[2], result[4], result[5]) == expected
