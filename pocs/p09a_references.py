"""Corpus entièrement FICTIF. Validation structurelle, pas de consultation juridique."""
from datetime import date
from .common import check

CORPUS = {
    "DEMO-ART-1": {"country": "DEMO", "start": "2025-01-01", "end": "2027-01-01",
                   "text": "Dans cet univers fictif, le délai de réponse est de dix jours.",
                   "source": "fixture://corpus-valide/DEMO-ART-1", "trusted": True},
    "DEMO-OLD": {"country": "DEMO", "start": "2020-01-01", "end": "2021-01-01",
                 "text": "Ancienne règle fictive.", "source": "fixture://corpus-valide/DEMO-OLD", "trusted": True},
}


def verify(citation, country, at):
    if not isinstance(citation, dict) or not isinstance(citation.get("id"), str):
        return False, "format_reference_invalide"
    if not isinstance(country, str) or not isinstance(at, str):
        return False, "contexte_invalide"
    try:
        requested_date = date.fromisoformat(at)
    except ValueError:
        return False, "date_invalide"
    ref = CORPUS.get(citation.get("id"))
    if not ref or not ref["trusted"]:
        return False, "reference_absente_ou_non_approuvee"
    if ref["country"] != country:
        return False, "mauvaise_juridiction"
    if not date.fromisoformat(ref["start"]) <= requested_date < date.fromisoformat(ref["end"]):
        return False, "version_inapplicable"
    quote = citation.get("quote", "")
    if not isinstance(quote, str) or not quote or quote not in ref["text"]:
        return False, "citation_alteree"
    return True, ref["source"]


def run():
    valid = {"id": "DEMO-ART-1", "quote": CORPUS["DEMO-ART-1"]["text"]}
    cases = {"valide": verify(valid, "DEMO", "2026-01-01")[0],
             "invente": verify({"id": "ARTICLE-999", "quote": "x"}, "DEMO", "2026-01-01")[0],
             "altere": verify({"id": "DEMO-ART-1", "quote": "mille jours"}, "DEMO", "2026-01-01")[0],
             "autre_pays": verify(valid, "AUTRE", "2026-01-01")[0],
             "expire": verify(valid, "DEMO", "2028-01-01")[0]}
    check(cases == {"valide": True, "invente": False, "altere": False, "autre_pays": False, "expire": False},
          "Référence invalide acceptée")
    return {"corpus": "FICTIF", "controles": cases,
            "limite": "une citation exacte ne prouve pas l'interprétation"}
