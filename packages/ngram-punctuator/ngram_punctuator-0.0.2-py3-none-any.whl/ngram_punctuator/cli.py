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

import click

from ngram_punctuator import Punctuator


@click.command(help="N-gram Punctuator")
@click.argument("text", type=click.STRING)
@click.option("--order", type=click.INT, default=3, help="N-gram order")
@click.option("--beam-size", type=click.INT, default=5, help="Beam size for beam search")
@click.option("--max-puncts", type=click.INT, help="Maximum number of punctuations")
@click.option("--ppl-drop-ratio", type=click.FLOAT, default=0.08, help="Minimum perplexity drop ratio")
def main(text, order, beam_size, max_puncts, ppl_drop_ratio):
    punctuator = Punctuator(order)
    result = punctuator.predict(
        text,
        beam_size=beam_size,
        max_puncts=max_puncts,
        ppl_drop_ratio=ppl_drop_ratio,
    )
    print(result)


if __name__ == "__main__":
    main()
