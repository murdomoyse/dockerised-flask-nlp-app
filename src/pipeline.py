import en_core_web_lg
from spacy_langdetect import LanguageDetector
from spacy.matcher import Matcher
import os

firstnames_list_path = os.path.join(os.path.dirname(__file__), "data", "firstnames-list.csv")
with open(firstnames_list_path, "r", encoding="latin-1") as f:
    names = [line.rstrip() for line in f]

nlp = en_core_web_lg.load()
nlp.add_pipe(LanguageDetector(), name="language_detector", last=True)
matcher = Matcher(nlp.vocab)
matcher.add("URL", None, [{"LIKE_URL": True}])
# Personally identifiable description
matcher.add(
    "Title matched",
    None,
    [
        {"TEXT": {"REGEX": r"(?i)(?:mrs|mr|miss|dr|ms)[.]?"}},
        {"TEXT": {"REGEX": r"[A-Z][a-z]*"}},
    ],
)
matcher.add(
    "Personal Description",
    None,
    [
        {"TAG": "JJ", "TEXT": {"IN": ["blonde", "ginger"]}}
    ],  # Adjectives associated with hair colour
    [
        {"TAG": "JJ"},
        {"TAG": "NN", "TEXT": {"IN": ["hair", "glasses"]}},
    ],  # Explicit characteristics
)
matcher.add("Token in names list", None, [{"TAG": "NNP", "LOWER": {"IN": names}}])
# http://regexlib.com/UserPatterns.aspx?authorid=d95177b0-6014-4e73-a959-73f1663ae814
# UK mobile phone number, with optional +44 national code.
# Allows optional brackets and spaces at appropriate positions.
matcher.add(
    "Telephone number",
    None,
    [{"TEXT": {"REGEX": r"(\+44\s?7\d{3}|\(?07\d{3}\)?)\s?\d{3}\s?\d{3}$"}}],
)
# https://emailregex.com
matcher.add(
    "Email",
    None,
    [{"TEXT": {"REGEX": r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"}}],
)
# https://stackoverflow.com/questions/164979/regex-for-matching-uk-postcodes
# Please note this just detects the UK postcode format and cannot verify postcodes, which are
# constantly changing and arbitrarily complex.
matcher.add(
    "UK postcode",
    None,
    [
        {
            "TEXT": {
                "REGEX": r"""(([A-Z][A-HJ-Y]?\d[A-Z\d]?|ASCN|STHL|TDCU|BBND|[BFS]IQQ|PCRN|TKCA)?
\d[A-Z]{2}|BFPO ?\d{1,4}|(KY\d|MSR|VG|AI)[ -]?\d{4}|[A-Z]{2}?\d{2}|GE ?CX|GIR ?0A{2}|SAN ?TA1)$"""
            }
        }
    ],
)

# Social media handle regex/detector (matches words starting with @)
matcher.add(
    "Social Media",
    None,
    [{"TEXT": {"REGEX": r"@\S+"}}],
)




