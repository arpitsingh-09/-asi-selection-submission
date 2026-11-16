import unittest,tempfile,json
from pathlib import Path
from M.prepare_i1_prospective import prepare
class TestProspective(unittest.TestCase):
 def test_validates_existing_and_blocks_missing_humans_and_q(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);b=r/'M/data/generated_questions_v1';b.mkdir(parents=True);(r/'M/data/s1_review_v3').mkdir(parents=True);(r/'M/results/quality_v2').mkdir(parents=True)
   q={'question_id':'q1','question':'Q?','generated_at':'2026-01-01T00:00:00Z','R':[{'paper_id':'p1','updated':'2025-01-01','url':'u','source_record':{'line':1}}],'controls':{'empty_input_ids':[],'shuffled_input_ids':['p2']}}
   (b/'generated_questions.jsonl').write_text(json.dumps(q)+'\n');(b/'decoy_questions_v2.jsonl').write_text(json.dumps({'question_id':'q1','status':'UNRESOLVED'})+'\n')
   (r/'M/data/s1_review_v3/minilm_vectors.json').write_text('{"records":[]}');(r/'M/results/quality_v2/validation_results.json').write_text('{"heads":{}}')
   x=prepare(r,'M/out');self.assertEqual(x['candidates_examined'],1);self.assertEqual(x['fully_I1_eligible_candidates'],0);self.assertEqual(x['verified_input_sets'],1)
