# HDR independent source review

No model judgments or human answers are prefilled. Review independently; coordinator mapping contains arm identities and should be withheld until completion.
125 records reduce to 107 literally identical-set groups. Reuse only exact full ordered-set identity; no paraphrase equivalence is inferred.

## First resolve the reference-feature definition

HDR = (discovered true features / all true features) × mean relationship correctness over discovered features. See [frozen source paper, section 3 and Appendix A](https://arxiv.org/html/2504.11524v1#S3). Fourteen-reference recovery recall is a separate outcome.
The source has 14 rules over three predicate fields; metadata lists four feature categories and four templates. Those counts describe different objects. No count is silently selected as the denominator. Template placeholders alone do not prove an independent outcome relationship for every placeholder.

Required one-time decision: define the true feature unit, reference_feature_ids and feature_mapping (exact rule indices and source_texts), justify omissions/overlaps, and explain how multiple rules and multiple generated claims determine a feature relationship score. Do not invent a new frozen method. If source evidence is insufficient, record unresolved and stop scoring.

Definition author / UTC time: ______
Source-supported definition and mapping: ______
Multiple-rule / multiple-claim relationship interpretation: ______
Rationale and source locations: ______

Literal rule predicate fields: partisan_language, political_event_reaction, template
Metadata feature category keys: political_endorsement, policy_stance, partisan_language, political_event_reaction
Metadata num_templates: 4
Metadata num_impactful_feature: 1 (not assumed to be the HDR denominator).

## Exact ground-truth evidence (zero-based rule indices)

0: If the "template" of the given tweet is "I have always shown strong support for [political_endorsement] and my recent posts clearly reflect my stance on [policy_stance]. The language I use often aligns with [partisan_language], especially when reacting to [political_event_reaction].", then it is highly likely to be classified as "likely republican voter" and a bit likely to be classified as "likely third-party/abstain voter".

1: If the "template" of the given tweet is "After the recent [political_event_reaction], I have become more vocal about my support for [political_endorsement]. My opinions on [policy_stance] are quite evident, and I tend to use [partisan_language] to express them.", then it is highly likely to be classified as "likely republican voter" and a bit likely to be classified as "likely democratic voter".

2: If the "template" of the given tweet is "My belief in [political_endorsement] has been strengthened by my reactions to [political_event_reaction]. This is why I consistently express my views on [policy_stance] using [partisan_language].", then it is likely to be classified as "likely republican voter" and unlikely to be classified as "likely democratic voter".

3: If the "template" of the given tweet is "In light of [political_event_reaction], my support for [political_endorsement] has grown. My stance on [policy_stance] is firm, and I often utilize [partisan_language] to articulate my perspective.", then it is likely to be classified as "likely republican voter" and unlikely to be classified as "likely democratic voter".

4: If the "partisan_language" of the given tweet is "promotes universal healthcare", then it is likely to be classified as "likely democratic voter" and unlikely to be classified as "likely republican voter".

5: If the "partisan_language" of the given tweet is "defends Second Amendment rights", then it is a bit unlikely to be classified as "likely republican voter" and highly unlikely to be classified as "likely third-party/abstain voter".

6: If the "partisan_language" of the given tweet is "advocates for libertarian policies", then it is likely to be classified as "likely democratic voter" and unlikely to be classified as "likely third-party/abstain voter".

7: If the "partisan_language" of the given tweet is "criticizes two-party system", then it is likely to be classified as "likely republican voter" and unlikely to be classified as "likely third-party/abstain voter".

8: If the "partisan_language" of the given tweet is "supports social justice initiatives", then it is likely to be classified as "likely republican voter" and unlikely to be classified as "likely third-party/abstain voter".

9: If the "political_event_reaction" of the given tweet is "criticizes Supreme Court decision favoring conservatives", then it is likely to be classified as "likely republican voter" and unlikely to be classified as "likely democratic voter".

10: If the "political_event_reaction" of the given tweet is "praises Biden's climate change policy", then it is likely to be classified as "likely democratic voter" and unlikely to be classified as "likely third-party/abstain voter".

11: If the "political_event_reaction" of the given tweet is "condemns government shutdown orchestrated by Republicans", then it is likely to be classified as "likely republican voter" and unlikely to be classified as "likely third-party/abstain voter".

12: If the "political_event_reaction" of the given tweet is "expresses frustration over lack of third-party debate presence", then it is likely to be classified as "likely democratic voter" and unlikely to be classified as "likely third-party/abstain voter".

13: If the "political_event_reaction" of the given tweet is "celebrates passage of bipartisan infrastructure bill", then it is a bit unlikely to be classified as "likely third-party/abstain voter" and highly unlikely to be classified as "likely republican voter".

## Per-case instructions

After the denominator is resolved, for each reference feature record discovery true/false, supporting generated hypothesis index and ground-truth rule index, brief rationale, and relationship correctness in [0,1] if discovered. Explicit negative judgments require evidence; unmatched literal text is unknown, not false. Do not fill relationship scores for undiscovered features. No pairwise 6×14 judgment matrix is required by this handoff; review the full six-hypothesis set once.
Use the existing payload schema documented in E6/HDR_SCORING.md. Coordinator expands exact duplicate groups to their original records, preserving each record arm/input ID and hypotheses hash. Judge identity, UTC time and evidence must accompany every actual judgment. No automatic approval follows from completing a form.

## HDR-8656dd07064b9ac8

H0: Individuals expressing frustration with the lack of third-party debate presence are more likely to vote Republican.

H1: Support for universal healthcare, coupled with criticism of Republicans, correlates with a Democratic voting preference.

H2: Endorsement of climate change initiatives, alongside criticism of the two-party system, predicts Republican voting.

H3: Consistent advocacy for third-party alternatives and universal healthcare suggests a likely Democratic voter.

H4: Reactions celebrating bipartisan infrastructure bills are associated with a higher likelihood of Republican voting.

H5: Promoting non-voting as protest, alongside libertarian views, indicates a likely Republican voter.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-18ef3610d559a8a5

H0: Tweets explicitly endorsing universal healthcare are more likely to be classified as supporting Democratic candidates.

H1: Tweets explicitly defending Second Amendment rights are more likely to be classified as supporting Republican candidates.

H2: Negative reactions to Republican-led government shutdowns increase the likelihood of a Democratic or third-party vote prediction.

H3: Positive reactions to Supreme Court decisions favoring conservatives increase the likelihood of a Republican vote prediction.

H4: Expressing frustration over the lack of third-party debate presence is more likely to correlate with a Democratic voting preference.

H5: Expressing frustration over the lack of third-party debate presence is also likely to correlate with a Republican voting preference.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-820b55a290b3de8d

H0: Individuals expressing support for third-party alternatives are more likely to also advocate for universal healthcare.

H1: Condemnation of Republican-led government shutdowns correlates with increased vocal support for conservative values.

H2: Frustration regarding the lack of third-party debate presence is associated with endorsements of either Democratic or Republican candidates.

H3: Support for immigration reform frequently co-occurs with expressions of opinions on universal healthcare.

H4: Criticism of mainstream political parties is often accompanied by advocacy for universal healthcare.

H5: Reactions to bipartisan infrastructure bills influence the expression of views on social justice initiatives.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-c3f7bbb9483b1b38

H0: Tweets containing explicitly positive language towards a candidate will correlate with a higher probability of voting for that candidate.

H1: Increased use of partisan hashtags will predict a higher likelihood of voting for a major party candidate.

H2: Tweets expressing negative sentiment towards a specific policy will correlate with a preference for the opposing party.

H3: References to past voting behavior will predict future voting preference with moderate accuracy.

H4: Tweets discussing major political events will be more likely to predict third-party voting than abstention.

H5: Tweets demonstrating alignment with party-affiliated slogans will predict voting for that party's candidate.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-9a4a32e90bcbbaef

H0: Expressions of frustration regarding third-party debate presence correlate with a likely Republican voter label.

H1: Support for promoting non-voting as protest aligns with a likely Republican voter classification.

H2: Criticism of tax cuts for corporations is associated with a likely Democratic voter label.

H3: Praise for Biden's climate change policy is observed more frequently in likely Democratic voters.

H4: Condemnation of government shutdowns orchestrated by Republicans correlates with a likely Republican voter.

H5: Advocating for universal healthcare is more common among likely Democratic voters.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-498445353ad61f71

H0: Individuals expressing criticism of Supreme Court decisions favoring conservatives are more likely to support third-party candidates.

H1: Reactions condemning government shutdowns orchestrated by Republicans correlate with a higher likelihood of supporting Democratic candidates.

H2: Praise for bipartisan infrastructure bills is associated with a greater inclination towards supporting immigration reform.

H3: Consistent criticism of mainstream political parties is a predictor of either Democratic candidate support or non-voting.

H4: Advocating for gun rights alongside criticism of the two-party system is more common among individuals likely to vote Republican.

H5: Expressions of frustration regarding the lack of third-party debate presence are linked to promoting non-voting as a form of protest.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-2d496dc4f124e455

H0: Tweets explicitly criticizing political institutions are more likely to be associated with a third-party or non-voting preference.

H1: The intensity of criticism towards political institutions is positively correlated with the likelihood of a non-Democratic or Republican voting preference.

H2: Tweets endorsing both gun rights and universal healthcare are more likely to be associated with a Republican or third-party voting preference.

H3: The combination of endorsing climate change initiatives and criticizing mainstream political parties predicts a Democratic or third-party voting preference.

H4: Expressing frustration over the lack of third-party debate presence is more likely to predict a third-party voting preference.

H5: Individuals expressing frustration about the lack of third-party debate presence are more likely to also express criticism of mainstream political parties.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-a1f2dca317a9fa0f

H0: Criticizing conservative-leaning Supreme Court decisions predicts increased support for Democratic candidates.

H1: Expressing disapproval of Supreme Court decisions correlates with a higher likelihood of advocating for third-party options.

H2: Blaming Republicans for government shutdowns increases expressed support for Democratic-aligned policy positions.

H3: Condemning government shutdowns orchestrated by Republicans correlates with stronger advocacy for gun rights.

H4: Advocating for climate change initiatives is associated with increased use of anti-two-party system language.

H5: Expressing opinions on tax cuts is linked to adopting language critical of mainstream political parties.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-134fea3027cb6dc5

H0: Positive perception of a candidate's climate change policy correlates with increased endorsement, even among those initially favoring gun rights.

H1: Consistent criticism of a candidate's gun rights stance predicts a shift towards third-party alternatives or non-voting.

H2: Frequent advocacy for non-voting is associated with increased expression of support for third-party platforms and ideologies.

H3: Individuals promoting non-voting often express dissatisfaction with both Democratic and Republican platforms.

H4: Blaming Republicans for government shutdowns strengthens expressions of support for Democratic policies like universal healthcare.

H5: Attributing government shutdowns to a specific party increases support for criticizing the two-party system and exploring alternative options.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-cf22e03a543e101e

H0: Individuals expressing criticism of Supreme Court decisions favoring conservatives are more likely to support the Democratic candidate.

H1: Reactions to government shutdowns, particularly condemnation of Republican orchestration, correlate with support for third-party alternatives.

H2: Celebration of bipartisan infrastructure bills is associated with increased support for immigration reform.

H3: Consistent criticism of mainstream political parties often precedes advocacy for libertarian policies and universal healthcare.

H4: Praise for Biden's climate change policy strengthens support for endorsing the Democratic candidate.

H5: Frustration regarding the lack of third-party debate presence is linked to increased support for non-voting as a form of protest.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-7fbee57b7b58704f

H0: Expressions of frustration regarding third-party debate presence correlate with a likely republican voter label.

H1: Support for immigration reform, coupled with libertarian language, indicates a likely democratic voter.

H2: Condemnation of government shutdowns orchestrated by Republicans often aligns with a likely republican voter.

H3: Praise for Biden's climate change policy is associated with a likely republican voter classification.

H4: Consistent criticism of the two-party system frequently indicates a likely republican voter.

H5: Advocating for universal healthcare, alongside libertarian language, suggests a likely democratic voter.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-ba9e4054f7e7f059

H0: Tweets explicitly criticizing the two-party system are more likely to be associated with a third-party voter prediction.

H1: The frequency of two-party system criticism is positively correlated with the likelihood of a non-Democratic/Republican voting preference.

H2: Endorsement of universal healthcare is more strongly associated with a Democratic voter prediction than a Republican voter prediction.

H3: Consistent endorsement of gun rights, regardless of other expressed views, increases the likelihood of a Republican voter prediction.

H4: Condemnation of Republican-led government shutdowns is associated with an increased likelihood of a Democratic voter prediction.

H5: Celebration of bipartisan infrastructure bills is associated with a decreased likelihood of a third-party voter prediction.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-cba0ff9367311ed7

H0: Endorsement of libertarian policies correlates with increased support for third-party candidates, even among those leaning towards major parties.

H1: Consistent advocacy for universal healthcare is a stronger predictor of Democratic candidate support than endorsement of gun rights.

H2: Condemnation of Republican-led government shutdowns increases support for Democratic candidates, particularly among those initially undecided.

H3: Celebration of bipartisan infrastructure bills correlates with a temporary softening of criticism towards the two-party system.

H4: Increased frustration with the two-party system is positively correlated with expressions advocating for non-voting as a protest strategy.

H5: Individuals expressing frustration with the two-party system are more likely to support third-party candidates than abstain from voting.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-b951216c202ab0d2

H0: Condemnation of Republican-led government shutdowns correlates with increased support for Democratic candidates.

H1: Celebration of bipartisan infrastructure bills predicts a temporary softening of partisan language.

H2: Increased criticism of the two-party system is associated with a higher likelihood of endorsing non-voting as protest.

H3: Frustration with the two-party system often precedes expressions of support for third-party alternatives.

H4: Consistent advocacy for universal healthcare increases the probability of supporting a Democratic candidate.

H5: Endorsement of both gun rights and climate change initiatives correlates with support for a libertarian or third-party candidate.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-8390aea25e9af914

H0: Individuals expressing frustration with the two-party system are more likely to support third-party candidates.

H1: Criticism of Supreme Court decisions favoring conservatives correlates with increased support for Democratic candidates.

H2: Condemnation of Republican-led government shutdowns is associated with increased support for third-party alternatives.

H3: Celebration of bipartisan infrastructure bills is a predictor of increased support for Democratic candidates.

H4: Advocating for libertarian policies, alongside criticism of conservative judicial decisions, indicates a likely Republican voter.

H5: Support for universal healthcare, coupled with criticism of tax cuts for corporations, is associated with Democratic candidate endorsement.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-04b18a7502cb349c

H0: Expressions of frustration regarding third-party debate presence correlate with a likely Republican voter label.

H1: Celebration of bipartisan infrastructure bills is associated with a likely Republican voter classification.

H2: Criticism of Supreme Court decisions favoring conservatives often indicates a likely Republican voter.

H3: Advocating for universal healthcare, coupled with gun rights endorsements, suggests a likely Republican voter.

H4: Support for promoting non-voting as protest aligns with a likely Democratic voter classification.

H5: Expressing frustration over the lack of third-party debate presence may indicate a likely Democratic voter.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-aff30b972af3af23

H0: Individuals expressing frustration with the lack of third-party debate presence are more likely to vote Republican.

H1: Support for universal healthcare correlates with a higher likelihood of endorsing the Democratic candidate.

H2: Condemnation of Republican-orchestrated government shutdowns predicts a preference for conservative values.

H3: Praise for Biden's climate change policy is associated with increased support for non-voting as protest.

H4: Advocating for libertarian policies is more likely to be associated with Republican voting preference.

H5: Strong support for Second Amendment rights often aligns with opposition to corporate tax cuts.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-858d234eb61ea5e1

H0: Tweets explicitly endorsing non-voting are more likely to be classified as belonging to Republican voters.

H1: The frequency of non-voting endorsement language is positively correlated with the likelihood of a Republican voter classification.

H2: Condemnation of Republican-led government shutdowns is more strongly associated with Democratic voter classification.

H3: Expressions of support for bipartisan infrastructure bills are more likely to be associated with Republican voter classification.

H4: Tweets expressing support for social justice initiatives alongside defense of Second Amendment rights are more likely to be classified as Republican voters.

H5: The predictive accuracy of voting preference classification improves when both social justice and Second Amendment stances are considered together.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-5d0b17b37aa96032

H0: Republican voters endorsing non-voting are more likely to express support for gun rights than Democratic voters.

H1: Endorsing non-voting alongside support for universal healthcare predicts a higher likelihood of voting Democratic.

H2: Frustration with the lack of third-party debate presence is more strongly correlated with Republican voting than Democratic voting.

H3: Individuals expressing frustration with the lack of third-party debate presence are less likely to vote for either major party candidate.

H4: Criticism of corporate tax cuts is a stronger predictor of Democratic candidate support than third-party candidate support.

H5: Explicit criticism of corporate tax cuts, coupled with frustration with the two-party system, increases the likelihood of third-party voting.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-6d48dd3b2dc5a278

H0: Explicit criticism of corporate tax cuts correlates with increased support for the Democratic candidate.

H1: Frequent criticism of corporate tax cuts predicts a higher likelihood of expressing support for third-party alternatives.

H2: Condemnation of Republican-led government shutdowns strengthens expressions of social justice initiatives.

H3: Reactions to government shutdowns correlate with a shift towards championing conservative values among some individuals.

H4: Endorsement of non-voting, coupled with support for universal healthcare, predicts a Democratic candidate preference.

H5: Non-voting advocacy combined with gun rights advocacy correlates with a Republican candidate preference.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-4c808490a64e431b

H0: Individuals expressing frustration with the lack of third-party debate presence are more likely to identify as Republican voters.

H1: Support for non-voting as protest correlates with a preference for conservative values, as evidenced in user language.

H2: Explicit endorsement of Democratic candidates is associated with expressed opposition to corporate tax cuts.

H3: Condemnation of Republican-led government shutdowns is a predictor of support for universal healthcare initiatives.

H4: Praise for Biden's climate change policy is a potential indicator of Republican voter affiliation.

H5: Advocating for third-party alternatives is often accompanied by expressions of support for social justice initiatives.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-cb056d639ccb777e

H0: Tweets criticizing Republican-led government shutdowns correlate with a likely Republican voter label.

H1: Support for third-party alternatives, coupled with libertarian language, predicts a likely Republican voter.

H2: Expressing frustration over the lack of third-party debate presence often aligns with a likely Republican voter.

H3: Endorsing climate change initiatives, alongside support for social justice, indicates a likely Republican voter.

H4: Criticism of Supreme Court decisions favoring conservatives is associated with a likely Republican voter.

H5: Advocating for universal healthcare, combined with criticism of mainstream parties, predicts a likely Republican voter.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-e34e1441343f7e0e

H0: Individuals expressing frustration with the lack of third-party debate presence are more likely to vote for a third party.

H1: Support for the Democratic candidate correlates with positive reactions to bipartisan infrastructure bills.

H2: Criticism of Supreme Court decisions favoring conservatives is associated with Republican voting preference.

H3: Advocating for universal healthcare alongside gun rights is a predictor of Democratic voter affiliation.

H4: Promotion of non-voting as protest aligns with support for climate change initiatives, indicating Democratic leanings.

H5: Endorsing climate change initiatives alongside libertarian policies suggests a Republican voting tendency.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-fe11a0b0d361cc99

H0: Tweets expressing frustration about the lack of third-party debate presence are more likely to be classified as likely Republican voter.

H1: Tweets expressing frustration about the lack of third-party debate presence, coupled with advocacy for libertarian policies, are more likely to be classified as likely Republican voter.

H2: Explicit endorsement of universal healthcare is positively correlated with a likely Democratic voter classification.

H3: Explicit endorsement of Second Amendment rights is positively correlated with a likely Republican voter classification.

H4: Celebration of the bipartisan infrastructure bill is more likely to be associated with a likely Democratic voter classification.

H5: Criticism of Supreme Court decisions favoring conservatives is more likely to be associated with a likely Republican voter classification.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-f02b9ec2e8a6a225

H0: Individuals endorsing Democratic candidates are more likely to support universal healthcare, even when also advocating for gun rights.

H1: Republican candidate endorsements correlate with stances defending Second Amendment rights, sometimes alongside support for universal healthcare.

H2: Frustration over third-party debate absence often precedes endorsements of either Democratic or Republican candidates.

H3: Individuals expressing frustration with the lack of third-party debate presence are more likely to advocate for libertarian policies.

H4: Criticism of conservative-leaning Supreme Court decisions frequently precedes endorsements of Democratic candidates.

H5: Criticism of Supreme Court decisions favoring conservatives can lead to endorsements of Republican candidates advocating for alternative policies.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-ef48e7aab90505aa

H0: Support for climate initiatives among self-identified conservatives correlates with increased Republican candidate endorsement.

H1: Libertarians expressing climate initiative support are more likely to advocate for third-party alternatives.

H2: Frequent criticism of the two-party system predicts a higher probability of endorsing non-voting as protest.

H3: Use of anti-two-party language correlates with increased expression of support for third-party candidates.

H4: Individuals advocating for non-voting are less likely to endorse either the Democratic or Republican candidate.

H5: Expressing support for non-voting correlates with increased advocacy for libertarian policies.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-eae9c6324ac52d2b

H0: Individuals expressing frustration with the lack of third-party debate presence are more likely to advocate for libertarian policies.

H1: Support for the Democratic candidate correlates with positive reactions to bipartisan infrastructure bills.

H2: Criticism of Supreme Court decisions favoring conservatives is associated with increased support for criticizing mainstream political parties.

H3: Celebration of climate change initiatives is often accompanied by expressions of support for promoting non-voting as a form of protest.

H4: Advocating for universal healthcare frequently co-occurs with expressions of frustration regarding the two-party system.

H5: Support for championing conservative values is often linked to stances on supporting immigration reform.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-d600bc8425bd9774

H0: Criticism of Supreme Court decisions favoring conservatives correlates with a likely Republican voter label.

H1: Condemning government shutdowns orchestrated by Republicans is associated with a likely Republican voter.

H2: Expressing support for climate change initiatives alongside criticism of the two-party system predicts a likely Republican voter.

H3: Advocating for third-party options and championing gun rights often indicates a likely Republican voter.

H4: Praise for Biden's climate change policy is associated with a likely Democratic voter.

H5: Promoting non-voting as protest aligns with a likely Democratic voter label.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-8fe627072ac32a7d

H0: Tweets expressing frustration with third-party debate presence are more likely to indicate a Republican voting preference.

H1: Explicit criticism of Republican-led government shutdowns correlates with a higher likelihood of Democratic candidate support.

H2: Support for universal healthcare, coupled with criticism of corporate tax cuts, predicts a Democratic voting tendency.

H3: Celebration of bipartisan infrastructure bills is associated with a higher probability of Republican voter identification.

H4: Advocating for non-voting as protest aligns with a higher likelihood of Republican or third-party voting preference.

H5: Defense of Second Amendment rights, alongside opposition to corporate tax cuts, suggests a Republican voting inclination.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-ebf4cc18ddefa13c

H0: Tweets explicitly condemning Republican-led government shutdowns are more likely to be associated with a Democratic voting preference.

H1: The frequency of condemnation of Republican-led government shutdowns is a stronger predictor of voting preference than the specific policy positions expressed.

H2: Users expressing frustration with third-party debate presence and opposing corporate tax cuts are more likely to be classified as likely Democratic voters.

H3: The correlation between frustration with third-party debate presence and opposition to corporate tax cuts is stronger for users predicted to vote for a third party.

H4: Endorsement of the Democratic candidate alongside support for universal healthcare is more likely to indicate a Republican voter expressing dissatisfaction with the Republican party.

H5: The combination of Democratic endorsement and universal healthcare support is associated with a lower confidence score in the predicted voting preference.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-33a903069372ec9c

H0: Condemnation of Republican shutdowns correlates with increased support for criticizing mainstream parties, particularly among those opposing corporate tax cuts.

H1: Explicitly criticizing Republican shutdowns is more likely to shift users towards expressing support for social justice initiatives.

H2: Celebration of bipartisan infrastructure bills is associated with increased expression of critiques against the two-party system, regardless of initial ideology.

H3: Reactions to infrastructure bills correlate with increased advocacy for universal healthcare, especially among those initially critical of mainstream parties.

H4: Frustration over third-party debate absence is linked to increased promotion of non-voting as a form of protest, particularly among those with libertarian views.

H5: Expressing frustration about third-party debate presence correlates with advocating for third-party alternatives, often accompanied by criticism of mainstream parties.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-1a3d37a3c44afe88

H0: Increased frustration over third-party debate absence correlates with a higher likelihood of promoting non-voting among users expressing libertarian views.

H1: Users expressing frustration about third-party debate presence are more likely to advocate for third-party alternatives than those who do not.

H2: Celebration of bipartisan infrastructure bills is associated with increased expression of critiques against the two-party system among users who also support universal healthcare.

H3: Reactions to bipartisan infrastructure bills correlate with a shift towards advocating for universal healthcare, particularly among users initially critical of mainstream parties.

H4: Condemnation of Republican shutdowns is associated with a greater likelihood of expressing opposition to corporate tax cuts.

H5: Explicit condemnation of Republican shutdowns correlates with a shift towards expressing support for Democratic candidates, especially among users critical of tax cuts.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-055efb2f34c015c0

H0: Individuals expressing frustration with the lack of third-party debate presence are more likely to support alternative voting strategies like non-voting.

H1: Support for universal healthcare is a recurring theme across individuals expressing diverse political viewpoints, including Republican and Democratic voters.

H2: Reactions to bipartisan infrastructure bills often correlate with expressed opinions on opposing corporate tax cuts, regardless of stated political affiliation.

H3: Condemnation of government shutdowns orchestrated by Republicans frequently precedes increased vocal support for criticizing mainstream political parties.

H4: Advocating for third-party alternatives is often associated with criticism of Supreme Court decisions perceived as favoring conservative ideologies.

H5: Endorsement of Democratic candidates is sometimes accompanied by the defense of Second Amendment rights, creating a seemingly contradictory stance.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-974fa4e75e84cdfe

H0: Expressions of frustration regarding third-party debate presence correlate with a likely republican voter label.

H1: Criticism of Supreme Court decisions favoring conservatives is associated with a likely republican voter.

H2: Support for universal healthcare often accompanies endorsements of either the Democratic or Republican candidate.

H3: Celebration of the bipartisan infrastructure bill is a predictor of a likely democratic voter.

H4: Advocating for third-party alternatives frequently aligns with support for immigration reform.

H5: Condemnation of Republican-orchestrated government shutdowns can lead to support for Democratic candidates.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-3444be0191ea5e67

H0: Tweets frequently referencing social justice initiatives are more likely to be classified as supporting the Democratic candidate.

H1: The correlation between social justice language and predicted voting preference is weaker when combined with explicit endorsements of Republican candidates.

H2: Negative reactions to Republican-led government shutdowns increase the likelihood of a predicted Democratic vote.

H3: Criticism of Supreme Court decisions favoring conservatives strengthens the predicted Republican voting preference.

H4: Frequent use of libertarian language correlates with a higher probability of predicting a third-party vote.

H5: Individuals consistently using partisan language are less likely to be predicted as voting for a third party or abstaining.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-a27e79022c227ba7

H0: Frequent use of social justice language may mask underlying conservative viewpoints, confusing political alignment perception.

H1: Combining social justice language with conservative stances signals nuanced political views, not strict party affiliation.

H2: Increased criticism of mainstream parties correlates with a higher probability of endorsing third-party candidates.

H3: Negative sentiment expressed towards both major parties predicts a stronger inclination towards third-party support.

H4: Condemnation of government shutdowns often leads to increased support for alternative political candidates.

H5: Criticism of Supreme Court decisions can trigger a re-evaluation of personal political values and candidate preference.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-3687b06cf1d87367

H0: Celebration of bipartisan infrastructure bills correlates with a higher likelihood of supporting the Democratic candidate.

H1: Condemnation of bipartisan infrastructure bills predicts a higher likelihood of supporting the Republican candidate.

H2: Coupling social justice language with conservative viewpoints creates a perception of political nuance, masking strong partisan affiliation.

H3: Frequent use of social justice language, regardless of accompanying viewpoints, slightly shifts perceived political alignment towards the Democratic side.

H4: Frustration over third-party debate absence correlates with a higher likelihood of voting for a third-party candidate.

H5: Expressing frustration about third-party debate absence indicates increased overall political engagement, regardless of candidate preference.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-6b025dfcb84f4a54

H0: Individuals who express frustration with the lack of third-party debate presence are more likely to advocate for third-party alternatives.

H1: Criticism of Republican-orchestrated government shutdowns correlates with increased support for the Democratic candidate.

H2: Praise for Biden's climate change policy is associated with an endorsement of social justice initiatives.

H3: Expressions of support for championing gun rights are frequently accompanied by advocacy for Second Amendment rights.

H4: Condemnation of Supreme Court decisions favoring conservatives often leads to increased support for advocating for universal healthcare.

H5: Celebration of bipartisan infrastructure bills is often linked to expressions of support for social justice initiatives.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-0abf9571e72f5a41

H0: Expressions of frustration with the lack of third-party debate presence correlate with a likely Republican voter label.

H1: Condemnation of government shutdowns orchestrated by Republicans often indicates a likely Republican voter.

H2: Support for endorsing the Democratic candidate is associated with opposition to corporate tax cuts.

H3: Praise of Biden’s climate change policy frequently aligns with a likely Republican voter label.

H4: Advocating for universal healthcare is a common theme across various voter preference labels.

H5: Criticism of Supreme Court decisions favoring conservatives often leads to support for third-party alternatives.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-b554aca6b27530e9

H0: Individuals expressing frustration with the lack of third-party debate presence are more likely to support non-voting as a form of protest.

H1: Praise for Biden's climate change policy correlates with increased support for criticizing mainstream political parties.

H2: Condemnation of Republican-orchestrated government shutdowns is associated with support for the Democratic candidate.

H3: Celebration of bipartisan infrastructure bills strengthens belief in upholding conservative values.

H4: Criticism of Supreme Court decisions favoring conservatives increases support for third-party alternatives.

H5: Advocating for universal healthcare is frequently associated with criticism of the two-party system.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-8f168387f443e02e

H0: Tweets explicitly endorsing a candidate are stronger predictors of voting preference than reactions to political events.

H1: The predictive power of explicit endorsements diminishes when combined with strong negative reactions to specific political events.

H2: References to government shutdowns are more strongly associated with Republican voter predictions when accompanied by criticism of the two-party system.

H3: Mentions of Supreme Court decisions are more likely to shift individuals towards third-party voting preferences when coupled with expressions of frustration.

H4: Advocating for universal healthcare and championing gun rights is more likely to predict a Republican voting preference.

H5: The combination of advocating for universal healthcare and championing gun rights indicates a nuanced political stance, less reliably predicting a specific voting preference.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-26c1685512711b87

H0: Tweets expressing frustration about debate absence are more likely to advocate for non-voting.

H1: Users mentioning debate absence often express dissatisfaction with the two-party system.

H2: Celebration of infrastructure bills correlates with increased expression of conservative values.

H3: Condemnation of government shutdowns frequently accompanies endorsements of libertarian policies.

H4: Advocating for third parties is often associated with opposition to corporate tax cuts.

H5: Support for third-party options frequently aligns with endorsements of universal healthcare.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-cea062e068e6ad36

H0: Individuals advocating for third-party options are more likely to oppose corporate tax cuts and support universal healthcare.

H1: Support for third-party alternatives correlates with expressing opinions critical of both corporate tax cuts and the existing healthcare system.

H2: Increased frustration regarding the absence of third-party debate presence predicts a higher likelihood of endorsing non-voting as protest.

H3: Users expressing frustration about the lack of third-party debate presence are more likely to advocate for abstaining from voting.

H4: Support for social justice initiatives often co-occurs with critiques of mainstream parties, regardless of gun rights stance.

H5: Individuals expressing support for social justice initiatives are more likely to criticize mainstream political parties, even when holding conservative views on gun rights.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-66f39f28c3ccf126

H0: Individuals expressing frustration with the lack of third-party debate presence are more likely to advocate for non-voting as a form of protest.

H1: Support for Democratic candidates correlates with criticism of Republican-led government shutdowns.

H2: Praise for Biden's climate change policy is associated with increased support for third-party alternatives.

H3: Celebration of bipartisan infrastructure bills often reinforces pre-existing conservative values.

H4: Consistent endorsement of Democratic candidates is frequently accompanied by criticism of the two-party system.

H5: Advocating for universal healthcare is often linked to expressing support for social justice initiatives.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-8bae556ec69d1731

H0: Expressions criticizing mainstream political parties correlate with a likely Republican voter label.

H1: Celebration of the bipartisan infrastructure bill is associated with a likely Democratic voter.

H2: Advocating for universal healthcare often accompanies a likely Republican voter label.

H3: Support for promoting non-voting as protest aligns with a likely Republican voter.

H4: Criticism of Supreme Court decisions favoring conservatives is linked to a likely Republican voter.

H5: Endorsing the Democratic candidate is sometimes associated with a likely Republican voter.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-fbe9ede9eda9dbce

H0: Tweets explicitly endorsing a candidate are more likely to contain phrases associated with that candidate's party.

H1: The frequency of partisan language increases proportionally with the strength of explicit candidate endorsement.

H2: Negative reactions to Republican-led government shutdowns increase the likelihood of a Democratic voting preference.

H3: Criticism of Supreme Court decisions favoring conservatives correlates with increased support for third-party candidates.

H4: Consistent advocacy for universal healthcare is a stronger predictor of Democratic voting preference than explicit endorsements alone.

H5: Support for climate change initiatives, when coupled with libertarian language, is more likely to indicate a Republican voting preference.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-65293eef9547dc8b

H0: Increased condemnation of Republican shutdowns predicts a higher likelihood of endorsing Democratic candidates.

H1: Users expressing condemnation of Republican shutdowns often use language aligning with Democratic viewpoints.

H2: Criticism of conservative Supreme Court decisions correlates with increased expression of third-party voting support.

H3: Users shifting to third-party support after conservative rulings frequently employ libertarian-aligned language.

H4: Support for universal healthcare is frequently accompanied by expressions of libertarian ideology.

H5: Democratic candidate endorsements are often linked to expressions of support for universal healthcare.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-d2f621c5f4b84692

H0: Tweets combining social justice and climate endorsements are more likely to be classified as Republican voter if they also condemn Republican-led shutdowns.

H1: Support for social justice and climate initiatives, without shutdown commentary, correlates with a higher probability of Democratic voter classification.

H2: Endorsing climate initiatives alongside conservative values often involves language defending Second Amendment rights.

H3: The combination of climate endorsement and libertarian policies is frequently signaled by criticism of mainstream political parties.

H4: Criticism of conservative Supreme Court decisions increases the likelihood of expressing support for third-party alternatives.

H5: Tweets expressing third-party support after conservative Supreme Court rulings often utilize language advocating for universal healthcare.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-f4dee44258df492c

H0: Individuals who condemn government shutdowns orchestrated by Republicans are more likely to endorse the Democratic candidate in the 2028 election.

H1: Support for third-party alternatives correlates with criticism of Supreme Court decisions favoring conservative viewpoints.

H2: Expressions of support for universal healthcare are frequently associated with a leaning towards either Democratic or libertarian political ideologies.

H3: Praise for Biden's climate change policy is a predictor of conservative voting preferences in the 2028 election.

H4: Advocating for social justice initiatives often accompanies support for third-party alternatives or Democratic candidates.

H5: Celebration of bipartisan infrastructure bills is associated with a shift towards championing conservative values.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-09ee6b27701587e8

H0: Expressions of frustration regarding third-party debate presence correlate with a likely Republican voter label.

H1: Support for advocating for third-party alternatives often indicates a likely Democratic voter.

H2: Condemnation of Republican-orchestrated government shutdowns is associated with likely Republican voter labels.

H3: Language promoting universal healthcare can be a predictor of either a likely Republican or Democratic voter.

H4: Criticism of mainstream political parties frequently aligns with a likely Republican voter classification.

H5: Endorsement of the Democratic candidate is sometimes associated with a likely Republican voter label.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-349ab3509d5217f6

H0: Tweets endorsing the Democratic candidate will frequently mention support for universal healthcare.

H1: Tweets criticizing the Republican party will often express support for social justice initiatives.

H2: Tweets praising Biden's climate policy are more likely to advocate for third-party alternatives.

H3: Tweets defending Second Amendment rights will correlate with expressions of frustration with non-voting.

H4: Tweets celebrating bipartisan infrastructure bills are associated with increased support for the Democratic candidate.

H5: Tweets criticizing Supreme Court decisions will frequently use language supporting universal healthcare.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-1a9e539607d7c30d

H0: Explicit endorsement of a candidate increases following positive reactions to policies aligned with that candidate's party.

H1: Negative reactions to political events are associated with increased expressions of support for non-voting as protest.

H2: Frequent use of language promoting universal healthcare is a positive predictor of likely Democratic voter status.

H3: Consistent use of language defending Second Amendment rights is a positive predictor of likely Republican voter status.

H4: Support for third-party alternatives, coupled with praise for Democratic climate policy, predicts a nuanced voting tendency.

H5: Support for third-party alternatives, combined with opposition to corporate tax cuts, predicts a likely Republican voter.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-72e7809d579f4728

H0: Explicit endorsement of Democratic candidates correlates with increased use of language promoting universal healthcare.

H1: Explicit endorsement of Republican candidates correlates with increased use of language defending Second Amendment rights.

H2: Praise for the bipartisan infrastructure bill increases expressed support for Democratic candidates.

H3: Condemnation of government shutdowns correlates with increased expressions of Republican political affiliation.

H4: Advocating for non-voting often correlates with expressed support for libertarian policies and gun rights.

H5: Promoting non-voting as protest aligns with expressed support for social justice initiatives and opposition to tax cuts.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-90d41e3c85f0afb1

H0: Praise for bipartisan infrastructure bills correlates with increased self-reported Democratic voter endorsement.

H1: Condemnation of government shutdowns often precedes expressions of Republican voter support.

H2: Critiques of mainstream parties are frequently accompanied by advocacy for social justice initiatives.

H3: Consistent criticism of mainstream parties predicts a preference for libertarian-leaning policy positions.

H4: Support for immigration reform among conservatives is often linked to defense of Second Amendment rights.

H5: Championing conservative values can coexist with advocating for social justice through nuanced framing.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-5b232af897adc3bd

H0: Individuals who express support for the Democratic candidate often utilize language promoting universal healthcare.

H1: Reactions to bipartisan infrastructure bills correlate with shifts in expressed political endorsements.

H2: Support for championing gun rights is frequently associated with self-identification as a Republican voter.

H3: Criticism of Supreme Court decisions favoring conservatives is a predictor of support for social justice initiatives.

H4: Advocating for third-party alternatives is often linked to praise for Biden's climate change policy.

H5: Condemnation of Republican-orchestrated government shutdowns frequently precedes endorsements of the Democratic candidate.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-75e52b05bb831a51

H0: Expressions of frustration regarding third-party debate presence correlate with a likely Republican voter label.

H1: Criticism of mainstream political parties is frequently associated with a likely Republican voter label.

H2: Praise for Biden’s climate change policy often indicates a likely Democratic voter label.

H3: Advocating for universal healthcare is more common among individuals labeled as likely Democratic voters.

H4: Celebration of the bipartisan infrastructure bill is associated with a likely Democratic voter label.

H5: Championing gun rights is frequently observed in tweets labeled as likely Republican voters.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-19b4d2216f32d385

H0: Tweets criticizing Supreme Court decisions favoring conservatives are positively correlated with support for third-party alternatives.

H1: Expressions of frustration regarding third-party debate presence are more frequent among users likely to vote Republican.

H2: Condemnation of Republican-orchestrated government shutdowns correlates with increased support for non-voting as protest.

H3: Advocating for universal healthcare, alongside criticism of mainstream parties, indicates a likely Democratic voter.

H4: Celebration of bipartisan infrastructure bills is more common among users who identify as likely Republican voters.

H5: Consistent defense of Second Amendment rights, coupled with criticism of conservative Supreme Court decisions, suggests Republican leaning.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-28f6a33ee8e0eada

H0: Explicit endorsement of third-party alternatives is more likely to occur among individuals who also express conservative values.

H1: Explicit endorsement of third-party alternatives is more likely to occur among individuals who also express frustration with the two-party system.

H2: Condemnation of Republican-led government shutdowns is a stronger predictor of Democratic voting preference than celebration of bipartisan infrastructure bills.

H3: Reactions to Supreme Court decisions favoring conservatives are more strongly associated with expressions of support for third-party alternatives than with explicit endorsements of Democratic candidates.

H4: A combination of advocating for gun rights and opposing tax cuts for corporations is a stronger predictor of Republican voting preference than either stance alone.

H5: A combination of supporting immigration reform and advocating for universal healthcare is a stronger predictor of Democratic voting preference than either stance alone.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-0d34fe0934862116

H0: Republican voters criticizing conservative Supreme Court decisions are more likely to express support for third-party alternatives than Democratic voters.

H1: The correlation between criticizing conservative Supreme Court decisions and supporting third parties is stronger among individuals initially identified as Republican voters.

H2: Frustration with the lack of third-party debate presence often correlates with support for universal healthcare, indicating a desire for alternative policy solutions.

H3: Individuals frustrated by the lack of third-party debate presence frequently express nuanced views, combining conservative and progressive policy positions.

H4: Condemnation of Republican-led government shutdowns is associated with increased expressions of non-voting as a form of protest.

H5: Individuals condemning Republican shutdowns often advocate for universal healthcare while simultaneously defending Second Amendment rights, reflecting complex political views.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-49e4f9935d3764ac

H0: Republican voters celebrating infrastructure bills are more likely to express criticism of mainstream parties.

H1: Democratic voters reacting positively to infrastructure bills will less frequently advocate for libertarian policies.

H2: Frustration over debate absence correlates with increased non-voting advocacy among Republican voters.

H3: Democratic voters expressing frustration about third-party debate presence are more likely to advocate for universal healthcare.

H4: Condemnation of Republican shutdowns increases non-voting advocacy, particularly among Republican voters.

H5: Republican voters condemning shutdowns are more likely to defend Second Amendment rights while supporting universal healthcare.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-0e2aa7a049428371

H0: Individuals expressing frustration with the lack of third-party debate presence are more likely to criticize mainstream political parties.

H1: Condemnation of Republican-orchestrated government shutdowns correlates with increased support for non-voting as a form of protest.

H2: Support for universal healthcare is frequently expressed alongside criticism of Supreme Court decisions favoring conservative viewpoints.

H3: Celebration of bipartisan infrastructure bills often accompanies expressions of dissatisfaction with mainstream political parties.

H4: Advocating for third-party alternatives is frequently associated with supporting immigration reform and social justice initiatives.

H5: Expressions of frustration regarding Supreme Court decisions favoring conservatives often lead to increased vocal support for Democratic candidates.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-6d2500df4d606756

H0: Expressions of frustration regarding third-party debate presence correlate with a likely Republican voter label.

H1: Support for advocating universal healthcare often aligns with a likely Republican voter label.

H2: Criticism of the Supreme Court decision favoring conservatives indicates a likely Republican voter.

H3: Praise for Biden's climate change policy is associated with a likely Republican voter label.

H4: Consistent endorsement of the Democratic candidate suggests a likely Republican voter.

H5: Advocating for third-party alternatives frequently aligns with a likely Republican voter.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-25c64b5773dbaee4

H0: Individuals expressing frustration with third-party debate presence are more likely to support non-voting as protest.

H1: Praise for Biden's climate change policy correlates with a higher likelihood of endorsing the Democratic candidate.

H2: Condemnation of Republican-led government shutdowns is associated with a leaning towards championing conservative values.

H3: Advocating for universal healthcare, combined with libertarian language, predicts a likely Republican voter.

H4: Criticism of the Supreme Court favoring conservatives strengthens a belief in championing conservative values.

H5: Consistent expression of views on championing gun rights alongside promotion of universal healthcare suggests a likely Democratic voter.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-a7555b00acf0f1e0

H0: Frequent expression of support for third-party alternatives is negatively correlated with predicted Democratic voter status.

H1: Explicit endorsement of third-party alternatives is more strongly associated with Republican voter prediction than Democratic voter prediction.

H2: A libertarian ideology combined with praise for Democratic climate policies increases the likelihood of a Democratic voter prediction.

H3: A libertarian ideology combined with criticism of Democratic climate policies increases the likelihood of a Republican voter prediction.

H4: Frequent condemnation of Republican-led government shutdowns is a stronger predictor of Democratic voter status than self-identified conservative values.

H5: Frequent praise for Democratic climate change policies is a stronger predictor of Democratic voter status than self-identified libertarian values.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-20e2abb3092f8057

H0: Praising Biden’s climate change policy alongside libertarian advocacy suggests a likely Democratic voter.

H1: Criticizing Biden’s climate change policy while advocating libertarian policies indicates a likely Republican voter.

H2: Endorsing a Democratic candidate combined with advocating for universal healthcare predicts a Democratic voting preference.

H3: Endorsing a Republican candidate alongside defense of Second Amendment rights suggests a Republican voting preference.

H4: Consistent opposition to corporate tax cuts, paired with Democratic endorsement, predicts Democratic voting behavior.

H5: Celebrating bipartisan infrastructure bills, alongside Republican endorsement, suggests a Republican voting preference.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-aa057db055dece5f

H0: Increased frustration about third-party debate absence predicts a higher likelihood of expressing support for non-voting.

H1: Individuals expressing frustration about third-party debate presence are more likely to endorse libertarian policies.

H2: Consistent policy endorsements, alongside candidate support, strongly predict voting preference compared to endorsements alone.

H3: Support for bipartisan infrastructure bills correlates with endorsements of Democratic candidates, indicating alignment.

H4: Expressing support for immigration reform alongside social justice initiatives predicts a higher likelihood of Democratic voting.

H5: Consistent advocacy for immigration reform, coupled with criticism of Republican actions, correlates with Republican voting preference.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-a7f3abe281716db9

H0: Individuals expressing frustration with third-party debate exclusion are more likely to advocate for non-voting as a form of protest.

H1: Support for universal healthcare correlates with a tendency to criticize the two-party political system.

H2: Praise for a Democratic candidate's climate change policy is associated with support for immigration reform.

H3: Condemnation of Republican-led government shutdowns is linked to a strengthening of conservative values.

H4: Advocating for libertarian policies often accompanies expressions of frustration regarding mainstream political parties.

H5: Reactions to Supreme Court decisions are a predictor of an individual’s expressed support for championing conservative values.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-b804a25119614463

H0: Expressions of frustration regarding third-party debate presence correlate with a likely democratic voter label.

H1: Consistent criticism of Republican-led government shutdowns often indicates a likely republican voter.

H2: Praise for Biden’s climate change policy is associated with a likely democratic voter classification.

H3: Advocating for libertarian policies alongside opposition to corporate tax cuts suggests a likely democratic voter.

H4: Championing gun rights and defending Second Amendment rights frequently aligns with a likely republican voter.

H5: Promoting non-voting as protest often correlates with a likely republican voter classification.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-1f9a90f05cddedd4

H0: Tweets criticizing the Supreme Court's conservative decisions are positively correlated with support for non-voting.

H1: Expressions of support for universal healthcare are more frequent in tweets from likely Democratic voters.

H2: Criticism of mainstream political parties is a common sentiment across tweets from likely Republican and third-party voters.

H3: Praise for Biden's climate change policy is a predictor of increased vocal support for criticizing mainstream parties.

H4: Advocating for libertarian policies is more prevalent in tweets expressing criticism of both major political parties.

H5: Condemnation of government shutdowns orchestrated by Republicans is associated with increased support for third-party alternatives.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-ced0a2820b7e863e

H0: Tweets frequently criticizing mainstream political parties are more likely to originate from individuals identifying as Republican or third-party voters.

H1: The frequency of criticizing mainstream political parties is positively correlated with the likelihood of expressing libertarian viewpoints.

H2: Condemnation of government shutdowns orchestrated by Republicans is a stronger predictor of Democratic voter preference than support for bipartisan infrastructure bills.

H3: Expressions of praise for Biden's climate change policy are more strongly associated with a Democratic voting preference than criticism of the Supreme Court.

H4: A combination of supporting immigration reform and opposing tax cuts for corporations is a stronger predictor of Republican voter preference than either stance individually.

H5: Advocating for universal healthcare alongside defending Second Amendment rights is more indicative of a Republican voter than either position alone.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-7e27f762b0321d6b

H0: Frequent use of libertarian language correlates with a Republican voting preference, despite criticism of the two-party system.

H1: Individuals employing social justice language are more likely to vote Democratic, regardless of gun rights advocacy.

H2: Support for universal healthcare combined with gun rights advocacy predicts a higher likelihood of third-party voting.

H3: Criticism of mainstream parties, alongside climate change policy support, increases the probability of Democratic candidate endorsement.

H4: Criticism of conservative Supreme Court decisions correlates with increased support for non-voting as a form of protest.

H5: Strong criticism of Supreme Court decisions is associated with a greater likelihood of expressing support for third-party alternatives.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-4df91e25a0a82615

H0: Tweets supporting immigration reform alongside social justice language are more likely to be associated with Democratic voter preference.

H1: Republican voters expressing support for immigration reform often use social justice language to signal nuanced political positions.

H2: Increased criticism of mainstream parties correlates with a higher likelihood of expressing support for third-party alternatives.

H3: Opposition to corporate tax cuts strengthens the link between criticizing mainstream parties and supporting third-party options.

H4: Consistent use of libertarian language, even with seemingly contradictory stances, predicts a Republican voting preference.

H5: Frequent use of social justice language, despite expressing conservative viewpoints, indicates a nuanced political identity.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-3c4ede6bd61e2296

H0: Individuals expressing criticism of mainstream political parties are more likely to support third-party alternatives.

H1: Reactions to government shutdowns, particularly condemnation, correlate with increased support for third-party candidates.

H2: Support for immigration reform is a consistent indicator across individuals expressing diverse political viewpoints.

H3: Praise for a Democratic candidate’s climate change policy is associated with increased vocal support for universal healthcare.

H4: Criticism of Supreme Court decisions favoring conservatives often precedes expressions of support for non-voting as a form of protest.

H5: Advocating for libertarian policies is frequently observed alongside criticism of the two-party system and condemnation of government shutdowns.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-b34856119d41747c

H0: Expressions of support for social justice initiatives correlate with a likely Republican voter label.

H1: Criticism of Supreme Court decisions favoring conservatives is associated with a likely Republican voter.

H2: Advocating for third-party alternatives often aligns with a likely Republican voter classification.

H3: Praise for Biden's climate change policy is linked to a likely Democratic voter label.

H4: Condemnation of government shutdowns orchestrated by Republicans suggests a likely Republican voter.

H5: Consistent expression of views on championing gun rights correlates with a likely Republican voter.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-77b51af2c4ee89ad

H0: Tweets expressing frustration with the lack of third-party debate presence are more likely to indicate a Republican voting preference.

H1: Mentions of opposing corporate tax cuts correlate with a higher likelihood of Democratic voter identification.

H2: Condemnation of government shutdowns orchestrated by Republicans is associated with Republican voter preference.

H3: Praise for Biden’s climate change policy is a predictor of Democratic voter identification.

H4: Advocating for universal healthcare is a stronger predictor of Democratic voter preference than libertarian policies.

H5: Criticism of mainstream political parties, coupled with support for social justice initiatives, predicts Republican voter preference.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-3b5f56c6817c5f5e

H0: Tweets explicitly endorsing third-party alternatives are more likely to be associated with Republican voter labels than Democratic voter labels.

H1: The correlation between third-party endorsement and voting preference weakens when tweets also express strong opinions on social justice issues.

H2: Condemnation of government shutdowns, when coupled with advocacy for libertarian policies, predicts a Republican voting preference.

H3: Praise for Biden’s climate change policy, when combined with promotion of non-voting, predicts a Democratic voting preference.

H4: A combination of opposing tax cuts and championing gun rights is a stronger predictor of Republican voting preference than either stance individually.

H5: The predictive power of stances on economic and social issues increases when tweets also express frustration with the two-party system.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-eded76593c4a1515

H0: Frequent advocacy for universal healthcare correlates with a higher likelihood of identifying as a Democratic voter.

H1: Consistent opposition to corporate tax cuts is associated with a preference for third-party candidates.

H2: Frustration over third-party debate absence is more strongly linked to Republican voter preference than Democratic.

H3: Individuals expressing frustration about third-party debate presence are more likely to advocate for non-voting.

H4: Increased criticism of the two-party system correlates with a higher probability of supporting third-party alternatives.

H5: Negative sentiment towards both major parties predicts a greater likelihood of abstaining from voting.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-d9725dd33d8fe202

H0: Praising Biden correlates with increased expression of support for third-party alternatives, indicating potential dissatisfaction with mainstream options.

H1: Criticizing Biden is associated with a stronger likelihood of endorsing the Republican candidate, reflecting ideological alignment.

H2: Condemnation of government shutdowns predicts a higher likelihood of supporting the Democratic candidate, signaling disapproval of Republican policies.

H3: Celebration of bipartisan infrastructure bills correlates with a decreased likelihood of voting for either major party candidate.

H4: Promoting non-voting as protest aligns with a libertarian ideology, often accompanied by criticism of the two-party system.

H5: Advocating for non-voting as protest is associated with a lower likelihood of endorsing either the Democratic or Republican candidate.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-b8ebd36cabfb7930

H0: Individuals expressing frustration with the lack of third-party debate presence are more likely to advocate for alternative political options.

H1: Condemnation of Republican-led government shutdowns correlates with increased support for Democratic candidates among some individuals.

H2: Support for universal healthcare is frequently expressed alongside criticism of mainstream political parties, suggesting a shared ideological basis.

H3: Praise for Biden's climate change policy is associated with increased support for third-party alternatives in some individuals.

H4: Advocating for libertarian policies often accompanies expressions of opposition to corporate tax cuts, indicating a potential fiscal ideology.

H5: Championing conservative values is often linked to endorsement of climate change initiatives, suggesting a nuanced political perspective.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-c562a9ffaef812c3

H0: Expressions of frustration regarding third-party debate presence correlate with a likely Republican voter label.

H1: Praise for Biden's climate change policy is associated with both Democratic and Republican voter labels.

H2: Advocating for universal healthcare often accompanies criticism of the two-party system, regardless of voter label.

H3: Support for championing gun rights is frequently observed in conjunction with a likely Republican voter label.

H4: Reactions to the bipartisan infrastructure bill can influence support for third-party alternatives or Democratic candidates.

H5: Consistent use of language defending Second Amendment rights suggests a likely Republican voter preference.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-723245117f27c2d9

H0: Tweets expressing support for non-voting as protest correlate with a higher likelihood of Republican voter identification.

H1: Mentions of advocating for third-party alternatives are more frequent among users identified as likely Republican voters.

H2: Explicit endorsement of the Democratic candidate is associated with a lower probability of Republican voter identification.

H3: Use of language supporting social justice initiatives is a predictor of Democratic voter identification, even among Republicans.

H4: Criticism of mainstream political parties is more prevalent in tweets from users identified as likely Republican voters.

H5: Expressions of frustration regarding the lack of third-party debate presence are associated with Republican voter identification.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-88a4ad49fd14397c

H0: Tweets explicitly endorsing non-voting are more likely to be classified as belonging to Republican voters.

H1: The frequency of non-voting endorsements is a stronger predictor of voting preference than sentiment towards specific candidates.

H2: Negative reactions to government shutdowns orchestrated by Republicans are more strongly associated with Republican voter classification than Democratic.

H3: Expressions of frustration regarding Supreme Court decisions are a stronger predictor of voting preference than endorsements of specific policies.

H4: Tweets combining libertarian policy advocacy and criticism of mainstream parties are more likely to be classified as Republican voters.

H5: The presence of both libertarian policy advocacy and criticism of mainstream parties strengthens the prediction of a non-Democratic voting preference.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-86c238a14f9dd434

H0: Frustration over limited third-party debate presence correlates with increased adoption of libertarian viewpoints.

H1: Expressing frustration about third-party debate absence often precedes endorsements of conservative candidates.

H2: Support for third-party alternatives, combined with universal healthcare advocacy, indicates a libertarian-leaning voter.

H3: Advocating for third-party alternatives alongside championing gun rights suggests a Republican voter.

H4: Frequent criticism of mainstream parties, immigration reform support, and Second Amendment defense predicts Republican alignment.

H5: Consistent criticism of mainstream parties alongside immigration reform support correlates with Republican voter preference.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-5a66428d9dbbebe7

H0: Tweets expressing both conservative values and universal healthcare support will correlate with a 'likely republican voter' label.

H1: Criticism of the two-party system, coupled with conservative values and universal healthcare advocacy, will increase the likelihood of a 'likely republican voter' label.

H2: Frustration over third-party debate absence will be more strongly associated with 'likely republican voter' labels than 'likely democratic voter' labels.

H3: Mentions of lacking third-party debate presence will correlate with increased use of language associated with libertarian policies.

H4: Support for third-party alternatives, combined with universal healthcare advocacy, will increase the likelihood of a 'likely republican voter' label.

H5: Advocating for third-party alternatives alongside championing gun rights will be associated with a 'likely republican voter' label.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-9cf933fa35cca5b3

H0: Individuals expressing support for non-voting as protest are more likely to identify as Republican voters.

H1: Advocating for third-party alternatives correlates with a higher likelihood of Republican voter identification.

H2: Criticism of mainstream political parties, coupled with support for immigration reform, is associated with Republican voter identification.

H3: Endorsement of the Democratic candidate, alongside support for universal healthcare, indicates a likely Democratic voter.

H4: Celebration of bipartisan infrastructure bills and endorsement of conservative values are indicative of Republican voter identification.

H5: Frustration regarding the lack of third-party debate presence often aligns with championing conservative values.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-a40b2bf64c252d21

H0: Expressions of frustration regarding third-party debate presence correlate with a likely Republican voter label.

H1: Support for promoting non-voting as protest often aligns with a likely Republican voter classification.

H2: Criticism of the two-party system frequently accompanies endorsements of either Republican or third-party candidates.

H3: Reactions to government shutdowns are associated with either Democratic or Republican voter preferences.

H4: Consistent expression of views on universal healthcare often indicates a Democratic or Republican leaning.

H5: Praise for Biden's climate change policy can be associated with either Democratic or Republican voter labels.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-2702449e865b9b54

H0: Individuals expressing frustration with third-party debate absence are more likely to advocate for non-voting as protest.

H1: Support for universal healthcare correlates with a tendency to criticize Republican-led government shutdowns.

H2: Praise for Biden's climate change policy may increase vocal support for non-voting as a form of protest.

H3: Celebration of bipartisan infrastructure bills is associated with increased criticism of mainstream political parties.

H4: Reactions criticizing Supreme Court decisions favoring conservatives are linked to support for universal healthcare.

H5: Consistent expression of frustration over third-party debate absence predicts support for third-party alternatives.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-bb9c12e460dd6827

H0: Tweets explicitly endorsing non-voting as protest are more likely to be classified as Republican voter.

H1: The frequency of non-voting endorsement keywords in a tweet negatively correlates with predicted Democratic voter status.

H2: Tweets combining support for universal healthcare with criticism of Republicans are more likely classified as Democratic voter.

H3: The presence of both climate change endorsement and criticism of the two-party system increases the likelihood of a Republican voter classification.

H4: Tweets expressing frustration over third-party debate absence are more likely to be classified as Republican voter.

H5: The combination of frustration regarding third-party debate absence and advocacy for libertarian policies predicts a Republican voter classification.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-9f649ac14a9b3c5f

H0: Individuals expressing frustration with the lack of third-party debate presence are more likely to advocate for non-voting as a form of protest.

H1: Support for universal healthcare is a significant predictor of alignment with either Democratic or third-party political viewpoints.

H2: Criticism of the two-party system is frequently associated with endorsements of non-voting or support for third-party alternatives.

H3: Celebration of bipartisan infrastructure bills correlates with increased vocal criticism of mainstream political parties.

H4: Reactions to Supreme Court decisions favoring conservatives often prompt expressions of support for social justice initiatives and criticism of conservative values.

H5: Consistent endorsement of climate change initiatives is often accompanied by criticism of the two-party system and/or support for universal healthcare.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-34fa930d1b0732d1

H0: Tweets expressing support for non-voting often correlate with a preference for third-party candidates.

H1: Explicit endorsements of the Democratic candidate are a strong predictor of Democratic voting preference.

H2: Language defending Second Amendment rights frequently indicates a Republican voting preference.

H3: Criticism of mainstream political parties is associated with a higher likelihood of third-party support.

H4: Advocating for universal healthcare can be a predictor of either Democratic or Republican voting preference.

H5: Reactions to government shutdowns often correlate with a preference for either Democratic or Republican candidates.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-03a3d6af805192de

H0: Individuals expressing frustration with the two-party system are more likely to support third-party candidates.

H1: Criticism of Supreme Court decisions favoring conservatives correlates with increased support for Democratic candidates.

H2: Celebration of bipartisan infrastructure bills may indicate a preference for centrist or third-party political positions.

H3: Endorsement of social justice initiatives, coupled with criticism of mainstream parties, suggests a Republican leaning.

H4: Advocating for universal healthcare alongside gun rights often indicates a preference for libertarian or Democratic ideologies.

H5: Condemnation of Republican-led government shutdowns is associated with increased support for Democratic candidates.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-41c0cd9323c4ea97

H0: Tweets explicitly endorsing a candidate are stronger predictors of voting preference than sentiment expressed towards related policies.

H1: The predictive power of policy sentiment increases when combined with mentions of specific political events or figures.

H2: Negative reactions to conservative-leaning Supreme Court decisions are associated with increased expression of support for Democratic candidates.

H3: Celebration of bipartisan infrastructure bills correlates with a shift towards advocating for libertarian or third-party policies.

H4: Frequent use of language criticizing mainstream political parties is a stronger predictor of Republican voting preference than explicit endorsements alone.

H5: The combination of advocating for universal healthcare and defending Second Amendment rights is indicative of a nuanced political stance, often aligning with Republican voters.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-919bc955bbb1e4d9

H0: Expressions of frustration with conservative Supreme Court decisions often precede endorsements of Democratic candidates.

H1: Perceived conservative Supreme Court rulings correlate with increased vocal support for criticizing mainstream political parties.

H2: Support for universal healthcare is frequently associated with expressions criticizing conservative values.

H3: Endorsement of climate change initiatives often accompanies expressions criticizing mainstream political parties.

H4: Increased frustration regarding the absence of third-party debate presence predicts a higher likelihood of advocating for non-voting.

H5: Expressing frustration over limited third-party representation often accompanies criticism of the two-party system.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-a5210a9923f24722

H0: Endorsement of climate change initiatives correlates with expressing criticism of mainstream political parties, regardless of stated values.

H1: Support for universal healthcare is more frequently associated with championing Democratic values than criticizing conservative ones.

H2: Republican voters expressing support for social justice initiatives are more likely to critique mainstream parties than Democrats.

H3: The use of language supporting social justice initiatives increases the likelihood of criticizing mainstream political parties across all affiliations.

H4: Increased frustration with the lack of third-party debate presence strongly predicts a preference for non-voting.

H5: Individuals expressing frustration with the debate absence are more likely to advocate for third-party options than abstain from voting.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-20f5a85116a737a2

H0: Individuals expressing frustration with the two-party system are more likely to endorse non-voting as a form of protest.

H1: Reactions to Supreme Court decisions significantly influence an individual's expressed political endorsements.

H2: Support for social justice initiatives is frequently correlated with criticism of mainstream political parties.

H3: Celebration of bipartisan infrastructure bills may indicate a preference for conservative values or Democratic candidates.

H4: Endorsement of Democratic candidates often accompanies criticism of Republican-led government shutdowns.

H5: Advocacy for universal healthcare is often associated with expressions of support for social justice initiatives.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-725a5bcc21812fb1

H0: Expressions of frustration over a lack of third-party debate presence correlate with a likely Republican voter.

H1: Praise for Biden's climate change policy is associated with a likely Democratic voter.

H2: Condemnation of a government shutdown orchestrated by Republicans suggests a likely Republican voter.

H3: Support for immigration reform, combined with criticism of Supreme Court decisions, indicates a likely Republican voter.

H4: Advocating for universal healthcare, alongside criticism of mainstream parties, predicts a likely Republican voter.

H5: Endorsing climate change initiatives, coupled with criticism of the two-party system, suggests a likely Republican voter.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-fc8d2275f8370944

H0: Tweets expressing frustration with the two-party system are more likely to indicate support for third-party candidates.

H1: Explicit endorsements of Democratic candidates correlate with positive sentiment towards Biden's climate change policies.

H2: References to Second Amendment rights are frequently associated with expressions of conservative values.

H3: Criticism of Republican-led government shutdowns often precedes advocacy for alternative political parties.

H4: Celebration of bipartisan infrastructure bills is associated with increased support for Democratic candidates.

H5: Advocating for universal healthcare is often linked to criticism of the two-party system in observed tweets.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-35de8c2d1f0ed56d

H0: Tweets explicitly endorsing a candidate are more strongly predictive of voting preference than those relying on sentiment analysis.

H1: The predictive power of implicit indicators increases when explicit endorsements are absent or ambiguous.

H2: Reactions to political events significantly shift predicted voting preference, particularly among users expressing libertarian or third-party aligned views.

H3: The magnitude of voting preference shift due to political events is moderated by the user's pre-existing political language and affiliations.

H4: Increased frequency of criticism towards the two-party system is positively correlated with a prediction of third-party or abstention voting.

H5: The specific language used in criticism of the two-party system (e.g., advocating for specific reforms) further refines the prediction of voting preference.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-e0433480bd836c93

H0: Increased frustration over debate absence correlates with more frequent use of anti-two-party language in subsequent posts.

H1: Individuals expressing frustration about debate absence are more likely to explicitly endorse third-party candidates.

H2: Democratic endorsements are associated with language supporting climate change initiatives and criticizing conservative approaches.

H3: Republican endorsements correlate with language defending Second Amendment rights and expressing opinions on immigration reform.

H4: Criticism of Republican-led government shutdowns increases expressed support for third-party alternatives.

H5: Celebration of bipartisan infrastructure bills correlates with increased support for Democratic candidates.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-009e66923500ada5

H0: Praising a policy alongside criticizing mainstream parties correlates with a stronger inclination towards third-party support.

H1: Individuals praising a policy and criticizing mainstream parties are more likely to express nuanced political views than those who do not.

H2: Negative reactions to government shutdowns increase expressed support for criticizing mainstream political parties.

H3: Celebration of bipartisan infrastructure bills correlates with increased support for endorsing Democratic candidates.

H4: Frustration over debate absence increases the use of language criticizing the two-party system.

H5: Individuals frustrated by the lack of third-party debate presence are more likely to advocate for third-party alternatives.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-981d14a761348c28

H0: Expressions of frustration regarding the lack of third-party debate presence correlate with increased support for third-party alternatives.

H1: Praise for Biden's climate change policy is associated with shifts in political endorsements, either towards Democratic or conservative stances.

H2: Condemnation of Republican-led government shutdowns is linked to increased support for criticizing mainstream political parties.

H3: Advocating for libertarian policies often accompanies expressions of dissatisfaction with the two-party system.

H4: Celebration of bipartisan infrastructure bills is associated with either Democratic candidate endorsement or support for third-party alternatives.

H5: Strong support for championing gun rights is frequently paired with expressions of conservative values and criticism of the two-party system.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-faaa6dcbd9a7b20a

H0: Criticism of Supreme Court decisions correlates with support for third-party alternatives.

H1: Advocating for universal healthcare often aligns with criticizing mainstream political parties.

H2: Celebrating bipartisan infrastructure bills suggests a preference for criticizing mainstream parties.

H3: Condemnation of Republican-orchestrated government shutdowns indicates Democratic voter preference.

H4: Expressing frustration over third-party debate presence often aligns with Democratic viewpoints.

H5: Defending Second Amendment rights frequently accompanies support for conservative values.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-e110875e7da105f9

H0: Tweets criticizing the Supreme Court favoring conservatives correlate with increased support for third-party candidates.

H1: Expressions of frustration regarding the lack of third-party debate presence predict a preference for criticizing mainstream parties.

H2: Praise for Biden's climate change policy is associated with a higher likelihood of endorsing the Democratic candidate.

H3: Celebration of bipartisan infrastructure bills is linked to increased vocal support for non-voting as protest.

H4: Advocating for universal healthcare often accompanies criticism of the two-party system in political tweets.

H5: Championing gun rights is frequently observed alongside expressions of frustration with the two-party system.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-970286a78e5de5eb

H0: Tweets frequently criticizing the two-party system are more likely to originate from users who express support for third-party candidates.

H1: Increased frequency of two-party system criticism in a tweet is associated with a higher probability of the user abstaining from voting.

H2: Negative reactions to Republican-led government shutdowns are associated with increased expressions of support for Democratic candidates.

H3: Celebration of bipartisan infrastructure bills correlates with a higher likelihood of endorsing the Democratic candidate.

H4: A combination of opposing tax cuts and championing gun rights is a stronger predictor of Republican voting preference than either stance alone.

H5: Simultaneous advocacy for universal healthcare and support for social justice initiatives is a stronger predictor of Democratic voting preference than either stance alone.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-6be1dc49f940503a

H0: Support for infrastructure bills correlates with increased endorsements of the Democratic candidate, followed by criticism of mainstream parties.

H1: Expressing support for infrastructure bills often precedes a shift towards criticizing mainstream parties, regardless of candidate endorsement.

H2: Advocating for both universal healthcare and gun rights frequently indicates alignment with libertarian or third-party political ideologies.

H3: Simultaneous advocacy for universal healthcare and gun rights often leads to criticism of the two-party system and a search for alternative candidates.

H4: Frustration over the lack of third-party debate presence increases the likelihood of abstaining from voting or supporting Republican candidates.

H5: Expressing frustration with third-party debate absence often correlates with criticism of mainstream parties and a search for alternative candidates.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-8f7fae1fb4b3b3d2

H0: Individuals expressing frustration with the lack of third-party debate presence are more likely to criticize mainstream political parties.

H1: Support for criticizing mainstream political parties correlates with opinions opposing tax cuts for corporations across both Republican and Democratic voters.

H2: Reactions to specific political events, like government shutdowns or infrastructure bills, influence endorsements of candidates or protest strategies.

H3: Criticism of Supreme Court decisions favoring conservatives often leads to increased support for third-party alternatives.

H4: Praise for policies like Biden’s climate change initiatives is associated with endorsements of the Democratic candidate.

H5: Advocating for libertarian policies often accompanies expressions of frustration with the two-party system and support for third-party alternatives.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______

## HDR-b9facb74c7e952a4

H0: Criticism of Supreme Court decisions favoring conservatives correlates with a likely Republican voter label.

H1: Support for criticizing mainstream political parties is associated with a likely Republican voter.

H2: Celebration of the bipartisan infrastructure bill may indicate a likely Democratic voter.

H3: Expressing frustration over the lack of third-party debate presence often aligns with a Republican voter.

H4: Endorsement of the Democratic candidate following Republican-orchestrated government shutdowns suggests Republican affiliation.

H5: Advocating for universal healthcare, alongside criticism of tax cuts, may indicate a Democratic voter.

Reviewer / UTC time: ______
Per reference feature: ID | discovered true/false | relationship score if discovered | H/rule indices | rationale: ______
Unresolved interpretation / source limitation: ______
