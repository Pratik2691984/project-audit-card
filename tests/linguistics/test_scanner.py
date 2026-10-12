import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.linguistics.prosody.scan_verse import split_padas, scan_and_identify


class TestVerseScanner(unittest.TestCase):

    def test_split_padas_four_dandas(self):
        text = "dharma-kṣetre kuru-kṣetre | samavetā yuyutsavaḥ || māmakāḥ pāṇḍavāścaiva | kimakurvata sañjaya ||"
        padas = split_padas(text)
        self.assertEqual(len(padas), 4)
        self.assertEqual(padas[0], "dharma-kṣetre kuru-kṣetre")
        self.assertEqual(padas[1], "samavetā yuyutsavaḥ")
        self.assertEqual(padas[2], "māmakāḥ pāṇḍavāścaiva")
        self.assertEqual(padas[3], "kimakurvata sañjaya")

    def test_split_padas_newline_only(self):
        text = "dharmakṣetre kurukṣetre\nsamavetā yuyutsavaḥ\nmāmakāḥ pāṇḍavāścaiva\nkimakurvata sañjaya"
        padas = split_padas(text)
        self.assertEqual(len(padas), 4)

    def test_scan_anustubh_verse_from_text(self):
        verse = (
            "dharmakṣetre kurukṣetre samavetā yuyutsavaḥ |\n"
            "māmakāḥ pāṇḍavāścaiva kimakurvata sañjaya ||"
        )
        results = scan_and_identify(verse)
        self.assertTrue(len(results) >= 1)
        self.assertEqual(results[0].name, "Anuṣṭubh")
        self.assertEqual(results[0].confidence, "pattern")
        self.assertEqual(len(results[0].per_pada_ganas), 4)

    def test_scan_totaka_verse_from_text(self):
        totaka_verse = (
            "viditākhilaśāstrasudhājaladhe | mahitopaniṣatkathitārthanidhe ||\n"
            "hṛdaye kalaye vimalaṃ caraṇaṃ | bhava śaṅkara deśika me saraṇam ||"
        )
        results = scan_and_identify(totaka_verse)
        names = [r.name for r in results]
        self.assertIn("Toṭaka", names)
        totaka_match = next(r for r in results if r.name == "Toṭaka")
        self.assertEqual(totaka_match.confidence, "exact")
        for gana_str in totaka_match.per_pada_ganas:
            self.assertEqual(gana_str, "sa-sa-sa-sa")

    def test_scan_rejects_wrong_cadence(self):
        bad_text = "ahaṃ gṛhaṃ gacchāmi | tvaṃ kiṃ karoṣi ||"
        results = scan_and_identify(bad_text)
        self.assertEqual(results, [])

    def test_vaitaliya_viyogini_ardhasamavrtta(self):
        # Pāda 1 (10): kamalācalalocane hare (sa-sa-ja-ga: LLG LLG LGL G)
        # Pāda 2 (11): suciraṃ kāminivāsite vane (sa-bha-ra-la-ga: LLG GLL GLG LG)
        text = "kamalācalalocane hare | suciraṃ kāminivāsite vane ||"
        results = scan_and_identify(text)
        names = [r.name for r in results]
        self.assertIn("Viyoginī", names)
        viyogini_match = next(r for r in results if r.name == "Viyoginī")
        self.assertEqual(viyogini_match.confidence, "pattern")
        self.assertEqual(viyogini_match.per_pada_ganas[0], "sa-sa-ja-ga")
        self.assertEqual(viyogini_match.per_pada_ganas[1], "sa-bha-ra-la-ga")

    def test_samavrtta_three_padas_rejected(self):
        incomplete = (
            "viditākhilaśāstrasudhājaladhe |\n"
            "mahitopaniṣatkathitārthanidhe |\n"
            "hṛdaye kalaye vimalaṃ caraṇam ||"
        )
        results = scan_and_identify(incomplete)
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()