# Modern analysis status — November 21, 2026

The three notebook rewrites are implemented. All three have run in fresh kernels on the corrected 7,332-article corpus. The 7,332 normalized full-text embeddings and all six standard BERTopic seed-42 fits are complete. The shared corpus hash matches the existing manifest exactly.

| Run | Topics | Mean c_v | Unassigned | Cosine silhouette |
| --- | ---: | ---: | ---: | ---: |
| n15_c25_s42 | 76 | 0.692 | 20.2% | 0.114 |
| n15_c50_s42 | 40 | 0.662 | 19.9% | 0.119 |
| n15_c100_s42 | 21 | 0.641 | 14.6% | 0.105 |
| n30_c25_s42 | 70 | 0.705 | 18.0% | 0.122 |
| n30_c50_s42 | 35 | 0.646 | 19.1% | 0.123 |
| n30_c100_s42 | 24 | 0.630 | 22.2% | 0.134 |

Full precision, timing, and provenance are in `Results/modern/experiments.csv` and each run's manifest. All top terms have full coverage in the common coherence reference. Silhouette excludes outliers and samples at most 2,000 assigned articles. These are full-corpus exploratory results, not held-out performance.

Every grid run has a topic inventory, development examples, size plots, publication counts/proportions for all 25 outlets, and publication figures for the 16 outlets with at least 50 articles. Labels are provisional keyword labels. Results from the old 7,337-article runs are not reused.

## Explicit team decisions and pending inputs

The user requested that **model selection remain pending for team article review**. `Results/modern/selection.json` is intentionally unfilled. No automatic selection, final thematic interpretation, or selected-model seed result is claimed.

1. Review run metrics and nonreserved representative articles, then record the chosen run, rationale, and team selector in `selection.json`.
2. Rerun notebook 02 to fit the selected configuration with seeds 7 and 21, export matched publication comparisons, and create its label table.
3. Confirm topic names with article evidence. Existing human edits are preserved across reruns.
4. Laura supplies the four LDA exports. Joint human review additionally needs confirmed classical labels and the shared review-reservation attestation.
5. Two team members independently complete the review packets. Real ratings are not available yet; no independent human scores have been generated.

The 100-article sample is reserved before new development review. Audit-packet IDs and legacy development examples are excluded. Share `Results/modern/review_sample.json` with Laura before topic naming.

## Verification and boundaries

Sixteen tests passed, including a real synthetic-data BERTopic fit/serialization check, exact corpus reconstruction, cache/run rejection, reserved-example separation, label preservation, publication denominators, seed-label permutation, LDA alignment, review freeze/roster validation, outlier exclusions, and degenerate kappa/bootstrap cases. Synthetic fixtures live only in temporary test directories and are not project findings.

Fresh-kernel notebook execution covers the real complete-grid/pending-team-input path. Completed-review behavior is tested with temporary fixtures; no genuine completed team input exists to exercise the final joint notebook branch yet. Publication figure layout was visually inspected.

`pr3-submission.tex`, the classical implementation, and legacy model artifacts are untouched. The PR3 evidence checklist and completion-plan CSV identify remaining work; team completion dates and PR2 feedback are not invented.

Held-out evaluation and shared-period publication sensitivity remain final-report work. See the [notebook README](notebooks/README.md) for commands, schemas, rubric, interpretation limits, and the rare-stratum issue.

## Guided reviewer notebook

The individual reviewer notebooks provide the 1–5 rubric, article display, commented answer-entry cells, save/correction controls, and resumable progress. `../human-review/review_coordinator.ipynb` handles preparation, progress counts, combined results, and interpretation. Each reviewer uses a separate ignored personal workbook and their own answer CSV. No genuine ratings or model selection have been supplied.

The notebook's default pending-input path executed successfully in a fresh kernel. Five additional tests exercise entry, resuming, corrections, stale edits, packet identity, outliers, separation of reviewer files, the notebook's item-number guard, and compatibility with the existing summary. The full suite now passes 21 tests. The original three analysis notebooks and study results are unchanged by this addition.

## Separate reviewer notebooks — November 22, 2026

