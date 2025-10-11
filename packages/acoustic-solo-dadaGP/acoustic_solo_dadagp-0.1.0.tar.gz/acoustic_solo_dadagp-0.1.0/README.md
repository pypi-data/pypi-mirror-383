# acoustic-solo-dadaGP

A modification of [DadaGP](https://github.com/dada-bots/dadaGP) tailored for **acoustic solo guitar** workflows. It supports alternative string tunings and multi‑track acoustic/clean guitar parts, with a simple CLI and a small public Python API.

---

## Table of Contents

1. [Background & Attribution](#background--attribution)  
2. [What’s Changed](#whats-changed)  
3. [Features](#features)  
4. [Installation](#installation)  
5. [Quick Start](#quick-start)  
6. [CLI Reference](#cli-reference)  
7. [Python Reference](#python-reference)  
8. [Contributing](#contributing)  
9. [License](#license)

---

## Background & Attribution

This project is a **fork** of [`dada-bots/dadaGP`](https://github.com/dada-bots/dadaGP). Credit to the original authors for the foundational GP↔︎token pipeline.

---

## What’s Changed

- **Enhanced Acoustic Support** — optimized defaults and checks for acoustic/clean guitar usage.
- **Compatibility with pyguitarpro** — works with `pyguitarpro>=0.9`.
- **Alternative Tunings** — supports non‑standard tunings (drop D, Celtic, etc.).
- **Multi‑track Handling** — process up to 3 acoustic/clean tracks; optional merge‑down to one.
- **Refined CLI** — ergonomic `asdadagp` tool for encode/decode/process/info.
- **Token Utilities** — helpers for measure splitting, repeats/alternatives, and tuning extraction.

---

## Features

- Convert `.gp3/.gp4/.gp5/.gpx` ⇆ token text files
- Optional **track merge**: keep only the first acoustic/clean track and strip `cleanX:` prefixes
- **Measure & repeat analysis** helpers (playing order, measure objects)
- Basic **file validation / info** summaries
- Small **Python API** for scripting

---

## Installation

### From PyPI (recommended)

```bash
pip install acoustic-solo-dadaGP
```

### From source

```bash
git clone https://github.com/austinliu05/acoustic-solo-dadaGP.git
cd acoustic-solo-dadaGP
pip install -e .
```

Python >=3.8 is required.

---

## Quick Start

```bash
# Encode a Guitar Pro file to tokens
asdadagp encode song.gp5 tokens.txt --artist "John Doe"

# Decode tokens back to Guitar Pro
asdadagp decode tokens.txt song_out.gp5

# Process tokens: merge to single acoustic track
asdadagp process tokens.txt processed.txt --merge-tracks

# Process tokens with structured measures JSON (includes tuning & playing order)
asdadagp process tokens.txt processed.json --merge-tracks --measures

# Inspect file info (works for both .gp* or token files)
asdadagp info song.gp5
asdadagp info tokens.txt
```

---

## CLI Reference

The package installs the `asdadagp` command.

### `encode` — Guitar Pro → tokens

```
asdadagp encode INPUT.gp[3|4|5|x] OUTPUT.txt [--artist NAME] [--tuning]
```

- `INPUT.gp*` — Guitar Pro file to encode
- `OUTPUT.txt` — destination token file (one token per line)
- `--artist NAME` — optional first‑line artist token (default: `"Unknown"`)
- `--tuning` — if set, append tuning info to note tokens; otherwise only string tunings in the header

### `decode` — tokens → Guitar Pro

```
asdadagp decode INPUT.txt OUTPUT.gp5
```

- `INPUT.txt` — token file produced by `encode`/processing
- `OUTPUT.gp5` — Guitar Pro output (GP5 format is typical target)

### `process` — transform token streams

```
asdadagp process INPUT.txt OUTPUT.(txt|json) [--merge-tracks] [--measures]
```

- `--merge-tracks` — Merge all tracks into 1 (otherwise it keeps only the first acoustic/clean guitar track) and
  remove `cleanX:` prefixes (e.g., `clean0:note:s6:f0:D3 → note:s6:f0:D3`)
- `--measures` — output a **JSON** object with:
  - `tokens` — index→token map (all processed tokens)
  - `measures` — list of per‑measure token lists
  - `playing_order` — measure indices in actual playback order accounting for repeats/alternatives
  - `tuning` — string tuning extracted from tokens

> If `--measures` is used, `OUTPUT` **must** end with `.json`.

### `info` — summarize a file

```
asdadagp info INPUT.(gp3|gp4|gp5|gpx|txt)
```

- For `.gp*` files: prints title/artist/album/track count/measure count/tempo + per‑track tunings
- For token files: prints token counts and rough token‑type histogram

---

## Python Reference

Import from the top‑level package `asdadagp`:

```python
from asdadagp import (
    __version__,
    # main conversions
    asdadagp_encode, guitarpro2tokens,
    asdadagp_decode, tokens2guitarpro,
    # processing helpers
    get_string_tunings, tracks_check, tokens_to_measures, measures_playing_order,
    # utilities
    get_tuning_type, get_fret, convert_spn_to_common,
    # constants
    instrument_groups, supported_times, wait_token_list2,
)
```

### Conversions

#### `asdadagp_encode(input_file: str, output_file: str, note_tuning: bool, artist_token: str) -> None`
Encodes a Guitar Pro file into a token text file.
- **input_file**: path to `.gp3/.gp4/.gp5/.gpx` file  
- **output_file**: path to write tokens (one per line)  
- **note_tuning**: if `True`, append tuning to note tokens  
- **artist_token**: first‑line artist token (e.g., `"John Doe"`)  

Related lower‑level function:

#### `guitarpro2tokens(song: guitarpro.Song, artist: str, verbose: bool, note_tuning: bool) -> list[str]`
Converts an in‑memory `guitarpro.Song` into tokens.

#### `asdadagp_decode(input_file: str, output_file: str) -> None`
Decodes a token text file back into a Guitar Pro file.  
Related lower‑level function:

#### `tokens2guitarpro(all_tokens: list[str], verbose: bool = False) -> guitarpro.Song`
Builds an in‑memory `guitarpro.Song` from tokens.

### Processing

#### `get_string_tunings(tokens: list[str]) -> list[str]`
Extracts per‑string tunings from a token list.

#### `tracks_check(tokens: list[str], merge_track: bool) -> list[str]`
Optionally merges to the first acoustic/clean track and removes `cleanX:` prefixes.

#### `tokens_to_measures(tokens: list[str]) -> list[TokenMeasure]`
Parses tokens into measure objects (repeat/alternative markers retained in structure).

#### `measures_playing_order(measures: list[TokenMeasure], tokens: bool = False) -> list[int] | list[list[str]]`
Computes actual playback order considering repeats and alternatives. If `tokens=True`, returns the measures’ token lists in order rather than indices.

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m "feat: add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

Released under the **MIT License**. See [LICENSE](LICENSE).  
Original project **dadaGP** by `dada-bots` is MIT as well.
