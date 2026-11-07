# Prior-Art and Citation Ledger

**Status:** LIVING document, append-only per entry. Verification pass: 2026-11-02.
**Rule:** only entries marked VERIFIED may be cited in the report. Apart warns that made-up references can disqualify a project.

| Status | Meaning |
|---|---|
| VERIFIED | Source located and read at least at abstract level; bibliographic details match |
| PARTIAL | Source exists, but a specific detail (author, venue, wording) is unconfirmed |
| NOT CHECKED | Known from memory or secondary citation; not yet located in this project |
| NOT FOUND | Searched and not located; do not cite |

## Sprint and Incident

| ID | Work | Status | Relevance |
|---|---|---|---|
| PA-01 | Apart Research, Swarm Alignment Hackathon page (fetched 2026-11-02) — https://apartresearch.com/sprints/swarm-alignment-2026 | VERIFIED | Rules, tracks, rubric, deadline |
| PA-02 | Wijk, Cotra and Greenblatt, METR/Redwood investigation of the OpenAI–Hugging Face incident (26 Aug 2026) — https://metr.org/hugging-face-incident-report-aug-2026.pdf | VERIFIED | Harm to an unrepresented third party; agents escalating to their own board; 3–6 transcripts considered alerting humans, none acted |

## Sprint Readings

| ID | Work | Status | Relevance |
|---|---|---|---|
| PA-03 | Hammond et al. (2025), Multi-Agent Risks from Advanced AI — arXiv:2502.14143 | VERIFIED | Taxonomy; information asymmetries, network effects |
| PA-04 | Tomašev et al. (2025), Distributional AGI Safety — arXiv:2512.16856 | VERIFIED | Sandbox economies with auditability and oversight |
| PA-05 | Chan et al. (2025), Infrastructure for AI Agents — arXiv:2501.10114 | VERIFIED | Attribution, interaction-shaping, response functions |
| PA-06 | Dafoe et al. (2020), Open Problems in Cooperative AI — arXiv:2012.08630 | VERIFIED | Tools that foster cooperation in agent populations |
| PA-07 | Conitzer and Oesterheld (2023), Foundations of Cooperative AI — doi:10.1609/aaai.v37i13.26791 | VERIFIED | AI agents differ from game theory's traditional agents |
| PA-08 | ARIA, Scaling Trust programme — https://aria.org.uk/opportunity-spaces/trust-everything-everywhere/scaling-trust/ | VERIFIED | Open coordination tooling |

## Closest Prior Art (Positioning)

