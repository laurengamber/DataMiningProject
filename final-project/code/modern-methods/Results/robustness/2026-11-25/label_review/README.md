# Team topic-label review

**November 26 ownership correction:** Keep `classical-methods/` unchanged. Approved LDA names and confirmation metadata are now comparison-owned; see `Results/comparison/n30_c25_s42/classical_labels.csv`, `classical_labels_identity.json`, and `classical_label_migration.json`. Earlier transfer entries below describe historical actions, superseded by this relocation.

The starting inventory contains 110 assistant drafts. All 110 labels have explicit human approval recorded in the decision ledger; no naming decisions remain pending. These are assisted naming decisions, not independent fit ratings.
Work through one 10-topic batch at a time. Start with flagged topics; read full representative articles in the local HTML cards. Keywords and examples can reveal mixed themes, source identity, newsletters, transcripts and page artifacts. Do not interpret low coherence or these automatic flags as human findings.

Record actual decisions in `team_decisions.csv`: `approve`, `revise`, or `defer`; final approved label; reviewer names; review date; article evidence notes; and an explicit reservation attestation only if true. All supplied evidence IDs exclude the reserved 100 articles. New supporting evidence must also be nonreserved and belong to the topic. Leave undecided entries blank. Rerunning preparation preserves the decision file.

| Batch | Topics | Full local article cards |
| --- | ---: | --- |
| 1 | 10 | [batch_01.html](batch_01.html) |
| 2 | 10 | [batch_02.html](batch_02.html) |
| 3 | 10 | [batch_03.html](batch_03.html) |
| 4 | 10 | [batch_04.html](batch_04.html) |
| 5 | 10 | [batch_05.html](batch_05.html) |
| 6 | 10 | [batch_06.html](batch_06.html) |
| 7 | 10 | [batch_07.html](batch_07.html) |
| 8 | 10 | [batch_08.html](batch_08.html) |
| 9 | 10 | [batch_09.html](batch_09.html) |
| 10 | 10 | [batch_10.html](batch_10.html) |
| 11 | 10 | [batch_11.html](batch_11.html) |

## After the team confirms all labels

1. Preserve a dated copy of the existing selected comparison directory and its `comparison_identity.json` before changing bound label inputs. Keep original reviewer files untouched if any exist.
2. Transfer only genuinely approved modern labels/evidence to `Results/modern/selected/n30_c25_s42/topic_labels.csv`, then set `confirmed=true` for those rows. Preserve its companion identity.
3. Keep all `classical-methods/` files unchanged. Store approved LDA names and evidence in `Results/comparison/<modern-run>/classical_labels.csv` (`topic_id`, `manual_label`, `evidence_notes`). Store approval and reservation metadata in `classical_labels_identity.json`, including corpus/run IDs, confirmed topic IDs, the table SHA-256, and SHA-256 hashes of the original assignments, terms, topics and manifest. The comparison applies these names to an in-memory copy only. Preserve the decision ledger as evidence; approval describes assisted comparison naming, not changes to the classical results.
4. The comparison identity deliberately rejects changed bound inputs. Archive the prior comparison folder, retaining draft edits, before regenerating it through the existing comparison notebook. Reconcile draft copies with approved labels instead of silently losing edits.
5. Run the comparison notebook to freeze packets; give each reviewer the same packet/freeze/status files and only their own answer CSV. Each independently rates all 100 articles for both models. No cross-reviewer answer exposure. Leave BERTopic unassigned fit scores blank.
6. Only after both genuine submissions are complete, enable the existing human summary: per-reviewer means, exact and within-one agreement, quadratic-weighted kappa, and 1,000 article-bootstrap resamples. Report assigned denominators, outlier exclusions and unusable resamples.

## Missing corpus audit

PR2 claims a manual 30-article audit, but saved relevance, boilerplate, malformed and notes fields are blank. The original `final-project/data/corpus_review.csv` is preserved. Ask the team for original judgments; otherwise perform a new dated human audit of those 30 articles and identify it as new. Do not backdate judgments or substitute assistant assessments.

## Additional approvals — November 25, 2026

Mary Kate explicitly approved the recommended labels and qualifications for LDA 15, BERTopic 9 and LDA 26. See `approved_decisions_next_three.json`. Six labels are now approved in the ledger. The first three are transferred to authoritative inputs; the newest three await transfer after preserving bound inputs and rebuilding the comparison through the existing workflow. Bound model/comparison inputs remain unchanged at this step. No reservation attestation or independent fit ratings were supplied.

