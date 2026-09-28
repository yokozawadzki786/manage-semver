"""Parse, compare and sort semantic versions including prereleases.

Follows SemVer 2.0.0. Build metadata is parsed and preserved but ignored
for comparison (per spec §10). Prerelease ordering follows spec §11: a
version with a prerelease is lower than the same version without, and
prerelease identifiers are compared field-by-field, numeric identifiers
compared as integers, alphanumeric compared lexically, numeric fields
always lower than alphanumeric.
"""

import re

# Strict SemVer 2.0.0 regex. Numeric identifiers must not have leading
# zeros (spec §9), which the {0|[1-9][0-9]*} alternation enforces.
_VERSION_RE = re.compile(
    r"^(?P<major>0|[1-9][0-9]*)"
    r"\.(?P<minor>0|[1-9][0-9]*)"
    r"\.(?P<patch>0|[1-9][0-9]*)"
    r"(?:-(?P<prerelease>(?:0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


class Version:
    """An immutable semantic version.

    Build metadata is stored but never participates in equality or ordering.
    """

    __slots__ = ("major", "minor", "patch", "prerelease", "build")

    def __init__(self, major, minor, patch, prerelease=(), build=()):
        self.major = major
        self.minor = minor
        self.patch = patch
        # Store as tuples of (is_numeric, value) for direct spec-compliant
        # comparison without re-parsing on every compare.
        self.prerelease = tuple(prerelease)
        self.build = tuple(build)

    def __repr__(self):
        return "Version({!r})".format(str(self))

    def __str__(self):
        s = "{}.{}.{}".format(self.major, self.minor, self.patch)
        if self.prerelease:
            s += "-" + ".".join(self._ident_str(i) for i in self.prerelease)
        if self.build:
            s += "+" + ".".join(self.build)
        return s

    @staticmethod
    def _ident_str(ident):
        _is_num, val = ident
        return str(val)

    def _cmp_key(self):
        # A version WITH a prerelease has LOWER precedence than the same
        # version without (spec §11). Represent "no prerelease" with a
        # sentinel that sorts ABOVE any real prerelease list.
        if not self.prerelease:
            return (self.major, self.minor, self.patch, 1, ())
        return (self.major, self.minor, self.patch, 0, self.prerelease)

    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._cmp_key() == other._cmp_key()

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._cmp_key() < other._cmp_key()

    def __le__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._cmp_key() <= other._cmp_key()

    def __gt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._cmp_key() > other._cmp_key()

    def __ge__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._cmp_key() >= other._cmp_key()

    def __ne__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._cmp_key() != other._cmp_key()

    def __hash__(self):
        return hash(self._cmp_key())


def _parse_identifier(raw):
    """Return (is_numeric, value) for a single prerelease identifier.

    Numeric identifiers are stored as ints so that 1 < 10 (not '1' < '10').
    The tuple's first element lets numeric identifiers sort below
    alphanumeric ones (spec §11: numeric < non-numeric).
    """
    if raw.isdigit():
        return (0, int(raw))
    return (1, raw)


def parse(text):
    """Parse a SemVer string into a Version.

    Raises ValueError if the string is not a valid semantic version.
    """
    m = _VERSION_RE.match(text)
    if m is None:
        raise ValueError("invalid semantic version: {!r}".format(text))

    prerelease = ()
    if m.group("prerelease"):
        prerelease = tuple(
            _parse_identifier(p) for p in m.group("prerelease").split(".")
        )

    build = ()
    if m.group("build"):
        build = tuple(m.group("build").split("."))

    return Version(
        int(m.group("major")),
        int(m.group("minor")),
        int(m.group("patch")),
        prerelease,
        build,
    )


def compare(a, b):
    """Return -1, 0, or 1 comparing two Version objects (or strings).

    Strings are parsed first; invalid strings raise ValueError.
    """
    if isinstance(a, str):
        a = parse(a)
    if isinstance(b, str):
        b = parse(b)
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


def sort(versions):
    """Return a new list of versions sorted in ascending order.

    Accepts Version objects or strings (which are parsed).
    """
    parsed = [parse(v) if isinstance(v, str) else v for v in versions]
    return sorted(parsed)
