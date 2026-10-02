# Cold-start notes (September 2026)

How the initial bibliography (146 entries, reduced to 128 after the affiliation check below) was assembled, and which decisions
the lab should double-check. Delete items from "Open questions" once resolved.

## Sources

1. Google Scholar profile exports (30 Sep 2026) of **Lucie Flek**, **Florian Mai** and
   **Nicholas Kluge Corrêa** — used as the list of candidates only (Scholar metadata is
   incomplete, so no BibTeX was copied from it).
2. **ACL Anthology** metadata (`acl-org/acl-anthology`, `data/xml`), searched for every
   member in `lab.toml` → exact titles, full author lists, pages, DOIs, URLs.
3. Group websites: `caisa-lab.github.io` (team list, older publication list),
   `mai-alignment.github.io` (curated `papers.bib` with accepted venues, e.g. ICML/EMNLP 2026).
4. Members' personal sites with BibTeX/citations: Nicholas Kluge Corrêa, Akbar Karimi,
   Allison Lahnala, Florian Mai.
5. PubMed (full author lists/DOIs for the Nature Human Behaviour, ICWSM 2025 and J.
   Psychopathology papers) and web searches to find archival versions of preprints and DOIs.

## Inclusion window

The lab (CAISA) started in 2020, so the bibliography starts in 2020. Lucie Flek's earlier
work (TU Darmstadt, UPenn, UCL, CERN/OSQAR physics) is not included. Per-person windows used:

| Person | Counted from | Notes |
|---|---|---|
| Lucie Flek | 2020 | everything since the lab was founded, incl. physics collaborations |
| Florian Mai | 2024 | only Bonn work; the KU Leuven planning papers (COLM 2024, WiNLP 2024), HyperMixer, Triple-Encoders, SpeechBrain 1.0 and End-to-end Planner Training are out |
| Nicholas Kluge Corrêa | Feb 2026 | before that he was at Uni Bonn's Center for Science and Thought (philosophy); only papers co-authored with lab members count for that period |
| Charles Welch | 2021–2024 | 2020 Michigan papers out; McMaster papers without current members out |
| Allison Lahnala | 2021–2025 | Chord Embeddings (EvoMUSART 2021) and McMaster-only 2026 papers out |
| Akbar Karimi | 2022 | Parma-era papers (UniParma, AEDA, R-CNN work) out |
| Others | while in the lab | e.g. Wei-Fan Chen's Paderborn papers and Gisela Vallejo's Melbourne papers are out |

## Merges (preprint → archival version)

