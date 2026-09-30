#!/usr/bin/env python3
"""Maintenance tool for the CAISA / DLT lab bibliography.

Pure standard library (Python >= 3.11). Run from anywhere:

    python3 scripts/bibtool.py check              # validate all bib/*.bib files
    python3 scripts/bibtool.py fmt                # rewrite bib files in canonical form
    python3 scripts/bibtool.py find "emergent"    # look for existing entries (dedupe!)
    python3 scripts/bibtool.py key "Title" "Last, First and ..." 2026
    python3 scripts/bibtool.py build              # check + regenerate site/index.html
    python3 scripts/bibtool.py stats              # quick numbers per year / category

See AGENTS.md for the conventions this tool enforces.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import tomllib
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIB_DIR = ROOT / "bib"
SITE_DIR = ROOT / "site"
MEMBERS_FILE = ROOT / "lab.toml"
TEMPLATE_FILE = SITE_DIR / "template.html"
OUTPUT_HTML = SITE_DIR / "index.html"        # standalone page: open locally or host anywhere
OUTPUT_ARTIFACT = SITE_DIR / "artifact.html"  # same page without <html>/<head> wrapper, for claude.ai artifacts
OUTPUT_JSON = SITE_DIR / "data.json"
HTML_WRAPPER = (
    "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
    "<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}"
    "body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n"
    "</head>\n<body>\n{body}\n</body>\n</html>\n"
)

FILE_HEADER = (
    "% Publications of the CAISA Lab / Data & Language Technologies Lab (b-it, University of Bonn)\n"
    "% Year: {year}. One entry per publication; see AGENTS.md before editing.\n"
    "% This file is normalised by `python3 scripts/bibtool.py fmt` (entries sorted by key).\n"
)

# Canonical field order when writing entries. Unknown fields go last, alphabetically.
FIELD_ORDER = [
    "title", "author", "editor", "booktitle", "journal", "volume", "number", "pages",
    "year", "month", "address", "publisher", "school", "institution", "organization",
    "series", "edition", "isbn", "howpublished", "doi", "url", "eprint", "archiveprefix",
    "primaryclass", "note", "abbr", "category", "keywords", "lab-authors", "code",
]
# How field names are spelled on output (BibTeX is case-insensitive).
FIELD_SPELLING = {"archiveprefix": "archivePrefix", "primaryclass": "primaryClass"}

REQUIRED = {
    "article": ["title", "author", "journal", "year"],
    "inproceedings": ["title", "author", "booktitle", "year"],
    "misc": ["title", "author", "year"],
    "proceedings": ["title", "editor", "year"],
    "book": ["title", "publisher", "year"],
    "incollection": ["title", "author", "booktitle", "publisher", "year"],
    "phdthesis": ["title", "author", "school", "year"],
    "techreport": ["title", "author", "institution", "year"],
}

CATEGORIES = ["conference", "journal", "workshop", "preprint", "book", "chapter",
              "proceedings", "thesis", "report"]

MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

KEY_STOPWORDS = {
    "a", "an", "the", "on", "of", "in", "for", "to", "and", "with", "from", "at", "by",
    "is", "are", "do", "does", "can", "how", "what", "why", "when", "which", "not", "we",
}


# --------------------------------------------------------------------------- parsing

class BibError(Exception):
    pass


class Entry:
    def __init__(self, etype: str, key: str, fields: dict[str, str], raw_values: dict[str, str],
                 path: Path | None = None, line: int = 0):
        self.type = etype.lower()
        self.key = key
        self.fields = fields          # lower-case name -> value without outer delimiters
        self.raw = raw_values         # lower-case name -> 'brace' | 'macro' | 'quote'
        self.path = path
        self.line = line

    def get(self, name: str, default: str = "") -> str:
        return self.fields.get(name.lower(), default)

    def where(self) -> str:
        rel = self.path.relative_to(ROOT) if self.path else "?"
        return f"{rel}:{self.line} [{self.key}]"


def _read_braced(text: str, i: int) -> tuple[str, int]:
    """text[i] == '{'; return (content, index after closing brace)."""
    depth, start = 0, i
    while i < len(text):
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
        i += 1
    raise BibError("unbalanced braces")


def _read_quoted(text: str, i: int) -> tuple[str, int]:
    depth, j = 0, i + 1
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif c == '"' and depth == 0:
            return text[i + 1:j], j + 1
        j += 1
    raise BibError("unterminated quoted value")


def parse_bib(text: str, path: Path | None = None) -> list[Entry]:
    entries: list[Entry] = []
    i, n = 0, len(text)
    while True:
        at = text.find("@", i)
        if at < 0:
            break
        # '@' inside a %-comment line is ignored
        line_start = text.rfind("\n", 0, at) + 1
        if text[line_start:at].lstrip().startswith("%"):
            i = at + 1
            continue
        line_no = text.count("\n", 0, at) + 1
        m = re.match(r"@\s*([A-Za-z]+)\s*([{(])", text[at:])
        if not m:
            raise BibError(f"{path}:{line_no}: malformed entry start")
        etype = m.group(1).lower()
        j = at + m.end()
        if etype in ("comment", "preamble", "string"):
            raise BibError(f"{path}:{line_no}: @{etype} is not allowed (see AGENTS.md)")
        km = re.match(r"\s*([^,\s]+)\s*,", text[j:])
        if not km:
            raise BibError(f"{path}:{line_no}: missing citation key")
        key = km.group(1)
        j += km.end()
        fields: dict[str, str] = {}
        raw: dict[str, str] = {}
        while True:
            ws = re.match(r"[\s,]*", text[j:])
            j += ws.end()
            if j >= n:
                raise BibError(f"{path}:{line_no}: entry {key} not closed")
            if text[j] in "})":
                j += 1
                break
            fm = re.match(r"([A-Za-z][\w\-:.]*)\s*=\s*", text[j:])
            if not fm:
                raise BibError(f"{path}:{line_no}: cannot parse field in {key} near: {text[j:j+40]!r}")
            name = fm.group(1).lower()
            j += fm.end()
            try:
                if text[j] == "{":
                    val, j = _read_braced(text, j)
                    kind = "brace"
                elif text[j] == '"':
                    val, j = _read_quoted(text, j)
                    kind = "quote"
                else:
                    vm = re.match(r"[\w\-]+", text[j:])
                    if not vm:
                        raise BibError("bad value")
                    val, kind = vm.group(0), "macro"
                    j += vm.end()
            except BibError as e:
                raise BibError(f"{path}:{line_no}: {key}.{name}: {e}") from None
            if name in fields:
                raise BibError(f"{path}:{line_no}: duplicate field '{name}' in {key}")
            fields[name] = re.sub(r"\s+", " ", val).strip()
            raw[name] = kind
        entries.append(Entry(etype, key, fields, raw, path, line_no))
        i = j
    return entries


def load_all() -> list[Entry]:
    entries: list[Entry] = []
    for path in sorted(BIB_DIR.glob("*.bib")):
        entries.extend(parse_bib(path.read_text(encoding="utf-8"), path))
    return entries


# --------------------------------------------------------------------------- writing

def format_entry(e: Entry) -> str:
    names = list(e.fields)
    order = {f: k for k, f in enumerate(FIELD_ORDER)}
    names.sort(key=lambda f: (order.get(f, len(FIELD_ORDER)), f))
    width = max(len(FIELD_SPELLING.get(f, f)) for f in names)
    lines = [f"@{e.type}{{{e.key},"]
    for f in names:
        v = e.fields[f]
        if f == "month" and v.lower()[:3] in MONTHS:
            val = v.lower()[:3]
        elif e.raw.get(f) == "macro" and re.fullmatch(r"\d+", v):
            val = f"{{{v}}}"
        else:
            val = f"{{{v}}}"
        lines.append(f"  {FIELD_SPELLING.get(f, f).ljust(width)} = {val},")
    lines.append("}")
    return "\n".join(lines)


def write_year_file(year: str, entries: list[Entry]) -> str:
    entries = sorted(entries, key=lambda e: e.key)
    body = "\n\n".join(format_entry(e) for e in entries)
    return FILE_HEADER.format(year=year) + "\n" + body + "\n"


# --------------------------------------------------------------------------- text utils

_ACCENTS = {"'": "\u0301", "`": "\u0300", "^": "\u0302", '"': "\u0308", "~": "\u0303",
            "=": "\u0304", ".": "\u0307", "u": "\u0306", "v": "\u030c", "H": "\u030b",
            "c": "\u0327", "k": "\u0328", "r": "\u030a"}
_SYMBOLS = {"o": "ø", "O": "Ø", "aa": "å", "AA": "Å", "ss": "ß", "ae": "æ", "AE": "Æ",
            "oe": "œ", "OE": "Œ", "l": "ł", "L": "Ł", "i": "ı", "j": "ȷ"}


def detex(s: str) -> str:
    """Best-effort LaTeX -> Unicode for display (braces removed)."""
    if not s:
        return ""
    def acc(m):
        cmd, arg = m.group(1), m.group(2) or m.group(3)
        arg = {"\\i": "i", "\\j": "j"}.get(arg, arg)
        return unicodedata.normalize("NFC", arg + _ACCENTS[cmd])
    s = re.sub(r"\\([`'^\"~=.])\s*(?:\{(\\?\w)\}|(\\?\w))", acc, s)
    s = re.sub(r"\\([uvHckr])\s*(?:\{(\\?\w)\}|\s+(\w))", acc, s)
    s = re.sub(r"\\(aa|AA|ss|ae|AE|oe|OE|o|O|l|L|i|j)(?![A-Za-z])\s*", lambda m: _SYMBOLS[m.group(1)], s)
    s = re.sub(r"\\(?:textit|textbf|emph|textsc|texttt|underline|mathrm|text)\s*", "", s)
    s = s.replace("\\&", "&").replace("\\%", "%").replace("\\_", "_").replace("\\$", "$").replace("\\#", "#")
    s = s.replace("---", "—").replace("--", "–").replace("~", " ")
    s = s.replace("``", "“").replace("''", "”")
    s = s.replace("{", "").replace("}", "").replace("$", "")
    s = re.sub(r"\\\s", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", detex(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("ø", "o").replace("ß", "ss").replace("ł", "l").replace("æ", "ae")
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def split_names(field: str) -> list[str]:
    """Split a BibTeX name list on top-level ' and '."""
    out, depth, cur, i = [], 0, "", 0
    while i < len(field):
        c = field[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        if depth == 0 and field[i:i + 5].lower() == " and " :
            out.append(cur.strip())
            cur, i = "", i + 5
            continue
        cur += c
        i += 1
    if cur.strip():
        out.append(cur.strip())
    return out


def display_name(name: str) -> str:
    name = name.strip()
    if "," in name:
        parts = [p.strip() for p in name.split(",")]
        if len(parts) == 2:
            last, first = parts
            return detex(f"{first} {last}".strip())
        if len(parts) == 3:  # Last, Jr, First
            last, jr, first = parts
            return detex(f"{first} {last} {jr}".strip())
    return detex(name)


def last_name(name: str) -> str:
    name = name.strip()
    if "," in name:
        return detex(name.split(",")[0])
    if name.startswith("{") and name.endswith("}"):
        return detex(name)
    return detex(name.split()[-1]) if name.split() else ""


def norm_title(t: str) -> str:
    return fold(t)


def suggest_key(title: str, authors: str, year: str) -> str:
    names = split_names(authors)
    first = names[0] if names else "anon"
    last = fold(last_name(first)).replace(" ", "") or "anon"
    words = [w for w in fold(title).split() if w not in KEY_STOPWORDS]
    word = words[0] if words else "untitled"
    return f"{last}{year}{word}"


# --------------------------------------------------------------------------- members

def load_members() -> list[dict]:
    if not MEMBERS_FILE.exists():
        return []
    data = tomllib.loads(MEMBERS_FILE.read_text(encoding="utf-8"))
    members = data.get("member", [])
    for m in members:
        m["id"] = fold(m["name"]).replace(" ", "-")
        m["_keys"] = {fold(m["name"])} | {fold(a) for a in m.get("aliases", [])}
    return members


def match_members(names: list[str], members: list[dict]) -> list[str]:
    ids = []
    for n in names:
        f = fold(display_name(n))
        for m in members:
            if f in m["_keys"] and m["id"] not in ids:
                ids.append(m["id"])
    return ids


# --------------------------------------------------------------------------- derived info

VENUE_RULES = [
    # (regex on venue string, short label)
    (r"findings of the association for computational linguistics:? *(acl|emnlp|naacl|eacl|aacl|ijcnlp)[^\d]*(\d{4})", None),
    (r"transactions of the association for computational linguistics", "TACL"),
    (r"empirical methods in natural language processing", "EMNLP"),
    (r"north american chapter|nations of the americas chapter", "NAACL"),
    (r"european chapter of the association", "EACL"),
    (r"annual meeting of the association for computational linguistics", "ACL"),
    (r"international conference on computational linguistics \(coling\)|^proceedings of the \d+\w* international conference on computational linguistics", "COLING"),
    (r"joint international conference on computational linguistics, language resources and evaluation", "LREC-COLING"),
    (r"language resources and evaluation conference|\blrec\b", "LREC"),
    (r"international conference on learning representations|\biclr\b", "ICLR"),
    (r"international conference on machine learning|\bicml\b", "ICML"),
    (r"aaai conference on artificial intelligence", "AAAI"),
    (r"web and social media", "ICWSM"),
    (r"research and development in information retrieval", "SIGIR"),
    (r"innovative concepts and theories in information retrieval|\bictir\b", "ICTIR"),
    (r"human information interaction and retrieval", "CHIIR"),
    (r"european conference on information retrieval", "ECIR"),
    (r"conversational user interfaces", "CUI"),
    (r"chi conference on human factors", "CHI EA"),
    (r"interspeech", "Interspeech"),
    (r"recent advances in natural language processing", "RANLP"),
    (r"nordic conference on computational linguistics", "NoDaLiDa"),
    (r"semantic evaluation|semeval", "SemEval"),
    (r"computational approaches to subjectivity", "WASSA"),
    (r"text, speech,? and dialogue", "TSD"),
    (r"natural language generation conference", "INLG"),
    (r"special interest group on discourse and dialogue|sigdial", "SIGDIAL"),
    (r"conference on language modeling", "COLM"),
    (r"machine learning and knowledge discovery in databases", "ECML PKDD"),
    (r"applications of natural language to information systems", "NLDB"),
    (r"web conference", "WWW"),
    (r"blackboxnlp", "BlackboxNLP"),
    (r"widening nlp", "WiNLP"),
    (r"perspectivist approaches to nlp", "NLPerspectives"),
    (r"computational linguistics and clinical psychology", "CLPsych"),
    (r"online abuse and harms", "WOAH"),
    (r"argument mining", "ArgMining"),
    (r"social media mining for health", "SMM4H"),
    (r"nature human behaviour", "Nat. Hum. Behav."),
    (r"communications earth", "Commun. Earth Environ."),
    (r"european physical journal c", "EPJ C"),
    (r"journal of physics g", "J. Phys. G"),
    (r"computing and software for big science", "CSBS"),
    (r"artificial intelligence review", "AI Review"),
    (r"^ai and ethics$", "AI and Ethics"),
    (r"discover artificial intelligence", "Discover AI"),
    (r"machine learning with applications", "MLWA"),
    (r"^patterns$", "Patterns"),
    (r"expert systems", "Expert Systems"),
    (r"psychopathology and clinical science", "J. Psychopathol. Clin. Sci."),
    (r"\besann\b|european symposium on artificial neural networks", "ESANN"),
    (r"konvens", "KONVENS"),
]


# ACL Anthology venue ids (from https://aclanthology.org/<year>.<venue>-...) -> (label, is_workshop).
# Main conferences are recognised from the booktitle via VENUE_RULES; list workshops here.
ACL_VENUES = {
    "abjadnlp": ("AbjadNLP", True), "analogyangle": ("Analogy-ANGLE", True),
    "argmining": ("ArgMining", True), "blackboxnlp": ("BlackboxNLP", True),
    "c3nlp": ("C3NLP", True), "clpsych": ("CLPsych", True), "comedi": ("CoMeDi", True),
    "cpss": ("CPSS", True), "delite": ("DELITE", True), "dialres": ("DialRes", True),
    "fieldmatters": ("FieldMatters", True), "gem": ("GEM", True), "hucllm": ("HuCLLM", True),
    "indor": ("InDor", True), "llmsec": ("LLMSEC", True), "mrl": ("MRL", True),
    "nlpcss": ("NLP+CSS", True), "nlperspectives": ("NLPerspectives", True),
    "practicald2t": ("PracticalD2T", True), "privatenlp": ("PrivateNLP", True),
    "semeval": ("SemEval", True), "smm4h": ("SMM4H", True), "socialnlp": ("SocialNLP", True),
    "socon": ("SoCon", True), "textgraphs": ("TextGraphs", True), "tllm": ("TLLM", True),
    "wasp": ("WASP", True), "wassa": ("WASSA", True), "winlp": ("WiNLP", True),
    "woah": ("WOAH", True), "icnlsp": ("ICNLSP", False), "inlg": ("INLG", False),
    "ranlp": ("RANLP", False), "nodalida": ("NoDaLiDa", False), "sigdial": ("SIGDIAL", False),
}


def acl_venue(e: Entry) -> tuple[str, bool] | None:
    m = re.search(r"aclanthology\.org/\d{4}\.([a-z0-9]+)-", e.get("url"))
    return ACL_VENUES.get(m.group(1)) if m else None


def venue_of(e: Entry) -> str:
    fields = ("title",) if e.type == "proceedings" else (
        "booktitle", "journal", "howpublished", "publisher", "school", "institution")
    for f in fields:
        if e.get(f):
            return detex(e.get(f))
    if e.get("eprint"):
        return "arXiv"
    return ""


def venue_short(e: Entry) -> str:
    if e.get("abbr"):
        return detex(e.get("abbr"))
    cat = category_of(e)
    if cat == "preprint":
        return "arXiv" if e.get("eprint") else "Preprint"
    acl = acl_venue(e)
    if acl and acl[1]:
        return acl[0]
    v = venue_of(e)
    low = v.lower()
    if cat != "workshop":
        m = re.search(VENUE_RULES[0][0], low)
        if m:
            return f"Findings {m.group(1).upper()}"
        for rx, label in VENUE_RULES[1:]:
            if re.search(rx, low):
                return label
    if acl:
        return acl[0]
    # parenthesised acronym, e.g. "... Workshop (LLMSEC)"
    m = re.search(r"\(([A-Z][A-Za-z0-9\-@&' ]{1,20})\)", v)
    if m:
        return re.sub(r"[\s\-]*(?:'\d\d|\d{4})$", "", m.group(1))
    if cat == "workshop":
        for rx, label in VENUE_RULES[1:]:
            if re.search(rx, low):
                return label + " workshop"
    return {"book": "Book", "phdthesis": "PhD thesis", "proceedings": "Proceedings"}.get(e.type, v[:40])


WORKSHOP_RX = re.compile(
    r"workshop|shared task|semeval|wassa|@|\bwinlp\b|\bsmm4h\b|\bllmsec\b|competition|challenge",
    re.I)


def category_of(e: Entry) -> str:
    if e.get("category"):
        return e.get("category").lower()
    t = e.type
    if t == "misc":
        return "preprint"
    if t == "article":
        j = e.get("journal").lower()
        if "arxiv" in j or "preprint" in j:
            return "preprint"
        return "journal"
    if t == "inproceedings":
        acl = acl_venue(e)
        if acl:
            return "workshop" if acl[1] else "conference"
        return "workshop" if WORKSHOP_RX.search(e.get("booktitle")) else "conference"
    return {"proceedings": "proceedings", "book": "book", "incollection": "chapter",
            "phdthesis": "thesis", "techreport": "report"}.get(t, "preprint")


def links_of(e: Entry) -> dict:
    out = {}
    if e.get("url"):
        out["url"] = e.get("url")
    if e.get("doi"):
        out["doi"] = "https://doi.org/" + e.get("doi")
    if e.get("eprint") and e.get("archiveprefix", "arXiv").lower() == "arxiv":
        out["arxiv"] = "https://arxiv.org/abs/" + e.get("eprint")
    if e.get("code"):
        out["code"] = e.get("code")
    return out


# --------------------------------------------------------------------------- checks

def check(entries: list[Entry], members: list[dict], vocab: set[str]) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    seen_keys: dict[str, Entry] = {}
    seen_titles: dict[str, Entry] = {}
    seen_arxiv: dict[str, Entry] = {}
    seen_doi: dict[str, Entry] = {}
    for e in entries:
        w = e.where()
        if e.type not in REQUIRED:
            errors.append(f"{w}: entry type @{e.type} not allowed (use one of {', '.join(REQUIRED)})")
            continue
        for f in REQUIRED[e.type]:
            if not e.get(f):
                errors.append(f"{w}: missing required field '{f}' for @{e.type}")
        if e.type == "book" and not (e.get("author") or e.get("editor")):
            errors.append(f"{w}: @book needs author or editor")
        if e.type == "misc" and not (e.get("eprint") or e.get("url") or e.get("howpublished")):
            errors.append(f"{w}: @misc needs eprint (arXiv id), url or howpublished")
        # year must match file name
        if e.path and e.get("year") != e.path.stem:
            errors.append(f"{w}: year={e.get('year')!r} but entry is in {e.path.name}")
        if not re.fullmatch(r"(19|20)\d\d", e.get("year")):
            errors.append(f"{w}: year must be four digits")
        if e.key in seen_keys:
            errors.append(f"{w}: duplicate key (also {seen_keys[e.key].where()})")
        seen_keys[e.key] = e
        if not re.fullmatch(r"[a-z]+\d{4}[a-z0-9]+", e.key):
            warnings.append(f"{w}: key does not follow <lastname><year><firstword> (suggest {suggest_key(e.get('title'), e.get('author') or e.get('editor'), e.get('year'))})")
        t = norm_title(e.get("title"))
        if t in seen_titles:
            errors.append(f"{w}: same title as {seen_titles[t].where()} — keep only the archival version")
        seen_titles[t] = e
        if e.get("eprint"):
            a = e.get("eprint").lower().removeprefix("arxiv:")
            if not re.fullmatch(r"\d{4}\.\d{4,5}(v\d+)?", a):
                warnings.append(f"{w}: eprint {a!r} does not look like a new-style arXiv id")
            if a in seen_arxiv:
                errors.append(f"{w}: arXiv {a} also used by {seen_arxiv[a].where()} — merge into one entry")
            seen_arxiv[a] = e
        if e.get("doi"):
            d = e.get("doi").lower()
            if d.startswith("http"):
                errors.append(f"{w}: doi must be the bare DOI (10.xxxx/...), not a URL")
            if d in seen_doi:
                errors.append(f"{w}: DOI also used by {seen_doi[d].where()}")
            seen_doi[d] = e
        if not (e.get("url") or e.get("doi") or e.get("eprint")):
            warnings.append(f"{w}: no url/doi/eprint — add a link if one exists")
        if e.get("month") and e.get("month").lower()[:3] not in MONTHS:
            errors.append(f"{w}: month must be jan..dec")
        cat = category_of(e)
        if cat not in CATEGORIES:
            errors.append(f"{w}: category {cat!r} not in {CATEGORIES}")
        if e.get("keywords"):
            for k in [k.strip() for k in e.get("keywords").split(",")]:
                if k and k not in vocab:
                    warnings.append(f"{w}: keyword {k!r} not in the [topics] vocabulary of lab.toml")
        names = split_names(e.get("author")) + split_names(e.get("editor"))
        if any(n.lower() == "others" for n in names) and not e.get("lab-authors"):
            warnings.append(f"{w}: author list ends in 'and others' — add lab-authors = {{...}} so lab members are credited")
        lab = match_members(names + split_names(e.get("lab-authors")), members)
        if members and not lab:
            warnings.append(f"{w}: no author matches a lab member in lab.toml (typo, missing alias, or not a lab paper?)")
        for f in ("title", "booktitle", "journal"):
            v = e.get(f)
            if v.count("{") != v.count("}"):
                errors.append(f"{w}: unbalanced braces in {f}")
    # near-duplicate titles (e.g. preprint + published version with slightly different title)
    items = list(seen_titles.items())
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i][0], items[j][0]
            if abs(len(a) - len(b)) < 25 and difflib.SequenceMatcher(None, a, b).ratio() > 0.9:
                warnings.append(f"near-duplicate titles: {items[i][1].where()} ~ {items[j][1].where()}")
    return errors, warnings


# --------------------------------------------------------------------------- export

def to_record(e: Entry, members: list[dict]) -> dict:
    authors = [display_name(n) for n in split_names(e.get("author"))]
    editors = [display_name(n) for n in split_names(e.get("editor"))]
    lab_extra = [display_name(n) for n in split_names(e.get("lab-authors"))]
    lab = match_members(split_names(e.get("author")) + split_names(e.get("editor")) + split_names(e.get("lab-authors")), members)
    month = e.get("month").lower()[:3]
    return {
        "key": e.key,
        "type": e.type,
        "category": category_of(e),
        "year": int(e.get("year")),
        "month": MONTHS.index(month) + 1 if month in MONTHS else 0,
        "title": detex(e.get("title")),
        "authors": authors,
        "editors": editors,
        "labAuthors": lab_extra,
        "members": lab,
        "venue": venue_of(e),
        "venueShort": venue_short(e),
        "keywords": [k.strip() for k in e.get("keywords").split(",") if k.strip()],
        "links": links_of(e),
        "note": detex(e.get("note")),
        "bibtex": format_entry(e),
    }


def build(entries: list[Entry], members: list[dict], topics: dict) -> dict:
    recs = [to_record(e, members) for e in entries]
    recs.sort(key=lambda r: (-r["year"], -r["month"], r["key"]))
    return {
        "count": len(recs),
        "topics": topics,
        "members": [{k: v for k, v in m.items() if not k.startswith("_")} for m in members],
        "publications": recs,
    }


# --------------------------------------------------------------------------- CLI

def load_vocab() -> tuple[set[str], dict]:
    if not MEMBERS_FILE.exists():
        return set(), {}
    data = tomllib.loads(MEMBERS_FILE.read_text(encoding="utf-8"))
    topics = data.get("topics", {})
    return set(topics), topics


def cmd_check(args) -> int:
    entries = load_all()
    members = load_members()
    vocab, _ = load_vocab()
    errors, warnings = check(entries, members, vocab)
    for w in warnings:
        if not args.quiet:
            print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"{len(entries)} entries in {len(list(BIB_DIR.glob('*.bib')))} files; "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    if args.strict and warnings:
        return 1
    return 1 if errors else 0


def cmd_fmt(args) -> int:
    """Rewrite every bib/<year>.bib canonically; entries with another year are moved to their file."""
    by_year: dict[str, list[Entry]] = {}
    for e in load_all():
        by_year.setdefault(e.get("year"), []).append(e)
    for year, ents in sorted(by_year.items()):
        if not re.fullmatch(r"(19|20)\d\d", year):
            print(f"skipping {len(ents)} entr(y/ies) with invalid year {year!r}; run check")
            continue
        path = BIB_DIR / f"{year}.bib"
        new = write_year_file(year, ents)
        if not path.exists() or new != path.read_text(encoding="utf-8"):
            path.write_text(new, encoding="utf-8")
            print("formatted", path.relative_to(ROOT))
    for path in sorted(BIB_DIR.glob("*.bib")):
        if path.stem not in by_year:
            path.unlink()
            print("removed empty", path.relative_to(ROOT))
    return 0


def cmd_find(args) -> int:
    raw_q = " ".join(args.query).strip().lower()
    q = fold(raw_q)
    hits = []
    for e in load_all():
        hay = " ".join([fold(e.get("title")), e.key, fold(e.get("author")), fold(e.get("editor"))])
        ids = " ".join([e.key, e.get("eprint"), e.get("doi"), e.get("url")]).lower()
        if (q and q in hay) or raw_q in ids:
            score = 1.0
        else:
            score = difflib.SequenceMatcher(None, q, fold(e.get("title"))).ratio()
        if score > 0.55:
            hits.append((score, e))
    for score, e in sorted(hits, key=lambda x: -x[0])[:15]:
        print(f"{score:.2f}  {e.where()}  {detex(e.get('title'))}")
    if not hits:
        print("no matching entries")
    return 0


def cmd_key(args) -> int:
    print(suggest_key(args.title, args.authors, args.year))
    return 0


def cmd_stats(args) -> int:
    entries = load_all()
    from collections import Counter
    years = Counter(e.get("year") for e in entries)
    cats = Counter(category_of(e) for e in entries)
    for y in sorted(years):
        c = Counter(category_of(e) for e in entries if e.get("year") == y)
        print(y, years[y], dict(c))
    print("total", len(entries), dict(cats))
    return 0


def cmd_build(args) -> int:
    entries = load_all()
    members = load_members()
    vocab, topics = load_vocab()
    errors, warnings = check(entries, members, vocab)
    if errors:
        for e in errors:
            print("ERROR:", e)
        print("fix errors before building")
        return 1
    data = build(entries, members, topics)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    OUTPUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tpl = TEMPLATE_FILE.read_text(encoding="utf-8")
    marker = "/*__BIB_DATA__*/null"
    if marker not in tpl:
        print(f"template {TEMPLATE_FILE} lacks marker {marker}")
        return 1
    fragment = tpl.replace(marker, payload.replace("</", "<\\/"))
    OUTPUT_ARTIFACT.write_text(fragment, encoding="utf-8")
    OUTPUT_HTML.write_text(HTML_WRAPPER.replace("{body}", fragment.strip()), encoding="utf-8")
    print(f"wrote {', '.join(str(p.relative_to(ROOT)) for p in (OUTPUT_HTML, OUTPUT_ARTIFACT, OUTPUT_JSON))} "
          f"({len(entries)} publications, {len(warnings)} warning(s))")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="validate bib files")
    c.add_argument("--strict", action="store_true", help="treat warnings as errors")
    c.add_argument("--quiet", action="store_true", help="only print errors")
    c.set_defaults(fn=cmd_check)
    sub.add_parser("fmt", help="rewrite bib files canonically").set_defaults(fn=cmd_fmt)
    f = sub.add_parser("find", help="search existing entries (title/key/arXiv/DOI/author)")
    f.add_argument("query", nargs="+")
    f.set_defaults(fn=cmd_find)
    k = sub.add_parser("key", help="suggest a citation key")
    k.add_argument("title")
    k.add_argument("authors", help="BibTeX author field, e.g. 'Flek, Lucie and Mai, Florian'")
    k.add_argument("year")
    k.set_defaults(fn=cmd_key)
    sub.add_parser("stats", help="counts per year and category").set_defaults(fn=cmd_stats)
    sub.add_parser("build", help="check, then regenerate site/index.html + site/data.json").set_defaults(fn=cmd_build)
    args = p.parse_args(argv)
    try:
        return args.fn(args)
    except BibError as e:
        print("PARSE ERROR:", e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
