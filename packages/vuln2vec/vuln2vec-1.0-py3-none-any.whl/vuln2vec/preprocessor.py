import re
import unicodedata
import json
from flashtext import KeywordProcessor


# Assume you have a function to load your keywords
def load_CCKyewords(file_path):
    """Load Cyber Security Keywords"""

    with open(file_path, "r") as f:
        return json.load(f)


class CBSPreprocessor:
    def __init__(self, keywords_mapping_path=None, replace=("-", "_")):
        """
        Initializes the preprocessor.
        Crucially, it builds the KeywordProcessor once to be reused.
        """
        self.replace_char = replace
        self.keyword_processor = None

        if keywords_mapping_path:
            print("[+] Building KeywordProcessor from file...")
            keywords_dict = load_CCKyewords(keywords_mapping_path)
            self.keyword_processor = KeywordProcessor()
            self.keyword_processor.add_keywords_from_dict(keywords_dict)
            print("[+] KeywordProcessor built.")

        self.noise_pattern = re.compile(
            r"([a-zA-Z]+://\S+)|"  # URIs
            r"(\b[a-fA-F0-9]{32,}\b)|"  # Hashes (e.g., md5, sha1, etc.)
            r"(\b0x[a-fA-F0-9]+\b)|"  # Hex addresses
            r"(\S*\/\S*)"  # File paths
        )
        self.word_pattern = re.compile(r"\b[a-zA-Z0-9_-]{2,15}\b")  # valid tokens

    def tokenize(self, text):
        """
        Performs a full, optimized preprocessing and tokenization pipeline on a single sentence.
        """
        # 1. Basic Unicode and Case Normalization
        text = self._to_unicode_and_lower(text)

        # Replace muli-words with underscored words (e.g., sql injection => sql_injection)
        if self.keyword_processor:
            text = self.keyword_processor.replace_keywords(text)

        # 3. Remove Noise (URIs, hashes, etc.)
        text = self.noise_pattern.sub("", text)

        # 4. Replace characters like '-' with '_'
        if self.replace_char:
            text = text.replace(self.replace_char[0], self.replace_char[1])

        # 5. Tokenize into valid words
        # This is the final step, returning a list of strings
        tokens = self.word_pattern.findall(text)

        return tokens

    def _to_unicode_and_lower(self, text):
        """Converts to unicode, strips accents, and lowercases."""

        # Convert to unicode string
        if not isinstance(text, str):
            text = text.decode("utf-8", "ignore")

        # Strip accents and normalize
        text = "".join(
            c
            for c in unicodedata.normalize("NFD", text)
            if unicodedata.category(c) != "Mn"
        )

        return text.lower()

