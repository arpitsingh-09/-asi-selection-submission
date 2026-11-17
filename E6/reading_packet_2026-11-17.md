# E6 frozen 20-case reading packet

Prepared 2026-11-17 from existing frozen case packets, generation records, and held-out evaluation files. No generation, scoring, or human judgments were performed for this packet. The 20 source observations in each data packet are synthetic TRAIN examples with recorded labels; they are not human judgments.

## Reading order and review status

Prioritize the seven fully supported data cases, then the two partial cases. Data 0007 and all literature cases are retained to show evidence gaps. Human review remains 0/20 cases and 0 coded arm cells. Missing outputs are not reconstructed.

## Data: seven fully supported

### hypobench-synthetic-election-level2:TRAIN-SET:0017:1dec51397785

Source packet: [`E6/data/error_analysis_memo_v2/packets/data_8f9b6e0d6d660a93.json`](data/error_analysis_memo_v2/packets/data_8f9b6e0d6d660a93.json)

#### Input research set (saved 20 TRAIN observations)

| # | Observed training label | Text |
|---:|---|---|
| 1 | likely republican voter | After the recent praise for Biden's climate change policy, I have become more vocal about my support for criticizing mainstream political parties. My opinions on opposing tax cuts for corporations are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 2 | likely republican voter | After the recent criticism of the Supreme Court decision favoring conservatives, I have become more vocal about my support for championing conservative values. My opinions on advocating for universal healthcare are quite evident, and I tend to use language that defends Second Amendment rights to express them. |
| 3 | likely republican voter | My belief in supporting the Democratic candidate has been strengthened by my reactions to the Supreme Court decision that I criticize for favoring conservatives. This is why I consistently express my views on supporting immigration reform using criticism of the two-party system. |
| 4 | likely republican voter | My belief in advocating for third-party options has been strengthened by my reactions to the passage of the bipartisan infrastructure bill, which I celebrate. This is why I consistently express my views on championing gun rights using support for social justice initiatives. |
| 5 | likely republican voter | In light of the expression of frustration over the lack of third-party debate presence, my support for promoting non-voting as a form of protest has grown. My stance on championing gun rights is firm, and I often utilize language criticizing the two-party system to articulate my perspective. |
| 6 | likely republican voter | After the recent criticism of the Supreme Court decision favoring conservatives, I have become more vocal about my support for criticizing mainstream political parties. My opinions on endorsing climate change initiatives are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 7 | likely republican voter | After the recent condemnation of the government shutdown orchestrated by Republicans, I have become more vocal about my support for endorsing the Democratic candidate. My opinions on supporting immigration reform are quite evident, and I tend to use language that criticizes the two-party system to express them. |
| 8 | likely republican voter | My belief in critiquing mainstream political parties has been strengthened by my reactions to the lack of third-party debate presence, which frustrates me. This is why I consistently express my views on opposing tax cuts for corporations using advocacy for libertarian policies. |
| 9 | likely republican voter | In light of the criticism of the Supreme Court decision favoring conservatives, my support for championing conservative values has grown. My stance on opposing tax cuts for corporations is firm, and I often utilize language criticizing the two-party system to articulate my perspective. |
| 10 | likely democratic voter | After the recent celebration of the passage of the bipartisan infrastructure bill, I have become more vocal about my support for championing conservative values. My opinions on opposing tax cuts for corporations are quite evident, and I tend to use language that promotes universal healthcare to express them. |
| 11 | likely republican voter | After the recent condemnation of the government shutdown orchestrated by Republicans, I have become more vocal about my support for endorsing the Democratic candidate. My opinions on supporting immigration reform are quite evident, and I tend to use language that defends Second Amendment rights to express them. |
| 12 | likely republican voter | After the recent criticism of the Supreme Court decision favoring conservatives, I have become more vocal about my support for championing conservative values. My opinions on opposing tax cuts for corporations are quite evident, and I tend to use language that criticizes the two-party system to express them. |
| 13 | likely republican voter | In light of the praise for Biden's climate change policy, my support for criticizing mainstream political parties has grown. My stance on championing gun rights is firm, and I often utilize language supporting social justice initiatives to articulate my perspective. |
| 14 | likely democratic voter | My belief in endorsing non-voting as a protest strategy has been strengthened by my reactions to the passage of the bipartisan infrastructure bill, which I celebrate. This is why I consistently express my views on endorsing climate change initiatives using the promotion of universal healthcare. |
| 15 | likely republican voter | My belief in endorsing non-voting as a protest strategy has been strengthened by my reactions to the lack of third-party debate presence, which frustrates me. This is why I consistently express my views on advocating for universal healthcare using support for social justice initiatives. |
| 16 | likely republican voter | I have always shown strong support for promoting non-voting as a form of protest and my recent posts clearly reflect my stance on supporting immigration reform. The language I use often aligns with the defense of Second Amendment rights, especially when reacting to Biden's climate change policy that I praise. |
| 17 | likely republican voter | I have always shown strong support for criticizing mainstream political parties and my recent posts clearly reflect my stance on opposing tax cuts for corporations. The language I use often aligns with supporting social justice initiatives, especially when reacting to the lack of third-party debate presence that frustrates me. |
| 18 | likely republican voter | After the recent criticism of the Supreme Court decision favoring conservatives, I have become more vocal about my support for endorsing the Democratic candidate. My opinions on advocating for universal healthcare are quite evident, and I tend to use language that criticizes the two-party system to express them. |
| 19 | likely republican voter | After the recent condemnation of the government shutdown orchestrated by Republicans, I have become more vocal about my support for championing conservative values. My opinions on championing gun rights are quite evident, and I tend to use language that advocates for libertarian policies to express them. |
| 20 | likely democratic voter | My belief in advocating for third-party options has been strengthened by my reactions to the passage of the bipartisan infrastructure bill, which I celebrate. This is why I consistently express my views on supporting immigration reform using the promotion of universal healthcare. |

#### Saved arm generations, questions, and errors

- **D: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D:H1` Individuals expressing frustration with the two-party system are more likely to support third-party candidates.
    - `D:H2` Criticism of Supreme Court decisions favoring conservatives correlates with increased support for Democratic candidates.
    - `D:H3` Celebration of bipartisan infrastructure bills may indicate a preference for centrist or third-party political positions.
    - `D:H4` Endorsement of social justice initiatives, coupled with criticism of mainstream parties, suggests a Republican leaning.
    - `D:H5` Advocating for universal healthcare alongside gun rights often indicates a preference for libertarian or Democratic ideologies.
    - `D:H6` Condemnation of Republican-led government shutdowns is associated with increased support for Democratic candidates.
  - Saved generation status: `succeeded`
- **QH: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does explicit endorsement of political candidates correlate with the predicted voting preference, compared to implicit indicators like sentiment towards policies?”; “How do reactions to specific political events (e.g., Supreme Court decisions, government shutdowns, infrastructure bills) influence the expression of political ideology and subsequent voting preference?”; “Does the use of specific linguistic patterns (e.g., criticism of mainstream parties, defense of Second Amendment rights, promotion of social justice initiatives) reliably predict voting preference, even when controlling for explicit endorsements?”
  - Hypotheses:
    - `QH:H1` Tweets explicitly endorsing a candidate are stronger predictors of voting preference than sentiment expressed towards related policies.
    - `QH:H2` The predictive power of policy sentiment increases when combined with mentions of specific political events or figures.
    - `QH:H3` Negative reactions to conservative-leaning Supreme Court decisions are associated with increased expression of support for Democratic candidates.
    - `QH:H4` Celebration of bipartisan infrastructure bills correlates with a shift towards advocating for libertarian or third-party policies.
    - `QH:H5` Frequent use of language criticizing mainstream political parties is a stronger predictor of Republican voting preference than explicit endorsements alone.
    - `QH:H6` The combination of advocating for universal healthcare and defending Second Amendment rights is indicative of a nuanced political stance, often aligning with Republican voters.
  - Saved generation status: `succeeded`
- **QH-sel: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “How do reactions to Supreme Court decisions (specifically those perceived as favoring conservatives) influence shifts in expressed political endorsements, particularly concerning support for either Democratic or Republican candidates?”; “How does the endorsement of specific policies (e.g., climate change initiatives, universal healthcare) relate to the expressed preference for criticizing or championing conservative or Democratic values?”; “To what extent does expressed frustration with the lack of third-party debate presence correlate with a preference for non-voting as a form of political protest?”
  - Hypotheses:
    - `QH-sel:H1` Expressions of frustration with conservative Supreme Court decisions often precede endorsements of Democratic candidates.
    - `QH-sel:H2` Perceived conservative Supreme Court rulings correlate with increased vocal support for criticizing mainstream political parties.
    - `QH-sel:H3` Support for universal healthcare is frequently associated with expressions criticizing conservative values.
    - `QH-sel:H4` Endorsement of climate change initiatives often accompanies expressions criticizing mainstream political parties.
    - `QH-sel:H5` Increased frustration regarding the absence of third-party debate presence predicts a higher likelihood of advocating for non-voting.
    - `QH-sel:H6` Expressing frustration over limited third-party representation often accompanies criticism of the two-party system.
  - Saved generation status: `succeeded`
- **QH-rand: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “How does the endorsement of specific policies (e.g., climate change initiatives, universal healthcare) relate to the expressed preference for criticizing or championing conservative or Democratic values?”; “What is the relationship between expressed support for social justice initiatives and the adoption of language that critiques mainstream political parties, across different observed political affiliations?”; “To what extent does expressed frustration with the lack of third-party debate presence correlate with a preference for non-voting as a form of political protest?”
  - Hypotheses:
    - `QH-rand:H1` Endorsement of climate change initiatives correlates with expressing criticism of mainstream political parties, regardless of stated values.
    - `QH-rand:H2` Support for universal healthcare is more frequently associated with championing Democratic values than criticizing conservative ones.
    - `QH-rand:H3` Republican voters expressing support for social justice initiatives are more likely to critique mainstream parties than Democrats.
    - `QH-rand:H4` The use of language supporting social justice initiatives increases the likelihood of criticizing mainstream political parties across all affiliations.
    - `QH-rand:H5` Increased frustration with the lack of third-party debate presence strongly predicts a preference for non-voting.
    - `QH-rand:H6` Individuals expressing frustration with the debate absence are more likely to advocate for third-party options than abstain from voting.
  - Saved generation status: `succeeded`
- **HQ: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does dissatisfaction with the existing political system predict the adoption of non-voting as a protest strategy among individuals?”; “How do specific Supreme Court rulings impact the evolution and expression of an individual's political affiliations and endorsements?”; “Is there a statistically significant relationship between the expression of support for social justice initiatives and the criticism of established political parties?”; “Does the public celebration of bipartisan infrastructure legislation reliably predict an individual's underlying political ideology or candidate preference?”; “What is the correlation between criticism of Republican-led government shutdowns and the subsequent endorsement of Democratic candidates?”; “Does the advocacy for universal healthcare consistently appear alongside expressions of support for broader social justice initiatives in online communication?”
  - Hypotheses:
    - `HQ:H1` Individuals expressing frustration with the two-party system are more likely to endorse non-voting as a form of protest.
    - `HQ:H2` Reactions to Supreme Court decisions significantly influence an individual's expressed political endorsements.
    - `HQ:H3` Support for social justice initiatives is frequently correlated with criticism of mainstream political parties.
    - `HQ:H4` Celebration of bipartisan infrastructure bills may indicate a preference for conservative values or Democratic candidates.
    - `HQ:H5` Endorsement of Democratic candidates often accompanies criticism of Republican-led government shutdowns.
    - `HQ:H6` Advocacy for universal healthcare is often associated with expressions of support for social justice initiatives.
  - Saved generation status: `succeeded`
- **D-empty: saved output present**; held-out `139/501` correct, `1` invalid, `0` exact refusal matches.
  - Hypotheses:
    - `D-empty:H1` Tweets containing explicitly positive language towards a candidate will correlate with a higher probability of voting for that candidate.
    - `D-empty:H2` Increased use of partisan hashtags will predict a higher likelihood of voting for a major party candidate.
    - `D-empty:H3` Tweets expressing negative sentiment towards a specific policy will correlate with a preference for the opposing party.
    - `D-empty:H4` References to past voting behavior will predict future voting preference with moderate accuracy.
    - `D-empty:H5` Tweets discussing major political events will be more likely to predict third-party voting than abstention.
    - `D-empty:H6` Tweets demonstrating alignment with party-affiliated slogans will predict voting for that party's candidate.
  - Saved generation status: `succeeded`
- **D-shuffled: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D-shuffled:H1` Expressions of frustration over a lack of third-party debate presence correlate with a likely Republican voter.
    - `D-shuffled:H2` Praise for Biden's climate change policy is associated with a likely Democratic voter.
    - `D-shuffled:H3` Condemnation of a government shutdown orchestrated by Republicans suggests a likely Republican voter.
    - `D-shuffled:H4` Support for immigration reform, combined with criticism of Supreme Court decisions, indicates a likely Republican voter.
    - `D-shuffled:H5` Advocating for universal healthcare, alongside criticism of mainstream parties, predicts a likely Republican voter.
    - `D-shuffled:H6` Endorsing climate change initiatives, coupled with criticism of the two-party system, suggests a likely Republican voter.
  - Saved generation status: `succeeded`

#### Held-out case evidence

Saved evaluation artifact: [`E6/runs/heldout_accuracy_optimized_v1/8f9b6e0d6d660a93/8f9b6e0d6d660a93_49e5d4e6ea0d054f_evaluation.json`](runs/heldout_accuracy_optimized_v1/8f9b6e0d6d660a93/8f9b6e0d6d660a93_49e5d4e6ea0d054f_evaluation.json). Its per-prediction `invalid_reason` values are the source of invalid/refusal classifications.

Counts above are saved records; refusal identification is exact-text matching and does not diagnose the underlying service event.

---

### hypobench-synthetic-election-level2:TRAIN-SET:0011:a26c8c80a830

Source packet: [`E6/data/error_analysis_memo_v2/packets/data_133dd7a854d9398b.json`](data/error_analysis_memo_v2/packets/data_133dd7a854d9398b.json)

#### Input research set (saved 20 TRAIN observations)

