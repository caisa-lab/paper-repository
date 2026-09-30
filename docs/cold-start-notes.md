# Cold-start notes (September 2026)

How the initial bibliography (146 entries, 2020–2026) was assembled, and which decisions
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
| Florian Mai | 2024 | follows the mai-alignment site: COLM 2024 and WiNLP 2024 are in; pre-Bonn papers (HyperMixer, Triple-Encoders, SpeechBrain 1.0, End-to-end Planner Training) are out |
| Nicholas Kluge Corrêa | 2024 | PhD thesis (Bonn, 2024) and later; *Worldwide AI Ethics* (Patterns 2023) and earlier work are out |
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
- **Borderline inclusions:** Welch et al. ACL 2022 papers with Michigan (`welch2022leveraging`,
  `shen2022knowledge`); `bauwens2025grampa` (David Kaczér's pre-PhD work); `liu2025illusion`
  (Lahnala with Penn); `mitchell2025shades` (large collaboration, Shangrui Nie).
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