Original corpus-audit judgments are unavailable per Mary Kate. A new dated audit is prepared in `../audit_review/2026-11-25/`; 0/30 judgments have been submitted.

## Nine approvals — November 25, 2026 (current)

Mary Kate explicitly approved LDA 27, LDA 37 and LDA 4, including mixed/format-driven and source/page-artifact qualifications as applicable. See `approved_decisions_third_three.json`. The ledger records 9/110 approvals, with 101 pending. Three approvals have been transferred into authoritative model inputs; six await preservation/transfer/rebuild. No reservation attestation, independent fit rating or new corpus-audit judgment was supplied. Earlier entries retain their historical counts.

## Twelve approvals — November 25, 2026 (current)

Mary Kate explicitly approved LDA 23, LDA 25 and BERTopic 12 and their qualifications. See `approved_decisions_fourth_three.json`. The ledger records 12/110 approved and 98 pending; batch 1 is complete. Three approvals are transferred into authoritative model inputs; nine await preservation/transfer/rebuild. No reservation attestation, independent fit rating or new audit judgment was supplied. Earlier entries retain historical counts.

## Fifteen approvals — November 25, 2026 (current)

Mary Kate explicitly approved BERTopic 13, 15 and 22 and their qualifications. See `approved_decisions_fifth_three.json`. The ledger records 15/110 approved and 95 pending. Three approvals are transferred into authoritative model inputs; twelve await preservation/transfer/rebuild. No reservation attestation, independent fit rating or new audit judgment was supplied. Earlier entries retain historical counts.

## Eighteen approvals — November 25, 2026 (current)

Mary Kate explicitly approved BERTopic 23, LDA 16 and LDA 18 and their qualifications. See `approved_decisions_sixth_three.json`. The ledger records 18/110 approved and 92 pending. Three approvals are transferred into authoritative model inputs; fifteen await preservation/transfer/rebuild. No reservation attestation, independent fit rating or new audit judgment was supplied. Earlier entries retain historical counts.

## Twenty-one approvals — November 25, 2026 (current)

Mary Kate explicitly approved LDA 38, BERTopic 30 and LDA 20 and their qualifications, including low confidence for the mixed LDA 38 label. See `approved_decisions_seventh_three.json`. The ledger records 21/110 approved and 89 pending; batches 1 and 2 are complete. Three approvals are transferred into authoritative model inputs; eighteen await preservation/transfer/rebuild. No reservation attestation, independent fit rating or new audit judgment was supplied. Earlier entries retain historical counts.

## Twenty-four approvals — November 25, 2026 (current)

Mary Kate explicitly approved BERTopic 34, LDA 13 and BERTopic 46 with their qualifications. See `approved_decisions_eighth_three.json`. The ledger records 24/110 approved and 86 pending. Three approvals are transferred into authoritative model inputs; twenty-one await preservation/transfer/rebuild. No reservation attestation, independent fit rating or new audit judgment was supplied. Earlier entries retain historical counts.

## Twenty-seven approvals — November 25, 2026 (current)

Mary Kate explicitly approved BERTopic 47, 48 and 51 with their qualifications. See `approved_decisions_ninth_three.json`. The ledger records 27/110 approved and 83 pending. Three approvals are transferred into authoritative model inputs; twenty-four await preservation/transfer/rebuild. No reservation attestation, independent fit rating or new audit judgment was supplied. Earlier entries retain historical counts.

## Thirty approvals — November 25, 2026 (current)

Mary Kate explicitly approved BERTopic 58, 59 and 60 with their qualifications. See `approved_decisions_tenth_three.json`. The ledger records 30/110 approved and 80 pending; batches 1–3 are complete. Three approvals are transferred into authoritative model inputs; twenty-seven await preservation/transfer/rebuild. No reservation attestation, independent fit rating or new audit judgment was supplied. Earlier entries retain historical counts.

## Thirty-three approvals — November 25, 2026 (current)