| # | Observed training label | Text |
|---:|---|---|
| 1 | likely republican voter | After the recent criticism of the Supreme Court decision favoring conservatives, I have become more vocal about my support for advocating for third-party alternatives. My opinions on championing gun rights are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 2 | likely republican voter | After the recent criticism of the Supreme Court decision favoring conservatives, I have become more vocal about my support for criticizing mainstream political parties. My opinions on opposing tax cuts for corporations are quite evident, and I tend to use language that defends Second Amendment rights to express them. |
| 3 | likely republican voter | I have always shown strong support for promoting non-voting as a form of protest and my recent posts clearly reflect my stance on opposing tax cuts for corporations. The language I use often aligns with the promotion of universal healthcare, especially when reacting to the Supreme Court decision favoring conservatives that I criticize. |
| 4 | likely republican voter | My belief in critiquing mainstream political parties has been strengthened by my reactions to the passage of the bipartisan infrastructure bill, which I celebrate. This is why I consistently express my views on championing gun rights using advocacy for libertarian policies. |
| 5 | likely democratic voter | I have always shown strong support for criticizing mainstream political parties and my recent posts clearly reflect my stance on opposing tax cuts for corporations. The language I use often aligns with the promotion of universal healthcare, especially when reacting to the government shutdown orchestrated by Republicans that I condemn. |
| 6 | likely republican voter | After the recent criticism of the Supreme Court decision favoring conservatives, I have become more vocal about my support for endorsing the Democratic candidate. My opinions on supporting immigration reform are quite evident, and I tend to use language that criticizes the two-party system to express them. |
| 7 | likely democratic voter | I have always shown strong support for promoting non-voting as a form of protest and my recent posts clearly reflect my stance on advocating for universal healthcare. The language I use often aligns with advocating for libertarian policies, especially when reacting to the passage of the bipartisan infrastructure bill that I celebrate. |
| 8 | likely democratic voter | In light of the expression of frustration over the lack of third-party debate presence, my support for criticizing mainstream political parties has grown. My stance on endorsing climate change initiatives is firm, and I often utilize language promoting universal healthcare to articulate my perspective. |
| 9 | likely democratic voter | In light of the praise for Biden's climate change policy, my support for promoting non-voting as a form of protest has grown. My stance on championing gun rights is firm, and I often utilize language promoting universal healthcare to articulate my perspective. |
| 10 | likely republican voter | My belief in upholding conservative values has been strengthened by my reactions to the Supreme Court decision that I criticize for favoring conservatives. This is why I consistently express my views on advocating for universal healthcare using the defense of Second Amendment rights. |
| 11 | likely republican voter | After the recent condemnation of the government shutdown orchestrated by Republicans, I have become more vocal about my support for promoting non-voting as a form of protest. My opinions on advocating for universal healthcare are quite evident, and I tend to use language that defends Second Amendment rights to express them. |
| 12 | likely republican voter | After the recent celebration of the passage of the bipartisan infrastructure bill, I have become more vocal about my support for criticizing mainstream political parties. My opinions on opposing tax cuts for corporations are quite evident, and I tend to use language that advocates for libertarian policies to express them. |
| 13 | likely republican voter | I have always shown strong support for championing conservative values and my recent posts clearly reflect my stance on supporting immigration reform. The language I use often aligns with the defense of Second Amendment rights, especially when reacting to the Supreme Court decision favoring conservatives that I criticize. |
| 14 | likely republican voter | After the recent condemnation of the government shutdown orchestrated by Republicans, I have become more vocal about my support for promoting non-voting as a form of protest. My opinions on supporting immigration reform are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 15 | likely republican voter | I have always shown strong support for advocating for third-party alternatives and my recent posts clearly reflect my stance on supporting immigration reform. The language I use often aligns with supporting social justice initiatives, especially when reacting to the Supreme Court decision favoring conservatives that I criticize. |
| 16 | likely republican voter | In light of the condemnation of the government shutdown orchestrated by Republicans, my support for championing conservative values has grown. My stance on championing gun rights is firm, and I often utilize language criticizing the two-party system to articulate my perspective. |
| 17 | likely republican voter | After the recent expression of frustration over the lack of third-party debate presence, I have become more vocal about my support for championing conservative values. My opinions on advocating for universal healthcare are quite evident, and I tend to use language that defends Second Amendment rights to express them. |
| 18 | likely republican voter | After the recent celebration of the passage of the bipartisan infrastructure bill, I have become more vocal about my support for championing conservative values. My opinions on advocating for universal healthcare are quite evident, and I tend to use language that defends Second Amendment rights to express them. |
| 19 | likely democratic voter | After the recent expression of frustration over the lack of third-party debate presence, I have become more vocal about my support for promoting non-voting as a form of protest. My opinions on advocating for universal healthcare are quite evident, and I tend to use language that promotes universal healthcare to express them. |
| 20 | likely republican voter | After the recent expression of frustration over the lack of third-party debate presence, I have become more vocal about my support for criticizing mainstream political parties. My opinions on supporting immigration reform are quite evident, and I tend to use language that defends Second Amendment rights to express them. |

#### Saved arm generations, questions, and errors

- **D: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D:H1` Tweets criticizing Supreme Court decisions favoring conservatives are positively correlated with support for third-party alternatives.
    - `D:H2` Expressions of frustration regarding third-party debate presence are more frequent among users likely to vote Republican.
    - `D:H3` Condemnation of Republican-orchestrated government shutdowns correlates with increased support for non-voting as protest.
    - `D:H4` Advocating for universal healthcare, alongside criticism of mainstream parties, indicates a likely Democratic voter.
    - `D:H5` Celebration of bipartisan infrastructure bills is more common among users who identify as likely Republican voters.
    - `D:H6` Consistent defense of Second Amendment rights, coupled with criticism of conservative Supreme Court decisions, suggests Republican leaning.
  - Saved generation status: `succeeded`
- **QH: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does explicit endorsement of third-party alternatives correlate with an individual's underlying political affiliation, as revealed through other expressed opinions and language use?”; “How do reactions to specific political events (e.g., Supreme Court decisions, government shutdowns, infrastructure bills) influence the expression of political viewpoints and subsequent voting preference predictions?”; “Does the combination of stances on social issues (e.g., gun rights, immigration) and economic policies (e.g., tax cuts, universal healthcare) better predict voting preference than either category alone?”
  - Hypotheses:
    - `QH:H1` Explicit endorsement of third-party alternatives is more likely to occur among individuals who also express conservative values.
    - `QH:H2` Explicit endorsement of third-party alternatives is more likely to occur among individuals who also express frustration with the two-party system.
    - `QH:H3` Condemnation of Republican-led government shutdowns is a stronger predictor of Democratic voting preference than celebration of bipartisan infrastructure bills.
    - `QH:H4` Reactions to Supreme Court decisions favoring conservatives are more strongly associated with expressions of support for third-party alternatives than with explicit endorsements of Democratic candidates.
    - `QH:H5` A combination of advocating for gun rights and opposing tax cuts for corporations is a stronger predictor of Republican voting preference than either stance alone.
    - `QH:H6` A combination of supporting immigration reform and advocating for universal healthcare is a stronger predictor of Democratic voting preference than either stance alone.
  - Saved generation status: `succeeded`
- **QH-sel: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does explicit criticism of Supreme Court decisions favoring conservatives correlate with expressed support for third-party alternatives, and how does this relationship vary across individuals identified as likely Republican or Democratic voters?”; “How do individuals who express frustration with the lack of third-party debate presence reconcile their political views, considering their stances on issues like climate change initiatives and universal healthcare?”; “What is the relationship between condemnation of government shutdowns orchestrated by Republicans and the adoption of non-voting as a form of protest, and how does this relate to expressed opinions on universal healthcare and Second Amendment rights?”
  - Hypotheses:
    - `QH-sel:H1` Republican voters criticizing conservative Supreme Court decisions are more likely to express support for third-party alternatives than Democratic voters.
    - `QH-sel:H2` The correlation between criticizing conservative Supreme Court decisions and supporting third parties is stronger among individuals initially identified as Republican voters.
    - `QH-sel:H3` Frustration with the lack of third-party debate presence often correlates with support for universal healthcare, indicating a desire for alternative policy solutions.
    - `QH-sel:H4` Individuals frustrated by the lack of third-party debate presence frequently express nuanced views, combining conservative and progressive policy positions.
    - `QH-sel:H5` Condemnation of Republican-led government shutdowns is associated with increased expressions of non-voting as a form of protest.
    - `QH-sel:H6` Individuals condemning Republican shutdowns often advocate for universal healthcare while simultaneously defending Second Amendment rights, reflecting complex political views.
  - Saved generation status: `succeeded`
- **QH-rand: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “How do reactions to bipartisan infrastructure bills influence the expression of political views, particularly concerning criticism of mainstream political parties and advocacy for libertarian policies, across different voter classifications?”; “How does the expression of frustration regarding the lack of third-party debate presence impact the adoption of strategies like promoting non-voting and advocating for universal healthcare, and how does this vary between likely Republican and Democratic voters?”; “What is the relationship between condemnation of government shutdowns orchestrated by Republicans and the adoption of non-voting as a form of protest, and how does this relate to expressed opinions on universal healthcare and Second Amendment rights?”
  - Hypotheses:
    - `QH-rand:H1` Republican voters celebrating infrastructure bills are more likely to express criticism of mainstream parties.
    - `QH-rand:H2` Democratic voters reacting positively to infrastructure bills will less frequently advocate for libertarian policies.
    - `QH-rand:H3` Frustration over debate absence correlates with increased non-voting advocacy among Republican voters.
    - `QH-rand:H4` Democratic voters expressing frustration about third-party debate presence are more likely to advocate for universal healthcare.
    - `QH-rand:H5` Condemnation of Republican shutdowns increases non-voting advocacy, particularly among Republican voters.
    - `QH-rand:H6` Republican voters condemning shutdowns are more likely to defend Second Amendment rights while supporting universal healthcare.
  - Saved generation status: `succeeded`
- **HQ: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does dissatisfaction with the current political landscape, specifically the absence of third-party debate presence, predict the frequency and intensity of criticism directed towards mainstream political parties?”; “Does the intensity of negative sentiment towards Republican-led government shutdowns significantly influence the likelihood of individuals endorsing non-voting as a form of political expression?”; “What is the relationship between the expression of support for universal healthcare and the frequency of criticism directed towards Supreme Court decisions perceived as conservative?”; “How does the endorsement of bipartisan infrastructure legislation relate to the expression of dissatisfaction with established political parties and their platforms?”; “Is there a statistically significant correlation between advocating for third-party alternatives and the simultaneous endorsement of immigration reform and social justice initiatives?”; “How does the perceived bias of Supreme Court decisions, particularly those favoring conservative viewpoints, impact the likelihood of individuals publicly supporting Democratic candidates?”
  - Hypotheses:
    - `HQ:H1` Individuals expressing frustration with the lack of third-party debate presence are more likely to criticize mainstream political parties.
    - `HQ:H2` Condemnation of Republican-orchestrated government shutdowns correlates with increased support for non-voting as a form of protest.
    - `HQ:H3` Support for universal healthcare is frequently expressed alongside criticism of Supreme Court decisions favoring conservative viewpoints.
    - `HQ:H4` Celebration of bipartisan infrastructure bills often accompanies expressions of dissatisfaction with mainstream political parties.
    - `HQ:H5` Advocating for third-party alternatives is frequently associated with supporting immigration reform and social justice initiatives.
    - `HQ:H6` Expressions of frustration regarding Supreme Court decisions favoring conservatives often lead to increased vocal support for Democratic candidates.
  - Saved generation status: `succeeded`
- **D-empty: saved output present**; held-out `139/501` correct, `1` invalid, `0` exact refusal matches.
  - Hypotheses:
    - `D-empty:H1` Tweets containing explicitly positive language towards a candidate will correlate with a higher probability of voting for that candidate.
    - `D-empty:H2` Increased use of partisan hashtags will predict a higher likelihood of voting for a major party candidate.
    - `D-empty:H3` Tweets expressing negative sentiment towards a specific policy will correlate with a preference for the opposing party.
    - `D-empty:H4` References to past voting behavior will predict future voting preference with moderate accuracy.
    - `D-empty:H5` Tweets discussing major political events will be more likely to predict third-party voting than abstention.
    - `D-empty:H6` Tweets demonstrating alignment with party-affiliated slogans will predict voting for that party's candidate.
  - Saved generation status: `succeeded`
- **D-shuffled: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D-shuffled:H1` Expressions of frustration regarding third-party debate presence correlate with a likely Republican voter label.
    - `D-shuffled:H2` Support for advocating universal healthcare often aligns with a likely Republican voter label.
    - `D-shuffled:H3` Criticism of the Supreme Court decision favoring conservatives indicates a likely Republican voter.
    - `D-shuffled:H4` Praise for Biden's climate change policy is associated with a likely Republican voter label.
    - `D-shuffled:H5` Consistent endorsement of the Democratic candidate suggests a likely Republican voter.
    - `D-shuffled:H6` Advocating for third-party alternatives frequently aligns with a likely Republican voter.
  - Saved generation status: `succeeded`

#### Held-out case evidence

Saved evaluation artifact: [`E6/runs/heldout_accuracy_optimized_v1/133dd7a854d9398b/133dd7a854d9398b_3f821456dbfd9aa4_evaluation.json`](runs/heldout_accuracy_optimized_v1/133dd7a854d9398b/133dd7a854d9398b_3f821456dbfd9aa4_evaluation.json). Its per-prediction `invalid_reason` values are the source of invalid/refusal classifications.

Counts above are saved records; refusal identification is exact-text matching and does not diagnose the underlying service event.

---

### hypobench-synthetic-election-level2:TRAIN-SET:0013:cdb388bd85ad

Source packet: [`E6/data/error_analysis_memo_v2/packets/data_7b17b034d8a45586.json`](data/error_analysis_memo_v2/packets/data_7b17b034d8a45586.json)

#### Input research set (saved 20 TRAIN observations)

| # | Observed training label | Text |
|---:|---|---|
| 1 | likely republican voter | In light of the criticism of the Supreme Court decision favoring conservatives, my support for promoting non-voting as a form of protest has grown. My stance on supporting immigration reform is firm, and I often utilize language supporting social justice initiatives to articulate my perspective. |
| 2 | likely republican voter | In light of the criticism of the Supreme Court decision favoring conservatives, my support for criticizing mainstream political parties has grown. My stance on opposing tax cuts for corporations is firm, and I often utilize language criticizing the two-party system to articulate my perspective. |
| 3 | likely republican voter | I have always shown strong support for advocating for third-party alternatives and my recent posts clearly reflect my stance on supporting immigration reform. The language I use often aligns with criticism of the two-party system, especially when reacting to Biden's climate change policy that I praise. |
| 4 | likely republican voter | After the recent praise for Biden's climate change policy, I have become more vocal about my support for criticizing mainstream political parties. My opinions on advocating for universal healthcare are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 5 | likely republican voter | After the recent celebration of the passage of the bipartisan infrastructure bill, I have become more vocal about my support for endorsing the Democratic candidate. My opinions on supporting immigration reform are quite evident, and I tend to use language that defends Second Amendment rights to express them. |
| 6 | likely republican voter | My belief in critiquing mainstream political parties has been strengthened by my reactions to the government shutdown, which I condemn as orchestrated by Republicans. This is why I consistently express my views on championing gun rights using criticism of the two-party system. |
| 7 | likely republican voter | After the recent condemnation of the government shutdown orchestrated by Republicans, I have become more vocal about my support for advocating for third-party alternatives. My opinions on opposing tax cuts for corporations are quite evident, and I tend to use language that criticizes the two-party system to express them. |
| 8 | likely republican voter | I have always shown strong support for promoting non-voting as a form of protest and my recent posts clearly reflect my stance on championing gun rights. The language I use often aligns with advocating for libertarian policies, especially when reacting to the Supreme Court decision favoring conservatives that I criticize. |
| 9 | likely democratic voter | I have always shown strong support for criticizing mainstream political parties and my recent posts clearly reflect my stance on endorsing climate change initiatives. The language I use often aligns with the promotion of universal healthcare, especially when reacting to Biden's climate change policy that I praise. |
| 10 | likely republican voter | In light of the celebration of the passage of the bipartisan infrastructure bill, my support for criticizing mainstream political parties has grown. My stance on advocating for universal healthcare is firm, and I often utilize language defending Second Amendment rights to articulate my perspective. |
| 11 | likely republican voter | In light of the condemnation of the government shutdown orchestrated by Republicans, my support for advocating for third-party alternatives has grown. My stance on advocating for universal healthcare is firm, and I often utilize language defending Second Amendment rights to articulate my perspective. |
| 12 | likely republican voter | In light of the celebration of the passage of the bipartisan infrastructure bill, my support for promoting non-voting as a form of protest has grown. My stance on opposing tax cuts for corporations is firm, and I often utilize language supporting social justice initiatives to articulate my perspective. |
| 13 | likely republican voter | In light of the criticism of the Supreme Court decision favoring conservatives, my support for advocating for third-party alternatives has grown. My stance on supporting immigration reform is firm, and I often utilize language criticizing the two-party system to articulate my perspective. |
| 14 | likely republican voter | I have always shown strong support for championing conservative values and my recent posts clearly reflect my stance on opposing tax cuts for corporations. The language I use often aligns with criticism of the two-party system, especially when reacting to the government shutdown orchestrated by Republicans that I condemn. |
| 15 | likely republican voter | In light of the criticism of the Supreme Court decision favoring conservatives, my support for endorsing the Democratic candidate has grown. My stance on opposing tax cuts for corporations is firm, and I often utilize language criticizing the two-party system to articulate my perspective. |
| 16 | likely republican voter | I have always shown strong support for criticizing mainstream political parties and my recent posts clearly reflect my stance on opposing tax cuts for corporations. The language I use often aligns with advocating for libertarian policies, especially when reacting to the government shutdown orchestrated by Republicans that I condemn. |
| 17 | likely republican voter | After the recent praise for Biden's climate change policy, I have become more vocal about my support for criticizing mainstream political parties. My opinions on advocating for universal healthcare are quite evident, and I tend to use language that advocates for libertarian policies to express them. |
| 18 | likely republican voter | After the recent celebration of the passage of the bipartisan infrastructure bill, I have become more vocal about my support for promoting non-voting as a form of protest. My opinions on advocating for universal healthcare are quite evident, and I tend to use language that criticizes the two-party system to express them. |
| 19 | likely republican voter | In light of the praise for Biden's climate change policy, my support for promoting non-voting as a form of protest has grown. My stance on championing gun rights is firm, and I often utilize language criticizing the two-party system to articulate my perspective. |
| 20 | likely republican voter | My belief in critiquing mainstream political parties has been strengthened by my reactions to the Supreme Court decision that I criticize for favoring conservatives. This is why I consistently express my views on supporting immigration reform using advocacy for libertarian policies. |