| ID | Work | Status | What it establishes · Our position |
|---|---|---|---|
| PA-09 | Piatti et al. (2024), Cooperate or Collapse (GovSim) — arXiv:2404.16698 | VERIFIED | Removing communication led to overuse of a shared resource (setting-specific). Our harm falls on a party outside the market, not on the agents' own commons |
| PA-10 | Shen, Zhu, Srinivasan and Sleight (2026), AI Organizations Are More Effective but Less Aligned than Individual Agents — arXiv:2604.10290 | VERIFIED | The general phenomenon. We test interventions, not the phenomenon |
| PA-11 | Hu et al. (2025), Stop Reducing Responsibility in LLM-Powered Multi-Agent Systems to Local Alignment — arXiv:2510.14008 | VERIFIED | Position paper: system-level responsibility. We supply a measured experiment |
| PA-12 | Constantinescu and Kaptein (2025), Responsibility Gaps, LLMs & Organisations — Science and Engineering Ethics 31(6):36 | VERIFIED | Many-hands problem for LLM organisations; cite when introducing accountability |
| PA-13 | Jiang et al. (2026), RiskLab (ACL 2026 demo) — https://aclanthology.org/2026.acl-demo.17/ | VERIFIED | Configurable multi-agent risk testbed. Our harness is not a contribution |
| PA-14 | Terrarium: Revisiting the Blackboard for Multi-Agent Safety — arXiv:2510.14312 | VERIFIED | Same |
| PA-15 | ORBIT (MATS), configurable multi-agent safety framework on Inspect | VERIFIED (project page) | Same |
| PA-16 | When Local Monitors Miss Compositional Harm — arXiv:2607.11751 | VERIFIED | Detection returns only when the observed view changes. Motivates E |
| PA-17 | Audit Without Verification: When LLM Accountability Layers Relay Rather Than Check — arXiv:2609.07680 | PARTIAL | Paper verified; the reviewer-reported author attribution is unconfirmed. Accountability needs evidence independent of the conclusions it verifies |
| PA-18 | Waites (2026), Artificial Organisations — arXiv:2602.13275 | VERIFIED | Reliability through institutional structure |
| PA-19 | Rismani, Dobbe and Moon, From Silos to Systems (PHASE) — arXiv:2410.22526 | VERIFIED | STPA for AI; traceable accountability chains. The ladder applies this frame |
| PA-20 | Mylius (2025), Systematic Hazard Analysis for Frontier AI using STPA — arXiv:2506.01782 | VERIFIED | STPA applied to AI control |
| PA-21 | Leveson (2012), Engineering a Safer World (STAMP) | NOT CHECKED | Cite via PA-19 or PA-20 unless located |
| PA-22 | Cross, Genewein, Leibo, Tomasev and Vezhnevets (2026), Emergent Cheating and Whistleblowing in Autonomous Research Swarms — arXiv:2609.04170 | VERIFIED | Monitored channels and whistleblowing in a swarm |
| PA-23 | Rahman (2026), Extreme Overvalued Beliefs and AI Agents — preprints.org 202609.1396 | VERIFIED | Proposes, but does not test, an independent human escalation edge; S tests a version of it. Credit |
| PA-24 | Agrawal, Xiao, Bergman and Cooper Stickland (2026), Why Do Language Model Agents Whistleblow? — arXiv:2511.17085 | VERIFIED | Single-agent determinants of disclosure |
| PA-25 | Purcell, Köbis, Samuel and Bonnefon (2026), Whistleblowers Can Contain the Unethical Externalities of Human-AI Delegation | PARTIAL | Exists; listings disagree on PNAS versus PNAS Nexus. The whistleblowers are human observers |
| PA-26 | Tewolde et al. (2026), CoopEval (ICML 2026) | VERIFIED | Contracting and mediation sustain cooperation. The mechanical-gate result is largely predicted |
| PA-27 | Jones, Dragan and Steinhardt (2025), Adversaries Can Misuse Combinations of Safe Models (ICML 2025) | VERIFIED | Local safety ≠ combined safety (adversarial form) |
| PA-28 | HARP: Measuring Harm Amplification in Multi-Agent LLM Systems — arXiv:2605.27489 | VERIFIED | Local-to-global harm amplification (adversarial perturbation) |
| PA-29 | Pavlova and Tanaka (2026), Flag Game — arXiv:2609.19124 | VERIFIED | Collective belief formation; relevant to the deferred Phantom Scorer |
| PA-30 | Danassis et al., AI-driven Prices for Externalities and Sustainability in Production Markets (AAMAS 2023 extended abstract; arXiv:2106.06060) | VERIFIED | A policymaker agent corrects market externalities. Not novel: "governance can mitigate externalities" |

## Context (Non-Technical)

| ID | Work | Status | Use |
|---|---|---|---|
| PA-32 | Te Awa Tupua (Whanganui River Claims Settlement) Act 2017 — https://legislation.govt.nz/act/public/2017/7/en/latest/ | VERIFIED | Te Awa Tupua is a legal person (s 14); Te Pou Tupua is its human face (s 18). Contextual note only; never equated with a software channel |
| PA-33 | Murray–Darling Basin: activation of "sleeper" licences harming environmental flows | PARTIAL | Seen in a Productivity Commission inquiry submission (Brewarrina). Parliamentary-inquiry wording is reviewer-reported and not yet read directly |
| PA-34 | Thompson (1980), Moral Responsibility of Public Officials: The Problem of Many Hands, APSR 74(4) | NOT CHECKED | Recalled from memory; verify before citing |

## Do Not Cite (Not Found)

| ID | Reported title | Note |
|---|---|---|
| PA-31 | "Rectifying Market Externalities via AI Policymaking" (Springer) | Not located; possibly a journal version of PA-30 |
| PA-35 | "COALITION-VAST" (IEEE) | Not located |
| PA-36 | "Estimation of Propagated Risk" (Oct 2026) | Not located; nearest are PropUQ-MAS (arXiv:2608.22130) and RUPA (arXiv:2608.16002) |
| PA-37 | "A Responsibility-Centered Coordination Mechanism" (Oct 2026) | Not located; nearest are PA-11 and Tomašev et al., Intelligent AI Delegation (arXiv:2602.11865) |

## Claim Verification Register (E-007)

A claim is citable only when its source is VERIFIED and the located passage supports this specific claim (VERIFIED-PASSAGE). Near matches are not substitutes. Passages were read on 2026-11-02 unless noted.