Mary Kate explicitly approved BERTopic 61, BERTopic 64 and LDA 1 with their qualifications. See `approved_decisions_eleventh_three.json`. The ledger records 33/110 approved and 77 pending. Three approvals are transferred into authoritative model inputs; thirty await preservation/transfer/rebuild. No reservation attestation, independent fit rating or new audit judgment was supplied. Earlier entries retain historical counts.

## Thirty-six approvals — November 25, 2026 (current)

Mary Kate explicitly approved BERTopic 67, LDA 0 and BERTopic 0 with their qualifications. See `approved_decisions_twelfth_three.json`. The ledger records 36/110 approved and 74 pending. Three approvals are transferred into authoritative model inputs; thirty-three await preservation/transfer/rebuild. No reservation attestation, independent fit rating or new audit judgment was supplied. Earlier entries retain historical counts.

## Thirty-nine approvals — November 25, 2026 (current)

Mary Kate explicitly approved BERTopic 1, LDA 2 and LDA 7 with their qualifications. See `approved_decisions_thirteenth_three.json`. The ledger records 39/110 approved and 71 pending. Three approvals are transferred into authoritative model inputs; thirty-six await preservation/transfer/rebuild. No reservation attestation, independent fit rating or new audit judgment was supplied. Earlier entries retain historical counts.

## All remaining recommendations presented — November 25, 2026

At Mary Kate's explicit request, all 71 remaining topics (23 LDA, 48 BERTopic) are presented together in [remaining_recommendations_2026-11-25.csv](remaining_recommendations_2026-11-25.csv), with a [local readable table](batch_remaining_approval.html) linking to existing full-text cards. Labels, counts, keywords, evidence summaries, qualifications and reading scope are recorded. The ledger remains at 39 approvals; none of these 71 proposals is yet approved. Selected passages from two representatives and the third title were inspected per topic; earlier deeper evidence for the first three pending topics remains in the guided recommendations. Original evidence IDs are nonreserved topic members. See `remaining_recommendations_provenance.json`.

## All 110 naming approvals recorded — November 25, 2026 (latest)

Mary Kate explicitly approved all remaining 71 labels and their stated qualifications with the chat response “Approve all 71.” The ledger now records 110/110 approved (40 LDA, 70 BERTopic), with no pending naming decisions. `approved_decisions_remaining_71.json` preserves the final decisions; the original 71-proposal snapshot remains unchanged as historical evidence. These are assisted naming approvals by Mary Kate, not independent fit ratings or approval by other team members. Three labels remain transferred into authoritative inputs; the other 107 await transfer/rebuild following the genuine shared-reservation attestation. Current comparison artifacts, drafts, classical exports, selected modern artifacts and prior review records were copied and hash-verified in `label_confirmation_archive/all_labels_approved_before_transfer/`. Bound inputs and comparison identity remain unchanged. No attestation, independent ratings or new corpus-audit judgments were inferred. The new dated audit remains 0/30 complete.

## Labels transferred and packets frozen — November 25, 2026 (latest)

All 110 approved labels (40 LDA, 70 BERTopic) are now transferred into authoritative label tables. Mary Kate supplied the explicit chat attestation “I attest that this is true” after the reservation requirement was explained. The dated record `label_review/reservation_attestation_2026-11-25.json` binds the unchanged 100-article reservation. It records Mary Kate’s statement only; no separate review or attestation by other team members is inferred. LDA’s manifest now has `labels_confirmed=true`, all 40 confirmed IDs and the actual `shared.corpus.digest(reservation)`. Earlier bound inputs, drafts and comparison outputs are preserved in `label_confirmation_archive/all_labels_approved_before_transfer/`. The prior comparison was moved intact and rebuilt through the existing notebook with its identity guard unchanged. Original assistant drafts are retained; `draft_label_reconciliation.csv` records their relationship to approved labels.

The frozen packet contains 100 reserved articles and 200 model/article items per reviewer: 100 LDA fit ratings and 76 assigned BERTopic fit ratings, plus 24 unassigned BERTopic items for qualitative review with blank fit scores. Separate working copies and personal notebooks are in `Results/comparison/n30_c25_s42/human_review/handoff/reviewer_1/` and `reviewer_2/`. Each contains only its own blank answer file. Both reviewers remain unassigned and at 0/200 completed items. No human means, agreement or kappa results were computed. The new dated corpus audit remains 0/30 and the historical PR2 claim remains unsupported. See `label_review/packet_preparation_verification.json` for packet and preservation checks.
