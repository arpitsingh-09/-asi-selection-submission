# Minimum legitimate already-asked source

The current saved source audit contains zero explicit research questions.
It cannot serve as a corpus. No external retrieval is needed merely to define
this missing input, and no source records have been invented.

The smallest technically usable input is one real, nonempty, explicit research
question from an identifiable prior publication or a genuine archived question
collection. One question only supports “matched within this one-question corpus”;
it cannot establish an unrestricted rate of questions already asked in science.
A defensible study needs researcher-approved domain, date boundary, corpus
coverage, selection rule, and treatment of unavailable sources. There is no
assignment-established numerical minimum corpus size in the current E6 record.

Provide source records with `paper_id` and `research_question` (string) or
`research_questions` (list of strings) for the existing importer. For each
question retain the original question wording, stable source identifier/URL,
publication/archive date, exact page/section or record locator, and a locally
saved source excerpt or record with its hash. Record who transcribed it and
when if it was manually transcribed. Verify that the wording actually occurs
in the source and satisfies the approved temporal/domain scope. A publisher
URL alone with no verified question-bearing content is insufficient.

Titles, abstracts, hypotheses, automatically inferred questions, and the study's
unvalidated target extractions are not substitute source questions. Target
extractions support reconstruction and do not independently establish prior
question occurrence. No automatic conversion is authorized.

The existing importer preserves source-file and source-record hashes and
byte-identical question deduplication. Its nonempty output remains a provisional
source audit until provenance is checked and the corpus and matcher are
approved and frozen. Keep source metadata in each input record and preserve
the source file alongside the corpus. Freeze a versioned manifest, corpus hash,
fixed binary matcher and denominator/missing-reference policy before scoring.
Report matched count, eligible generated-question count, coverage limitations,
and unavailable-corpus status; questionless arms are unavailable, not zero.
