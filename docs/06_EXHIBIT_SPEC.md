# Exhibit Specification v0.1: The Observatory

**Status:** FROZEN as intent 2026-11-02 (tag `founding-v0.1`). Visual details may evolve; the data rules below may change only via errata.

## Data-Ink Rules (Binding)

1. **Every mark has a source.** Each visual element maps to a logged field or a computed metric, documented in a source table shipped with the exhibit. Anything that is not data is labelled *metaphor* in plain words.
2. **Stars light only when the record supports them.** No animation implies an event the log does not contain.
3. **Matched reruns are never called counterfactuals.**
4. **Uncertainty travels with every effect estimate** (interval shown, N stated).
5. **Claims are shown as claims.** Agent text appears in quotation, never as narration of what an agent believed.
6. **Exhibits are built from results that exist.** Nothing is designed around an expected finding.

## The Four Exhibits

| Exhibit | Shows | Data source |
|---|---|---|
| The Seven Seats | One ring per episode: six district seats, one dark seat. The dark seat's fill is the downstream shortfall | Engine truth: commits, `S` |
| The Ladder | Where episodes stopped progressing (hazard → evidence → access → assessment → escalation → intervention → outcome), stacked by cell, beside mean shortfall with intervals | Ladder computation (`01` §9) |
| The Witness Record | One agent at a time: what it could see (view), said (claim) and did (act), against what was true | Four descriptions per event |
| Two Rivers | One scenario side by side under two cells, labelled "matched rerun" | Paired episodes from the blocked design |

## Visual Identity

- **Lineage:** the dark field and gilded line of Schrödinger's Civilization and Sīdus, kept intact.
- **Physically meaningful cosmos:** the river's course is the causal graph; flows are drawn as threads whose width is units of water.
- **Optional metaphor, labelled:** Neptune was located in 1846 from its pull on Uranus's orbit. The ledger likewise infers an absent party from the perturbations it causes. Where the analogy breaks: the designers know the downstream community exists; it is the agents' objectives that omit it.
- **Contextual note (not a claim of equivalence):** Te Awa Tupua (PA-32) is a legal person with human guardians who speak for it. That framework arises from a specific Māori legal, cultural and historical context; our scripted supervisor and reporting route are a far narrower engineering mechanism. The note is respectful, brief, and never central.

## Accessibility

Text alternatives for every figure (source tables double as alternatives); reduced-motion respected; keyboard navigable; sufficient contrast on the dark field; readable at phone width.

## Size and Hosting Budget

See `DEPLOY.md` (whole release 15 MB or less, first load 1.5 MB or less, no runtime calls).