Human-review notebooks now live in `../human-review/`. The shared notebook has been renamed and refocused as `review_coordinator.ipynb`. New `reviewer_1.ipynb` and `reviewer_2.ipynb` are preconfigured for their respective answer CSVs and contain only the independent reading, rating, saving, and progress steps. Combined-score and team-interpretation cells remain in the shared notebook.

The full suite passes 22 tests, including six reviewer-workflow tests checking that each new notebook saves only its own reviewer file and resumes existing answers. Both new notebooks executed in fresh kernels with their safe pending-input defaults. The existing three analysis notebooks, saved study outputs, and PR3 manuscript were preserved. The validation command now follows the new folder layout and accepts `--execute reviewer_1 reviewer_2`.

## Coordinator notebook refocused — November 22, 2026

`../human-review/review_coordinator.ipynb` now contains only coordinator work: preparation instructions, packet lookup, aggregate completion counts, explicitly enabled combined results, interpretation notes, and PR3 handoff. Individual article display and answer entry remain in the two reviewer notebooks. Reviewer code and saved outputs, answer files, analysis notebooks, and the manuscript were preserved.

The coordinator notebook executed successfully in a fresh kernel with pending inputs, and the full suite passes 23 tests. The additional coordinator test covers read-only progress, incomplete/missing submissions, explicit summary generation after completion, and unchanged original reviewer files. Use `--execute coordinator`; the old `--execute 04` command remains an alias.

## Joint comparison moved to its own notebook — November 22, 2026

`../comparison/pipeline_comparison.ipynb` now owns the PR2 cross-method evaluation: shared coherence/diversity, top-ten Jaccard overlap and ties, assignment contingency, both publication heatmaps and matched shares, measured runtime context, frozen review packets, and the combined quantitative/human table. Modern notebook 03 now exports only modern inventories, publication results, and its modern evidence/completion tables. Reviewer and coordinator instructions point to the new notebook.

Existing `Results/classical/` and `Results/comparison/<run>/human_review/` paths remain unchanged. The new notebook validates exported artifacts without loading model pickles or embeddings, preserves reviewer answers, and rejects mismatched comparison identities. Use `verify_notebooks.py --execute comparison`. Model selection, LDA exports, confirmed labels, and genuine ratings are still pending; no current joint empirical findings are claimed.

All 28 tests pass. Modern notebook 03 and the new comparison notebook executed in fresh kernels with the actual available inputs. A separate fresh-kernel execution on temporary synthetic exports and ratings exercised the complete comparison path; those fixture ratings were never written to study outputs. The classical implementation, modern fitting helpers, six fitted runs, and PR3 manuscript are unchanged.

## Selected comparison completed — November 25, 2026

Mary Kate selected `n30_c25_s42` after reviewing the current shortlist. The existing six seed-42 fits and embeddings were reused; selected seeds 7 and 21 are complete. Shared quantitative comparison now reads LDA directly from `../classical-methods/results/`. Older entries above describe historical pending states.

The selected BERTopic model has 70 topics, c_v=0.704696, diversity=0.651429 and 18.0442% unassigned; LDA has 40 topics, c_v=0.655233 and diversity=0.710000. BERTopic seed ARIs are 0.961365 and 0.976049 on 77.70% and 77.44% of articles, respectively; LDA ARIs are 0.323033 and 0.346897 on all articles. These denominators must accompany comparisons.

Comparison tables, plots, draft inventories and both seed summaries are saved under `Results/comparison/n30_c25_s42/`. Assistant draft labels remain separate from confirmed-label inputs, and no human-review packet or scores were created. LDA timing context remains unavailable. The current selection evidence explicitly describes passage-based development review, not independent human scores.

See [PR3 results notes](../../progress-report-3/pr3-results-notes.md) for all research-question findings, limitations, evidence links and reproduction commands. The existing PR3 manuscript, tables and figures remain unchanged.

## Robustness and partial human confirmation — November 25, 2026 (latest)

The computational follow-up is complete in [Results/robustness/2026-11-25](Results/robustness/2026-11-25/README.md), separate from selected full-corpus model exports. New LDA fits at seeds 42/7/21 reproduce the existing seed-42 assignments and recorded seed ARIs; matched publication comparisons expose substantial changes, including a seed-7 reversal of the Vox–Reuters litigation ordering. All six existing BERTopic configurations now have publication/theme sensitivity analysis with unmatched-topic and split/merge diagnostics. No expanded grid was run.

