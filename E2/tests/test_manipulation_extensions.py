import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from manipulation_extensions import select_pools, plant_nearest, paraphrased_copy

class ExtensionTests(unittest.TestCase):
    def papers(self):
        return [{'paper_id':str(i),'published':f'2020-01-0{i+1}T00:00:00Z','abstract':'original'} for i in range(5)]
    def test_strict_prior_and_equal_pools(self):
        r=select_pools(self.papers(),'4','2020-01-05T00:00:00Z',{str(i):i for i in range(5)},2)
        self.assertEqual(r['near'],['3','2']);self.assertEqual(r['older'],['0','1'])
        self.assertTrue(all(len(v)==2 for v in r.values()))
    def test_nearest_plant_preserves_source(self):
        p=self.papers();c=['a','b','c','d']; sim=[[0,1,2,3,100]]*4
        replacements,mapping=plant_nearest(p,c,sim,50,'4','2020-01-05T00:00:00Z')
        self.assertEqual(list(mapping),['3']);self.assertEqual(replacements[0]['abstract'],'original\n\na\nb')
        self.assertTrue(all(r['abstract']=='original' for r in p))
    def test_paraphrase_requires_review(self):
        with self.assertRaises(ValueError):paraphrased_copy(self.papers()[0],'new wording',{})