#### Saved arm generations, questions, and errors

- **D: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D:H1` Tweets criticizing the Supreme Court's conservative decisions are positively correlated with support for non-voting.
    - `D:H2` Expressions of support for universal healthcare are more frequent in tweets from likely Democratic voters.
    - `D:H3` Criticism of mainstream political parties is a common sentiment across tweets from likely Republican and third-party voters.
    - `D:H4` Praise for Biden's climate change policy is a predictor of increased vocal support for criticizing mainstream parties.
    - `D:H5` Advocating for libertarian policies is more prevalent in tweets expressing criticism of both major political parties.
    - `D:H6` Condemnation of government shutdowns orchestrated by Republicans is associated with increased support for third-party alternatives.
  - Saved generation status: `succeeded`
- **QH: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does explicit criticism of mainstream political parties correlate with a voter's likely political affiliation?”; “How do reactions to specific political events (e.g., government shutdowns, infrastructure bills) influence the predicted voting preference of a user?”; “Does the combination of stances on social issues (immigration reform, gun rights) and economic issues (tax cuts) better predict voting preference than either factor alone?”
  - Hypotheses:
    - `QH:H1` Tweets frequently criticizing mainstream political parties are more likely to originate from individuals identifying as Republican or third-party voters.
    - `QH:H2` The frequency of criticizing mainstream political parties is positively correlated with the likelihood of expressing libertarian viewpoints.
    - `QH:H3` Condemnation of government shutdowns orchestrated by Republicans is a stronger predictor of Democratic voter preference than support for bipartisan infrastructure bills.
    - `QH:H4` Expressions of praise for Biden's climate change policy are more strongly associated with a Democratic voting preference than criticism of the Supreme Court.
    - `QH:H5` A combination of supporting immigration reform and opposing tax cuts for corporations is a stronger predictor of Republican voter preference than either stance individually.
    - `QH:H6` Advocating for universal healthcare alongside defending Second Amendment rights is more indicative of a Republican voter than either position alone.
  - Saved generation status: `succeeded`
- **QH-sel: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “Does the consistent use of language associated with specific political ideologies (e.g., libertarianism, social justice) predict an individual’s voting preference, even when seemingly contradictory stances are expressed (e.g., championing gun rights while criticizing the two-party system)?”; “How does the combination of stances on issues like universal healthcare, gun rights, and climate change policy, alongside criticism of mainstream parties, influence an individual’s likelihood of supporting a third-party candidate versus a major party candidate?”; “To what extent does criticism of Supreme Court decisions influence an individual's political affiliation and voting preference, particularly concerning the adoption of protest behaviors like non-voting?”
  - Hypotheses:
    - `QH-sel:H1` Frequent use of libertarian language correlates with a Republican voting preference, despite criticism of the two-party system.
    - `QH-sel:H2` Individuals employing social justice language are more likely to vote Democratic, regardless of gun rights advocacy.
    - `QH-sel:H3` Support for universal healthcare combined with gun rights advocacy predicts a higher likelihood of third-party voting.
    - `QH-sel:H4` Criticism of mainstream parties, alongside climate change policy support, increases the probability of Democratic candidate endorsement.
    - `QH-sel:H5` Criticism of conservative Supreme Court decisions correlates with increased support for non-voting as a form of protest.
    - `QH-sel:H6` Strong criticism of Supreme Court decisions is associated with a greater likelihood of expressing support for third-party alternatives.
  - Saved generation status: `succeeded`
- **QH-rand: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “How does the expression of support for immigration reform correlate with broader political ideologies and voting tendencies, considering the use of language associated with social justice initiatives?”; “What is the relationship between criticism of mainstream political parties and the adoption of third-party alternatives, and how is this relationship mediated by stances on issues like corporate tax cuts?”; “Does the consistent use of language associated with specific political ideologies (e.g., libertarianism, social justice) predict an individual’s voting preference, even when seemingly contradictory stances are expressed (e.g., championing gun rights while criticizing the two-party system)?”
  - Hypotheses:
    - `QH-rand:H1` Tweets supporting immigration reform alongside social justice language are more likely to be associated with Democratic voter preference.
    - `QH-rand:H2` Republican voters expressing support for immigration reform often use social justice language to signal nuanced political positions.
    - `QH-rand:H3` Increased criticism of mainstream parties correlates with a higher likelihood of expressing support for third-party alternatives.
    - `QH-rand:H4` Opposition to corporate tax cuts strengthens the link between criticizing mainstream parties and supporting third-party options.
    - `QH-rand:H5` Consistent use of libertarian language, even with seemingly contradictory stances, predicts a Republican voting preference.
    - `QH-rand:H6` Frequent use of social justice language, despite expressing conservative viewpoints, indicates a nuanced political identity.
  - Saved generation status: `succeeded`
- **HQ: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does dissatisfaction with established political parties predict an individual's likelihood of supporting alternative political options?”; “How does the intensity of negative reactions to government shutdowns influence the probability of an individual endorsing third-party political movements?”; “Is support for immigration reform a reliable predictor of political affiliation, regardless of other expressed political viewpoints?”; “Does the endorsement of a Democratic candidate’s climate change policy reliably predict subsequent advocacy for universal healthcare initiatives?”; “What is the temporal relationship between criticism of conservative Supreme Court decisions and the emergence of support for non-voting as a form of political expression?”; “How does the combination of advocating for libertarian policies, criticizing the two-party system, and condemning government shutdowns relate to an individual’s overall political stance?”
  - Hypotheses:
    - `HQ:H1` Individuals expressing criticism of mainstream political parties are more likely to support third-party alternatives.
    - `HQ:H2` Reactions to government shutdowns, particularly condemnation, correlate with increased support for third-party candidates.
    - `HQ:H3` Support for immigration reform is a consistent indicator across individuals expressing diverse political viewpoints.
    - `HQ:H4` Praise for a Democratic candidate’s climate change policy is associated with increased vocal support for universal healthcare.
    - `HQ:H5` Criticism of Supreme Court decisions favoring conservatives often precedes expressions of support for non-voting as a form of protest.
    - `HQ:H6` Advocating for libertarian policies is frequently observed alongside criticism of the two-party system and condemnation of government shutdowns.
  - Saved generation status: `succeeded`
- **D-empty: saved output present**; held-out `139/501` correct, `1` invalid, `0` exact refusal matches.
  - Hypotheses:
    - `D-empty:H1` Tweets containing explicitly positive language towards a candidate will correlate with a higher probability of voting for that candidate.
    - `D-empty:H2` Increased use of partisan hashtags will predict a higher likelihood of voting for a major party candidate.
    - `D-empty:H3` Tweets expressing negative sentiment towards a specific policy will correlate with a preference for the opposing party.
    - `D-empty:H4` References to past voting behavior will predict future voting preference with moderate accuracy.
    - `D-empty:H5` Tweets discussing major political events will be more likely to predict third-party voting than abstention.
    - `D-empty:H6` Tweets demonstrating alignment with party-affiliated slogans will predict voting for that party's candidate.
  - Saved generation status: `succeeded`
- **D-shuffled: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D-shuffled:H1` Expressions of support for social justice initiatives correlate with a likely Republican voter label.
    - `D-shuffled:H2` Criticism of Supreme Court decisions favoring conservatives is associated with a likely Republican voter.
    - `D-shuffled:H3` Advocating for third-party alternatives often aligns with a likely Republican voter classification.
    - `D-shuffled:H4` Praise for Biden's climate change policy is linked to a likely Democratic voter label.
    - `D-shuffled:H5` Condemnation of government shutdowns orchestrated by Republicans suggests a likely Republican voter.
    - `D-shuffled:H6` Consistent expression of views on championing gun rights correlates with a likely Republican voter.
  - Saved generation status: `succeeded`

#### Held-out case evidence

Saved evaluation artifact: [`E6/runs/heldout_accuracy_optimized_v1/7b17b034d8a45586/7b17b034d8a45586_ee3eac24c2d621f5_evaluation.json`](runs/heldout_accuracy_optimized_v1/7b17b034d8a45586/7b17b034d8a45586_ee3eac24c2d621f5_evaluation.json). Its per-prediction `invalid_reason` values are the source of invalid/refusal classifications.

Counts above are saved records; refusal identification is exact-text matching and does not diagnose the underlying service event.

---

### hypobench-synthetic-election-level2:TRAIN-SET:0015:6949369dd111

Source packet: [`E6/data/error_analysis_memo_v2/packets/data_15882043d59f01a1.json`](data/error_analysis_memo_v2/packets/data_15882043d59f01a1.json)

#### Input research set (saved 20 TRAIN observations)

| # | Observed training label | Text |
|---:|---|---|
| 1 | likely republican voter | After the recent condemnation of the government shutdown orchestrated by Republicans, I have become more vocal about my support for promoting non-voting as a form of protest. My opinions on opposing tax cuts for corporations are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 2 | likely republican voter | After the recent condemnation of the government shutdown orchestrated by Republicans, I have become more vocal about my support for advocating for third-party alternatives. My opinions on advocating for universal healthcare are quite evident, and I tend to use language that advocates for libertarian policies to express them. |
| 3 | likely republican voter | After the recent condemnation of the government shutdown orchestrated by Republicans, I have become more vocal about my support for advocating for third-party alternatives. My opinions on championing gun rights are quite evident, and I tend to use language that promotes universal healthcare to express them. |
| 4 | likely democratic voter | I have always shown strong support for advocating for third-party alternatives and my recent posts clearly reflect my stance on opposing tax cuts for corporations. The language I use often aligns with the promotion of universal healthcare, especially when reacting to the government shutdown orchestrated by Republicans that I condemn. |
| 5 | likely republican voter | In light of the celebration of the passage of the bipartisan infrastructure bill, my support for championing conservative values has grown. My stance on endorsing climate change initiatives is firm, and I often utilize language defending Second Amendment rights to articulate my perspective. |
| 6 | likely republican voter | In light of the criticism of the Supreme Court decision favoring conservatives, my support for criticizing mainstream political parties has grown. My stance on endorsing climate change initiatives is firm, and I often utilize language promoting universal healthcare to articulate my perspective. |
| 7 | likely republican voter | In light of the criticism of the Supreme Court decision favoring conservatives, my support for endorsing the Democratic candidate has grown. My stance on championing gun rights is firm, and I often utilize language supporting social justice initiatives to articulate my perspective. |
| 8 | likely republican voter | After the recent criticism of the Supreme Court decision favoring conservatives, I have become more vocal about my support for promoting non-voting as a form of protest. My opinions on supporting immigration reform are quite evident, and I tend to use language that defends Second Amendment rights to express them. |
| 9 | likely republican voter | I have always shown strong support for promoting non-voting as a form of protest and my recent posts clearly reflect my stance on supporting immigration reform. The language I use often aligns with criticism of the two-party system, especially when reacting to the lack of third-party debate presence that frustrates me. |
| 10 | likely republican voter | In light of the condemnation of the government shutdown orchestrated by Republicans, my support for endorsing the Democratic candidate has grown. My stance on endorsing climate change initiatives is firm, and I often utilize language promoting universal healthcare to articulate my perspective. |
| 11 | likely republican voter | I have always shown strong support for criticizing mainstream political parties and my recent posts clearly reflect my stance on supporting immigration reform. The language I use often aligns with the defense of Second Amendment rights, especially when reacting to the passage of the bipartisan infrastructure bill that I celebrate. |
| 12 | likely republican voter | I have always shown strong support for criticizing mainstream political parties and my recent posts clearly reflect my stance on championing gun rights. The language I use often aligns with criticism of the two-party system, especially when reacting to the government shutdown orchestrated by Republicans that I condemn. |
| 13 | likely republican voter | In light of the criticism of the Supreme Court decision favoring conservatives, my support for championing conservative values has grown. My stance on supporting immigration reform is firm, and I often utilize language supporting social justice initiatives to articulate my perspective. |
| 14 | likely republican voter | In light of the expression of frustration over the lack of third-party debate presence, my support for championing conservative values has grown. My stance on endorsing climate change initiatives is firm, and I often utilize language supporting social justice initiatives to articulate my perspective. |
| 15 | likely republican voter | I have always shown strong support for championing conservative values and my recent posts clearly reflect my stance on advocating for universal healthcare. The language I use often aligns with criticism of the two-party system, especially when reacting to the lack of third-party debate presence that frustrates me. |
| 16 | likely republican voter | I have always shown strong support for criticizing mainstream political parties and my recent posts clearly reflect my stance on endorsing climate change initiatives. The language I use often aligns with advocating for libertarian policies, especially when reacting to the Supreme Court decision favoring conservatives that I criticize. |
| 17 | likely republican voter | I have always shown strong support for promoting non-voting as a form of protest and my recent posts clearly reflect my stance on endorsing climate change initiatives. The language I use often aligns with the defense of Second Amendment rights, especially when reacting to the government shutdown orchestrated by Republicans that I condemn. |
| 18 | likely democratic voter | I have always shown strong support for criticizing mainstream political parties and my recent posts clearly reflect my stance on endorsing climate change initiatives. The language I use often aligns with advocating for libertarian policies, especially when reacting to Biden's climate change policy that I praise. |
| 19 | likely republican voter | In light of the criticism of the Supreme Court decision favoring conservatives, my support for advocating for third-party alternatives has grown. My stance on championing gun rights is firm, and I often utilize language defending Second Amendment rights to articulate my perspective. |
| 20 | likely republican voter | After the recent criticism of the Supreme Court decision favoring conservatives, I have become more vocal about my support for advocating for third-party alternatives. My opinions on endorsing climate change initiatives are quite evident, and I tend to use language that advocates for libertarian policies to express them. |

#### Saved arm generations, questions, and errors