The coverage-only rule selects 2016–2018, retaining 4,931 articles from 11 publications. The seed-42 exploratory split has 5,866 training and 1,466 held-out articles, with ten singleton publication/year strata retained in training. Training-only vocabularies/fits give held-out-reference coherence 0.613030 for LDA and 0.633697 for BERTopic; LDA held-out perplexity is 6,922.24. BERTopic leaves 454/1,466 held-out articles unassigned (30.97%). Prior full-corpus development is disclosed; these are not untouched test results. New stage timings, historical LDA search evidence and a verified primary-source comparison with Kang et al. are documented in the notes.

Mary Kate explicitly approved LDA 22 and BERTopic 4/5 during guided review. The approved BERTopic 5 label is **Uber leadership and corporate culture**. Exactly three of 110 labels are approved; the other 107, the shared-reservation attestation and two independent 100-article rating submissions remain pending. LDA's manifest explicitly records partial confirmation and `labels_confirmed=false`. No review packet, human fit scores or audit judgments were generated. The original 30-article audit fields remain blank. [Eleven label-review batches](Results/robustness/2026-11-25/label_review/README.md) and a preserved decision ledger support the remaining human work.

Earlier comparison artifacts and label inputs are preserved in the label-update archive before rebuilding the current comparison identity. New reporting hooks keep computational checklists current on rerun without confirming human work. Modern notebook 03, comparison and robustness results executed in fresh kernels; the test suite passes 37 tests. Original PR3 manuscript/tables/figures, fitting helpers, model assignments/terms/mixtures and review reservation are preserved. See the separate [results notes](../../progress-report-3/pr3-results-notes.md) for findings, denominators, limitations and exact commands.

## Human review resumed — November 25, 2026 (latest)

Verified 3/110 naming approvals; 107 remain pending. Assistant recommendations for LDA 15, BERTopic 9 and LDA 26 are ready for actual decisions. Their nine article IDs match their topics and exclude the reserved sample. No bound model/comparison inputs, reservation, or original PR3 manuscript/tables/figures were changed.

Mary Kate confirmed original corpus-audit judgments are unavailable and requested a new dated audit. [New audit materials](Results/robustness/2026-11-25/audit_review/2026-11-25/README.md) preserve the same 30 articles in ten groups of three, original CSV bytes and provenance. Human fields are blank (0/30 complete). The historical PR2 audit claim remains unsupported by saved judgments. No independent fit ratings or reservation attestation have been supplied. Earlier test results cover the earlier code state; this update prepares review artifacts only.

## Six explicit naming approvals — November 25, 2026 (latest)

Mary Kate approved LDA 15, BERTopic 9 and LDA 26, including the recommended qualifications, in chat. The ledger now records 6/110 approvals; 104 labels remain pending. `approved_decisions_next_three.json` preserves the new approvals and assistant reading scope. The first three approvals are in authoritative model inputs; these newest three await preservation/transfer/rebuild. Bound inputs and comparison identity are unchanged at this step. No independent fit ratings, reservation attestation or new audit judgments were supplied.

## Nine naming approvals — November 25, 2026 (latest)

Mary Kate explicitly approved LDA 27, LDA 37 and LDA 4 with the presented qualifications. The ledger now records 9/110 approved, 101 pending. `approved_decisions_third_three.json` preserves these decisions. Three approvals are transferred into authoritative model inputs; six await preservation/transfer/rebuild. No bound inputs, reservation, independent ratings or corpus-audit judgments changed.

## Twelve naming approvals — November 25, 2026 (latest)

Mary Kate explicitly approved LDA 23, LDA 25 and BERTopic 12 with their qualifications. The ledger records 12/110 approved, 98 pending; batch 1 is complete. `approved_decisions_fourth_three.json` preserves these decisions. Three approvals are in authoritative model inputs; nine await preservation/transfer/rebuild. Bound inputs and reservation remain unchanged. Independent fit ratings, reservation attestation and the new 30-article audit judgments remain pending.

## Fifteen naming approvals — November 25, 2026 (latest)

