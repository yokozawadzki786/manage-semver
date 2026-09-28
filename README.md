# Semver

Parse, compare and sort semantic versions (SemVer 2.0.0) including prereleases.

## Usage

```python
from semver import Version, parse, compare, sort

v = parse("1.2.3-alpha.1+build.5")
print(v.major)       # 1
print(v.prerelease)  # ((1, 'alpha'), (0, 1))

print(compare("1.0.0-alpha", "1.0.0"))   # -1
print(compare("1.0.0-1", "1.0.0-10"))    # -1  (numeric, not lexical)

ordered = sort(["2.0.0", "1.0.0-alpha", "1.0.0"])
print([str(v) for v in ordered])
# ['1.0.0-alpha', '1.0.0', '2.0.0']
```

## Exports

- `Version` — immutable version object with `major`, `minor`, `patch`, `prerelease`, `build` attributes. Supports `<`, `<=`, `==`, `!=`, `>=`, `>` and is hashable.
- `parse(text)` — parse a string into a `Version`. Raises `ValueError` on invalid input.
- `compare(a, b)` — return `-1`, `0`, or `1`. Accepts `Version` objects or strings.
- `sort(versions)` — return a new list sorted ascending. Accepts `Version` objects or strings.

## Why

Needed a zero-dependency SemVer parser for environments where `pip install` is not available. The trade-off: no range matching (`^1.2.3`, `~1.0.0`), no `bump()` helpers — just parsing, comparison, and sorting done correctly per spec.

## Edge cases

- **Build metadata is ignored for comparison** (spec §10). `1.0.0+a == 1.0.0+b`.
- **Leading zeros rejected** (spec §9). `parse("01.0.0")` raises `ValueError`.
- **Numeric prerelease identifiers compared as integers**. `1.0.0-1 < 1.0.0-10` (not lexical string order).
- **Numeric prerelease identifiers sort below alphanumeric** (spec §11). `1.0.0-1 < 1.0.0-alpha`.

## Running tests

```
PYTHONPATH=src python -m unittest discover -s tests
```
