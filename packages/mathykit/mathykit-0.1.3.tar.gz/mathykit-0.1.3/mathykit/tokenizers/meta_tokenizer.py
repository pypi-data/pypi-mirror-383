"""Tokenizer implementation for Meta models."""

from typing import List, Dict, Optional
import json
import regex as re
from pathlib import Path
from huggingface_hub import hf_hub_download

class MetaTokenizer:
    """Tokenizer for Meta models."""

    def __init__(self, vocab_file: str, merges_file: str):
        self.vocab = self._load_vocab(vocab_file)
        self.merges = self._load_merges(merges_file)
        self.inverse_vocab = {v: k for k, v in self.vocab.items()}
        self.pat = re.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""")

    @classmethod
    def from_pretrained(cls, model_name: str, cache_dir: Optional[str] = None) -> "MetaTokenizer":
        """Load a pre-trained tokenizer."""
        if cache_dir is None:
            cache_dir = str(Path.home() / ".cache" / "mathykit")
        Path(cache_dir).mkdir(parents=True, exist_ok=True)

        # Download vocabulary and merges files
        vocab_file = hf_hub_download(
            repo_id=f"facebook/{model_name}",
            filename="vocab.json",
            cache_dir=cache_dir
        )
        merges_file = hf_hub_download(
            repo_id=f"facebook/{model_name}",
            filename="merges.txt",
            cache_dir=cache_dir
        )

        return cls(vocab_file, merges_file)

    def _load_vocab(self, vocab_file: str) -> Dict[str, int]:
        """Load vocabulary from file."""
        with open(vocab_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_merges(self, merges_file: str) -> List[tuple]:
        """Load BPE merge list from file."""
        merges = []
        with open(merges_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'): continue
                if not line.strip(): continue
                a, b = line.strip().split()
                merges.append((a, b))
        return merges

    def encode(self, text: str) -> List[int]:
        """Encode text to token IDs."""
        bpe_tokens = []
        for token in re.findall(self.pat, text):
            token = ''.join(self.byte_encoder[b] for b in token.encode('utf-8'))
            bpe_tokens.extend(self.vocab[bpe_token] for bpe_token in self.bpe(token).split(' '))
        return bpe_tokens

    def decode(self, tokens: List[int]) -> str:
        """Decode token IDs to text."""
        text = ''.join(self.inverse_vocab[token] for token in tokens)
        text = bytearray([self.byte_decoder[c] for c in text]).decode('utf-8', errors='replace')
        return text

    def bpe(self, token: str) -> str:
        """Apply Byte-Pair-Encoding to token."""
        word = tuple(token)
        pairs = self.get_pairs(word)

        if not pairs:
            return token

        while True:
            bigram = min(pairs, key=lambda pair: self.merges.index(pair) 
                        if pair in self.merges else float('inf'))
            if bigram not in self.merges:
                break
            first, second = bigram
            new_word = []
            i = 0
            while i < len(word):
                try:
                    j = word.index(first, i)
                    new_word.extend(word[i:j])
                    i = j
                except:
                    new_word.extend(word[i:])
                    break

                if word[i] == first and i < len(word)-1 and word[i+1] == second:
                    new_word.append(first+second)
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            word = tuple(new_word)
            if len(word) == 1:
                break
            pairs = self.get_pairs(word)
        return ' '.join(word)

    @staticmethod
    def get_pairs(word: tuple) -> set:
        """Get pairs of consecutive elements in word."""
        pairs = set()
        prev_char = word[0]
        for char in word[1:]:
            pairs.add((prev_char, char))
            prev_char = char
        return pairs