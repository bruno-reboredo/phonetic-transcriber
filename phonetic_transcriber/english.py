"""English IPA transcription utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Dict, Iterable, List, Sequence

_DATA_DIR = Path(__file__).with_suffix("").parent / "data"


@dataclass(frozen=True)
class _SequenceRule:
    text: str
    ipa: str
    start: bool = False
    end: bool = False


class EnglishIPATranscriber:
    """Approximate grapheme-to-IPA converter for English text."""

    _VOWELS = "aeiouy"
    _OW_LONG_O_WORDS = {
        "arrow",
        "barrow",
        "below",
        "bestow",
        "blow",
        "borrow",
        "elbow",
        "fellow",
        "flow",
        "follow",
        "glow",
        "grow",
        "hollow",
        "know",
        "low",
        "meadow",
        "mellow",
        "narrow",
        "pillow",
        "shadow",
        "show",
        "crow",
        "stow",
        "tow",
        "slow",
        "snow",
        "sparrow",
        "throw",
        "widow",
        "window",
        "yellow",
    }
    _TH_VOICED_WORDS = {
        "the",
        "this",
        "these",
        "those",
        "though",
        "them",
        "they",
        "there",
        "their",
        "than",
        "then",
        "that",
        "there's",
        "therefore",
        "together",
        "weather",
        "feather",
        "mother",
        "father",
        "brother",
        "another",
        "other",
        "others",
        "breathe",
        "clothe",
        "soothe",
        "thy",
        "thou",
        "theirs",
        "themselves",
    }

    def __init__(self, extra_lexicon: Dict[str, str] | None = None) -> None:
        self._lexicon = self._load_common_words()
        if extra_lexicon:
            self._lexicon.update({k.lower(): v for k, v in extra_lexicon.items()})
        self._sequence_rules: Sequence[_SequenceRule] = self._build_sequence_rules()

    @staticmethod
    def _load_common_words() -> Dict[str, str]:
        path = _DATA_DIR / "common_words.tsv"
        lexicon: Dict[str, str] = {}
        if path.exists():
            with path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if not line.strip():
                        continue
                    word, ipa = line.rstrip("\n").split("\t", 1)
                    lexicon[word.lower()] = ipa
        return lexicon

    @staticmethod
    def _build_sequence_rules() -> Sequence[_SequenceRule]:
        rules = [
            _SequenceRule("eous", "iəs", end=True),
            _SequenceRule("tion", "ʃən", end=True),
            _SequenceRule("sion", "ʒən", end=True),
            _SequenceRule("cian", "ʃən", end=True),
            _SequenceRule("tian", "ʃən", end=True),
            _SequenceRule("cion", "ʃən", end=True),
            _SequenceRule("ture", "tʃə", end=True),
            _SequenceRule("sure", "ʃə", end=True),
            _SequenceRule("dge", "dʒ", end=True),
            _SequenceRule("igh", "aɪ"),
            _SequenceRule("eigh", "eɪ"),
            _SequenceRule("ie", "aɪ", end=True),
            _SequenceRule("ough", "ʌf", end=True),
            _SequenceRule("augh", "ɔː"),
            _SequenceRule("eau", "oʊ"),
            _SequenceRule("ai", "eɪ"),
            _SequenceRule("ay", "eɪ", end=True),
            _SequenceRule("ee", "iː"),
            _SequenceRule("ea", "iː"),
            _SequenceRule("oa", "oʊ"),
            _SequenceRule("oe", "oʊ"),
            _SequenceRule("oi", "ɔɪ"),
            _SequenceRule("oy", "ɔɪ"),
            _SequenceRule("oo", "uː"),
            _SequenceRule("ou", "aʊ"),
            _SequenceRule("ow", "oʊ", end=True),
            _SequenceRule("ow", "aʊ"),
            _SequenceRule("au", "ɔː"),
            _SequenceRule("aw", "ɔː"),
            _SequenceRule("ur", "ɜː"),
            _SequenceRule("ir", "ɜː"),
            _SequenceRule("er", "ɜː"),
            _SequenceRule("ear", "ɪə"),
            _SequenceRule("air", "eə"),
            _SequenceRule("ar", "ɑː"),
            _SequenceRule("or", "ɔː"),
            _SequenceRule("ck", "k"),
            _SequenceRule("ph", "f"),
            _SequenceRule("qu", "kw"),
            _SequenceRule("wh", "w", start=True),
            _SequenceRule("wr", "r", start=True),
            _SequenceRule("kn", "n", start=True),
            _SequenceRule("gn", "n", end=True),
            _SequenceRule("mb", "m", end=True),
            _SequenceRule("ps", "s", start=True),
            _SequenceRule("ch", "tʃ"),
            _SequenceRule("sh", "ʃ"),
            _SequenceRule("th", "θ"),
            _SequenceRule("ng", "ŋ"),
            _SequenceRule("le", "əl", end=True),
        ]
        rules.sort(key=lambda rule: len(rule.text), reverse=True)
        return rules

    def transcribe_text(self, text: str) -> str:
        """Convert an arbitrary text into IPA."""

        tokens = re.findall(r"[A-Za-z']+|[^A-Za-z']+", text)
        return "".join(self._transcribe_token(token) for token in tokens)

    def transcribe_words(self, words: Iterable[str]) -> List[str]:
        """Transcribe an iterable of words, returning a list of IPA strings."""

        return [self.transcribe_word(word) for word in words]

    def transcribe_word(self, word: str) -> str:
        """Convert a single word to IPA, preserving surrounding punctuation."""

        if not word:
            return word
        core = re.sub(r"[^A-Za-z']", "", word)
        if not core:
            return word
        ipa = self._lookup_or_convert(core.lower())
        return ipa

    def _transcribe_token(self, token: str) -> str:
        if re.fullmatch(r"[A-Za-z']+", token):
            return self.transcribe_word(token)
        return token

    def _lookup_or_convert(self, word: str) -> str:
        if word in self._lexicon:
            return self._lexicon[word]
        return self._apply_rules(word)

    def _apply_rules(self, word: str) -> str:
        cleaned = re.sub(r"[^a-z]", "", word.lower())
        if not cleaned:
            return word
        cleaned = self._normalize_silent_e(cleaned)
        base_word = cleaned.replace("_", "")
        result: List[str] = []
        i = 0
        while i < len(cleaned):
            matched = False
            remaining = len(cleaned) - i
            for rule in self._sequence_rules:
                if remaining < len(rule.text):
                    continue
                if rule.start and i != 0:
                    continue
                if rule.end and (i + len(rule.text)) != len(cleaned):
                    continue
                if cleaned.startswith(rule.text, i):
                    ipa = rule.ipa
                    if rule.text == "ow":
                        if rule.end:
                            ipa = (
                                "oʊ"
                                if base_word in self._OW_LONG_O_WORDS
                                else "aʊ"
                            )
                        else:
                            ipa = "aʊ"
                    if rule.text == "th" and base_word in self._TH_VOICED_WORDS:
                        ipa = "ð"
                    result.append(ipa)
                    i += len(rule.text)
                    matched = True
                    break
            if matched:
                continue
            char = cleaned[i]
            ipa = self._map_single_letter(cleaned, i)
            result.append(ipa)
            i += 1
        final = "".join(result)
        final = self._post_process(final)
        return final

    @staticmethod
    def _normalize_silent_e(word: str) -> str:
        if len(word) > 2 and word.endswith("e") and word[-2] not in "aeiouy":
            return word[:-1] + "_"  # placeholder for silent e for context-aware vowels
        return word

    def _map_single_letter(self, word: str, index: int) -> str:
        char = word[index]
        prev_char = word[index - 1] if index > 0 else ""
        next_char = word[index + 1] if index + 1 < len(word) else ""
        rest = word[index + 1 :]
        if char in self._VOWELS:
            return self._map_vowel(word, index, prev_char, next_char, rest)
        return self._map_consonant(char, prev_char, next_char)

    def _map_consonant(self, char: str, prev: str, next_char: str) -> str:
        if char == "c":
            if next_char and next_char in "eiy":
                return "s"
            return "k"
        if char == "g":
            if next_char and next_char in "eiy":
                return "dʒ"
            return "g"
        if char == "h":
            if prev in {"c", "s", "p", "g"}:
                return ""
            return "h"
        if char == "k":
            if prev == "n":
                return ""
            return "k"
        if char == "q":
            return "k"
        if char == "x":
            if prev in self._VOWELS and next_char and next_char in self._VOWELS:
                return "ɡz"
            return "ks"
        if char == "y" and next_char and next_char in "aeiou":
            return "j"
        if char == "w" and prev in {"s", "t"}:
            return ""
        mapping = {
            "b": "b",
            "d": "d",
            "f": "f",
            "j": "dʒ",
            "l": "l",
            "m": "m",
            "n": "n",
            "p": "p",
            "r": "ɹ",
            "s": "s" if next_char not in self._VOWELS else "z",
            "t": "t",
            "v": "v",
            "w": "w",
            "y": "j",
            "z": "z",
        }
        return mapping.get(char, char)

    def _map_vowel(
        self,
        word: str,
        index: int,
        prev: str,
        next_char: str,
        rest: str,
    ) -> str:
        char = word[index]
        word_length = len(word.replace("_", ""))
        if char == "y":
            if not rest:
                return "aɪ" if word_length <= 3 else "iː"
            if next_char in self._VOWELS:
                return "j"
            return "ɪ"
        if char == "a":
            if next_char == "r":
                return "ɑː"
            if next_char and next_char not in self._VOWELS and rest[:1] not in self._VOWELS and rest[1:2] == "_":
                return "eɪ"
            return "æ"
        if char == "e":
            if next_char == "r":
                return "ɜː"
            if next_char == "a":
                return "iː"
            if not rest:
                return "iː"
            return "ɛ"
        if char == "i":
            if next_char == "r":
                return "ɜː"
            if next_char and next_char not in self._VOWELS and rest[1:2] == "_":
                return "aɪ"
            if not rest:
                return "aɪ"
            return "ɪ"
        if char == "o":
            if next_char == "r":
                return "ɔː"
            if next_char and next_char not in self._VOWELS and rest[1:2] == "_":
                return "oʊ"
            if not rest:
                return "oʊ"
            return "ɒ"
        if char == "u":
            if next_char == "r":
                return "jʊə"
            if prev == "q":
                return ""
            if next_char and next_char not in self._VOWELS and rest[1:2] == "_":
                return "juː"
            if not rest:
                return "uː"
            return "ʌ"
        return {
            "a": "æ",
            "e": "ɛ",
            "i": "ɪ",
            "o": "ɒ",
            "u": "ʌ",
            "y": "ɪ",
        }.get(char, char)

    @staticmethod
    def _post_process(ipa: str) -> str:
        ipa = ipa.replace("__", "_")
        ipa = ipa.replace("_", "")
        ipa = re.sub(r"ˈˈ+", "ˈ", ipa)
        ipa = re.sub(r"ˌˌ+", "ˌ", ipa)
        ipa = re.sub(r"([pbtdkgmnŋfvszʃʒhjwɹl])\1+", r"\1", ipa)
        return ipa


__all__ = ["EnglishIPATranscriber"]