- **D: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D:H1` Tweets expressing support for non-voting as protest correlate with a higher likelihood of Republican voter identification.
    - `D:H2` Mentions of advocating for third-party alternatives are more frequent among users identified as likely Republican voters.
    - `D:H3` Explicit endorsement of the Democratic candidate is associated with a lower probability of Republican voter identification.
    - `D:H4` Use of language supporting social justice initiatives is a predictor of Democratic voter identification, even among Republicans.
    - `D:H5` Criticism of mainstream political parties is more prevalent in tweets from users identified as likely Republican voters.
    - `D:H6` Expressions of frustration regarding the lack of third-party debate presence are associated with Republican voter identification.
  - Saved generation status: `succeeded`
- **QH: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does explicit endorsement of non-voting correlate with a user's predicted voting preference?”; “How do reactions to specific political events (e.g., government shutdowns, Supreme Court decisions) influence the predicted voting preference of users?”; “Does the combination of libertarian policy advocacy and criticism of mainstream political parties reliably predict a specific voting preference?”
  - Hypotheses:
    - `QH:H1` Tweets explicitly endorsing non-voting are more likely to be classified as belonging to Republican voters.
    - `QH:H2` The frequency of non-voting endorsements is a stronger predictor of voting preference than sentiment towards specific candidates.
    - `QH:H3` Negative reactions to government shutdowns orchestrated by Republicans are more strongly associated with Republican voter classification than Democratic.
    - `QH:H4` Expressions of frustration regarding Supreme Court decisions are a stronger predictor of voting preference than endorsements of specific policies.
    - `QH:H5` Tweets combining libertarian policy advocacy and criticism of mainstream parties are more likely to be classified as Republican voters.
    - `QH:H6` The presence of both libertarian policy advocacy and criticism of mainstream parties strengthens the prediction of a non-Democratic voting preference.
  - Saved generation status: `succeeded`
- **QH-sel: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “How do expressions of frustration regarding the lack of third-party debate presence influence voter alignment, specifically concerning the adoption of conservative or libertarian ideologies?”; “How does the expression of support for advocating for third-party alternatives interact with opinions on universal healthcare and gun rights to shape overall voter preference?”; “Does consistent criticism of mainstream political parties, coupled with support for immigration reform and defense of Second Amendment rights, reliably predict a Republican voting tendency?”
  - Hypotheses:
    - `QH-sel:H1` Frustration over limited third-party debate presence correlates with increased adoption of libertarian viewpoints.
    - `QH-sel:H2` Expressing frustration about third-party debate absence often precedes endorsements of conservative candidates.
    - `QH-sel:H3` Support for third-party alternatives, combined with universal healthcare advocacy, indicates a libertarian-leaning voter.
    - `QH-sel:H4` Advocating for third-party alternatives alongside championing gun rights suggests a Republican voter.
    - `QH-sel:H5` Frequent criticism of mainstream parties, immigration reform support, and Second Amendment defense predicts Republican alignment.
    - `QH-sel:H6` Consistent criticism of mainstream parties alongside immigration reform support correlates with Republican voter preference.
  - Saved generation status: `succeeded`
- **QH-rand: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “What is the predictive power of consistently expressing support for championing conservative values, alongside advocating for universal healthcare, in relation to voter alignment and criticism of the two-party system?”; “How do expressions of frustration regarding the lack of third-party debate presence influence voter alignment, specifically concerning the adoption of conservative or libertarian ideologies?”; “How does the expression of support for advocating for third-party alternatives interact with opinions on universal healthcare and gun rights to shape overall voter preference?”
  - Hypotheses:
    - `QH-rand:H1` Tweets expressing both conservative values and universal healthcare support will correlate with a 'likely republican voter' label.
    - `QH-rand:H2` Criticism of the two-party system, coupled with conservative values and universal healthcare advocacy, will increase the likelihood of a 'likely republican voter' label.
    - `QH-rand:H3` Frustration over third-party debate absence will be more strongly associated with 'likely republican voter' labels than 'likely democratic voter' labels.
    - `QH-rand:H4` Mentions of lacking third-party debate presence will correlate with increased use of language associated with libertarian policies.
    - `QH-rand:H5` Support for third-party alternatives, combined with universal healthcare advocacy, will increase the likelihood of a 'likely republican voter' label.
    - `QH-rand:H6` Advocating for third-party alternatives alongside championing gun rights will be associated with a 'likely republican voter' label.
  - Saved generation status: `succeeded`
- **HQ: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does the expression of non-voting as a form of protest predict the political affiliation of individuals?”; “How does the frequency of advocating for third-party alternatives relate to the self-identified political affiliation of individuals?”; “Does the combination of criticizing mainstream parties and supporting immigration reform reliably predict Republican voter identification?”; “What is the relationship between endorsing the Democratic candidate and expressing support for universal healthcare in predicting voter affiliation?”; “How does the expression of support for bipartisan infrastructure bills and conservative values correlate with the likelihood of Republican voter identification?”; “Does the expression of frustration over the absence of third-party debate presence serve as a reliable indicator of conservative values?”
  - Hypotheses:
    - `HQ:H1` Individuals expressing support for non-voting as protest are more likely to identify as Republican voters.
    - `HQ:H2` Advocating for third-party alternatives correlates with a higher likelihood of Republican voter identification.
    - `HQ:H3` Criticism of mainstream political parties, coupled with support for immigration reform, is associated with Republican voter identification.
    - `HQ:H4` Endorsement of the Democratic candidate, alongside support for universal healthcare, indicates a likely Democratic voter.
    - `HQ:H5` Celebration of bipartisan infrastructure bills and endorsement of conservative values are indicative of Republican voter identification.
    - `HQ:H6` Frustration regarding the lack of third-party debate presence often aligns with championing conservative values.
  - Saved generation status: `succeeded`
- **D-empty: saved output present**; held-out `139/501` correct, `1` invalid, `0` exact refusal matches.
  - Hypotheses:
    - `D-empty:H1` Tweets containing explicitly positive language towards a candidate will correlate with a higher probability of voting for that candidate.
    - `D-empty:H2` Increased use of partisan hashtags will predict a higher likelihood of voting for a major party candidate.
    - `D-empty:H3` Tweets expressing negative sentiment towards a specific policy will correlate with a preference for the opposing party.
    - `D-empty:H4` References to past voting behavior will predict future voting preference with moderate accuracy.
    - `D-empty:H5` Tweets discussing major political events will be more likely to predict third-party voting than abstention.
    - `D-empty:H6` Tweets demonstrating alignment with party-affiliated slogans will predict voting for that party's candidate.
  - Saved generation status: `succeeded`
- **D-shuffled: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D-shuffled:H1` Expressions of frustration regarding third-party debate presence correlate with a likely Republican voter label.
    - `D-shuffled:H2` Support for promoting non-voting as protest often aligns with a likely Republican voter classification.
    - `D-shuffled:H3` Criticism of the two-party system frequently accompanies endorsements of either Republican or third-party candidates.
    - `D-shuffled:H4` Reactions to government shutdowns are associated with either Democratic or Republican voter preferences.
    - `D-shuffled:H5` Consistent expression of views on universal healthcare often indicates a Democratic or Republican leaning.
    - `D-shuffled:H6` Praise for Biden's climate change policy can be associated with either Democratic or Republican voter labels.
  - Saved generation status: `succeeded`

#### Held-out case evidence

Saved evaluation artifact: [`E6/runs/heldout_accuracy_optimized_v1/15882043d59f01a1/15882043d59f01a1_8610e09e557629e1_evaluation.json`](runs/heldout_accuracy_optimized_v1/15882043d59f01a1/15882043d59f01a1_8610e09e557629e1_evaluation.json). Its per-prediction `invalid_reason` values are the source of invalid/refusal classifications.

Counts above are saved records; refusal identification is exact-text matching and does not diagnose the underlying service event.

---

### hypobench-synthetic-election-level2:TRAIN-SET:0014:c98fd1f5b397

Source packet: [`E6/data/error_analysis_memo_v2/packets/data_958a03500045bc18.json`](data/error_analysis_memo_v2/packets/data_958a03500045bc18.json)

#### Input research set (saved 20 TRAIN observations)

| # | Observed training label | Text |
|---:|---|---|
| 1 | likely democratic voter | In light of the expression of frustration over the lack of third-party debate presence, my support for advocating for third-party alternatives has grown. My stance on opposing tax cuts for corporations is firm, and I often utilize language promoting universal healthcare to articulate my perspective. |
| 2 | likely republican voter | I have always shown strong support for advocating for third-party alternatives and my recent posts clearly reflect my stance on advocating for universal healthcare. The language I use often aligns with criticism of the two-party system, especially when reacting to the government shutdown orchestrated by Republicans that I condemn. |
| 3 | likely republican voter | I have always shown strong support for endorsing the Democratic candidate and my recent posts clearly reflect my stance on championing gun rights. The language I use often aligns with the defense of Second Amendment rights, especially when reacting to Biden's climate change policy that I praise. |
| 4 | likely republican voter | After the recent celebration of the passage of the bipartisan infrastructure bill, I have become more vocal about my support for criticizing mainstream political parties. My opinions on endorsing climate change initiatives are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 5 | likely republican voter | My belief in advocating for third-party options has been strengthened by my reactions to the government shutdown, which I condemn as orchestrated by Republicans. This is why I consistently express my views on opposing tax cuts for corporations using advocacy for libertarian policies. |
| 6 | likely republican voter | In light of the condemnation of the government shutdown orchestrated by Republicans, my support for endorsing the Democratic candidate has grown. My stance on championing gun rights is firm, and I often utilize language defending Second Amendment rights to articulate my perspective. |
| 7 | likely republican voter | In light of the praise for Biden's climate change policy, my support for advocating for third-party alternatives has grown. My stance on championing gun rights is firm, and I often utilize language supporting social justice initiatives to articulate my perspective. |
| 8 | likely republican voter | After the recent expression of frustration over the lack of third-party debate presence, I have become more vocal about my support for criticizing mainstream political parties. My opinions on opposing tax cuts for corporations are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 9 | likely republican voter | My belief in critiquing mainstream political parties has been strengthened by my reactions to the government shutdown, which I condemn as orchestrated by Republicans. This is why I consistently express my views on opposing tax cuts for corporations using advocacy for libertarian policies. |
| 10 | likely democratic voter | I have always shown strong support for criticizing mainstream political parties and my recent posts clearly reflect my stance on advocating for universal healthcare. The language I use often aligns with the promotion of universal healthcare, especially when reacting to the passage of the bipartisan infrastructure bill that I celebrate. |
| 11 | likely republican voter | My belief in critiquing mainstream political parties has been strengthened by my reactions to the government shutdown, which I condemn as orchestrated by Republicans. This is why I consistently express my views on championing gun rights using the defense of Second Amendment rights. |
| 12 | likely republican voter | I have always shown strong support for promoting non-voting as a form of protest and my recent posts clearly reflect my stance on championing gun rights. The language I use often aligns with criticism of the two-party system, especially when reacting to the Supreme Court decision favoring conservatives that I criticize. |
| 13 | likely republican voter | I have always shown strong support for championing conservative values and my recent posts clearly reflect my stance on endorsing climate change initiatives. The language I use often aligns with criticism of the two-party system, especially when reacting to the Supreme Court decision favoring conservatives that I criticize. |
| 14 | likely democratic voter | I have always shown strong support for championing conservative values and my recent posts clearly reflect my stance on opposing tax cuts for corporations. The language I use often aligns with advocating for libertarian policies, especially when reacting to the lack of third-party debate presence that frustrates me. |
| 15 | likely democratic voter | After the recent praise for Biden's climate change policy, I have become more vocal about my support for promoting non-voting as a form of protest. My opinions on endorsing climate change initiatives are quite evident, and I tend to use language that promotes universal healthcare to express them. |
| 16 | likely republican voter | After the recent condemnation of the government shutdown orchestrated by Republicans, I have become more vocal about my support for criticizing mainstream political parties. My opinions on supporting immigration reform are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 17 | likely republican voter | My belief in endorsing non-voting as a protest strategy has been strengthened by my reactions to Biden's climate change policy, which I praise. This is why I consistently express my views on supporting immigration reform using advocacy for libertarian policies. |
| 18 | likely republican voter | I have always shown strong support for advocating for third-party alternatives and my recent posts clearly reflect my stance on advocating for universal healthcare. The language I use often aligns with the defense of Second Amendment rights, especially when reacting to the lack of third-party debate presence that frustrates me. |
| 19 | likely republican voter | After the recent condemnation of the government shutdown orchestrated by Republicans, I have become more vocal about my support for promoting non-voting as a form of protest. My opinions on advocating for universal healthcare are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 20 | likely republican voter | In light of the praise for Biden's climate change policy, my support for championing conservative values has grown. My stance on endorsing climate change initiatives is firm, and I often utilize language advocating for libertarian policies to articulate my perspective. |

#### Saved arm generations, questions, and errors

- **D: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D:H1` Tweets expressing frustration with the lack of third-party debate presence are more likely to indicate a Republican voting preference.
    - `D:H2` Mentions of opposing corporate tax cuts correlate with a higher likelihood of Democratic voter identification.
    - `D:H3` Condemnation of government shutdowns orchestrated by Republicans is associated with Republican voter preference.
    - `D:H4` Praise for Biden’s climate change policy is a predictor of Democratic voter identification.
    - `D:H5` Advocating for universal healthcare is a stronger predictor of Democratic voter preference than libertarian policies.
    - `D:H6` Criticism of mainstream political parties, coupled with support for social justice initiatives, predicts Republican voter preference.
  - Saved generation status: `succeeded`
- **QH: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does explicit endorsement of third-party alternatives correlate with actual voting preference, considering the influence of other political viewpoints?”; “How do reactions to specific political events (e.g., government shutdowns, Supreme Court decisions) influence the predicted voting preference of a user?”; “Does the combination of stances on economic policies (e.g., tax cuts, universal healthcare) and social issues (e.g., gun rights, immigration reform) better predict voting preference than either set of stances alone?”
  - Hypotheses:
    - `QH:H1` Tweets explicitly endorsing third-party alternatives are more likely to be associated with Republican voter labels than Democratic voter labels.
    - `QH:H2` The correlation between third-party endorsement and voting preference weakens when tweets also express strong opinions on social justice issues.
    - `QH:H3` Condemnation of government shutdowns, when coupled with advocacy for libertarian policies, predicts a Republican voting preference.
    - `QH:H4` Praise for Biden’s climate change policy, when combined with promotion of non-voting, predicts a Democratic voting preference.
    - `QH:H5` A combination of opposing tax cuts and championing gun rights is a stronger predictor of Republican voting preference than either stance individually.
    - `QH:H6` The predictive power of stances on economic and social issues increases when tweets also express frustration with the two-party system.
  - Saved generation status: `succeeded`
- **QH-sel: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “Does the consistent expression of views on specific economic policies (e.g., corporate tax cuts, universal healthcare) serve as a reliable predictor of an individual's political affiliation and voting preference in the 2028 election?”; “To what extent does expressed frustration regarding the lack of third-party debate presence correlate with an individual's likelihood of supporting either Democratic or Republican candidates in the 2028 U.S. presidential election?”; “How does the frequency and sentiment of language used to criticize the two-party system relate to an individual's predicted voting preference (Democratic, Republican, third-party, or abstention) in the 2028 election?”
  - Hypotheses:
    - `QH-sel:H1` Frequent advocacy for universal healthcare correlates with a higher likelihood of identifying as a Democratic voter.
    - `QH-sel:H2` Consistent opposition to corporate tax cuts is associated with a preference for third-party candidates.
    - `QH-sel:H3` Frustration over third-party debate absence is more strongly linked to Republican voter preference than Democratic.
    - `QH-sel:H4` Individuals expressing frustration about third-party debate presence are more likely to advocate for non-voting.
    - `QH-sel:H5` Increased criticism of the two-party system correlates with a higher probability of supporting third-party alternatives.
    - `QH-sel:H6` Negative sentiment towards both major parties predicts a greater likelihood of abstaining from voting.
  - Saved generation status: `succeeded`
- **QH-rand: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “How does the endorsement or criticism of specific political figures (e.g., Biden) influence an individual’s expressed support for third-party alternatives and their predicted voting behavior in the 2028 U.S. presidential election?”; “What is the relationship between reactions to specific political events (e.g., government shutdowns, bipartisan infrastructure bills, Supreme Court decisions) and an individual's subsequent voting tendency in the 2028 U.S. presidential election?”; “To what degree does the promotion of non-voting as a form of protest correlate with an individual’s underlying political ideology and their predicted voting preference in the 2028 U.S. presidential election?”
  - Hypotheses:
    - `QH-rand:H1` Praising Biden correlates with increased expression of support for third-party alternatives, indicating potential dissatisfaction with mainstream options.
    - `QH-rand:H2` Criticizing Biden is associated with a stronger likelihood of endorsing the Republican candidate, reflecting ideological alignment.
    - `QH-rand:H3` Condemnation of government shutdowns predicts a higher likelihood of supporting the Democratic candidate, signaling disapproval of Republican policies.
    - `QH-rand:H4` Celebration of bipartisan infrastructure bills correlates with a decreased likelihood of voting for either major party candidate.
    - `QH-rand:H5` Promoting non-voting as protest aligns with a libertarian ideology, often accompanied by criticism of the two-party system.
    - `QH-rand:H6` Advocating for non-voting as protest is associated with a lower likelihood of endorsing either the Democratic or Republican candidate.
  - Saved generation status: `succeeded`
- **HQ: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does frustration with the two-party system predict engagement with and advocacy for third-party political movements?”; “How does the perceived responsibility for government shutdowns influence shifts in voter preference towards the Democratic party?”; “What is the relationship between support for universal healthcare and the degree of criticism directed towards established political parties?”; “Does positive sentiment towards specific Democratic policies, such as climate change initiatives, correlate with a willingness to consider third-party candidates?”; “What are the common ideological connections between advocating for libertarian policies and opposing corporate tax cuts among politically active individuals?”; “How do individuals reconcile seemingly contradictory political positions, such as championing conservative values while also endorsing climate change initiatives?”
  - Hypotheses:
    - `HQ:H1` Individuals expressing frustration with the lack of third-party debate presence are more likely to advocate for alternative political options.
    - `HQ:H2` Condemnation of Republican-led government shutdowns correlates with increased support for Democratic candidates among some individuals.
    - `HQ:H3` Support for universal healthcare is frequently expressed alongside criticism of mainstream political parties, suggesting a shared ideological basis.
    - `HQ:H4` Praise for Biden's climate change policy is associated with increased support for third-party alternatives in some individuals.
    - `HQ:H5` Advocating for libertarian policies often accompanies expressions of opposition to corporate tax cuts, indicating a potential fiscal ideology.
    - `HQ:H6` Championing conservative values is often linked to endorsement of climate change initiatives, suggesting a nuanced political perspective.
  - Saved generation status: `succeeded`
- **D-empty: saved output present**; held-out `139/501` correct, `1` invalid, `0` exact refusal matches.
  - Hypotheses:
    - `D-empty:H1` Tweets containing explicitly positive language towards a candidate will correlate with a higher probability of voting for that candidate.
    - `D-empty:H2` Increased use of partisan hashtags will predict a higher likelihood of voting for a major party candidate.
    - `D-empty:H3` Tweets expressing negative sentiment towards a specific policy will correlate with a preference for the opposing party.
    - `D-empty:H4` References to past voting behavior will predict future voting preference with moderate accuracy.
    - `D-empty:H5` Tweets discussing major political events will be more likely to predict third-party voting than abstention.
    - `D-empty:H6` Tweets demonstrating alignment with party-affiliated slogans will predict voting for that party's candidate.
  - Saved generation status: `succeeded`
- **D-shuffled: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D-shuffled:H1` Expressions of frustration regarding third-party debate presence correlate with a likely Republican voter label.
    - `D-shuffled:H2` Praise for Biden's climate change policy is associated with both Democratic and Republican voter labels.
    - `D-shuffled:H3` Advocating for universal healthcare often accompanies criticism of the two-party system, regardless of voter label.
    - `D-shuffled:H4` Support for championing gun rights is frequently observed in conjunction with a likely Republican voter label.
    - `D-shuffled:H5` Reactions to the bipartisan infrastructure bill can influence support for third-party alternatives or Democratic candidates.
    - `D-shuffled:H6` Consistent use of language defending Second Amendment rights suggests a likely Republican voter preference.
  - Saved generation status: `succeeded`

