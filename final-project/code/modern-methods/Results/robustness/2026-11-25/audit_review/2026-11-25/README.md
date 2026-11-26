# New human corpus audit — prepared November 25, 2026

Mary Kate explicitly reported that original judgments are unavailable and requested a new dated human audit in Codex chat on November 25, 2026. Completed November 26, 2026: all 30/30 explicit assisted human judgments are recorded. This does not substantiate or replace the historical PR2 assertion that all 30 articles passed.

The same 30 article IDs and original order are retained. `original_corpus_review.csv` is a byte-identical local snapshot; the original `final-project/data/corpus_review.csv` remains unchanged. Full-text cards and the snapshot are local and ignored by Git. Source hashes and article IDs are recorded in `provenance.json`. No article overlaps the reserved 100-article independent fit-rating sample.

Work through three articles at a time. Read the full stored text in each card, then record your actual judgments in `human_judgments.csv` or supply them in chat for transcription. Keep reviewer name and actual review date blank until a person submits judgments. Preparation date is not review date. Use `review_mode` to identify direct human review or assisted review accurately.

For this new audit, use these explicit field definitions (not a recovered historical rubric):

- `relevance`: `central`, `peripheral`, `not_relevant`, or `uncertain`. Central means autonomous vehicles, driving automation, or directly related technology/policy/business is a main subject; peripheral means a substantive mention within broader coverage; not_relevant means no substantive coverage. A keyword alone is insufficient.
- `boilerplate`: `present`, `absent`, or `uncertain` for extraneous navigation, promotion, repeated page furniture or embedded code. Explain the example and whether it interferes with reading; a normal byline is not by itself boilerplate.
- `malformed`: `present`, `absent`, or `uncertain` for truncation, garbling, encoding damage or extraction errors. Note the affected passage and severity.
- `notes`: give a brief rationale, particularly for peripheral relevance, defects or uncertainty. Do not infer any judgment from a blank cell.

These are corpus-quality judgments, separate from topic naming and independent 1–5 model-fit ratings. Do not edit model exports or silently remove corpus articles based on this audit. Summarize findings only after actual judgments exist; retain uncertainties and denominators. If the audit motivates corpus changes, document that as a separate analysis decision.

## Article groups

- [Batch 1: articles 1–3](batch_01.html)
- [Batch 2: articles 4–6](batch_02.html)
- [Batch 3: articles 7–9](batch_03.html)
- [Batch 4: articles 10–12](batch_04.html)
- [Batch 5: articles 13–15](batch_05.html)
- [Batch 6: articles 16–18](batch_06.html)
- [Batch 7: articles 19–21](batch_07.html)
- [Batch 8: articles 22–24](batch_08.html)
- [Batch 9: articles 25–27](batch_09.html)
- [Batch 10: articles 28–30](batch_10.html)

## Completed audit — November 26, 2026

Mary Kate explicitly accepted items 1–3 and subsequently answered “Yes” to acceptance of suggestions 4–30 and their rationales. All **30/30** rows now contain her name, actual review date and assisted-review description. The assistant read the full stored text of all 30 articles. Direct human reading scope remains unconfirmed; this is not independent human full-text review. The original 30 IDs and order are unchanged and none overlaps the reserved 100-article model-fit sample.

| Dimension | Category | Count / 30 | Proportion |
| --- | --- | ---: | ---: |
| relevance | `central` | 24/30 | 80.0% |
| relevance | `peripheral` | 5/30 | 16.7% |
| relevance | `not_relevant` | 1/30 | 3.3% |
| relevance | `uncertain` | 0/30 | 0.0% |
| boilerplate | `present` | 7/30 | 23.3% |
| boilerplate | `absent` | 23/30 | 76.7% |
| boilerplate | `uncertain` | 0/30 | 0.0% |
| malformed | `present` | 4/30 | 13.3% |
| malformed | `absent` | 24/30 | 80.0% |
| malformed | `uncertain` | 2/30 | 6.7% |

Central plus peripheral relevance totals **29/30 (96.7%)**. Boilerplate and malformed categories overlap: **9/30 (30.0%)** have at least one `present` defect, rather than 11 distinct articles. The two malformed uncertainties are retained and are not counted as either present or absent. Percentages are descriptive for these 30 articles only.

