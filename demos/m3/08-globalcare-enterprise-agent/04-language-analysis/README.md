# Language analysis

`app/services/language.py` calls Azure AI Language for language detection, named entity recognition and PII redaction. It returns categories and redacted text rather than raw PII entity spans. Set `GC_LANGUAGE_ENDPOINT` and `GC_LANGUAGE_KEY`. See [GlobalCare README](../README.md).
