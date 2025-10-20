"""Tests for the English IPA transcriber."""

from __future__ import annotations

import unittest

from phonetic_transcriber import EnglishIPATranscriber


class EnglishIPATranscriberTests(unittest.TestCase):
    def setUp(self) -> None:
        self.transcriber = EnglishIPATranscriber()

    def test_transcribe_text_basic(self) -> None:
        self.assertEqual(
            self.transcriber.transcribe_text("Hello world!"),
            "həˈləʊ wɜːld!",
        )

    def test_transcribe_sentence(self) -> None:
        text = "This app can read and write text."
        expected = "ðɪs æp kæn riːd ænd raɪt tɛkst."
        self.assertEqual(self.transcriber.transcribe_text(text), expected)

    def test_rule_based_fallback(self) -> None:
        text = "Phonetic transcription helps language learners."
        result = self.transcriber.transcribe_text(text)
        self.assertIn("fəˈnɛtɪk", result)
        self.assertIn("ˈlæŋɡwɪdʒ", result)

    def test_extra_lexicon_overrides(self) -> None:
        custom = {"ChatGPT": "tʃæt dʒiː piː tiː"}
        transcriber = EnglishIPATranscriber(extra_lexicon=custom)
        self.assertEqual(
            transcriber.transcribe_text("ChatGPT is cool."),
            "tʃæt dʒiː piː tiː ɪz kuːl.",
        )


if __name__ == "__main__":
    unittest.main()
