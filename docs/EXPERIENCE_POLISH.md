# Seal, soundtrack and diorama polish — 7 November 2026

This presentation-only update preserves the released manuscript, original submission PDF, experimental records, analysis and diorama engine. It builds on Claude's existing hub and the previous reading edition. The supplied seal is used for SVG/ICO/PNG favicons, Apple touch icons, web manifests and social-preview artwork on the portfolio and Seventh Seat pages. Browser and social caches control when refreshed icons appear; PDF viewers have their own application icons.

The optional soundtrack reuses the author's eight original Rushii recordings unchanged. There are no new provider calls or purchases. See `observatory/research/audio/README.md` for the drop-in workflow. Music continues while the diorama is embedded in the hub; the standalone view remains available. Closing the embedded view unloads its graphics document. Motion follows reduced-motion preferences.

## Scientific review

The independent records audit again passed 1,187 checks across all 96 evaluation episodes and 24 matched blocks. All 32 frozen scientific source hashes match. Neither primary hypothesis meets the preregistered confidence-interval rule: absence of support is not proof of zero effect. The hub now states that distinction and explains shortfall and the four matched conditions in plain language. Zero structured concern/report actions does not imply no discussion of risk. H4 was not collected; AWC remains the documented conservative phase-end proxy. These synthetic findings do not establish real-world safety or consciousness claims.

The cited primary-source pages were checked for consistency with the paper's bounded background claims: [GovSim](https://arxiv.org/abs/2404.16698), [Agrawal et al.](https://arxiv.org/abs/2511.17085), [PHASE](https://arxiv.org/abs/2410.22526), [research swarms](https://arxiv.org/abs/2609.04170), [independent records](https://arxiv.org/abs/2609.07680), [externality pricing](https://arxiv.org/abs/2106.06060), and [Creeping Trap](https://www.reigndragon.ai/findings/creeping-trap). The last remains an unreviewed findings page, not an available peer-reviewed paper. This is a consistency and arithmetic review, not an independent replication of those studies.

## Verification and deployment boundary

The candidate passed 248 browser checks (including actual audio playback, deferred audio download, pause, volume, embedded experimental diorama measurements and content policy) and the original diorama passed 97 checks. No screenshots were needed for this pass. Audio remains unloaded until requested; the initial page payload is about 325 kB and the complete version about 16.4 MB. The paper and all scientific exhibit data remain unchanged.

The presentation archive is installed separately from the portfolio. `deploy/install_experience.py` validates a pinned archive and the exact previous/new serving-file hashes, preserves prior files, changes only the Seventh Seat serving allowlist and static release symlink, and gracefully reloads **blog.service**. It checks all live files, HTML policies, audio range requests and sibling publication routes; failure restores the previous serving file and release. The old research and reading release tags are unchanged. A published archive alone is not proof of a live deployment.
