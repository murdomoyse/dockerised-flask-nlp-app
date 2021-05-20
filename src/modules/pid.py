from pipeline import matcher, nlp
from typing import List, Tuple, Dict, Union
from collections import defaultdict
import re


def get_matches(doc, matcher=matcher, nlp=nlp) -> List[Tuple[str, str]]:
    """Return matched phrases from a spacy matcher and a spacy doc

    Args:
        doc (spaCy Doc) : spacy doc object
        matcher (SpaCy Matcher) : spacy Matcher object
        nlp (spaCy language model) : spacy language model object

    Returns:
        List : List of strings of matches found in the doc
    """
    matches = [
        (doc[start:end].text, nlp.vocab.strings[match_id])
        for match_id, start, end in matcher(doc)
    ]

    return matches


def personal_information_rule(
    comment,
    title,
    ner_labels=["PERSON", "NORP"],
    ner_exceptions=[
        "scan",
        "Scan",
        "Dentist",
        "Dentists",
        "Dental",
        "dentist",
        "dentists",
        "Surgery",
        "surgery",
        "Hospital",
        "hospital",
        "ward",
        "Ward",
        "Healthcare",
        "Optician",
        "optician",
        "Opticians",
        "opticians",
        "Pharmacist",
        "Royal",  # Usually hospital names
        "Chemist",
        "Practice",
        "practice",
        "G. P.",
        "g. p.",
        " Road",
        "St ",  # St. Marys or saints are usually hospital names
        "A&E"
    ],
) -> Tuple[
    int,
    List[Tuple[str, str]],
    List[Tuple[str, str]],
    List[Tuple[str, str]],
    List[Tuple[str, str]],
]:
    """
    Look for personally identifiable info, e.g. names, contact information, distinguishing
    characteristics

    Args:
        comment (spaCy Doc) : spacy doc object for the comment
        title (SpaCy doc) : spacy doc object for the title

    Returns:
        result (int) : 0/1/2 for pass/fail/human moderation
        matched_comment_entities (list) : Entities from NER found in comment
        matched_title_entities (list) : Entities from NER found in title
        comment_patterns (list) : Patterns found in comment (ie regex/hardcoded matches)
        title_patterns (list) : Patterns found in title (ie regex/hardcoded matches)
    """
    # People or nationality/religious persuasion is detected in comment and title.
    # Detected entities containing the exceptions are excluded.
    matched_comment_entities = [
        (ent.text, ent.label_)
        for ent in comment.ents
        if ent.label_ in ner_labels
        and any(exception in ent.text for exception in ner_exceptions)
        is False  # This is True if an exception is present in the entity
    ]
    matched_title_entities = [
        (ent.text, ent.label_)
        for ent in title.ents
        if ent.label_ in ner_labels
        and any(exception in ent.text for exception in ner_exceptions) is False
    ]

    # Confidence scores are calculated via beam trace
    comment_confidences = get_beam_trace_confidence_scores(
        [comment.text], ner_labels=ner_labels, ner_exceptions=ner_exceptions
    )
    title_confidences = get_beam_trace_confidence_scores(
        [title.text], ner_labels=ner_labels, ner_exceptions=ner_exceptions
    )

    # Pattern matches
    comment_patterns = get_matches(comment)
    title_patterns = get_matches(title)

    # Default to send to human moderation
    result = 2

    # Any detected items fails the comment
    if (
        matched_comment_entities
        or matched_title_entities
        or comment_patterns
        or title_patterns
    ):
        result = 1

    confidences = (
        []
        if comment_confidences is False and title_confidences is False
        else comment_confidences + title_confidences
    )

    return (
        result,
        matched_comment_entities,
        matched_title_entities,
        confidences,
        comment_patterns,
        title_patterns,
    )


def get_beam_trace_confidence_scores(
    texts: list,
    ner_labels: list,
    ner_exceptions: list,
    nlp=nlp,
    beam_width=16,
    beam_density=0.0001,
) -> List[Dict[str, Union[str, float]]]:
    """
    https://stackoverflow.com/questions/59877735/how-to-get-probability-of-prediction-per-entity-from-spacy-ner-model
    Get beam trace confidence scores for ner as described in the link.
    Note these confidence scores may not line up exactly with the entities detected
    by the normal NER pipeline in spaCy; sometimes very low probability tags are shown.

    Args
        texts (list) :
        nlp (spaCy language model) : language model to implement beam trace
        beam_width (int) :
        beam_density (int) :

    Returns
        confidences (list): Confidence scores for detected entities
    """
    docs = list(nlp.pipe(texts, disable=["ner"]))
    beams = nlp.entity.beam_parse(
        docs, beam_width=beam_width, beam_density=beam_density
    )

    entity_scores = defaultdict(float)
    for doc, beam in zip(docs, beams):
        for score, ents in nlp.entity.moves.get_beam_parses(beam):
            for start, end, label in ents:
                if label in ner_labels and doc[start:end].text not in ner_exceptions:
                    entity_scores[(doc[start:end], label)] += score

    confidences = [
        {"text": k[0], "label": k[1], "prob": v} for k, v in entity_scores.items()
    ]

    return confidences
