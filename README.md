# paper-repository

Keeps track of all our papers: the bibliography of the **CAISA Lab / Data & Language
Technologies Lab** (b-it, University of Bonn) and its **mAI alignment group**.

**Publication browser: <https://claude.ai/artifact/LJWES5xBbU3q7evbLSYjJb>**

## Every lab member: get your papers in here

Add each of your publications **as soon as it is archival** (accepted at a conference,
workshop or journal), or even earlier, as soon as the **preprint** is out. When the preprint
is later published, upgrade the entry to the archival version (see [`AGENTS.md`](AGENTS.md)).

Every week, Claude scans for new lab publications and adds them automatically. If your
paper is still missing after that, **add it yourself and open a pull request**: follow
[`AGENTS.md`](AGENTS.md), or ask a coding agent to do it for you.

> **Travel requests are only approved for papers that are listed in this repository.**
> Check that your paper is here before you submit a travel request.

## Using the repository

- **Browse it:** <https://claude.ai/artifact/LJWES5xBbU3q7evbLSYjJb> (search, filters, statistics,
  co-authorship, one-click BibTeX). Offline copy: open [`site/index.html`](site/index.html).
- **Cite from it:** `bib/<year>.bib` — one BibTeX file per year, archival versions preferred
  over preprints. For everything at once: `cat bib/*.bib > caisa.bib`.
- **Add to it:** follow [`AGENTS.md`](AGENTS.md) (works for people and for coding agents).
  In short: search for duplicates, add the entry to the right year file, run
  `python3 scripts/bibtool.py fmt && python3 scripts/bibtool.py build`, commit `bib/` + `site/`.

| | |
|---|---|
| `bib/` | the bibliography, 2020–today |
| `lab.toml` | lab members (with name variants) and the topic vocabulary |
| `scripts/bibtool.py` | validate, format, search, build the browser (Python ≥ 3.11, no dependencies) |
| `site/` | publication browser: `template.html` (source), `index.html` / `artifact.html` / `data.json` (generated) |
| `docs/cold-start-notes.md` | how the initial list was compiled and what still needs checking |

```sh
python3 scripts/bibtool.py find "theory of mind"   # is it already in?
python3 scripts/bibtool.py check                    # validate everything
python3 scripts/bibtool.py stats                    # counts per year and type
python3 scripts/bibtool.py build                    # regenerate site/
```