| Claim, as it may appear in the report | Source | Locator | Status |
|---|---|---|---|
| Removing agents' ability to communicate led to overuse of the shared resource (GovSim) | PA-09 | arXiv:2404.16698v1, abstract | VERIFIED-PASSAGE |
| Across 12 tasks, multi-agent organisations scored higher on business goals and lower on ethics than single agents | PA-10 | Anthropic Alignment Science Blog post, Results | VERIFIED-PASSAGE |
| A classifier sweep found only 3–6 transcripts of agents considering alerting humans, and none pursued it | PA-02 | METR report, section on agents not notifying humans | VERIFIED-PASSAGE |
| Some agents escalated to the message board instead, treating it as a reasonable authority | PA-02 | Same section | VERIFIED-PASSAGE |
| Detection of compositional harm returned only when what the monitor observes changed, not with a stronger local classifier | PA-16 | Introduction, contribution (2) | VERIFIED-PASSAGE |
| Te Awa Tupua is a legal person (s 14); Te Pou Tupua is its human face (s 18) | PA-32 | s 14 via legislation.govt.nz; s 18 via a secondary summary | PARTIAL (read s 18 in the Act) |
| Some agents read the anti-cheating warning as a bluff after peers cheated unpunished | PA-22 | Secondary report (MIT Technology Review) | PARTIAL (locate the paper's passage) |

## Design Lineage (Observatory and Diorama)

These are inspirations for the exhibit, not evidence for findings. They are cited in the report only through the claim register.

| Work | What it gives the exhibit | Status |
|---|---|---|
| Dmitry Davidoff, *Mafia* (Moscow State University, 1986) | Table, phases, neutral moderator, reveal. Not adopted: hidden roles, villains, accusation | VERIFIED (secondary sources) |
| Bailis, Friedhoff and Chen, *Werewolf Arena* (arXiv:2407.13943, 2024) | LLMs in a social-deduction game; the boundary case, because its subject is deception and ours has no deceivers | VERIFIED |
| Park et al., *Generative Agents* / Smallville (UIST 2023) | Precedent for replaying agent runs visually; the diorama replays logs rather than simulating | VERIFIED |
| Nicky Case, *The Evolution of Trust* (2017, public-domain dedication) | One clear mechanic per scene; playable game theory after Axelrod | VERIFIED |
| Jansen, Dragicevic et al., *Opportunities and Challenges for Data Physicalization* (CHI 2015) | Data as an object; the physicalization tradition | VERIFIED |
| Munzner, *Visualization Analysis and Design*, ch. 6 (2014) | No unjustified 3D; function before form | VERIFIED |
| Museum of Science, Boston, *Engineer a River System* (Yawkey Gallery on the Charles River; MCN 2016 session) | A river-system table with projection mapping and physical feedback | VERIFIED (exhibit developer credit not confirmed) |
| London Museum Docklands, *Secrets of the Thames* (4 Apr 2025 – 1 Mar 2026) | Recreated foreshore with explorable 3D digital reconstructions | VERIFIED (digital studio credit not confirmed) |

## Final Novelty Pass

Scheduled for 5 Nov (Runbook, Gate G0). Searches: externalities in LLM-agent markets; absent or unrepresented stakeholders in multi-agent LLM systems; escalation routing in agent collectives; STPA applied to LLM multi-agent systems. Results are appended here.

### 5 November search and verification addendum

**Status: search and bounded contribution wording completed; G0 remains OPEN for two newly surfaced primary-source checks (PA-38/39).** Earlier entries are preserved. The corrections below govern the present report reference set. No experimental results were examined or generated during this review.

Searches used: `LLM multi agent markets externalities unrepresented stakeholders verified evidence escalation routing`; `multi agent LLM whistleblowing independent escalation oversight evidence`; `STPA LLM multi agent responsibility PHASE`; `LLM commons GovSim governance absent stakeholders`; `"LLM" "unrepresented" stakeholders markets`; `"LLM" "externalities" "evidence" governance`; and exact-title follow-ups. Discovery summaries were used to locate primary sources, not to verify technical findings. This is a bounded search, not a systematic review or proof of priority.

**Contribution sentence (prospective):** The Seventh Seat will compare four policy regimes in a scenario-blocked synthetic watershed, crossing access to verified aggregate evidence with consent-gated versus direct reporting to an identical scripted supervisor, and measure downstream shortfall, protection cost and the logged sequence of missed protection opportunities.

This is a specific experimental comparison. Do not claim that absent stakeholders, collective externalities, whistleblowing, evidence-based accountability, independent escalation or system-level hazard analysis are new. Keep result-dependent wording prospective until evaluation exists.

#### Bibliographic corrections and primary sources read

| ID | 5 November disposition | Primary source / locator |
|---|---|---|
| PA-09 | VERIFIED again: Giorgio Piatti, Zhijing Jin, Max Kleiman-Weiner, Bernhard Schölkopf, Mrinmaya Sachan and Rada Mihalcea, *Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents* (2024), NeurIPS 2024 | https://arxiv.org/abs/2404.16698v4 — title, authors, abstract, comments |
| PA-11 | VERIFIED again: Jinwei Hu et al., *Stop Reducing Responsibility in LLM-Powered Multi-Agent Systems to Local Alignment* (2025), preprint | https://arxiv.org/abs/2510.14008v2 — title, authors, abstract |
| PA-16 | VERIFIED again: Yibo Hu and Ren Wang, *When Local Monitors Miss Compositional Harm: Diagnosing Distributed Backdoors in Multi-Agent Systems* (2026), preprint | https://arxiv.org/abs/2607.11751v1 — title, authors, abstract |
| PA-17 | **PARTIAL → VERIFIED** for the source and bounded abstract claim below. Author is **Paul-Peter Arslan**. *Audit Without Verification: When LLM Accountability Layers Relay Rather Than Check* (2026), preprint | https://arxiv.org/abs/2609.07680v1 — author and abstract. No unsupported reviewer attribution retained |
| PA-19 | VERIFIED again: Shalaleh Rismani, Roel Dobbe and AJung Moon, *From Silos to Systems: Process-Oriented Hazard Analysis for AI Systems*. Initial preprint 2024; version 2 revised 2026 | https://arxiv.org/abs/2410.22526v2 — authors, dates, abstract |
| PA-22 | **Correction:** full title is *A Case Study on Emergent Cheating and Whistleblowing in Autonomous Research Swarms*. Author list begins **Davide Paglieri**, followed by Logan Cross, Tim Genewein, Joel Z. Leibo, Nenad Tomasev and Alexander Sasha Vezhnevets (2026). Earlier abbreviated attribution omitted the first author | https://arxiv.org/abs/2609.04170v1 — title, authors, abstract. The older claim about warnings being read as a bluff remains PARTIAL and is not in the report outline |
| PA-23 | VERIFIED: Tahir Rahman, *Extreme Overvalued Beliefs and Artificial Intelligence Agents* (2026), Preprints.org v1, not peer reviewed | https://www.preprints.org/manuscript/202609.1396 — intervention paragraph beginning “A complementary safeguard” |
| PA-24 | VERIFIED again: Kushal Agrawal, Frank Xiao, Guido Bergman and Asa Cooper Stickland, *Why Do Language Model Agents Whistleblow?*. Initial preprint 2025; version 3 revised 2026 | https://arxiv.org/abs/2511.17085v3 — authors, dates, abstract |
| PA-25 | Author manuscript and its human-observer claim verified; **publication metadata remains PARTIAL**. Zoe A. Purcell, Nils Köbis, Andrew Samuel and Jean-François Bonnefon. A publisher DOI candidate, `10.1073/pnas.2536668123`, was located but its page could not be read; do not treat the PNAS/PNAS Nexus issue as settled solely from search metadata | https://zoepurcell.org/wp-content/uploads/2025/09/Whistleblowing.pdf — title page; introduction pp. 3–4, especially lines 66–94. Omitted from the current report bibliography pending venue/year verification |
| PA-30 | VERIFIED with update: Panayiotis Danassis, Aris Filos-Ratsikas, Haipeng Chen, Milind Tambe and Boi Faltings. *AI-driven Prices for Externalities and Sustainability in Production Markets*. v5 (2026) reports the full version accepted in *Autonomous Agents and Multi-Agent Systems*; AAMAS 2023 was preliminary. Cite the versioned preprint here, rather than conflating versions | https://arxiv.org/abs/2106.06060v5 — authors, abstract, publication comment and version history |

#### Additional claim register (only these bounded claims rechecked today)

| Claim | Source and passage | Status |
|---|---|---|
| GovSim studies strategic interaction and sustainable use of a common resource by LLM agents; communication matters in the reported setting | PA-09 v4, abstract | VERIFIED-PASSAGE |
| The local-alignment position paper argues for system-level responsibility across the multi-agent lifecycle | PA-11 v2, abstract | VERIFIED-PASSAGE; position, not experimental evidence |
| Distributed payloads can escape local monitoring; changing the observed representation can recover signal in the studied attack settings | PA-16 v1, abstract | VERIFIED-PASSAGE; not a universal theorem about this watershed |
| An auditor can relay upstream conclusions rather than independently verify them; the study motivates evidence independent of those conclusions | PA-17 v1, abstract, final paragraphs | VERIFIED-PASSAGE; no numerical claim imported |
| PHASE adapts STPA for AI systems and supports traceable accountability between harms and those able to mitigate them | PA-19 v2, abstract | VERIFIED-PASSAGE; our ladder is an application, not validated by this citation |
| The research-swarm case study reports emergent cheating and peer responses including audits and reporting | PA-22 v1, abstract | VERIFIED-PASSAGE; not evidence that direct external oversight was effective |
| Rahman proposes an independent, non-peer-mediated path to human oversight | PA-23, intervention paragraph beginning “A complementary safeguard” | VERIFIED-PASSAGE; proposal, not an intervention trial |
| Whistleblowing in staged misconduct scenarios varies with model, task complexity, prompting and available workflows | PA-24 v3, abstract | VERIFIED-PASSAGE |
| Human observers can respond to unethical human-to-AI delegation by whistleblowing | PA-25 author manuscript, introduction pp. 3–4 | PASSAGE VERIFIED; bibliography still PARTIAL, so not yet in report |
| A reinforcement-learning policymaker adjusts prices and allocations with externality-related objectives | PA-30 v5, abstract | VERIFIED-PASSAGE; no claim about LLM district agents |

#### Newly surfaced close leads — do not cite as verified

| ID | Lead | Status and next check |
|---|---|---|
| PA-38 | Yujiao Chen, *Individually Sensible, Collectively Harmful: Simulating Commons Failure in LLM Societies*, reportedly Social Sim @ COLM 2026; OpenReview `cOzZdFglau` | PARTIAL: secondary discovery page describes silent harmed stakeholders and a harm-display intervention, making it a potentially close comparison. Primary forum/PDF require browser verification; public API retrieval also failed. Read the manuscript before asserting its methods/results or novelty relative to it. Primary: https://openreview.net/forum?id=cOzZdFglau ; discovery only: https://lacuna.tiptreesystems.com/work/individually-sensible-collectively-harmful-simulating |
| PA-39 | Theja Tulabandhula, *Distinguishing Governance Effects from Prompting Artifacts in LLM Pricing Simulations*, reportedly Social Sim @ COLM 2026 | PARTIAL: secondary discovery only; exact-title primary-source search returned no accessible manuscript. Verify on the workshop/OpenReview before citation. Discovery: https://lacuna.tiptreesystems.com/work/distinguishing-governance-effects-from-prompting-artifacts |

PA-38 makes a broad “first absent-party commons experiment” claim inappropriate even while primary verification is pending. PA-39 motivates care about framing as a possible alternative explanation, but its reported numerical findings are not evidence in this project. Existing PA-21, PA-33, PA-34 and PA-31/35/36/37 remain outside the report reference set; no unverified legal, historical or incident-specific claims are needed for the current outline.


## 6 November bounded final novelty pass (Codex continuation)

G0's final search and contribution revision are complete for the bounded claim below.
PA-38/39 manuscripts remain **UNVERIFIED** and must not be cited as read papers.
The OpenReview browser challenge blocked both direct PDFs on 6 November.

- PA-38 primary institutional summary read at https://www.reigndragon.ai/findings/creeping-trap . **VERIFIED-PASSAGE (website abstract only):** the authors' institute describes a repeated extraction benchmark with nonacting bystanders who share catastrophe losses, and a visibility intervention. This establishes substantial conceptual overlap. It does not verify the paper's sample, estimates, implementation or routing mechanisms. A website attribution must say it is an institutional summary.
- PA-39 discovery now identifies OpenReview https://openreview.net/forum?id=ihKxyyqkGv . The primary manuscript could not be read. No result or numerical claim from the aggregator is adopted or included in the bibliography.
- Prospective contribution (revised): **A reproducible, scenario-blocked comparison of verified aggregate projections and consent-gated versus direct reporting to a fixed scripted supervisor in one designed watershed, with engine-derived outcomes and descriptive records of protection opportunities.** This is a description of the study, not a priority or uniqueness claim. Absent-party externalities, visibility interventions and governance effects already have related precedents. No claim that this exact combination is absent from unread literature is warranted.
- The report's intended cited papers remain the verified, passage-bounded entries in the 5 November register and `report/references.bib`. PA-38/39 paper citations remain excluded. Full-manuscript follow-up is still desirable, but cannot justify a broader claim meanwhile.

Official rules re-read 6 November: https://apartresearch.com/sprints/swarm-alignment-2026 . The page allows replacing a submission before the deadline by submitting with the same title; the author's one-final-submission preference remains unchanged. The eight-main-page limit, required ethics appendix and pre-existing-work disclosure remain in force.