- *Survey-to-Behavior* (arXiv 2508.11414) → **From Value Conditioning to Behavioral Shift**, EMNLP 2026
- *In-training defenses* (arXiv 2508.06249) → ICML 2026
- *Reinforcement Learning Amplifies…* (arXiv 2605.31328) → EMNLP 2026 (published title: "…Can Amplify…")
- *Data Attribution of EM* → BlackboxNLP 2026; *Unified Moral-Value Dataset* → VALE @ IJCAI 2026
- *PERSPECTRA* (arXiv 2602.08716) → ICLR 2026
- *Language-specific Calibration for Pruning* (arXiv 2408.14398) → TACL 2026 ("On the Limitations of Language-targeted Pruning")
- *The Muddy Waters of Modeling Empathy* (arXiv 2501.14981) → EMNLP 2025 ("The Practical Impacts of Theoretical Constructs…")
- *More Agents Helps…* (arXiv 2511.07112) → Findings ACL 2026
- *Disparities in Multilingual LLM-Based Healthcare Q&A* (arXiv 2510.17476) → NLDB 2026 ("Zoom In Disparities…")
- *Detection of Medical Conspiracy Theories with Limited Resources* → Expert Systems 2026
- *From FLOPs to Footprints* (arXiv 2512.04142) → Communications Earth & Environment 2026
- *Explaining GPTs' Schema of Depression* (arXiv 2411.13800) → J. Psychopathology and Clinical Science 2026
- *USDC* (CoRR 2024) → Findings ACL 2025; *Pitfalls of Conversational LLMs on News Debiasing* → DELITE 2024
- *Can Stories Help LLMs Reason?* (NeurIPS'24 workshop, arXiv 2410.19221) → Analogy-ANGLE 2025
- *Enforcing Fundamental Relations…* (arXiv 2501.05588) → Computing and Software for Big Science 2025
- *The Impact of Differential Privacy on Group Disparity Mitigation*: PrivateNLP 2022 and
  Findings NAACL 2024 have the same title — only the Findings 2024 version is kept
- *Perceived and Intended Sarcasm Detection…*: Findings EMNLP 2021 kept, W-NUT 2021 duplicate dropped
- *Learning to Plan Long-Term for Language Modeling* (arXiv 2409.00070) merged into the WiNLP 2024 paper
- *Dynamic Normativity* arXiv 2406.11039 merged into Nicholas's PhD thesis
- Book chapters of *Normative Ethics, AI, and Value Alignment* (Springer 2026) are one `@book`

## Open questions (please check)

- **Membership years** in `lab.toml` marked `approx` are guesses (esp. Nicholas Kluge Corrêa,
  Wei-Fan Chen, Mounika Marreddy, Charles Welch, Allison Lahnala).
- **Borderline exclusions** (add if they count): Lahnala & Welch, *Examining the Utility of
  Self-disclosure Types…* (Findings EACL 2026); Marreddy's 2023 and 2026 papers without lab
  co-authors; Florian Mai, *Triple-Encoders* (ACL 2024) and *End-to-end Planner Training* (arXiv 2024);
  Dagstuhl report *Framing in Communication* (2022); LilTii (Hugging Face blog, 2026).
- **Not yet findable:** *RheumBench* (Lechner et al., 2026, on Scholar without venue/link) — add
  once there is a preprint or venue.
- **Details to verify:** venue/booktitle of *DIME* (KONVENS 2026) and *Code-Guided Reasoning…*
  (ESANN 2026); title of the IASEAI'26 paper (Scholar: "Independent Alignment Mechanisms…",
  mai-alignment site: "Independent Safety Mechanisms…"); first names of S. Giri and C. Herbrik
  (`labonte2026structured`); *Plausible but Wrong* was reportedly presented at ICML 2026
  (workshop?) — kept as arXiv.
- **Missing links:** `huang2022usernlp`, `steinigen2026code` (see `bibtool.py check`).

## Affiliation check (Sep 2026)

Every entry without Lucie Flek or Florian Mai as author (plus Florian's 2024 papers) was checked
for the affiliation printed on the paper. Direct PDF access was blocked, so the evidence comes
from web-search snippets of the papers/arXiv HTML, PubMed author data and members' CVs.

**Removed (18)** — written at another lab:
- Florian Mai at KU Leuven: `cornille2024learning` (COLM 2024), `mai2024improving` (WiNLP 2024)
- Lahnala & Welch at University of Michigan: `lahnala2021exploring`
- Sarumi with Daniel Braun's group at Marburg (2025+), Welch at McMaster: `sarumi2025impact`,
  `sarumi2025nlp`, `sarumi2026fine`
- Lea Fischbach at the Forschungszentrum Deutscher Sprachatlas, Marburg: `fischbach2024comparative`
- Nicholas Kluge Corrêa at the Center for Science and Thought (philosophy, Uni Bonn) or PUCRS, before
  joining CAISA in Feb 2026: `correa2024catalog`, `correa2024dynamic` (PhD thesis),
  `correa2024teenytinyllama`, `chang2025global`, `correa2025crossing`, `correa2025tucano`,
  `klugecorrea2025codes`, `pasetti2025technical`, `falk2026computation`, and the two 2026 books
  `correa2026normative` and `klugecorrea2026standardization` (published after he joined, but CST/PhD work)

**Kept, affiliation confirmed as ours:** `shen2022knowledge`, `welch2022leveraging` (Welch: CAISA,
Marburg), `liu2025illusion`, `varadarajan2025linking` (Lahnala: Bonn), `mitchell2025shades` (Nie, Bonn),
`frenda2026indor` (Ashraf, CAISA member).

**Kept, but not verified — please check the PDFs:**
- `breitwieser2022contextualizing` — presumably Marburg-era CAISA
- `bauwens2025grampa` — co-authors are KU Leuven; possibly David Kaczér's pre-Bonn master's work
- `debnath2024examination` — workshop abstract; Lahnala was a Bonn PhD student then, but it may be a
  talk without a paper (excluded by AGENTS.md)
