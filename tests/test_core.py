import unittest

from semver import Version, parse, compare, sort


class TestParse(unittest.TestCase):
    def test_basic(self):
        v = parse("1.2.3")
        self.assertEqual(v.major, 1)
        self.assertEqual(v.minor, 2)
        self.assertEqual(v.patch, 3)
        self.assertEqual(v.prerelease, ())
        self.assertEqual(v.build, ())

    def test_with_prerelease(self):
        v = parse("1.0.0-alpha.1")
        self.assertEqual(v.prerelease, ((1, "alpha"), (0, 1)))

    def test_with_build(self):
        v = parse("1.0.0+build.123")
        self.assertEqual(v.build, ("build", "123"))

    def test_prerelease_and_build(self):
        v = parse("1.0.0-beta+exp.sha.5114f85")
        self.assertEqual(v.prerelease, ((1, "beta"),))
        self.assertEqual(v.build, ("exp", "sha", "5114f85"))

    def test_str_roundtrip(self):
        cases = [
            "0.0.0",
            "1.0.0",
            "1.2.3",
            "1.0.0-alpha",
            "1.0.0-alpha.1",
            "1.0.0-alpha.beta",
            "1.0.0+build",
            "1.0.0-alpha+build",
        ]
        for c in cases:
            self.assertEqual(str(parse(c)), c)

    def test_leading_zero_rejected(self):
        with self.assertRaises(ValueError):
            parse("01.0.0")
        with self.assertRaises(ValueError):
            parse("1.01.0")
        with self.assertRaises(ValueError):
            parse("1.0.01")

    def test_prerelease_leading_zero_rejected(self):
        with self.assertRaises(ValueError):
            parse("1.0.0-01")

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            parse("")

    def test_missing_patch_rejected(self):
        with self.assertRaises(ValueError):
            parse("1.2")

    def test_garbage_rejected(self):
        with self.assertRaises(ValueError):
            parse("not-a-version")


class TestCompare(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(compare("1.0.0", "1.0.0"), 0)

    def test_major(self):
        self.assertEqual(compare("2.0.0", "1.0.0"), 1)
        self.assertEqual(compare("1.0.0", "2.0.0"), -1)

    def test_minor(self):
        self.assertEqual(compare("1.2.0", "1.1.0"), 1)

    def test_patch(self):
        self.assertEqual(compare("1.0.2", "1.0.1"), 1)

    def test_prerelease_lower_than_release(self):
        self.assertEqual(compare("1.0.0-alpha", "1.0.0"), -1)

    def test_numeric_prerelease_order(self):
        # 1.0.0-1 < 1.0.0-10 (numeric comparison, not lexical)
        self.assertEqual(compare("1.0.0-1", "1.0.0-10"), -1)

    def test_alpha_prerelease_order(self):
        self.assertEqual(compare("1.0.0-alpha", "1.0.0-beta"), -1)

    def test_numeric_lower_than_alpha(self):
        # spec §11: numeric identifiers always lower than alphanumeric
        self.assertEqual(compare("1.0.0-1", "1.0.0-alpha"), -1)

    def test_prerelease_field_count(self):
        # more fields = higher when prefix is equal
        self.assertEqual(compare("1.0.0-alpha", "1.0.0-alpha.1"), -1)

    def test_build_ignored(self):
        self.assertEqual(compare("1.0.0+a", "1.0.0+b"), 0)
        self.assertEqual(compare("1.0.0-alpha+x", "1.0.0-alpha+y"), 0)

    def test_version_objects(self):
        a = parse("1.0.0")
        b = parse("2.0.0")
        self.assertEqual(compare(a, b), -1)


class TestVersionEquality(unittest.TestCase):
    def test_build_does_not_affect_equality(self):
        self.assertEqual(parse("1.0.0+a"), parse("1.0.0+b"))

    def test_prerelease_affects_equality(self):
        self.assertNotEqual(parse("1.0.0-alpha"), parse("1.0.0-beta"))

    def test_hashable(self):
        s = {parse("1.0.0"), parse("1.0.0+build"), parse("2.0.0")}
        self.assertEqual(len(s), 2)


class TestSort(unittest.TestCase):
    def test_sort_strings(self):
        result = sort(["3.0.0", "1.0.0", "2.0.0"])
        self.assertEqual([str(v) for v in result], ["1.0.0", "2.0.0", "3.0.0"])

    def test_sort_with_prerelease(self):
        result = sort([
            "1.0.0",
            "1.0.0-rc.1",
            "1.0.0-alpha.1",
            "1.0.0-beta",
            "0.9.0",
        ])
        self.assertEqual(
            [str(v) for v in result],
            ["0.9.0", "1.0.0-alpha.1", "1.0.0-beta", "1.0.0-rc.1", "1.0.0"],
        )

    def test_sort_mixed(self):
        result = sort([parse("2.0.0"), "1.0.0"])
        self.assertEqual([str(v) for v in result], ["1.0.0", "2.0.0"])

    def test_sort_empty(self):
        self.assertEqual(sort([]), [])


if __name__ == "__main__":
    unittest.main()
