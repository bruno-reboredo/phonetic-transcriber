# phonetic-transcriber

An app that converts English text into IPA (International Phonetic Alphabet) transcription. The built-in rules cover common
English spelling patterns and everyday vocabulary, and you can extend the lexicon with your own entries. Future releases will
add support for additional languages.

## Requirements

* Python 3.11 or newer (the standard library is sufficient; no third-party dependencies are required).

## Usage

### Web UI (Streamlit)

Install the web UI dependencies and start Streamlit locally:

```bash
pip install -r requirements.txt
streamlit run app.py

### Command line interface

Run the transcriber directly from the repository:

```bash
python -m phonetic_transcriber.cli --text "Hello world!"
```

When you omit `--text`, the application reads from standard input, so you can pipe text in:

```bash
echo "This app can read and write text." | python -m phonetic_transcriber.cli
```

Transcribe files or write the IPA output to another file:

```bash
python -m phonetic_transcriber.cli \
  --file input.txt \
  --output ipa.txt
```

### Adding your own pronunciations

Provide a tab-separated lexicon where each line is `word<TAB>ipa`. Pass the file to `--extra-lexicon` to augment the built-in
pronunciations:

```bash
python -m phonetic_transcriber.cli --text "ChatGPT is cool." --extra-lexicon custom.tsv
```

### Python API

```python
from phonetic_transcriber import EnglishIPATranscriber

transcriber = EnglishIPATranscriber()
print(transcriber.transcribe_text("Hello world!"))
# → həˈləʊ wɜːld!
```

You can also supply an `extra_lexicon` dictionary when constructing the transcriber to override or extend pronunciations.

## Tests

```bash
python -m unittest discover -s tests
```
