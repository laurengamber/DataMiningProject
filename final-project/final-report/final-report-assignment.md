Purpose
The final project report is the culmination of your proposal and three progress reports. Your goal is to produce a complete, polished research paper that is as close as reasonably possible to submission to an appropriate academic conference.

This is a cumulative submission. You must revise and strengthen the entire manuscript based on previous feedback, complete the planned analyses, and present a coherent study rather than simply combine material from earlier reports.

A strong final paper should demonstrate a meaningful research question, sound data mining methodology, credible evaluation, careful interpretation, reproducible analysis, and professional scholarly communication. Developing a new algorithm is not required. A rigorous comparison, thoughtful adaptation of existing methods, analysis of a challenging dataset, or meaningful application can constitute a valuable contribution.

Conference venue and format
Identify a conference that could reasonably be considered for the completed study. 

The selected conference establishes the intended audience, paper organization, formatting, and scholarly standard. You are not required to submit the paper to the conference.

Required manuscript content
The exact organization may be adjusted to match the selected conference and the nature of the project. However, the manuscript should contain the following elements.

1. Title, authors, abstract, and keywords
Provide:

A concise and informative title

The names of all group members

An abstract that summarizes the problem, data, methods, evaluation, principal results, and contribution

Appropriate keywords

The abstract must report actual findings. Avoid vague statements such as “results are discussed” or claims that are not supported by the completed analysis.

2. Introduction
The introduction should establish:

The specific problem being investigated

The scientific, technical, or practical importance of the problem

The limitation, gap, or unmet need addressed by the study

The research questions or analytical objectives

A concise overview of the proposed approach

The main contributions of the completed work

The final paragraph should clearly summarize the paper’s contributions. These contributions must be supported by the study rather than describing planned work.

3. Related work
Synthesize and critically compare the most relevant scholarly literature. Organize the discussion around themes, approaches, findings, or limitations rather than summarizing papers individually.

Explain:

What has already been studied

Which methods and datasets have been used

What limitations remain

How the present study differs from or builds upon prior research

All references must be credible, relevant, and verified by the authors. Do not cite a source that you have not located and examined.

4. Data
Describe the data sufficiently for readers to understand and evaluate the study. Include:

Data source, collection context, and access conditions

Unit of observation

Sample size and relevant variables

Target variable or outcome, when applicable

Inclusion and exclusion criteria

Missing values, duplicates, imbalance, outliers, and measurement concerns

Preprocessing, transformations, and feature construction

Data partitioning and measures used to prevent leakage

Representativeness, privacy, licensing, and ethical considerations

Include appropriate descriptive statistics, tables, or figures. Explain important data decisions rather than merely listing preprocessing operations.

5. Methodology
Describe the methods with enough detail for a technically qualified reader to understand and reproduce the study. Include:

A simple and meaningful baseline or reference method

The primary data mining methods

Mathematical formulations, algorithm descriptions, or model diagrams when useful

Important assumptions and design choices

Model configurations and hyperparameters

Feature selection or dimensionality reduction procedures

Comparison methods and ablation studies, when appropriate

Software, libraries, and computational resources

Explain why each method is appropriate for the research question and data. A list of algorithms without justification is not sufficient.

Any preprocessing, feature selection, sampling, or hyperparameter tuning that uses outcome information must be performed only within the training data or training folds.

6. Experimental design
Present a complete and defensible evaluation protocol. Address:

Training, validation, and testing procedures

Cross validation or repeated evaluation, when appropriate

Hyperparameter selection

Performance metrics and their relevance to the problem

Treatment of class imbalance or unequal error costs

Random seeds or repeated trials

Statistical uncertainty or significance assessment, when appropriate

Temporal, spatial, individual, or group dependence

Robustness, sensitivity, subgroup, or ablation analyses

Criteria used to compare methods and interpret success

The evaluation design must reflect the intended use of the model. For example, random splitting is not appropriate when deployment requires prediction for future periods, new individuals, new locations, or previously unseen groups.

The final test data should not be used for preprocessing decisions, model selection, hyperparameter tuning, or repeated experimentation.

7. Results
Present the completed results using carefully designed tables and figures. Raw software output or screenshots are not acceptable.

For each major analysis:

State the question being examined

Present the relevant quantitative or qualitative evidence

Compare the baseline and primary methods

Report variability or uncertainty when appropriate

Describe important patterns, errors, or failure cases

Relate the result to the research question

Report negative or unexpected findings when they are relevant. Do not selectively present only the strongest results.

Clearly distinguish validation performance from final test performance. Report enough information to support the conclusions, including sample sizes, metric definitions, and evaluation conditions.

8. Discussion
Interpret the results rather than repeating them. Discuss:

What was learned from the study

Whether and how the research questions were answered

Why the observed results may have occurred

How the findings compare with prior research

Scientific, technical, or practical implications

Important error patterns and failure cases

Alternative explanations

Conditions under which the findings may or may not generalize