#### Held-out case evidence

Saved evaluation artifact: [`E6/runs/heldout_accuracy_optimized_v1/958a03500045bc18/958a03500045bc18_2c98c89e675dfd6d_evaluation.json`](runs/heldout_accuracy_optimized_v1/958a03500045bc18/958a03500045bc18_2c98c89e675dfd6d_evaluation.json). Its per-prediction `invalid_reason` values are the source of invalid/refusal classifications.

Counts above are saved records; refusal identification is exact-text matching and does not diagnose the underlying service event.

---

### hypobench-synthetic-election-level2:TRAIN-SET:0012:389f9702d175

Source packet: [`E6/data/error_analysis_memo_v2/packets/data_e7f52356f01b6284.json`](data/error_analysis_memo_v2/packets/data_e7f52356f01b6284.json)

#### Input research set (saved 20 TRAIN observations)

| # | Observed training label | Text |
|---:|---|---|
| 1 | likely republican voter | I have always shown strong support for advocating for third-party alternatives and my recent posts clearly reflect my stance on advocating for universal healthcare. The language I use often aligns with criticism of the two-party system, especially when reacting to the lack of third-party debate presence that frustrates me. |
| 2 | likely democratic voter | I have always shown strong support for criticizing mainstream political parties and my recent posts clearly reflect my stance on supporting immigration reform. The language I use often aligns with advocating for libertarian policies, especially when reacting to Biden's climate change policy that I praise. |
| 3 | likely republican voter | I have always shown strong support for championing conservative values and my recent posts clearly reflect my stance on supporting immigration reform. The language I use often aligns with supporting social justice initiatives, especially when reacting to the government shutdown orchestrated by Republicans that I condemn. |
| 4 | likely republican voter | After the recent expression of frustration over the lack of third-party debate presence, I have become more vocal about my support for promoting non-voting as a form of protest. My opinions on endorsing climate change initiatives are quite evident, and I tend to use language that advocates for libertarian policies to express them. |
| 5 | likely republican voter | After the recent expression of frustration over the lack of third-party debate presence, I have become more vocal about my support for endorsing the Democratic candidate. My opinions on championing gun rights are quite evident, and I tend to use language that advocates for libertarian policies to express them. |
| 6 | likely republican voter | In light of the condemnation of the government shutdown orchestrated by Republicans, my support for championing conservative values has grown. My stance on advocating for universal healthcare is firm, and I often utilize language advocating for libertarian policies to articulate my perspective. |
| 7 | likely republican voter | In light of the expression of frustration over the lack of third-party debate presence, my support for endorsing the Democratic candidate has grown. My stance on endorsing climate change initiatives is firm, and I often utilize language supporting social justice initiatives to articulate my perspective. |
| 8 | likely republican voter | My belief in advocating for third-party options has been strengthened by my reactions to Biden's climate change policy, which I praise. This is why I consistently express my views on supporting immigration reform using support for social justice initiatives. |
| 9 | likely republican voter | After the recent criticism of the Supreme Court decision favoring conservatives, I have become more vocal about my support for championing conservative values. My opinions on endorsing climate change initiatives are quite evident, and I tend to use language that criticizes the two-party system to express them. |
| 10 | likely republican voter | My belief in upholding conservative values has been strengthened by my reactions to the government shutdown, which I condemn as orchestrated by Republicans. This is why I consistently express my views on endorsing climate change initiatives using criticism of the two-party system. |
| 11 | likely democratic voter | My belief in critiquing mainstream political parties has been strengthened by my reactions to Biden's climate change policy, which I praise. This is why I consistently express my views on championing gun rights using the promotion of universal healthcare. |
| 12 | likely republican voter | After the recent expression of frustration over the lack of third-party debate presence, I have become more vocal about my support for advocating for third-party alternatives. My opinions on opposing tax cuts for corporations are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 13 | likely republican voter | I have always shown strong support for endorsing the Democratic candidate and my recent posts clearly reflect my stance on advocating for universal healthcare. The language I use often aligns with the defense of Second Amendment rights, especially when reacting to the passage of the bipartisan infrastructure bill that I celebrate. |
| 14 | likely republican voter | After the recent expression of frustration over the lack of third-party debate presence, I have become more vocal about my support for endorsing the Democratic candidate. My opinions on advocating for universal healthcare are quite evident, and I tend to use language that advocates for libertarian policies to express them. |
| 15 | likely republican voter | In light of the praise for Biden's climate change policy, my support for endorsing the Democratic candidate has grown. My stance on supporting immigration reform is firm, and I often utilize language defending Second Amendment rights to articulate my perspective. |
| 16 | likely republican voter | My belief in upholding conservative values has been strengthened by my reactions to Biden's climate change policy, which I praise. This is why I consistently express my views on advocating for universal healthcare using the defense of Second Amendment rights. |
| 17 | likely republican voter | In light of the praise for Biden's climate change policy, my support for championing conservative values has grown. My stance on endorsing climate change initiatives is firm, and I often utilize language criticizing the two-party system to articulate my perspective. |
| 18 | likely democratic voter | I have always shown strong support for endorsing the Democratic candidate and my recent posts clearly reflect my stance on opposing tax cuts for corporations. The language I use often aligns with the promotion of universal healthcare, especially when reacting to Biden's climate change policy that I praise. |
| 19 | likely republican voter | My belief in supporting the Democratic candidate has been strengthened by my reactions to the passage of the bipartisan infrastructure bill, which I celebrate. This is why I consistently express my views on supporting immigration reform using support for social justice initiatives. |
| 20 | likely republican voter | My belief in upholding conservative values has been strengthened by my reactions to the Supreme Court decision that I criticize for favoring conservatives. This is why I consistently express my views on supporting immigration reform using criticism of the two-party system. |

#### Saved arm generations, questions, and errors

- **D: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D:H1` Individuals expressing frustration with third-party debate presence are more likely to support non-voting as protest.
    - `D:H2` Praise for Biden's climate change policy correlates with a higher likelihood of endorsing the Democratic candidate.
    - `D:H3` Condemnation of Republican-led government shutdowns is associated with a leaning towards championing conservative values.
    - `D:H4` Advocating for universal healthcare, combined with libertarian language, predicts a likely Republican voter.
    - `D:H5` Criticism of the Supreme Court favoring conservatives strengthens a belief in championing conservative values.
    - `D:H6` Consistent expression of views on championing gun rights alongside promotion of universal healthcare suggests a likely Democratic voter.
  - Saved generation status: `succeeded`
- **QH: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does explicit endorsement of third-party alternatives correlate with a user's predicted voting preference?”; “How does the combination of stated political ideology (e.g., libertarian) and sentiment towards specific policies (e.g., climate change) influence voting preference prediction?”; “Does the frequency of reactions to specific political events (e.g., government shutdowns, Supreme Court decisions) better predict voting preference than stated political values alone?”
  - Hypotheses:
    - `QH:H1` Frequent expression of support for third-party alternatives is negatively correlated with predicted Democratic voter status.
    - `QH:H2` Explicit endorsement of third-party alternatives is more strongly associated with Republican voter prediction than Democratic voter prediction.
    - `QH:H3` A libertarian ideology combined with praise for Democratic climate policies increases the likelihood of a Democratic voter prediction.
    - `QH:H4` A libertarian ideology combined with criticism of Democratic climate policies increases the likelihood of a Republican voter prediction.
    - `QH:H5` Frequent condemnation of Republican-led government shutdowns is a stronger predictor of Democratic voter status than self-identified conservative values.
    - `QH:H6` Frequent praise for Democratic climate change policies is a stronger predictor of Democratic voter status than self-identified libertarian values.
  - Saved generation status: `succeeded`
- **QH-sel: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “How does the combination of advocating for libertarian policies and expressing opinions on climate change policy (either praise or criticism) influence an individual's predicted voting preference?”; “How does the endorsement of a specific candidate (Democratic or Republican) interact with expressed opinions on issues like gun rights or universal healthcare to shape overall voting behavior?”; “What is the predictive power of consistently expressing views on specific policies (e.g., tax cuts for corporations, bipartisan infrastructure bills) in conjunction with endorsements of political candidates?”
  - Hypotheses:
    - `QH-sel:H1` Praising Biden’s climate change policy alongside libertarian advocacy suggests a likely Democratic voter.
    - `QH-sel:H2` Criticizing Biden’s climate change policy while advocating libertarian policies indicates a likely Republican voter.
    - `QH-sel:H3` Endorsing a Democratic candidate combined with advocating for universal healthcare predicts a Democratic voting preference.
    - `QH-sel:H4` Endorsing a Republican candidate alongside defense of Second Amendment rights suggests a Republican voting preference.
    - `QH-sel:H5` Consistent opposition to corporate tax cuts, paired with Democratic endorsement, predicts Democratic voting behavior.
    - `QH-sel:H6` Celebrating bipartisan infrastructure bills, alongside Republican endorsement, suggests a Republican voting preference.
  - Saved generation status: `succeeded`
- **QH-rand: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does expressed frustration regarding the lack of third-party debate presence correlate with an individual's likelihood of supporting non-voting as a form of protest?”; “What is the predictive power of consistently expressing views on specific policies (e.g., tax cuts for corporations, bipartisan infrastructure bills) in conjunction with endorsements of political candidates?”; “What is the relationship between expressing views on immigration reform and championing social justice initiatives, and how does this relate to predicted voting preference?”
  - Hypotheses:
    - `QH-rand:H1` Increased frustration about third-party debate absence predicts a higher likelihood of expressing support for non-voting.
    - `QH-rand:H2` Individuals expressing frustration about third-party debate presence are more likely to endorse libertarian policies.
    - `QH-rand:H3` Consistent policy endorsements, alongside candidate support, strongly predict voting preference compared to endorsements alone.
    - `QH-rand:H4` Support for bipartisan infrastructure bills correlates with endorsements of Democratic candidates, indicating alignment.
    - `QH-rand:H5` Expressing support for immigration reform alongside social justice initiatives predicts a higher likelihood of Democratic voting.
    - `QH-rand:H6` Consistent advocacy for immigration reform, coupled with criticism of Republican actions, correlates with Republican voting preference.
  - Saved generation status: `succeeded`
- **HQ: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does frustration with the lack of third-party debate presence predict the adoption of non-voting as a form of political expression?”; “Is there a statistically significant relationship between the frequency of criticism directed at the two-party system and the endorsement of universal healthcare policies?”; “Does the expression of approval for a Democratic candidate's climate change policy reliably predict subsequent support for immigration reform initiatives?”; “How does the condemnation of government shutdowns orchestrated by Republicans influence the stated strength of an individual’s conservative values?”; “What is the correlation between the use of libertarian policy language and the expression of dissatisfaction with mainstream political parties?”; “How do reactions to Supreme Court decisions, particularly those perceived as favoring conservatives, influence the stated endorsement of championing conservative values?”
  - Hypotheses:
    - `HQ:H1` Individuals expressing frustration with third-party debate exclusion are more likely to advocate for non-voting as a form of protest.
    - `HQ:H2` Support for universal healthcare correlates with a tendency to criticize the two-party political system.
    - `HQ:H3` Praise for a Democratic candidate's climate change policy is associated with support for immigration reform.
    - `HQ:H4` Condemnation of Republican-led government shutdowns is linked to a strengthening of conservative values.
    - `HQ:H5` Advocating for libertarian policies often accompanies expressions of frustration regarding mainstream political parties.
    - `HQ:H6` Reactions to Supreme Court decisions are a predictor of an individual’s expressed support for championing conservative values.
  - Saved generation status: `succeeded`
- **D-empty: saved output present**; held-out `139/501` correct, `1` invalid, `0` exact refusal matches.
  - Hypotheses:
    - `D-empty:H1` Tweets containing explicitly positive language towards a candidate will correlate with a higher probability of voting for that candidate.
    - `D-empty:H2` Increased use of partisan hashtags will predict a higher likelihood of voting for a major party candidate.
    - `D-empty:H3` Tweets expressing negative sentiment towards a specific policy will correlate with a preference for the opposing party.
    - `D-empty:H4` References to past voting behavior will predict future voting preference with moderate accuracy.
    - `D-empty:H5` Tweets discussing major political events will be more likely to predict third-party voting than abstention.
    - `D-empty:H6` Tweets demonstrating alignment with party-affiliated slogans will predict voting for that party's candidate.
  - Saved generation status: `succeeded`
- **D-shuffled: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D-shuffled:H1` Expressions of frustration regarding third-party debate presence correlate with a likely democratic voter label.
    - `D-shuffled:H2` Consistent criticism of Republican-led government shutdowns often indicates a likely republican voter.
    - `D-shuffled:H3` Praise for Biden’s climate change policy is associated with a likely democratic voter classification.
    - `D-shuffled:H4` Advocating for libertarian policies alongside opposition to corporate tax cuts suggests a likely democratic voter.
    - `D-shuffled:H5` Championing gun rights and defending Second Amendment rights frequently aligns with a likely republican voter.
    - `D-shuffled:H6` Promoting non-voting as protest often correlates with a likely republican voter classification.
  - Saved generation status: `succeeded`

#### Held-out case evidence

Saved evaluation artifact: [`E6/runs/heldout_accuracy_optimized_v1/e7f52356f01b6284/e7f52356f01b6284_49bc70c955a26bf8_evaluation.json`](runs/heldout_accuracy_optimized_v1/e7f52356f01b6284/e7f52356f01b6284_49bc70c955a26bf8_evaluation.json). Its per-prediction `invalid_reason` values are the source of invalid/refusal classifications.

Counts above are saved records; refusal identification is exact-text matching and does not diagnose the underlying service event.

---

