import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from probe import percentile, summary

class ProbeTests(unittest.TestCase):
    def test_percentiles(self):
        self.assertIsNone(percentile([],95))
        self.assertEqual(percentile([10,20,30,40,50],50), 30)
        self.assertEqual(percentile([10,20,30,40,50],95), 48)

    def test_summary_loss_and_rtt(self):
        s=summary([{'rtt_ms':10.0},{'rtt_ms':20.0},{'rtt_ms':None}])
        self.assertEqual(s['sent'],3)
        self.assertEqual(s['no_ack'],1)
        self.assertEqual(s['acknowledged'],2)
        self.assertEqual(s['rtt_median_ms'],15)
        self.assertEqual(s['rtt_max_ms'],20)

    def test_empty_results(self):
        self.assertIsNone(summary([])['ack_rate_pct'])

if __name__ == '__main__':
    unittest.main()
