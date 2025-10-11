# N-gram Punctuator

[![PyPI](https://img.shields.io/pypi/v/ngram-punctuator)](https://pypi.org/project/ngram-punctuator)
[![License](https://img.shields.io/github/license/pengzhendong/ngram-punctuator)](https://github.com/pengzhendong/ngram-punctuator/blob/master/LICENSE)

An N-gram based punctuation restoration tool that automatically adds punctuation to text without punctuation marks.

## Features

- Restores punctuation marks to unpunctuated text using N-gram language models
- Supports multiple punctuation marks including `!`, `'`, `,`, `.`, `?`, `。`, `…`, `，`, `、`, `！` and `？`
- Configurable N-gram order (3-gram to 6-gram)
- Beam search algorithm for optimal punctuation placement
- CLI interface for easy usage
- Support for both English and Chinese text

## Installation

```bash
pip install ngram-punctuator
```

## Usage

### Command Line Interface

```bash
# Basic usage
ngram-punctuator "how are you"
# >>> how are you?

# Specify N-gram order (3, 4, 5, or 6)
ngram-punctuator --order 4 "你好吗"
# >>> 你好吗？

# Adjust beam size for better accuracy (higher values may improve results but slow down processing)
ngram-punctuator --beam-size 10 "Artificial intelligence is changing our daily lives in many ways from smart home devices to personalized recommendations it makes technology more convenient and efficient"
# >>> Artificial intelligence is changing our daily lives, in many ways, from smart home devices to personalized recommendations, it makes technology more convenient and efficient.

# Limit the maximum number of punctuation marks to add
ngram-punctuator --max-puncts 8 "中华文明有着五千年的悠久历史从夏商周到秦汉唐宋元明清每个朝代都留下了丰富的文化遗产长城故宫兵马俑敦煌莫高窟这些都是中华民族的宝贵财富值得我们好好保护和传承"
# >>> 中华文明有着五千年的悠久历史，从夏商周到秦汉唐宋元明清，每个朝代都留下了丰富的文化遗产长城故宫兵马俑，敦煌莫高窟，这些都是中华民族的宝贵财富，值得我们好好保护和传承。

# Adjust perplexity drop ratio for more conservative punctuation
ngram-punctuator --ppl-drop-ratio 0.1 "这个new feature的UI设计需要optimize一下user experience特别是mobile端的responsive design要考虑cross platform compatibility还有API的integration问题我们要做AB testing来validate hypothesis"
# >>> 这个 new feature 的 UI 设计需要 optimize 一下 user experience, 特别是 mobile 端的 responsive design, 要考虑 cross platform compatibility, 还有 API 的 integration 问题，我们要做 AB testing, 来 validate hypothesis.
```

### Python API

```python
from ngram_punctuator import Punctuator

# Initialize punctuator with default settings (3-gram model)
punctuator = Punctuator()

# Add punctuation to text
text = "The sun sets slowly over the calm blue ocean"
result = punctuator.predict(text)
print(result)  # Output: "The sun sets, slowly over the calm blue ocean."

# Initialize with specific N-gram order
punctuator = Punctuator(order=4)

# Advanced usage with parameters
result = punctuator.predict(
    text="人工智能技术正在深刻改变我们的生活方式从智能手机到自动驾驶汽车从医疗诊断到金融风控AI的应用已经渗透到各个领域",
    beam_size=10,
    max_puncts=5,
    ppl_drop_ratio=0.15
)
print(result)  # Output: "人工智能技术，正在深刻改变我们的生活方式。从智能手机到自动驾驶汽车从医疗诊断到金融风控 AI 的应用，已经渗透到各个领域。"
```

## How It Works

The N-gram Punctuator uses statistical language models to determine the most likely positions for punctuation marks in unpunctuated text:

1. **Text Preprocessing**: The input text is tokenized using a BPE (Byte Pair Encoding) tokenizer
2. **N-gram Perplexity**: N-gram language models calculate perplexity for different punctuation placement possibilities
3. **Beam Search**: A beam search algorithm explores multiple punctuation placement options
4. **Optimization**: The system selects the punctuation arrangement with the lowest perplexity

The models are trained on large text corpora and can effectively restore punctuation for both English and Chinese text.

## Parameters

- `order`: N-gram order (3, 4, 5, or 6). Higher orders may capture more context but require more computational resources.
- `beam_size`: Number of candidates to keep during beam search. Larger values may improve accuracy but slow down processing.
- `max_puncts`: Maximum number of punctuation marks to insert. If not specified, it defaults to 1/4 of the text length.
- `ppl_drop_ratio`: Minimum perplexity drop ratio (between 0.0 and 1.0). Higher values make the system more conservative in adding punctuation.

## License

[LICENSE](LICENSE)