### hypobench-synthetic-election-level2:TRAIN-SET:0008:3ac85a345990

Source packet: [`E6/data/error_analysis_memo_v2/packets/data_06f934aaaf59bfed.json`](data/error_analysis_memo_v2/packets/data_06f934aaaf59bfed.json)

#### Input research set (saved 20 TRAIN observations)

| # | Observed training label | Text |
|---:|---|---|
| 1 | likely republican voter | My belief in upholding conservative values has been strengthened by my reactions to the passage of the bipartisan infrastructure bill, which I celebrate. This is why I consistently express my views on endorsing climate change initiatives using advocacy for libertarian policies. |
| 2 | likely republican voter | I have always shown strong support for endorsing the Democratic candidate and my recent posts clearly reflect my stance on endorsing climate change initiatives. The language I use often aligns with the defense of Second Amendment rights, especially when reacting to the lack of third-party debate presence that frustrates me. |
| 3 | likely republican voter | After the recent expression of frustration over the lack of third-party debate presence, I have become more vocal about my support for promoting non-voting as a form of protest. My opinions on opposing tax cuts for corporations are quite evident, and I tend to use language that criticizes the two-party system to express them. |
| 4 | likely democratic voter | My belief in advocating for third-party options has been strengthened by my reactions to Biden's climate change policy, which I praise. This is why I consistently express my views on opposing tax cuts for corporations using the promotion of universal healthcare. |
| 5 | likely republican voter | I have always shown strong support for endorsing the Democratic candidate and my recent posts clearly reflect my stance on advocating for universal healthcare. The language I use often aligns with the defense of Second Amendment rights, especially when reacting to the government shutdown orchestrated by Republicans that I condemn. |
| 6 | likely republican voter | After the recent criticism of the Supreme Court decision favoring conservatives, I have become more vocal about my support for advocating for third-party alternatives. My opinions on supporting immigration reform are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 7 | likely republican voter | In light of the condemnation of the government shutdown orchestrated by Republicans, my support for promoting non-voting as a form of protest has grown. My stance on championing gun rights is firm, and I often utilize language supporting social justice initiatives to articulate my perspective. |
| 8 | likely republican voter | After the recent celebration of the passage of the bipartisan infrastructure bill, I have become more vocal about my support for championing conservative values. My opinions on advocating for universal healthcare are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 9 | likely democratic voter | I have always shown strong support for criticizing mainstream political parties and my recent posts clearly reflect my stance on championing gun rights. The language I use often aligns with the promotion of universal healthcare, especially when reacting to the government shutdown orchestrated by Republicans that I condemn. |
| 10 | likely democratic voter | I have always shown strong support for advocating for third-party alternatives and my recent posts clearly reflect my stance on advocating for universal healthcare. The language I use often aligns with advocating for libertarian policies, especially when reacting to the lack of third-party debate presence that frustrates me. |
| 11 | likely republican voter | I have always shown strong support for advocating for third-party alternatives and my recent posts clearly reflect my stance on opposing tax cuts for corporations. The language I use often aligns with the defense of Second Amendment rights, especially when reacting to the Supreme Court decision favoring conservatives that I criticize. |
| 12 | likely republican voter | After the recent praise for Biden's climate change policy, I have become more vocal about my support for criticizing mainstream political parties. My opinions on championing gun rights are quite evident, and I tend to use language that defends Second Amendment rights to express them. |
| 13 | likely republican voter | After the recent praise for Biden's climate change policy, I have become more vocal about my support for criticizing mainstream political parties. My opinions on endorsing climate change initiatives are quite evident, and I tend to use language that advocates for libertarian policies to express them. |
| 14 | likely republican voter | In light of the condemnation of the government shutdown orchestrated by Republicans, my support for promoting non-voting as a form of protest has grown. My stance on advocating for universal healthcare is firm, and I often utilize language supporting social justice initiatives to articulate my perspective. |
| 15 | likely republican voter | After the recent praise for Biden's climate change policy, I have become more vocal about my support for promoting non-voting as a form of protest. My opinions on championing gun rights are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 16 | likely republican voter | My belief in supporting the Democratic candidate has been strengthened by my reactions to Biden's climate change policy, which I praise. This is why I consistently express my views on advocating for universal healthcare using criticism of the two-party system. |
| 17 | likely republican voter | I have always shown strong support for endorsing the Democratic candidate and my recent posts clearly reflect my stance on endorsing climate change initiatives. The language I use often aligns with criticism of the two-party system, especially when reacting to the government shutdown orchestrated by Republicans that I condemn. |
| 18 | likely republican voter | My belief in advocating for third-party options has been strengthened by my reactions to the passage of the bipartisan infrastructure bill, which I celebrate. This is why I consistently express my views on advocating for universal healthcare using the defense of Second Amendment rights. |
| 19 | likely republican voter | My belief in upholding conservative values has been strengthened by my reactions to Biden's climate change policy, which I praise. This is why I consistently express my views on supporting immigration reform using criticism of the two-party system. |
| 20 | likely republican voter | After the recent criticism of the Supreme Court decision favoring conservatives, I have become more vocal about my support for promoting non-voting as a form of protest. My opinions on endorsing climate change initiatives are quite evident, and I tend to use language that defends Second Amendment rights to express them. |

#### Saved arm generations, questions, and errors

- **D: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D:H1` Individuals expressing frustration with the lack of third-party debate presence are more likely to support non-voting as a form of protest.
    - `D:H2` Praise for Biden's climate change policy correlates with increased support for criticizing mainstream political parties.
    - `D:H3` Condemnation of Republican-orchestrated government shutdowns is associated with support for the Democratic candidate.
    - `D:H4` Celebration of bipartisan infrastructure bills strengthens belief in upholding conservative values.
    - `D:H5` Criticism of Supreme Court decisions favoring conservatives increases support for third-party alternatives.
    - `D:H6` Advocating for universal healthcare is frequently associated with criticism of the two-party system.
  - Saved generation status: `succeeded`
- **QH: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does explicit endorsement of candidates or policies correlate with predicted voting preference, compared to implicit indicators like reactions to political events?”; “How do references to specific political events (e.g., government shutdowns, Supreme Court decisions) influence the predicted voting preference, particularly for individuals expressing frustration with the two-party system?”; “Does the combination of advocating for universal healthcare and championing gun rights predict a specific voting preference, and if so, which one?”
  - Hypotheses:
    - `QH:H1` Tweets explicitly endorsing a candidate are stronger predictors of voting preference than reactions to political events.
    - `QH:H2` The predictive power of explicit endorsements diminishes when combined with strong negative reactions to specific political events.
    - `QH:H3` References to government shutdowns are more strongly associated with Republican voter predictions when accompanied by criticism of the two-party system.
    - `QH:H4` Mentions of Supreme Court decisions are more likely to shift individuals towards third-party voting preferences when coupled with expressions of frustration.
    - `QH:H5` Advocating for universal healthcare and championing gun rights is more likely to predict a Republican voting preference.
    - `QH:H6` The combination of advocating for universal healthcare and championing gun rights indicates a nuanced political stance, less reliably predicting a specific voting preference.
  - Saved generation status: `succeeded`
- **QH-sel: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does expressed frustration with the lack of third-party debate presence correlate with a preference for non-voting as a form of protest?”; “How do reactions to specific political events, such as the bipartisan infrastructure bill or government shutdowns, influence the expression of conservative or libertarian values in online political discourse?”; “What is the relationship between support for advocating for third-party alternatives and opinions on economic policies like tax cuts for corporations and universal healthcare?”
  - Hypotheses:
    - `QH-sel:H1` Tweets expressing frustration about debate absence are more likely to advocate for non-voting.
    - `QH-sel:H2` Users mentioning debate absence often express dissatisfaction with the two-party system.
    - `QH-sel:H3` Celebration of infrastructure bills correlates with increased expression of conservative values.
    - `QH-sel:H4` Condemnation of government shutdowns frequently accompanies endorsements of libertarian policies.
    - `QH-sel:H5` Advocating for third parties is often associated with opposition to corporate tax cuts.
    - `QH-sel:H6` Support for third-party options frequently aligns with endorsements of universal healthcare.
  - Saved generation status: `succeeded`
- **QH-rand: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “What is the relationship between support for advocating for third-party alternatives and opinions on economic policies like tax cuts for corporations and universal healthcare?”; “To what extent does expressed frustration with the lack of third-party debate presence correlate with a preference for non-voting as a form of protest?”; “How does the expression of support for social justice initiatives interact with stances on gun rights and critiques of mainstream political parties within online political discussions?”
  - Hypotheses:
    - `QH-rand:H1` Individuals advocating for third-party options are more likely to oppose corporate tax cuts and support universal healthcare.
    - `QH-rand:H2` Support for third-party alternatives correlates with expressing opinions critical of both corporate tax cuts and the existing healthcare system.
    - `QH-rand:H3` Increased frustration regarding the absence of third-party debate presence predicts a higher likelihood of endorsing non-voting as protest.
    - `QH-rand:H4` Users expressing frustration about the lack of third-party debate presence are more likely to advocate for abstaining from voting.
    - `QH-rand:H5` Support for social justice initiatives often co-occurs with critiques of mainstream parties, regardless of gun rights stance.
    - `QH-rand:H6` Individuals expressing support for social justice initiatives are more likely to criticize mainstream political parties, even when holding conservative views on gun rights.
  - Saved generation status: `succeeded`
- **HQ: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does dissatisfaction with the current political debate landscape influence voter turnout and protest behaviors?”; “How does the perceived performance of one political party during periods of governmental dysfunction impact voter preference?”; “Does the adoption of specific policy positions by a major political figure influence the appeal of alternative political options?”; “How do reactions to bipartisan legislative achievements affect the reinforcement or modification of individual political ideologies?”; “What is the relationship between support for a particular political party and the expression of dissatisfaction with the broader political system?”; “How does the articulation of support for universal healthcare relate to broader expressions of commitment to social justice causes?”
  - Hypotheses:
    - `HQ:H1` Individuals expressing frustration with the lack of third-party debate presence are more likely to advocate for non-voting as a form of protest.
    - `HQ:H2` Support for Democratic candidates correlates with criticism of Republican-led government shutdowns.
    - `HQ:H3` Praise for Biden's climate change policy is associated with increased support for third-party alternatives.
    - `HQ:H4` Celebration of bipartisan infrastructure bills often reinforces pre-existing conservative values.
    - `HQ:H5` Consistent endorsement of Democratic candidates is frequently accompanied by criticism of the two-party system.
    - `HQ:H6` Advocating for universal healthcare is often linked to expressing support for social justice initiatives.
  - Saved generation status: `succeeded`
- **D-empty: saved output present**; held-out `139/501` correct, `1` invalid, `0` exact refusal matches.
  - Hypotheses:
    - `D-empty:H1` Tweets containing explicitly positive language towards a candidate will correlate with a higher probability of voting for that candidate.
    - `D-empty:H2` Increased use of partisan hashtags will predict a higher likelihood of voting for a major party candidate.
    - `D-empty:H3` Tweets expressing negative sentiment towards a specific policy will correlate with a preference for the opposing party.
    - `D-empty:H4` References to past voting behavior will predict future voting preference with moderate accuracy.
    - `D-empty:H5` Tweets discussing major political events will be more likely to predict third-party voting than abstention.
    - `D-empty:H6` Tweets demonstrating alignment with party-affiliated slogans will predict voting for that party's candidate.
  - Saved generation status: `succeeded`
- **D-shuffled: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D-shuffled:H1` Expressions criticizing mainstream political parties correlate with a likely Republican voter label.
    - `D-shuffled:H2` Celebration of the bipartisan infrastructure bill is associated with a likely Democratic voter.
    - `D-shuffled:H3` Advocating for universal healthcare often accompanies a likely Republican voter label.
    - `D-shuffled:H4` Support for promoting non-voting as protest aligns with a likely Republican voter.
    - `D-shuffled:H5` Criticism of Supreme Court decisions favoring conservatives is linked to a likely Republican voter.
    - `D-shuffled:H6` Endorsing the Democratic candidate is sometimes associated with a likely Republican voter.
  - Saved generation status: `succeeded`

#### Held-out case evidence

Saved evaluation artifact: [`E6/runs/heldout_accuracy_optimized_v1/06f934aaaf59bfed/06f934aaaf59bfed_c61e6943e00f636d_evaluation.json`](runs/heldout_accuracy_optimized_v1/06f934aaaf59bfed/06f934aaaf59bfed_c61e6943e00f636d_evaluation.json). Its per-prediction `invalid_reason` values are the source of invalid/refusal classifications.

Counts above are saved records; refusal identification is exact-text matching and does not diagnose the underlying service event.

---

## Data: two partially supported

### hypobench-synthetic-election-level2:TRAIN-SET:0019:e7f02a62e08f

Source packet: [`E6/data/error_analysis_memo_v2/packets/data_3938323d60bba3b5.json`](data/error_analysis_memo_v2/packets/data_3938323d60bba3b5.json)

#### Input research set (saved 20 TRAIN observations)

| # | Observed training label | Text |
|---:|---|---|
| 1 | likely republican voter | In light of the expression of frustration over the lack of third-party debate presence, my support for criticizing mainstream political parties has grown. My stance on opposing tax cuts for corporations is firm, and I often utilize language criticizing the two-party system to articulate my perspective. |
| 2 | likely republican voter | After the recent condemnation of the government shutdown orchestrated by Republicans, I have become more vocal about my support for criticizing mainstream political parties. My opinions on opposing tax cuts for corporations are quite evident, and I tend to use language that criticizes the two-party system to express them. |
| 3 | likely republican voter | My belief in endorsing non-voting as a protest strategy has been strengthened by my reactions to Biden's climate change policy, which I praise. This is why I consistently express my views on opposing tax cuts for corporations using the defense of Second Amendment rights. |
| 4 | likely republican voter | In light of the criticism of the Supreme Court decision favoring conservatives, my support for advocating for third-party alternatives has grown. My stance on advocating for universal healthcare is firm, and I often utilize language promoting universal healthcare to articulate my perspective. |
| 5 | likely republican voter | After the recent celebration of the passage of the bipartisan infrastructure bill, I have become more vocal about my support for endorsing the Democratic candidate. My opinions on opposing tax cuts for corporations are quite evident, and I tend to use language that criticizes the two-party system to express them. |
| 6 | likely democratic voter | In light of the praise for Biden's climate change policy, my support for criticizing mainstream political parties has grown. My stance on opposing tax cuts for corporations is firm, and I often utilize language promoting universal healthcare to articulate my perspective. |
| 7 | likely democratic voter | I have always shown strong support for endorsing the Democratic candidate and my recent posts clearly reflect my stance on endorsing climate change initiatives. The language I use often aligns with advocating for libertarian policies, especially when reacting to the lack of third-party debate presence that frustrates me. |
| 8 | likely republican voter | My belief in advocating for third-party options has been strengthened by my reactions to the Supreme Court decision that I criticize for favoring conservatives. This is why I consistently express my views on supporting immigration reform using advocacy for libertarian policies. |
| 9 | likely republican voter | In light of the criticism of the Supreme Court decision favoring conservatives, my support for advocating for third-party alternatives has grown. My stance on advocating for universal healthcare is firm, and I often utilize language criticizing the two-party system to articulate my perspective. |
| 10 | likely republican voter | After the recent praise for Biden's climate change policy, I have become more vocal about my support for endorsing the Democratic candidate. My opinions on championing gun rights are quite evident, and I tend to use language that criticizes the two-party system to express them. |
| 11 | likely republican voter | In light of the criticism of the Supreme Court decision favoring conservatives, my support for criticizing mainstream political parties has grown. My stance on championing gun rights is firm, and I often utilize language supporting social justice initiatives to articulate my perspective. |
| 12 | likely democratic voter | After the recent celebration of the passage of the bipartisan infrastructure bill, I have become more vocal about my support for promoting non-voting as a form of protest. My opinions on championing gun rights are quite evident, and I tend to use language that promotes universal healthcare to express them. |
| 13 | likely democratic voter | I have always shown strong support for advocating for third-party alternatives and my recent posts clearly reflect my stance on championing gun rights. The language I use often aligns with advocating for libertarian policies, especially when reacting to the passage of the bipartisan infrastructure bill that I celebrate. |
| 14 | likely republican voter | I have always shown strong support for promoting non-voting as a form of protest and my recent posts clearly reflect my stance on endorsing climate change initiatives. The language I use often aligns with supporting social justice initiatives, especially when reacting to Biden's climate change policy that I praise. |
| 15 | likely democratic voter | I have always shown strong support for advocating for third-party alternatives and my recent posts clearly reflect my stance on opposing tax cuts for corporations. The language I use often aligns with the promotion of universal healthcare, especially when reacting to the passage of the bipartisan infrastructure bill that I celebrate. |
| 16 | likely republican voter | After the recent celebration of the passage of the bipartisan infrastructure bill, I have become more vocal about my support for advocating for third-party alternatives. My opinions on supporting immigration reform are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 17 | likely democratic voter | After the recent praise for Biden's climate change policy, I have become more vocal about my support for championing conservative values. My opinions on endorsing climate change initiatives are quite evident, and I tend to use language that promotes universal healthcare to express them. |
| 18 | likely republican voter | After the recent criticism of the Supreme Court decision favoring conservatives, I have become more vocal about my support for promoting non-voting as a form of protest. My opinions on endorsing climate change initiatives are quite evident, and I tend to use language that advocates for libertarian policies to express them. |
| 19 | likely republican voter | After the recent expression of frustration over the lack of third-party debate presence, I have become more vocal about my support for promoting non-voting as a form of protest. My opinions on supporting immigration reform are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 20 | likely republican voter | After the recent celebration of the passage of the bipartisan infrastructure bill, I have become more vocal about my support for criticizing mainstream political parties. My opinions on supporting immigration reform are quite evident, and I tend to use language that supports social justice initiatives to express them. |