Mary Kate explicitly approved BERTopic 13, 15 and 22 with their qualifications. The ledger records 15/110 approved, 95 pending. `approved_decisions_fifth_three.json` preserves these decisions and reading scope. Three approvals are in authoritative model inputs; twelve await preservation/transfer/rebuild. Bound inputs and reservation remain unchanged. Independent fit ratings, reservation attestation and new corpus-audit judgments remain pending.

## Eighteen naming approvals — November 25, 2026 (latest)

Mary Kate explicitly approved BERTopic 23, LDA 16 and LDA 18 with their qualifications. The ledger records 18/110 approved, 92 pending. `approved_decisions_sixth_three.json` preserves these decisions and reading scope. Three approvals are in authoritative model inputs; fifteen await preservation/transfer/rebuild. Bound inputs and reservation remain unchanged. Independent fit ratings, reservation attestation and new corpus-audit judgments remain pending.

## Twenty-one naming approvals — November 25, 2026 (latest)

Mary Kate explicitly approved LDA 38, BERTopic 30 and LDA 20 with their qualifications, including low confidence for LDA 38. The ledger records 21/110 approved, 89 pending; batches 1 and 2 are complete. `approved_decisions_seventh_three.json` preserves these decisions. Three approvals are in authoritative model inputs; eighteen await preservation/transfer/rebuild. Bound inputs and reservation remain unchanged. Independent fit ratings, reservation attestation and new corpus-audit judgments remain pending.

## Twenty-four naming approvals — November 25, 2026 (latest)

Mary Kate explicitly approved BERTopic 34, LDA 13 and BERTopic 46 with their qualifications. The ledger records 24/110 approved, 86 pending. `approved_decisions_eighth_three.json` preserves these decisions. Three approvals are in authoritative model inputs; twenty-one await preservation/transfer/rebuild. Bound inputs and reservation remain unchanged. Independent fit ratings, reservation attestation and new corpus-audit judgments remain pending.

## Twenty-seven naming approvals — November 25, 2026 (latest)

Mary Kate explicitly approved BERTopic 47, 48 and 51 with their qualifications. The ledger records 27/110 approved, 83 pending. `approved_decisions_ninth_three.json` preserves these decisions. Three approvals are in authoritative model inputs; twenty-four await preservation/transfer/rebuild. Bound inputs and reservation remain unchanged. Independent fit ratings, reservation attestation and new corpus-audit judgments remain pending.

## Thirty naming approvals — November 25, 2026 (latest)

Mary Kate explicitly approved BERTopic 58, 59 and 60 with their qualifications. The ledger records 30/110 approved, 80 pending; batches 1–3 are complete. `approved_decisions_tenth_three.json` preserves these decisions. Three approvals are in authoritative model inputs; twenty-seven await preservation/transfer/rebuild. Bound inputs and reservation remain unchanged. Independent fit ratings, reservation attestation and new corpus-audit judgments remain pending.

## Thirty-three naming approvals — November 25, 2026 (latest)

Mary Kate explicitly approved BERTopic 61, BERTopic 64 and LDA 1 with their qualifications. The ledger records 33/110 approved, 77 pending. `approved_decisions_eleventh_three.json` preserves these decisions. Three approvals are in authoritative model inputs; thirty await preservation/transfer/rebuild. Bound inputs and reservation remain unchanged. Independent fit ratings, reservation attestation and new corpus-audit judgments remain pending.

## Thirty-six naming approvals — November 25, 2026 (latest)

Mary Kate explicitly approved BERTopic 67, LDA 0 and BERTopic 0 with their qualifications. The ledger records 36/110 approved, 74 pending. `approved_decisions_twelfth_three.json` preserves these decisions. Three approvals are in authoritative model inputs; thirty-three await preservation/transfer/rebuild. Bound inputs and reservation remain unchanged. Independent fit ratings, reservation attestation and new corpus-audit judgments remain pending.

## Thirty-nine naming approvals — November 25, 2026 (latest)

Mary Kate explicitly approved BERTopic 1, LDA 2 and LDA 7 with their qualifications. The ledger records 39/110 approved, 71 pending. `approved_decisions_thirteenth_three.json` preserves these decisions. Three approvals are in authoritative model inputs; thirty-six await preservation/transfer/rebuild. Bound inputs and reservation remain unchanged. Independent fit ratings, reservation attestation and new corpus-audit judgments remain pending.

