# DomePy : A modern [Dome](https://domeapi.io/) client for Python

Dome is a unified API over prediction markets. The `DomePy` package provides an idiomatic Python client for [Dome](https://domeapi.io). It provides both an Async API and a Sync API.

## Install
```bash
uv add domepy
```
or
```bash
pip install domepy
```

## Usage
`DomePy` aims to feel just like Dome's API.

```python
from domepy import syncdome

with syncdome() as dome:
    orders = dome.polymarket.orders(slug="bitcoin-up-or-down-july-25-8pm-et")
    # more methods available on polymarket. install and try them out!

```

There is full editor autocomplete on the responses.
