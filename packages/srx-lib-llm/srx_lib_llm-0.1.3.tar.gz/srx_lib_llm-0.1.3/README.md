# srx-lib-llm

LLM helpers for SRX services built on LangChain.

What it includes:
- `responses_chat(prompt, cache=False)`: simple text chat via OpenAI Responses API
- Tool strategy base and registry
- Tavily search tool strategy

Designed to work with official OpenAI only.

## Install

PyPI (public):

- `pip install srx-lib-llm`

uv (pyproject):
```
[project]
dependencies = ["srx-lib-llm>=0.1.0"]
```

## Usage

```
from srx_lib_llm import responses_chat
text = await responses_chat("Hello there", cache=True)
```

Tools:
```
from srx_lib_llm.tools import ToolStrategyBase, register_strategy, get_strategies
from srx_lib_llm.tools.tavily import TavilyToolStrategy

register_strategy(TavilyToolStrategy())
strategies = get_strategies()
```

## Environment Variables

- `OPENAI_API_KEY` (required)
- `OPENAI_MODEL` (optional, default: `gpt-4.1-nano`)
- `TAVILY_API_KEY` (optional, for the Tavily tool)

## Release

Tag `vX.Y.Z` to publish to GitHub Packages via Actions.

## License

Proprietary © SRX