Examples and severity:

- **Relevance:** article 446324 (item 16, Audi investment) is `not_relevant` under the substantive-coverage rule: the body only names autonomous driving in a list, then develops electrification/digital services. This borderline decision is preserved. Peripheral articles are 321565, 829443, 2025463, 118371 and 871970, spanning roundups, a dashboard critique, shared mobility and oil/EV forecasting.
- **Boilerplate:** IDs 221300 and 1654474 retain wire-distribution/update instructions; 684367 has a comment invitation; 363606 contains a gallery shortcode; 15792 includes repeated refresh instructions and a related-story prompt; 1767208 retains a site footer; 2316736 includes newsletter promotion. Most add small, readable interruptions; the duplicated report in 15792 is more substantial.
- **Malformed:** 363606 retains unrendered gallery markup (low interference); 1106821 has repeated joined text boundaries (minor but repeated); 15792 duplicates a substantial opening block (inflated repetition and word counts); 118371 appears to omit the promised conclusion (material loss, unknown extent).
- **Uncertain malformed:** 221300 contains “NHTSA said Thursday said it confirmed”; 1637484 contains “start-ups like Boxbot Ike.” Both are local wording defects of uncertain editorial versus extraction origin.

Limitations: one assisted reviewer accepted assistant assessments; no independent second audit or agreement estimate exists. The same historical sample was reused, and representativeness for all 7,332 articles/25 publications was not established here. No publisher-original completeness check or factual validation was performed. “Absent” means no obvious issue identified in stored text. Relevant quotations, bylines, captions, editorial update explanations and republication credits were not automatically treated as boilerplate; missing linked media alone was not automatically treated as malformed prose.

**This new audit does not substantiate PR2's historical claim or establish that the earlier review occurred.** The original blank judgment fields remain unchanged. The separate two-reviewer model-fit evaluation remains pending. No models, labels, assignments, reservation, frozen packets, reviewer answers, or PR3 manuscript/tables/figures were changed.

Records: [completed ledger](human_judgments.csv), [items 1–3 acceptance](accepted_decisions_2026-11-26_items_01-03.json), [items 4–30 acceptance](accepted_decisions_2026-11-26_items_04-30.json), [machine-readable summary](completed_audit_summary_2026-11-26.json), and [completion verification](completion_verification_2026-11-26.json). The original assistant proposal file and preparation-time provenance remain unchanged historical records; their earlier pending/blank wording is superseded by the acceptance records and current ledger.

## Possible data follow-up (not executed)

Consider a separate, versioned cleaning study: verify the suspected missing conclusion and two ambiguous wording defects against originals; remove demonstrably extraneous footers/prompts/shortcodes; repair repeated boundary joins and within-article duplicated blocks; and clarify the substantive-relevance threshold before reconsidering borderline item 16. Any proposed removals or corrections need an explicit change log and a separately versioned corpus, with downstream model sensitivity assessed separately. Acceptance of this audit authorizes recording findings, not these data/model changes. The existing corpus and fitted results remain unchanged.

## Earlier review progress — November 26, 2026 (historical snapshot; superseded above)

Mary Kate explicitly accepted the suggestions and rationales for items 1–3 in chat. The ledger records the actual review date, November 26, 2026, and assisted review following the assistant's full-stored-text inspection. Mary Kate's direct reading scope was not confirmed; no full-article human reading is claimed. Item 2 retains `uncertain` for malformed text. The [acceptance record](accepted_decisions_2026-11-26_items_01-03.json) preserves the explicit message and accepted rows.

At Mary Kate's request, the assistant read all remaining 27 stored articles in full and prepared [suggestions for items 4–30](assistant_suggestions_2026-11-26.json). These are proposals only: the remaining human fields stay blank until explicit decisions arrive. All 30 HTML text cards match the original CSV text. Publisher-original completeness was not verified.

The preparation-time `provenance.json`, original CSV, snapshot and full-text cards remain preserved. Their preparation-time blank-status statements are historical; the current ledger and `audit_status.json` track progress. This is a new audit and cannot substantiate the historical PR2 assertion. Final category counts, proportions and interpretations await the remaining human decisions. No corpus or fitted-model changes are proposed or implemented at this stage.
