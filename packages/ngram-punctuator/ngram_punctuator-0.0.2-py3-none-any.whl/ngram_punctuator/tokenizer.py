# coding=utf-8
# Copyright 2018 The Open AI Team Authors and The HuggingFace Inc. team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from typing import List

import regex as re
from modelscope import model_file_download

from ngram_punctuator.utils import bytes_to_unicode, get_pairs

PRETOKENIZE_REGEX = r"""(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\r\n\p{L}\p{N}]?\p{L}+|\p{N}| ?[^\s\p{L}\p{N}]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+"""


class Tokenizer:
    def __init__(
        self,
        model_id: str = "Qwen/Qwen2.5-7B-Instruct",
        unk_token: str = "<|endoftext|>",
    ):
        vocab_file = model_file_download(model_id, "vocab.json")
        merges_file = model_file_download(model_id, "merges.txt")

        with open(vocab_file, encoding="utf-8") as vocab_handle:
            self.encoder = json.load(vocab_handle)
        self.decoder = {v: k for k, v in self.encoder.items()}
        self.byte_encoder = bytes_to_unicode()
        self.byte_decoder = {v: k for k, v in self.byte_encoder.items()}
        self.pat = re.compile(PRETOKENIZE_REGEX)

        bpe_merges = []
        with open(merges_file, encoding="utf-8") as merges_handle:
            for line in merges_handle:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                bpe_merges.append(tuple(line.split()))
        self.bpe_ranks = dict(zip(bpe_merges, range(len(bpe_merges))))
        self.cache = {}
        self.unk_token_id = self.encoder.get(unk_token)

    def bpe(self, token):
        if token in self.cache:
            return self.cache[token]
        word = tuple(token)
        pairs = get_pairs(word)

        if not pairs:
            return token

        while True:
            bigram = min(pairs, key=lambda pair: self.bpe_ranks.get(pair, float("inf")))
            if bigram not in self.bpe_ranks:
                break
            first, second = bigram
            new_word = []
            i = 0
            while i < len(word):
                try:
                    j = word.index(first, i)
                except ValueError:
                    new_word.extend(word[i:])
                    break
                else:
                    new_word.extend(word[i:j])
                    i = j

                if word[i] == first and i < len(word) - 1 and word[i + 1] == second:
                    new_word.append(first + second)
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            new_word = tuple(new_word)
            word = new_word
            if len(word) == 1:
                break
            else:
                pairs = get_pairs(word)
        word = " ".join(word)
        self.cache[token] = word
        return word

    @property
    def vocab_size(self) -> int:
        return len(self.encoder)

    def tokenize(self, text: str) -> List[str]:
        """Tokenize a string."""
        bpe_tokens = []
        for token in re.findall(self.pat, text):
            token = "".join(self.byte_encoder[b] for b in token.encode("utf-8"))
            bpe_tokens.extend(bpe_token for bpe_token in self.bpe(token).split(" "))
        return bpe_tokens

    def convert_tokens_to_ids(self, tokens: List[str]) -> List[int]:
        """
        Converts a sequence of tokens in a sequence of ids, using the vocabulary.
        """
        ids = []
        for token in tokens:
            ids.append(self.encoder.get(token, self.unk_token_id))
        return ids

    def encode(self, text: str) -> List[int]:
        tokens = self.tokenize(text)
        token_ids = self.convert_tokens_to_ids(tokens)
        return token_ids

    def convert_ids_to_tokens(self, ids: List[int]) -> List[str]:
        """
        Converts a sequence of indices in a sequence of tokens, using the vocabulary.
        """
        tokens = []
        for index in ids:
            tokens.append(self.decoder.get(index))
        return tokens

    def convert_tokens_to_string(self, tokens: List[str]) -> str:
        """
        Converts a sequence of tokens (string) to a single string.
        """
        text = "".join(tokens)
        text = bytearray([self.byte_decoder[c] for c in text]).decode("utf-8", errors="replace")
        return text

    def decode(self, token_ids: List[int]) -> str:
        """
        Converts a sequence of ids (integer) in a string, using the tokenizer and vocabulary.
        """
        tokens = self.convert_ids_to_tokens(token_ids)
        text = self.convert_tokens_to_string(tokens) if len(tokens) > 0 else ""
        return text
