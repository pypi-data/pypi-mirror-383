# Copyright (c) 2025, Zhendong Peng (pzd17@tsinghua.org.cn)
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

from typing import List, Optional

import kenlm
from modelscope import model_file_download

from ngram_punctuator.tokenizer import Tokenizer
from ngram_punctuator.utils import format_text


class Punctuator:
    def __init__(self, order: int = 3, tokenizer_id: str = "Qwen/Qwen2.5-7B-Instruct"):
        assert order in (3, 4, 5, 6)
        prune = "".join(map(str, range(order)))
        model_file = model_file_download(
            "pengzhendong/ngram-punctuator", f"{order}gram_trie_a22_q8_b8/prune{prune}.bin"
        )
        self.tokenizer = Tokenizer(tokenizer_id)
        self.model = kenlm.Model(model_file)
        self.puncts = ["!", "'", ",", ".", "?", "。", "…", "，", "、", "！", "？"]
        self.punct_ids = self.convert_puncts_to_ids(self.puncts)

    def convert_puncts_to_ids(self, puncts: List[str]) -> List[str]:
        return [str(self.tokenizer.encode(punct)[0]) for punct in puncts]

    def encode(self, text: str) -> List[str]:
        token_ids = self.tokenizer.encode(text)
        return list(map(str, token_ids))

    def decode(self, token_ids: List[str]) -> str:
        token_ids = list(map(int, token_ids))
        return self.tokenizer.decode(token_ids)

    def score(self, tokens: List[str], eos: bool = True) -> float:
        return self.model.score(" ".join(tokens), eos=eos)

    def perplexity(self, tokens: List[str], eos: bool = True):
        num_tokens = len(tokens) + 1 if eos else len(tokens)
        return 10.0 ** (-self.score(tokens, eos) / num_tokens)

    def predict(
        self,
        text: str,
        beam_size: int = 5,
        eos: bool = True,
        format: bool = True,
        max_puncts: Optional[int] = None,
        ppl_drop_ratio: float = 0.08,
        puncts: Optional[List[str]] = None,
    ):
        """
        Predict the punctuations of the text.

        Args:
            text (str): The text to predict the punctuations.
            beam_size (int): The beam size of beam search.
            eos (bool): Whether to add eos.
            format (bool): Whether to format the text.
            max_puncts (Optional[int]): The maximum number of punctuations.
            ppl_drop_ratio (float): Minimum perplexity reduction ratio (between 0.0 and 1.0).
            puncts (Optional[List[str]]): The punctuations to predict.
        Returns:
            str: The punctuated text.
        """
        punct_ids = self.punct_ids
        if puncts is not None:
            puncts = list(set(self.puncts) & set(puncts))
            punct_ids = self.convert_puncts_to_ids(puncts)

        if format:
            text = format_text(text)
        tokens = self.encode(text)
        if max_puncts is None:
            max_puncts = max(1, len(tokens) // 4)

        beams = [(self.perplexity(tokens, eos), tokens)]
        for _ in range(max_puncts):
            new_beams = []
            for ppl, seq in beams:
                for i in range(1, len(seq) + 1):
                    for punct_id in punct_ids:
                        new_seq = seq[:i] + [punct_id] + seq[i:] if i < len(seq) else seq + [punct_id]
                        new_ppl = self.perplexity(new_seq, eos)
                        if (ppl - new_ppl) / ppl > ppl_drop_ratio:
                            new_beams.append((new_ppl, new_seq))
            if not new_beams:
                break
            beams = sorted(new_beams, key=lambda x: x[0])[:beam_size]
        return self.decode(beams[0][1])