## All 71 remaining labels presented — November 25, 2026 (latest)

At Mary Kate's request, all remaining labels are presented together in `Results/robustness/2026-11-25/label_review/remaining_recommendations_2026-11-25.csv` with reading scope and qualifications. Counts and evidence membership/reservation exclusion verified. Still 39 approved, 71 pending (23 LDA, 48 BERTopic); no new approvals inferred. Three approved labels are transferred; thirty-six await preservation/transfer/rebuild. Bound inputs remain unchanged. Independent ratings, reservation attestation and new audit judgments remain pending.

## All 110 naming approvals recorded — November 25, 2026 (latest)

Mary Kate explicitly approved all remaining 71 labels and their stated qualifications with the chat response “Approve all 71.” The ledger now records 110/110 approved (40 LDA, 70 BERTopic), with no pending naming decisions. `approved_decisions_remaining_71.json` preserves the final decisions; the original 71-proposal snapshot remains unchanged as historical evidence. These are assisted naming approvals by Mary Kate, not independent fit ratings or approval by other team members. Three labels remain transferred into authoritative inputs; the other 107 await transfer/rebuild following the genuine shared-reservation attestation. Current comparison artifacts, drafts, classical exports, selected modern artifacts and prior review records were copied and hash-verified in `label_confirmation_archive/all_labels_approved_before_transfer/`. Bound inputs and comparison identity remain unchanged. No attestation, independent ratings or new corpus-audit judgments were inferred. The new dated audit remains 0/30 complete.

## Labels transferred and packets frozen — November 25, 2026 (latest)

All 110 approved labels (40 LDA, 70 BERTopic) are now transferred into authoritative label tables. Mary Kate supplied the explicit chat attestation “I attest that this is true” after the reservation requirement was explained. The dated record `label_review/reservation_attestation_2026-11-25.json` binds the unchanged 100-article reservation. It records Mary Kate’s statement only; no separate review or attestation by other team members is inferred. LDA’s manifest now has `labels_confirmed=true`, all 40 confirmed IDs and the actual `shared.corpus.digest(reservation)`. Earlier bound inputs, drafts and comparison outputs are preserved in `label_confirmation_archive/all_labels_approved_before_transfer/`. The prior comparison was moved intact and rebuilt through the existing notebook with its identity guard unchanged. Original assistant drafts are retained; `draft_label_reconciliation.csv` records their relationship to approved labels.

The frozen packet contains 100 reserved articles and 200 model/article items per reviewer: 100 LDA fit ratings and 76 assigned BERTopic fit ratings, plus 24 unassigned BERTopic items for qualitative review with blank fit scores. Separate working copies and personal notebooks are in `Results/comparison/n30_c25_s42/human_review/handoff/reviewer_1/` and `reviewer_2/`. Each contains only its own blank answer file. Both reviewers remain unassigned and at 0/200 completed items. No human means, agreement or kappa results were computed. The new dated corpus audit remains 0/30 and the historical PR2 claim remains unsupported. See `label_review/packet_preparation_verification.json` for packet and preservation checks.

Validation of this completed label transfer: the existing 37-test suite passed; after the checklist correction, all six focused reporting/robustness tests passed. The comparison notebook completed again in a fresh kernel, retained the same frozen packet hash and blank reviewer files, and preserved the pending interpretation task. Modern checklists were refreshed from authoritative labels without rerunning modern experiments. Logs are in `Results/robustness/2026-11-25/label_confirmation_verification/`. Git whitespace validation passed with standard CRLF CSV line endings recognized.

## Substantive interpretations approved — November 26, 2026 (latest)

Mary Kate explicitly approved the three presented conclusions and qualifications: recurring AV themes alongside format-driven clusters; publication differences conditional on topic definitions and robustness; and complementary model descriptions without an overall winner. The exact decision and supporting evidence hashes are in `Results/robustness/2026-11-26/interpretation_review/approved_interpretations.json`, and the current results notes include the approved wording. This records Mary Kate’s review only. Independent fit ratings, corpus-audit judgments, report preparation and any additional team review remain separate. No model, label, reservation, frozen packet or reviewer-answer files were changed. Existing generated checklists referring to team interpretation should be read with this dated approval record; broader team approval has not been inferred.