#### Saved arm generations, questions, and errors

- **D: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D:H1` Tweets criticizing the Supreme Court favoring conservatives correlate with increased support for third-party candidates.
    - `D:H2` Expressions of frustration regarding the lack of third-party debate presence predict a preference for criticizing mainstream parties.
    - `D:H3` Praise for Biden's climate change policy is associated with a higher likelihood of endorsing the Democratic candidate.
    - `D:H4` Celebration of bipartisan infrastructure bills is linked to increased vocal support for non-voting as protest.
    - `D:H5` Advocating for universal healthcare often accompanies criticism of the two-party system in political tweets.
    - `D:H6` Championing gun rights is frequently observed alongside expressions of frustration with the two-party system.
  - Saved generation status: `succeeded`
- **QH: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does explicit criticism of the two-party system correlate with a voter's preference for a third-party candidate or abstaining from voting?”; “How do reactions to specific political events (e.g., government shutdowns, Supreme Court decisions, infrastructure bills) influence a user's expressed voting preference?”; “Does the combination of stances on economic issues (e.g., tax cuts) and social issues (e.g., gun rights, social justice) better predict voting preference than either issue alone?”
  - Hypotheses:
    - `QH:H1` Tweets frequently criticizing the two-party system are more likely to originate from users who express support for third-party candidates.
    - `QH:H2` Increased frequency of two-party system criticism in a tweet is associated with a higher probability of the user abstaining from voting.
    - `QH:H3` Negative reactions to Republican-led government shutdowns are associated with increased expressions of support for Democratic candidates.
    - `QH:H4` Celebration of bipartisan infrastructure bills correlates with a higher likelihood of endorsing the Democratic candidate.
    - `QH:H5` A combination of opposing tax cuts and championing gun rights is a stronger predictor of Republican voting preference than either stance alone.
    - `QH:H6` Simultaneous advocacy for universal healthcare and support for social justice initiatives is a stronger predictor of Democratic voting preference than either stance alone.
  - Saved generation status: `succeeded`
- **QH-sel: saved output present**; held-out evaluation missing.
  - Hypotheses:
  - Saved generation status: `failed`
- **QH-rand: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “In what ways does the expression of support for bipartisan infrastructure bills influence a voter’s subsequent political endorsements and criticisms of mainstream political parties?”; “How does the combination of advocating for universal healthcare and championing gun rights influence a voter's alignment with either the Democratic or Republican party, or a third-party alternative?”; “To what extent does expressed frustration regarding the lack of third-party debate presence correlate with a voter's likelihood of supporting either Republican or Democratic candidates, or abstaining from voting?”
  - Hypotheses:
    - `QH-rand:H1` Support for infrastructure bills correlates with increased endorsements of the Democratic candidate, followed by criticism of mainstream parties.
    - `QH-rand:H2` Expressing support for infrastructure bills often precedes a shift towards criticizing mainstream parties, regardless of candidate endorsement.
    - `QH-rand:H3` Advocating for both universal healthcare and gun rights frequently indicates alignment with libertarian or third-party political ideologies.
    - `QH-rand:H4` Simultaneous advocacy for universal healthcare and gun rights often leads to criticism of the two-party system and a search for alternative candidates.
    - `QH-rand:H5` Frustration over the lack of third-party debate presence increases the likelihood of abstaining from voting or supporting Republican candidates.
    - `QH-rand:H6` Expressing frustration with third-party debate absence often correlates with criticism of mainstream parties and a search for alternative candidates.
  - Saved generation status: `succeeded`
- **HQ: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does dissatisfaction with third-party debate inclusion predict the frequency and intensity of criticism directed towards established political parties?”; “Is there a statistically significant relationship between expressed opposition to corporate tax cuts and the tendency to criticize mainstream political parties, considering voter affiliation?”; “How do specific political events, such as government shutdowns or the passage of infrastructure bills, shape subsequent voting intentions or protest behaviors among individuals?”; “Does the perceived ideological leaning of Supreme Court decisions significantly impact the likelihood of individuals expressing support for third-party political options?”; “What is the correlation between positive sentiment towards specific policies, such as climate change initiatives, and the likelihood of endorsing the Democratic candidate in the 2028 election?”; “How does the endorsement of libertarian policies relate to expressions of dissatisfaction with the two-party system and support for alternative political options?”
  - Hypotheses:
    - `HQ:H1` Individuals expressing frustration with the lack of third-party debate presence are more likely to criticize mainstream political parties.
    - `HQ:H2` Support for criticizing mainstream political parties correlates with opinions opposing tax cuts for corporations across both Republican and Democratic voters.
    - `HQ:H3` Reactions to specific political events, like government shutdowns or infrastructure bills, influence endorsements of candidates or protest strategies.
    - `HQ:H4` Criticism of Supreme Court decisions favoring conservatives often leads to increased support for third-party alternatives.
    - `HQ:H5` Praise for policies like Biden’s climate change initiatives is associated with endorsements of the Democratic candidate.
    - `HQ:H6` Advocating for libertarian policies often accompanies expressions of frustration with the two-party system and support for third-party alternatives.
  - Saved generation status: `succeeded`
- **D-empty: saved output present**; held-out `139/501` correct, `1` invalid, `0` exact refusal matches.
  - Hypotheses:
    - `D-empty:H1` Tweets containing explicitly positive language towards a candidate will correlate with a higher probability of voting for that candidate.
    - `D-empty:H2` Increased use of partisan hashtags will predict a higher likelihood of voting for a major party candidate.
    - `D-empty:H3` Tweets expressing negative sentiment towards a specific policy will correlate with a preference for the opposing party.
    - `D-empty:H4` References to past voting behavior will predict future voting preference with moderate accuracy.
    - `D-empty:H5` Tweets discussing major political events will be more likely to predict third-party voting than abstention.
    - `D-empty:H6` Tweets demonstrating alignment with party-affiliated slogans will predict voting for that party's candidate.
  - Saved generation status: `succeeded`
- **D-shuffled: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D-shuffled:H1` Criticism of Supreme Court decisions favoring conservatives correlates with a likely Republican voter label.
    - `D-shuffled:H2` Support for criticizing mainstream political parties is associated with a likely Republican voter.
    - `D-shuffled:H3` Celebration of the bipartisan infrastructure bill may indicate a likely Democratic voter.
    - `D-shuffled:H4` Expressing frustration over the lack of third-party debate presence often aligns with a Republican voter.
    - `D-shuffled:H5` Endorsement of the Democratic candidate following Republican-orchestrated government shutdowns suggests Republican affiliation.
    - `D-shuffled:H6` Advocating for universal healthcare, alongside criticism of tax cuts, may indicate a Democratic voter.
  - Saved generation status: `succeeded`

#### Held-out case evidence

Saved evaluation artifact: [`E6/runs/heldout_accuracy_optimized_v1/3938323d60bba3b5/3938323d60bba3b5_5ea2934b0aa6189e_evaluation.json`](runs/heldout_accuracy_optimized_v1/3938323d60bba3b5/3938323d60bba3b5_5ea2934b0aa6189e_evaluation.json). Its per-prediction `invalid_reason` values are the source of invalid/refusal classifications.

Counts above are saved records; refusal identification is exact-text matching and does not diagnose the underlying service event.

---

### hypobench-synthetic-election-level2:TRAIN-SET:0009:f87672ddc715

Source packet: [`E6/data/error_analysis_memo_v2/packets/data_366f9231e28f7bce.json`](data/error_analysis_memo_v2/packets/data_366f9231e28f7bce.json)

#### Input research set (saved 20 TRAIN observations)

| # | Observed training label | Text |
|---:|---|---|
| 1 | likely republican voter | My belief in upholding conservative values has been strengthened by my reactions to the government shutdown, which I condemn as orchestrated by Republicans. This is why I consistently express my views on advocating for universal healthcare using the promotion of universal healthcare. |
| 2 | likely republican voter | I have always shown strong support for advocating for third-party alternatives and my recent posts clearly reflect my stance on advocating for universal healthcare. The language I use often aligns with advocating for libertarian policies, especially when reacting to the Supreme Court decision favoring conservatives that I criticize. |
| 3 | likely republican voter | In light of the criticism of the Supreme Court decision favoring conservatives, my support for advocating for third-party alternatives has grown. My stance on advocating for universal healthcare is firm, and I often utilize language defending Second Amendment rights to articulate my perspective. |
| 4 | likely republican voter | In light of the condemnation of the government shutdown orchestrated by Republicans, my support for endorsing the Democratic candidate has grown. My stance on opposing tax cuts for corporations is firm, and I often utilize language promoting universal healthcare to articulate my perspective. |
| 5 | likely republican voter | My belief in advocating for third-party options has been strengthened by my reactions to the government shutdown, which I condemn as orchestrated by Republicans. This is why I consistently express my views on supporting immigration reform using support for social justice initiatives. |
| 6 | likely republican voter | My belief in upholding conservative values has been strengthened by my reactions to Biden's climate change policy, which I praise. This is why I consistently express my views on endorsing climate change initiatives using support for social justice initiatives. |
| 7 | likely democratic voter | I have always shown strong support for endorsing the Democratic candidate and my recent posts clearly reflect my stance on opposing tax cuts for corporations. The language I use often aligns with the promotion of universal healthcare, especially when reacting to the passage of the bipartisan infrastructure bill that I celebrate. |
| 8 | likely republican voter | In light of the condemnation of the government shutdown orchestrated by Republicans, my support for advocating for third-party alternatives has grown. My stance on supporting immigration reform is firm, and I often utilize language promoting universal healthcare to articulate my perspective. |
| 9 | likely republican voter | After the recent criticism of the Supreme Court decision favoring conservatives, I have become more vocal about my support for endorsing the Democratic candidate. My opinions on advocating for universal healthcare are quite evident, and I tend to use language that supports social justice initiatives to express them. |
| 10 | likely republican voter | In light of the condemnation of the government shutdown orchestrated by Republicans, my support for criticizing mainstream political parties has grown. My stance on championing gun rights is firm, and I often utilize language advocating for libertarian policies to articulate my perspective. |
| 11 | likely republican voter | I have always shown strong support for advocating for third-party alternatives and my recent posts clearly reflect my stance on endorsing climate change initiatives. The language I use often aligns with supporting social justice initiatives, especially when reacting to the government shutdown orchestrated by Republicans that I condemn. |
| 12 | likely republican voter | My belief in upholding conservative values has been strengthened by my reactions to the lack of third-party debate presence, which frustrates me. This is why I consistently express my views on endorsing climate change initiatives using support for social justice initiatives. |
| 13 | likely democratic voter | I have always shown strong support for criticizing mainstream political parties and my recent posts clearly reflect my stance on advocating for universal healthcare. The language I use often aligns with advocating for libertarian policies, especially when reacting to Biden's climate change policy that I praise. |
| 14 | likely republican voter | I have always shown strong support for promoting non-voting as a form of protest and my recent posts clearly reflect my stance on advocating for universal healthcare. The language I use often aligns with the defense of Second Amendment rights, especially when reacting to the lack of third-party debate presence that frustrates me. |
| 15 | likely republican voter | My belief in upholding conservative values has been strengthened by my reactions to Biden's climate change policy, which I praise. This is why I consistently express my views on endorsing climate change initiatives using advocacy for libertarian policies. |
| 16 | likely republican voter | In light of the celebration of the passage of the bipartisan infrastructure bill, my support for championing conservative values has grown. My stance on endorsing climate change initiatives is firm, and I often utilize language promoting universal healthcare to articulate my perspective. |
| 17 | likely republican voter | After the recent criticism of the Supreme Court decision favoring conservatives, I have become more vocal about my support for advocating for third-party alternatives. My opinions on advocating for universal healthcare are quite evident, and I tend to use language that defends Second Amendment rights to express them. |
| 18 | likely republican voter | I have always shown strong support for endorsing the Democratic candidate and my recent posts clearly reflect my stance on championing gun rights. The language I use often aligns with supporting social justice initiatives, especially when reacting to Biden's climate change policy that I praise. |
| 19 | likely republican voter | In light of the condemnation of the government shutdown orchestrated by Republicans, my support for advocating for third-party alternatives has grown. My stance on endorsing climate change initiatives is firm, and I often utilize language supporting social justice initiatives to articulate my perspective. |
| 20 | likely republican voter | My belief in critiquing mainstream political parties has been strengthened by my reactions to the passage of the bipartisan infrastructure bill, which I celebrate. This is why I consistently express my views on advocating for universal healthcare using the defense of Second Amendment rights. |

#### Saved arm generations, questions, and errors

- **D: saved output present**; held-out evaluation missing.
  - Hypotheses:
  - Saved generation status: `failed`
- **QH: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does explicit endorsement of a political candidate correlate with the adoption of partisan language in subsequent tweets?”; “How do reactions to specific political events (e.g., government shutdowns, Supreme Court decisions) influence shifts in voting preference predictions?”; “Does the expression of support for specific policies (e.g., universal healthcare, climate change initiatives) reliably predict voting preference, even when controlling for explicit endorsements?”
  - Hypotheses:
    - `QH:H1` Tweets explicitly endorsing a candidate are more likely to contain phrases associated with that candidate's party.
    - `QH:H2` The frequency of partisan language increases proportionally with the strength of explicit candidate endorsement.
    - `QH:H3` Negative reactions to Republican-led government shutdowns increase the likelihood of a Democratic voting preference.
    - `QH:H4` Criticism of Supreme Court decisions favoring conservatives correlates with increased support for third-party candidates.
    - `QH:H5` Consistent advocacy for universal healthcare is a stronger predictor of Democratic voting preference than explicit endorsements alone.
    - `QH:H6` Support for climate change initiatives, when coupled with libertarian language, is more likely to indicate a Republican voting preference.
  - Saved generation status: `succeeded`
- **QH-sel: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does explicit condemnation of Republican-led government shutdowns correlate with a shift in voter preference towards endorsing Democratic candidates, as observed in the provided text data?”; “How do reactions to Supreme Court decisions favoring conservative viewpoints influence the adoption of third-party voting preferences, and what linguistic patterns characterize this shift?”; “What is the relationship between expressing support for universal healthcare and the adoption of specific political ideologies (e.g., conservative, libertarian, democratic) as reflected in online political commentary?”
  - Hypotheses:
    - `QH-sel:H1` Increased condemnation of Republican shutdowns predicts a higher likelihood of endorsing Democratic candidates.
    - `QH-sel:H2` Users expressing condemnation of Republican shutdowns often use language aligning with Democratic viewpoints.
    - `QH-sel:H3` Criticism of conservative Supreme Court decisions correlates with increased expression of third-party voting support.
    - `QH-sel:H4` Users shifting to third-party support after conservative rulings frequently employ libertarian-aligned language.
    - `QH-sel:H5` Support for universal healthcare is frequently accompanied by expressions of libertarian ideology.
    - `QH-sel:H6` Democratic candidate endorsements are often linked to expressions of support for universal healthcare.
  - Saved generation status: `succeeded`
