#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finds (and with --write repairs) all-caps Turkish words in src/Localization/tr-TR.json that still carry a
lowercase "ı" or "i" - at the start, in the middle or at the end of the word: "HESABı", "BAŞLıK", "ıŞIK", "GRAFiK".

    python tools/fix_upper_i.py            # report only
    python tools/fix_upper_i.py --write    # repair in place

What counts as a broken word
    A run of letters that contains "ı"/"i" and whose OTHER letters are all uppercase (at least two of them).
    Mixed-case names such as PlayStation, DrawBridge, GitHub or #BisikletHayattır have lowercase letters besides
    the i and are left alone - the naive rule "two uppercase letters plus an i" would corrupt 140+ of them.

How it is repaired
    "i" -> "İ" always. "ı" -> "I" when the nearest vowel (the preceding one first) is a back vowel (a ı o u),
    otherwise "İ" - so a typo like "BİLGı" still becomes "BİLGİ".

Never touched: JSON keys, {TOKENS}, <tags>, escape sequences.

Note: text that is stored in normal case ("Paradox Hesabı") and only LOOKS wrong in game ("PARADOX HESABı") is
not a data problem. The game upper-cases it with invariant rules; the mod fixes that at runtime (TurkishCasing.cs).
"""
import collections
import io
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TR_PATH = os.path.join(ROOT, "src", "Localization", "tr-TR.json")

UPPER = set("ABCDEFGHIJKLMNOPQRSTUVWXYZÇĞİÖŞÜ")
BACK_VOWELS = set("aıouAIOU")
FRONT_VOWELS = set("eiöüEİÖÜ")
PROTECTED_SPAN = re.compile(r"\{[^{}]*\}|<[^<>]*>|\\[nrt]")
WORD = re.compile(r"[^\W\d_]+")


def is_broken(word):
    if "ı" not in word and "i" not in word:
        return False
    rest = [c for c in word if c not in "ıi"]
    return len(rest) >= 2 and all(c in UPPER for c in rest)


def repair(word):
    out = list(word)
    for index, char in enumerate(word):
        if char == "i":
            out[index] = "İ"
        elif char == "ı":
            harmony = None
            for other in list(reversed(word[:index])) + list(word[index + 1:]):
                if other in BACK_VOWELS:
                    harmony = "back"
                    break
                if other in FRONT_VOWELS:
                    harmony = "front"
                    break
            out[index] = "İ" if harmony == "front" else "I"
    return "".join(out)


def fix_text(text):
    """Returns (new_text, [(before, after), ...]); protected spans are copied through untouched."""
    changes = []
    pieces = []
    cursor = 0
    for span in PROTECTED_SPAN.finditer(text):
        pieces.append((text[cursor:span.start()], True))
        pieces.append((span.group(0), False))
        cursor = span.end()
    pieces.append((text[cursor:], True))

    def replace(match):
        word = match.group(0)
        if is_broken(word):
            fixed = repair(word)
            changes.append((word, fixed))
            return fixed
        return word

    return "".join(WORD.sub(replace, part) if editable else part for part, editable in pieces), changes


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    write = "--write" in sys.argv[1:]
    with io.open(TR_PATH, encoding="utf-8") as fh:
        data = json.load(fh, object_pairs_hook=collections.OrderedDict)

    total = 0
    for key, value in data.items():                     # values only; keys are never rewritten
        fixed, changes = fix_text(value)
        if changes:
            total += len(changes)
            print("%s: %s" % (key, ", ".join("%s -> %s" % pair for pair in changes)))
            data[key] = fixed

    print("%d entries scanned, %d broken all-caps word(s) %s." % (len(data), total, "repaired" if write else "found"))
    if write and total:
        with io.open(TR_PATH, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(data, ensure_ascii=False, indent=2))
            fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
