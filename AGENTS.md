# AGENTS.md — maintaining the lab bibliography

Instructions for anyone (human or AI agent) who adds or edits publications in this
repository. Read this whole file before your first change. `CLAUDE.md` points here.

The repository is the single source of truth for the publications of the
**CAISA Lab / Data & Language Technologies (DLT) Lab** at b-it, University of Bonn
(PI: Lucie Flek), including the **mAI alignment group** (Florian Mai).

## Layout

| Path | What it is |
|---|---|
| `bib/<year>.bib` | One BibTeX file per year with **all** lab publications of that year (papers, preprints, journal articles, books, theses, edited proceedings). |
| `lab.toml` | Lab members (names, aliases, role, group, years) and the topic vocabulary for `keywords`. |
| `scripts/bibtool.py` | Validator/formatter/exporter. Python ≥ 3.11, standard library only. |
| `site/template.html` | Source of the publication browser (HTML/JS). Edit this, never `index.html`. |
| `site/index.html`, `site/artifact.html`, `site/data.json` | **Generated** by `bibtool.py build`. Commit them, never edit by hand. |
| `docs/cold-start-notes.md` | How the bibliography was seeded, what was deliberately left out, open questions. |

## What counts as a lab publication

Include a publication if **at least one author was a lab member (see `lab.toml`) when the
work was published**, and the work was done in or with the lab. This covers:

- conference, workshop and journal papers, including shared-task system papers;
- preprints (arXiv, PsyArXiv, …) that have **no** archival version yet;
- books, book chapters written by members, PhD theses of members;
- edited proceedings where a member is an editor (`@proceedings`).

Do **not** include:

- members' papers from before they joined (e.g. a PhD student's master's work at another
  university) unless the paper is clearly lab work;
- alumni papers written after they left, unless a current member is a co-author;
- talks, posters without a paper, blog posts, datasets or models without a paper,
  errata/corrections, "meet the authors" pieces, Dagstuhl-style participant lists.

When unsure, add the entry and mention the doubt in the PR/commit message, or ask the PI.

## One publication = one entry (archival version wins)

Every publication appears **exactly once**. If several versions exist, record the most
archival one, in this order of preference:

1. journal article / conference or workshop proceedings (ACL Anthology, PMLR, ACM, Springer, OpenReview proceedings of ICLR, …)
2. accepted-but-not-yet-published version (use the venue as `booktitle`/`journal`, e.g. "EMNLP 2026")
3. preprint (`@misc` with `eprint`)

Keep the arXiv id of a published paper in `eprint` (+ `archivePrefix = {arXiv}`): it gives
readers a free PDF, and it lets the validator catch duplicates. If the title changed between
preprint and publication, use the **published** title.

## Adding a publication — step by step

1. **Check it is not already there** (titles change, so search several ways):
   ```sh
   python3 scripts/bibtool.py find "emergent misalignment"
   python3 scripts/bibtool.py find 2508.06249        # arXiv id
   ```
   If it exists as a preprint and has now been published, **upgrade** that entry
   (see "Upgrading a preprint" below) instead of adding a new one.
2. **Get metadata from an authoritative source**, in this order: ACL Anthology (the `.bib`
   link on the paper page), the publisher/DOI page, DBLP, OpenReview, arXiv.
   **Never copy BibTeX from Google Scholar** — it abbreviates first names, truncates
   author lists and often shows the preprint instead of the published version.
3. **Rewrite it to the conventions below** (field names, author format, key, keywords).
4. **Put it into `bib/<year>.bib`**, where `<year>` is the publication year of the version
   you record (for journals: the year of the volume/issue). If the file does not exist yet,
   create it with just the entry; `fmt` adds the header.
5. **New author who is a lab member?** Add them to `lab.toml` (with `since`), otherwise the
   paper is not credited to them in the browser.
6. **Format, validate and rebuild:**
   ```sh
   python3 scripts/bibtool.py fmt      # canonical field order, sorting, spacing
   python3 scripts/bibtool.py build    # validates, then regenerates site/index.html + data.json
   ```
   Fix every `ERROR`. Read the warnings — each one is either a real problem or should be
   an informed exception.
7. **Commit** `bib/`, `lab.toml` (if changed) and `site/` together, e.g.
   `bib: add kaczer2026training (ICML 2026)`, and open a pull request. CI runs the same checks.
8. **Update the shared web page** (see "Publishing the browser").

### Upgrading a preprint to its published version

- Change the entry type (`@misc` → `@inproceedings`/`@article`), add
  `booktitle`/`journal`, `pages`, `publisher`, `doi`, the venue `url`; keep `eprint`.
- Update the title if it changed. If the publication year differs from the preprint year,
  change `year`, change the key's year (e.g. `nie2025survey` → `nie2026value`) and move the
  entry to the other year file (`fmt` does the move for you after you change `year`).
- Delete any other entry for the same work (the validator flags shared titles, arXiv ids and DOIs).

## Entry conventions

**Citation key:** `<first author's last name><year><first significant title word>`, all
lowercase ASCII, no separators: `flek2020returning`, `kaczer2026training`,
`sadirijavadi2026charisma`. Get a suggestion with:
```sh
python3 scripts/bibtool.py key "In-Training Defenses against Emergent Misalignment" "Kaczér, David and Mai, Florian" 2026
```
If the key is taken, append the next title word (`flek2025inlg` / `flek2025inlgdemos`).
For `@proceedings` use `<first editor><year><venue acronym>` (e.g. `soni2024hucllm`).
Do not rename existing keys except when upgrading a preprint to another year.