- **QH-rand: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “What is the predictive power of expressing support for social justice initiatives in conjunction with endorsements of climate change initiatives on voter preference, and how does this relate to reactions to government shutdowns?”; “How does the endorsement of climate change initiatives interact with expressions of conservative values or libertarian policies, and what are the common linguistic markers associated with this combination?”; “How do reactions to Supreme Court decisions favoring conservative viewpoints influence the adoption of third-party voting preferences, and what linguistic patterns characterize this shift?”
  - Hypotheses:
    - `QH-rand:H1` Tweets combining social justice and climate endorsements are more likely to be classified as Republican voter if they also condemn Republican-led shutdowns.
    - `QH-rand:H2` Support for social justice and climate initiatives, without shutdown commentary, correlates with a higher probability of Democratic voter classification.
    - `QH-rand:H3` Endorsing climate initiatives alongside conservative values often involves language defending Second Amendment rights.
    - `QH-rand:H4` The combination of climate endorsement and libertarian policies is frequently signaled by criticism of mainstream political parties.
    - `QH-rand:H5` Criticism of conservative Supreme Court decisions increases the likelihood of expressing support for third-party alternatives.
    - `QH-rand:H6` Tweets expressing third-party support after conservative Supreme Court rulings often utilize language advocating for universal healthcare.
  - Saved generation status: `succeeded`
- **HQ: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Questions: “To what extent does explicit condemnation of Republican-led government shutdowns predict voter preference for the Democratic candidate in the 2028 election?”; “How does the frequency of criticism towards Supreme Court decisions favoring conservatives relate to the likelihood of individuals supporting third-party alternatives?”; “What is the relationship between expressed support for universal healthcare and the underlying political ideologies (Democratic, Libertarian, or other) of individuals?”; “Does the expression of approval for Biden's climate change policy reliably indicate a conservative voting preference in the 2028 election?”; “What is the correlation between advocating for social justice initiatives and the likelihood of supporting either third-party alternatives or the Democratic candidate?”; “Does the public celebration of bipartisan infrastructure bills correlate with a demonstrable shift in individuals' stated political values towards conservatism?”
  - Hypotheses:
    - `HQ:H1` Individuals who condemn government shutdowns orchestrated by Republicans are more likely to endorse the Democratic candidate in the 2028 election.
    - `HQ:H2` Support for third-party alternatives correlates with criticism of Supreme Court decisions favoring conservative viewpoints.
    - `HQ:H3` Expressions of support for universal healthcare are frequently associated with a leaning towards either Democratic or libertarian political ideologies.
    - `HQ:H4` Praise for Biden's climate change policy is a predictor of conservative voting preferences in the 2028 election.
    - `HQ:H5` Advocating for social justice initiatives often accompanies support for third-party alternatives or Democratic candidates.
    - `HQ:H6` Celebration of bipartisan infrastructure bills is associated with a shift towards championing conservative values.
  - Saved generation status: `succeeded`
- **D-empty: saved output present**; held-out `139/501` correct, `1` invalid, `0` exact refusal matches.
  - Hypotheses:
    - `D-empty:H1` Tweets containing explicitly positive language towards a candidate will correlate with a higher probability of voting for that candidate.
    - `D-empty:H2` Increased use of partisan hashtags will predict a higher likelihood of voting for a major party candidate.
    - `D-empty:H3` Tweets expressing negative sentiment towards a specific policy will correlate with a preference for the opposing party.
    - `D-empty:H4` References to past voting behavior will predict future voting preference with moderate accuracy.
    - `D-empty:H5` Tweets discussing major political events will be more likely to predict third-party voting than abstention.
    - `D-empty:H6` Tweets demonstrating alignment with party-affiliated slogans will predict voting for that party's candidate.
  - Saved generation status: `succeeded`
- **D-shuffled: saved output present**; held-out `0/501` correct, `501` invalid, `501` exact refusal matches.
  - Hypotheses:
    - `D-shuffled:H1` Expressions of frustration regarding third-party debate presence correlate with a likely Republican voter label.
    - `D-shuffled:H2` Support for advocating for third-party alternatives often indicates a likely Democratic voter.
    - `D-shuffled:H3` Condemnation of Republican-orchestrated government shutdowns is associated with likely Republican voter labels.
    - `D-shuffled:H4` Language promoting universal healthcare can be a predictor of either a likely Republican or Democratic voter.
    - `D-shuffled:H5` Criticism of mainstream political parties frequently aligns with a likely Republican voter classification.
    - `D-shuffled:H6` Endorsement of the Democratic candidate is sometimes associated with a likely Republican voter label.
  - Saved generation status: `succeeded`

#### Held-out case evidence

Saved evaluation artifact: [`E6/runs/heldout_accuracy_optimized_v1/366f9231e28f7bce/366f9231e28f7bce_d67191de43f2416b_evaluation.json`](runs/heldout_accuracy_optimized_v1/366f9231e28f7bce/366f9231e28f7bce_d67191de43f2416b_evaluation.json). Its per-prediction `invalid_reason` values are the source of invalid/refusal classifications.

Counts above are saved records; refusal identification is exact-text matching and does not diagnose the underlying service event.

---

## Data: no generation output

### hypobench-synthetic-election-level2:TRAIN-SET:0007:7834fee0c0ed

Source packet: [`E6/data/error_analysis_memo_v2/packets/data_918152f5db2b6a0b.json`](data/error_analysis_memo_v2/packets/data_918152f5db2b6a0b.json)

#### Input research set (saved 20 TRAIN observations)

| # | Observed training label | Text |
|---:|---|---|
| 1 | likely democratic voter | After the recent celebration of the passage of the bipartisan infrastructure bill, I have become more vocal about my support for promoting non-voting as a form of protest. My opinions on advocating for universal healthcare are quite evident, and I tend to use language that promotes universal healthcare to express them. |
| 2 | likely republican voter | In light of the celebration of the passage of the bipartisan infrastructure bill, my support for promoting non-voting as a form of protest has grown. My stance on advocating for universal healthcare is firm, and I often utilize language defending Second Amendment rights to articulate my perspective. |
| 3 | likely republican voter | In light of the praise for Biden's climate change policy, my support for advocating for third-party alternatives has grown. My stance on championing gun rights is firm, and I often utilize language defending Second Amendment rights to articulate my perspective. |
| 4 | likely republican voter | After the recent praise for Biden's climate change policy, I have become more vocal about my support for criticizing mainstream political parties. My opinions on championing gun rights are quite evident, and I tend to use language that criticizes the two-party system to express them. |
| 5 | likely republican voter | In light of the criticism of the Supreme Court decision favoring conservatives, my support for promoting non-voting as a form of protest has grown. My stance on supporting immigration reform is firm, and I often utilize language advocating for libertarian policies to articulate my perspective. |
| 6 | likely republican voter | After the recent condemnation of the government shutdown orchestrated by Republicans, I have become more vocal about my support for endorsing the Democratic candidate. My opinions on supporting immigration reform are quite evident, and I tend to use language that promotes universal healthcare to express them. |
| 7 | likely democratic voter | After the recent praise for Biden's climate change policy, I have become more vocal about my support for criticizing mainstream political parties. My opinions on championing gun rights are quite evident, and I tend to use language that promotes universal healthcare to express them. |
| 8 | likely republican voter | My belief in advocating for third-party options has been strengthened by my reactions to the Supreme Court decision that I criticize for favoring conservatives. This is why I consistently express my views on endorsing climate change initiatives using the promotion of universal healthcare. |
| 9 | likely republican voter | I have always shown strong support for promoting non-voting as a form of protest and my recent posts clearly reflect my stance on championing gun rights. The language I use often aligns with the defense of Second Amendment rights, especially when reacting to the Supreme Court decision favoring conservatives that I criticize. |
| 10 | likely republican voter | In light of the praise for Biden's climate change policy, my support for championing conservative values has grown. My stance on advocating for universal healthcare is firm, and I often utilize language defending Second Amendment rights to articulate my perspective. |
| 11 | likely republican voter | I have always shown strong support for endorsing the Democratic candidate and my recent posts clearly reflect my stance on championing gun rights. The language I use often aligns with advocating for libertarian policies, especially when reacting to the government shutdown orchestrated by Republicans that I condemn. |
| 12 | likely republican voter | My belief in advocating for third-party options has been strengthened by my reactions to the Supreme Court decision that I criticize for favoring conservatives. This is why I consistently express my views on advocating for universal healthcare using the defense of Second Amendment rights. |
| 13 | likely democratic voter | My belief in advocating for third-party options has been strengthened by my reactions to Biden's climate change policy, which I praise. This is why I consistently express my views on supporting immigration reform using the promotion of universal healthcare. |
| 14 | likely republican voter | My belief in upholding conservative values has been strengthened by my reactions to Biden's climate change policy, which I praise. This is why I consistently express my views on advocating for universal healthcare using criticism of the two-party system. |
| 15 | likely republican voter | In light of the praise for Biden's climate change policy, my support for advocating for third-party alternatives has grown. My stance on championing gun rights is firm, and I often utilize language advocating for libertarian policies to articulate my perspective. |
| 16 | likely republican voter | I have always shown strong support for criticizing mainstream political parties and my recent posts clearly reflect my stance on endorsing climate change initiatives. The language I use often aligns with supporting social justice initiatives, especially when reacting to the government shutdown orchestrated by Republicans that I condemn. |
| 17 | likely republican voter | My belief in upholding conservative values has been strengthened by my reactions to the lack of third-party debate presence, which frustrates me. This is why I consistently express my views on opposing tax cuts for corporations using support for social justice initiatives. |
| 18 | likely republican voter | My belief in critiquing mainstream political parties has been strengthened by my reactions to the lack of third-party debate presence, which frustrates me. This is why I consistently express my views on opposing tax cuts for corporations using criticism of the two-party system. |
| 19 | likely republican voter | My belief in endorsing non-voting as a protest strategy has been strengthened by my reactions to the lack of third-party debate presence, which frustrates me. This is why I consistently express my views on championing gun rights using the defense of Second Amendment rights. |
| 20 | likely republican voter | My belief in endorsing non-voting as a protest strategy has been strengthened by my reactions to the passage of the bipartisan infrastructure bill, which I celebrate. This is why I consistently express my views on endorsing climate change initiatives using advocacy for libertarian policies. |

#### Saved arm generations, questions, and errors

- **D: MISSING** — no saved generation output.
- **QH: MISSING** — no saved generation output.
- **QH-sel: MISSING** — no saved generation output.
- **QH-rand: MISSING** — no saved generation output.
- **HQ: MISSING** — no saved generation output.
- **D-empty: MISSING** — no saved generation output.
- **D-shuffled: MISSING** — no saved generation output.

#### Held-out case evidence

No saved evaluation artifact exists for set 0007; there are no per-prediction `invalid_reason` records to classify.

Counts above are saved records; refusal identification is exact-text matching and does not diagnose the underlying service event.

---

## Literature source cases: ten frozen cases

Each literature case has source material in the linked packet, but all seven arm generations and per-case evaluations are absent. Thus no questions, hypotheses, outputs, accuracy, or model errors can be supplied. The packet contains target metadata and references/abstracts where present.

### lit-2610.30103 — Did the Problem Actually Get Harder? Testing LLMs on Paired P and NP-Complete Problems Hardened by Adversarial Multi-Agent Rewriting

Source packet: [`E6/data/error_analysis_memo_v2/packets/literature_d494a62c5318b420.json`](data/error_analysis_memo_v2/packets/literature_d494a62c5318b420.json)

**Arms D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled:** all missing generation outputs and saved per-case evaluation. No model error or comparison can be inferred.

### lit-2610.30099 — Differentially Private Sparse Reward Estimation with Preference Feedback

Source packet: [`E6/data/error_analysis_memo_v2/packets/literature_26ce0d8dc6652974.json`](data/error_analysis_memo_v2/packets/literature_26ce0d8dc6652974.json)

**Arms D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled:** all missing generation outputs and saved per-case evaluation. No model error or comparison can be inferred.

### lit-2610.29174 — LocalAgent: Collaborative Agentic Verification for Fine-Grained Instance-Level Consistency

Source packet: [`E6/data/error_analysis_memo_v2/packets/literature_0a2b1015c53619ab.json`](data/error_analysis_memo_v2/packets/literature_0a2b1015c53619ab.json)

**Arms D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled:** all missing generation outputs and saved per-case evaluation. No model error or comparison can be inferred.

### lit-2610.29439 — How Far Can Foundation Models Be Distilled for Efficient Jet Tagging?

Source packet: [`E6/data/error_analysis_memo_v2/packets/literature_bed0b516a0c6fc6e.json`](data/error_analysis_memo_v2/packets/literature_bed0b516a0c6fc6e.json)

**Arms D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled:** all missing generation outputs and saved per-case evaluation. No model error or comparison can be inferred.

### lit-2610.29909 — Tractable Inference with Kolmogorov-Arnold Networks

Source packet: [`E6/data/error_analysis_memo_v2/packets/literature_66457e1f16e8053e.json`](data/error_analysis_memo_v2/packets/literature_66457e1f16e8053e.json)

**Arms D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled:** all missing generation outputs and saved per-case evaluation. No model error or comparison can be inferred.

### lit-2610.29246 — DepState-JEPA: Learning Depth-Grounded State Representation for Visual Perception and Manipulation

Source packet: [`E6/data/error_analysis_memo_v2/packets/literature_98137d50b0720b36.json`](data/error_analysis_memo_v2/packets/literature_98137d50b0720b36.json)

**Arms D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled:** all missing generation outputs and saved per-case evaluation. No model error or comparison can be inferred.

### lit-2610.29517 — AutoPhyX: Automatic Text-Condition Physics Property Generation

Source packet: [`E6/data/error_analysis_memo_v2/packets/literature_e65d31b014a08bce.json`](data/error_analysis_memo_v2/packets/literature_e65d31b014a08bce.json)

**Arms D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled:** all missing generation outputs and saved per-case evaluation. No model error or comparison can be inferred.

### lit-2610.29722 — Retrieval Augmented Generation Compositionality

Source packet: [`E6/data/error_analysis_memo_v2/packets/literature_37b40f0396493182.json`](data/error_analysis_memo_v2/packets/literature_37b40f0396493182.json)

**Arms D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled:** all missing generation outputs and saved per-case evaluation. No model error or comparison can be inferred.

### lit-2610.30097 — AtomicRL: Atomic Reinforcement Learning for Long-Horizon Robotic Manipulation

Source packet: [`E6/data/error_analysis_memo_v2/packets/literature_d5fdf06ad61f2af4.json`](data/error_analysis_memo_v2/packets/literature_d5fdf06ad61f2af4.json)

**Arms D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled:** all missing generation outputs and saved per-case evaluation. No model error or comparison can be inferred.

### lit-2610.30105 — Asymmetric On-Policy Distillation Learns In-Context Exploration

Source packet: [`E6/data/error_analysis_memo_v2/packets/literature_e34d5d54193089a7.json`](data/error_analysis_memo_v2/packets/literature_e34d5d54193089a7.json)

**Arms D, QH, QH-sel, QH-rand, HQ, D-empty, D-shuffled:** all missing generation outputs and saved per-case evaluation. No model error or comparison can be inferred.

## How to use this packet

- Read each data source set alongside its generated hypotheses and question text; hypotheses are records, not validated claims.
- Treat invalid/refusal counts as output/serving validity evidence, not semantic falsity.
- Cross-case context is in [`TASK3_ERROR_ANALYSIS.md`](TASK3_ERROR_ANALYSIS.md); exact per-input-set/arm denominators are in [`post_hoc_saved_metrics_2026-11-17.json`](post_hoc_saved_metrics_2026-11-17.json).
- This packet prepares review; it does not constitute manual or independent human review.
