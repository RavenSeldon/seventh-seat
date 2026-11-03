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
