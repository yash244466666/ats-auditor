# SkillSpan-derived phrase data — CC BY 4.0

`skillspan_phrases.json` contains a filtered phrase lexicon derived solely from the training split of **SkillSpan: Hard and Soft Skill Extraction from English Job Postings**, Mike Zhang, Kristian Jensen, Sif Sonniks and Barbara Plank, NAACL 2022.

- Paper: https://aclanthology.org/2022.naacl-main.366/
- Original data: https://github.com/kris927b/SkillSpan
- Snapshot: `2ccf3de5b5af7a5409b8dd814fb1315dd6e0ae1b`
- Data license declared by the authors' dataset card: https://huggingface.co/datasets/jjzha/skillspan/blob/main/README.md
- License: **Creative Commons Attribution 4.0 International**, https://creativecommons.org/licenses/by/4.0/legalcode

Changes by ATS Auditor contributors: case normalization, punctuation tokenization, exclusion of placeholders/control characters, length filtering, distinct-training-document frequency filtering and a training-only exact-span precision threshold. Only the resulting phrases and provenance are redistributed; original job sentences and applicant resumes are not included.

The authors do not endorse ATS Auditor. Preserve attribution, this notice and the license link when redistributing this data or modified versions, and identify modifications. This data notice is an exception to the root MIT code license; our independently written Python code remains MIT. No development or test labels were used to construct the lexicon.