**Entry types** (nothing else is allowed): `@inproceedings` (conference *and* workshop papers),
`@article` (journals, incl. TACL), `@misc` (preprints), `@proceedings` (edited volumes),
`@book`, `@incollection` (chapters), `@phdthesis`, `@techreport`.
No `@string`, `@preamble` or `@comment`; `%` comments are dropped by `fmt`.

**Fields**

| Field | Rule |
|---|---|
| `title` | Title case as published. Protect capitalisation that must survive styles with braces: `{LLMs}`, `{BERT}`, `{Portuguese}`. |
| `author` / `editor` | `Last, First and Last, First`. Full first names, no initials if they are known. Multi-word last names stay together: `Sadiri Javadi, Vahid`, `Kluge Corrêa, Nicholas`, `de Oliveira, Nythamar`. Unicode is fine (`Kaczér`, `Jørgenvåg`). |
| `lab-authors` | Only when the author list is truncated with `and others` (huge collaborations): list the lab members who are authors, same name format. |
| `booktitle` / `journal` | Full official name, e.g. `Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing`, `Findings of the Association for Computational Linguistics: ACL 2026`. |
| `year` | Four digits; must equal the file name. |
| `month` | Bare three-letter macro: `month = oct`. |
| `pages` | En-dash as `--`: `1888--1896`. Article numbers are fine: `pages = {e70360}`. |
| `doi` | Bare DOI, no URL prefix: `10.18653/v1/2025.findings-acl.96`. |
| `url` | Canonical landing page of the recorded version (ACL Anthology page, OpenReview forum, publisher). For preprints: `https://arxiv.org/abs/<id>`. |
| `eprint` + `archivePrefix` | arXiv id without version (`2508.06249`) and `archivePrefix = {arXiv}`. |
| `keywords` | 1–4 topic ids from `[topics]` in `lab.toml`, comma-separated: `keywords = {alignment, robustness}`. Add a new topic to `lab.toml` first if really needed. |
| `abbr` | Optional short venue label for the browser when the automatic one is wrong (e.g. `ICML`, `AITJ`). |
| `category` | Optional override of the automatic category (`conference`, `workshop`, `journal`, `preprint`, `book`, `chapter`, `proceedings`, `thesis`, `report`). Needed for workshop papers whose booktitle does not say "workshop" and that are not in the ACL Anthology. |
| `code` | Optional link to code/data. |
| `note` | Optional, short, human-readable (e.g. "Also presented at WiNLP 2024"). |

Do not add `abstract`, `file`, `pdf`, `bibtex_show`, `selected` or other tool-specific fields.

**Workshop vs. conference** is derived automatically: ACL Anthology workshop ids
(e.g. `2026.wassa-1.17`) are recognised via their URL, other booktitles via the words
"Workshop", "Shared Task", "SemEval", … Check the category shown by `bibtool.py build`
output or in the browser and set `category` if it is wrong.

## Checks enforced by `bibtool.py`

Errors (must fix): parse errors, unknown entry types, missing required fields, `year` ≠ file,
duplicate keys, duplicate titles / arXiv ids / DOIs, DOI given as URL, bad `month`,
unbalanced braces. Warnings (review): key not following the pattern, no link, keyword not in
the vocabulary, `and others` without `lab-authors`, no author matching `lab.toml`,
near-duplicate titles.

## Publishing the browser

`build` writes the same page twice, with all data embedded:

- `site/index.html` — a complete HTML document: open it directly in a browser or host it
  anywhere (e.g. GitHub Pages);
- `site/artifact.html` — the same page without the `<html>/<head>` wrapper, the format
  claude.ai artifacts expect.

The shared copy is the claude.ai artifact
<https://claude.ai/artifact/LJWES5xBbU3q7evbLSYjJb> (also linked in `README.md`). After `build`:

- **Claude Code agents:** republish `site/artifact.html` to that **same** URL (Artifact tool,
  `action: publish`, `url` = the URL above, `file_path` = `site/artifact.html`; read it first
  if the tool asks). Never create a new artifact: the link people bookmarked would go stale.
- **Humans:** ask the artifact's owner to republish, or open `site/index.html` locally.
  Viewers need to be given access via the artifact's Share menu.

## Changing the browser itself

Edit `site/template.html` (single file, vanilla JS, no build step, no external requests
except Google Fonts), keep the `/*__BIB_DATA__*/null` marker, then run `build` and open
`site/index.html` to check it. The data shape is produced by `to_record()` in `bibtool.py`.

## Quick checklist

- [ ] searched for duplicates (`find` by title words and arXiv id)
- [ ] archival version recorded; arXiv id kept in `eprint`
- [ ] metadata from ACL Anthology / publisher / DBLP, not Google Scholar
- [ ] full author names, `Last, First`, new lab members added to `lab.toml`
- [ ] key follows `<lastname><year><word>`; entry in the right `bib/<year>.bib`
- [ ] `keywords` from the vocabulary
- [ ] `fmt` + `build` run with 0 errors; `site/` committed with the bib change
- [ ] artifact republished (or owner asked to)