Claims should remain proportional to the evidence. Predictive association should not be described as causation unless the research design supports a causal conclusion.

9. Limitations and responsible use
Provide a specific and candid discussion of limitations. Relevant issues may include:

Sample size or data quality

Sampling and representation bias

Measurement or construct validity

Limited external validity

Unequal performance across populations or conditions

Privacy and sensitive information

Potential misuse or inappropriate deployment

Dependence on generated labels, synthetic data, pretrained models, or external systems

Computational requirements or environmental costs

Reproducibility constraints

Avoid claiming that there are no ethical considerations without careful justification. Even projects using public or nonsensitive data may create concerns involving bias, misuse, misleading interpretation, or unequal errors.

10. Conclusion
Concisely summarize:

The problem addressed

The approach taken

The principal findings

The contribution of the study

The most important limitation or direction for future research

Do not introduce new evidence in the conclusion.

11. References
Use the citation and reference style required by the selected conference. Cite all datasets, software, pretrained models, external code, and scholarly sources.

Every reference must appear in the manuscript, and every in text citation must have a corresponding reference entry.

Reproducibility materials
Submit or provide access to a well organized code repository containing:

A README file explaining how to reproduce the analysis

Data access instructions or a permitted copy of the data

Data preparation and analysis code

Environment or dependency information

Instructions for training and evaluating the models

Random seeds when relevant

Saved results or logs needed to verify the reported findings

The code should run in a logical sequence and should not depend on undocumented manual steps. If data, code, or models cannot be shared because of privacy, licensing, or computational restrictions, explain the restriction and provide the most complete reproducibility documentation permitted.

Response to feedback memo
Submit a separate response memo describing how you addressed feedback on Progress Report 3.

For each substantive comment:

Summarize the comment

Explain the revision made

Identify the manuscript section in which the revision appears

If the recommendation was not adopted, provide a reasoned explanation

The memo should focus on substantive analytical and writing revisions rather than minor formatting corrections.

Contribution statement for group projects
Group projects must include a brief contribution statement identifying each member’s role in:

Data preparation

Method development and implementation

Experimental design

Analysis and interpretation

Visualization

Writing and revision

Reproducibility materials

All members are expected to understand the complete project and contribute meaningfully to both the technical work and the manuscript.

Use of artificial intelligence tools
Artificial intelligence tools may be used to support brainstorming, coding, editing, or troubleshooting unless otherwise restricted by course policy. However:

You remain responsible for every claim, citation, result, and line of submitted code.

Generated references must be independently located and verified.

Generated code must be understood, tested, and documented.

Artificial intelligence tools must not be used to fabricate data, results, citations, or completed analyses.

Any substantive use should be disclosed in a brief statement describing the tool and its role.

The submitted manuscript must represent the group’s own research decisions, analysis, interpretation, and understanding.

Submission requirements
Submit one final package per group containing:

The final conference style paper in PDF format

A separate response to feedback memo in PDF format

A link to the code repository or an uploaded archive of the reproducibility materials

A contribution statement for group projects

Any supplementary material needed to evaluate the work

The paper must:

Follow the approved conference format

Not exceed ten pages, including references, unless the instructor has approved a different venue requirement

Contain complete results rather than plans for future experiments

Include legible, numbered, and captioned tables and figures

Cite every table and figure in the text

Use consistent terminology, notation, metrics, and numerical precision

Be carefully proofread and free of unresolved comments or placeholders

A paper may identify future research, but analyses essential to answering the central research questions must be completed.

Evaluation criteria
The final submission will be evaluated according to the following criteria:

Criterion	Expectations	Points
Problem definition and motivation	Clearly define the research question, explain its importance, and identify the project’s objectives.	10
Related work	Discuss relevant literature and explain how it informs the proposed approach and the project’s contribution.	10
Data understanding and preparation	Describe the dataset, relevant variables, data quality issues, preprocessing, and exploratory analysis. Justify key preparation decisions.	20
Methodology	Clearly explain and justify the selected methods, their implementation, and their suitability for the research question.	25
Experimental design and evaluation	Use appropriate baselines, validation procedures, tuning strategies, and evaluation metrics. Address data leakage and ensure fair comparisons.	25
Results, interpretation, and discussion	Present results clearly, connect findings to the research question, and discuss limitations, ethical considerations, and potential improvements.	35
Organization and presentation	Provide a coherent, clearly written report with informative figures and tables, consistent formatting, and appropriate citations.	15
Reproducibility and contributions	Document the procedures and settings needed to reproduce the analysis. For group projects, clearly describe each member’s contributions.	10
Total		150
Final standard
The paper will be assessed as a research manuscript, not merely as a record of completed programming work. Model complexity alone does not demonstrate a strong project. The most successful papers will connect a meaningful question to credible data, appropriate methods, rigorous evaluation, restrained interpretation, and reproducible evidence.

The final manuscript does not need to guarantee acceptance at the selected conference. It should, however, be sufficiently complete and polished that a knowledgeable reader could evaluate it as a serious conference submission.