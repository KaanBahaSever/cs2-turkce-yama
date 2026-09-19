#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cities: Skylines II - Turkish Localization / update tooling

Compares a fresh English localization dump against the current Turkish translation
and the stored English baseline, and reports what has to be (re)translated.

    python tools/check_updates.py                      # scan updates/incoming_en/
    python tools/check_updates.py path/to/dump         # scan another folder
    python tools/check_updates.py --merge updates/keys_to_translate.json
                                                       # merge the filled-in report + roll the baseline
    python tools/check_updates.py --validate           # integrity check of the current translation

The dump may be split into any number of files ("[A]0- en-US.json", "[A]1- en-US.json", ...).
"""
from __future__ import annotations

import argparse
import collections
import glob
import io
import json
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TR_PATH = os.path.join(ROOT, "src", "Localization", "tr-TR.json")
BASELINE_DIR = os.path.join(ROOT, "originals", "en-US")
BASELINE_PATH = os.path.join(BASELINE_DIR, "en-US.json")
INCOMING_DIR = os.path.join(ROOT, "updates", "incoming_en")
REPORT_PATH = os.path.join(ROOT, "updates", "keys_to_translate.json")
CONSOLIDATED_NAME = "en-US.json"

TOKEN_RE = re.compile(r"\{[^{}]*\}")
TAG_RE = re.compile(r"<[^<>]*>")
# an all-caps word that still contains a lowercase dotless/dotted i  ->  "GRAFıK", "HAKKıNDA"
BROKEN_CASE_RE = re.compile(r"(?<![a-zçğıöşü])[A-ZÇĞİÖŞÜ]{2,}[ıi][A-ZÇĞİÖŞÜ]+|(?<![A-Za-zçğıöşüÇĞİÖŞÜ])[A-ZÇĞİÖŞÜ]+[ıi][A-ZÇĞİÖŞÜ]{2,}")


# --------------------------------------------------------------------------- io
def read_json(path):
    with io.open(path, "r", encoding="utf-8-sig") as fh:
        return json.load(fh, object_pairs_hook=collections.OrderedDict)


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(data, ensure_ascii=False, indent=2))
        fh.write("\n")


def natural_key(path):
    """Sort "[A]10- en-US.json" after "[A]9- en-US.json"."""
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r"(\d+)", os.path.basename(path))]


def discover(directory):
    """All split dump files of a folder, in natural order (the consolidated copy is skipped)."""
    files = glob.glob(os.path.join(glob.escape(directory), "*en-US.json"))
    if not files:
        files = glob.glob(os.path.join(glob.escape(directory), "*.json"))
    files = [f for f in files if os.path.basename(f) != CONSOLIDATED_NAME]
    return sorted(files, key=natural_key)


def merge_split(files):
    """Merge split files into one ordered dict. Later files win; conflicts are reported."""
    merged = collections.OrderedDict()
    conflicts = []
    for path in files:
        data = read_json(path)
        if not isinstance(data, dict):
            raise ValueError("%s is not a JSON object" % path)
        for key, value in data.items():
            if not isinstance(value, str):
                raise ValueError("%s: value of %r is not a string" % (path, key))
            if key in merged and merged[key] != value:
                conflicts.append((key, merged[key], value, os.path.basename(path)))
            merged[key] = value
    return merged, conflicts


# ----------------------------------------------------------------------- checks
def structure_problems(english, turkish):
    """Tokens, tags, line breaks and markdown markers that do not survive translation."""
    problems = []
    if sorted(TOKEN_RE.findall(english)) != sorted(TOKEN_RE.findall(turkish)):
        problems.append("token")
    en_tags = sorted(t for t in TAG_RE.findall(english) if "|" not in t)
    tr_tags = sorted(t for t in TAG_RE.findall(turkish) if "|" not in t)
    if en_tags != tr_tags or len(TAG_RE.findall(english)) != len(TAG_RE.findall(turkish)):
        problems.append("tag")
    if english.count("\n") != turkish.count("\n"):
        problems.append("newline")
    if turkish.count("**") % 2:
        problems.append("markdown")
    if english.strip() and not turkish.strip():
        problems.append("empty")
    if BROKEN_CASE_RE.search(turkish) and not BROKEN_CASE_RE.search(english):
        problems.append("turkish-case")
    return problems


def diff(new_en, old_en, tr):
    # every entry carries an empty "tr" slot, so the report itself can be filled in and merged
    added = collections.OrderedDict(
        (k, collections.OrderedDict([("en", v), ("tr", "")])) for k, v in new_en.items() if k not in tr)
    modified = collections.OrderedDict()
    for key, value in new_en.items():
        if key in tr and key in old_en and old_en[key] != value:
            modified[key] = collections.OrderedDict(
                [("en", value), ("old_en", old_en[key]), ("old_tr", tr[key]), ("tr", "")])
    removed = [k for k in tr if k not in new_en]
    return added, modified, removed


def flatten_translations(data):
    """A flat {key: turkish} file, or the filled-in report ({"new": {key: {"en", "tr"}}, "modified": {...}})."""
    if not (isinstance(data.get("new"), dict) or isinstance(data.get("modified"), dict)):
        return data
    flat = collections.OrderedDict()
    for section in ("new", "modified"):
        for key, value in (data.get(section) or {}).items():
            flat[key] = (value.get("tr") or "") if isinstance(value, dict) else value
    return flat


# --------------------------------------------------------------------- commands
def load_state(incoming_dir):
    files = discover(incoming_dir)
    if not files:
        return None, None, None, None
    new_en, conflicts = merge_split(files)
    tr = read_json(TR_PATH) if os.path.exists(TR_PATH) else collections.OrderedDict()
    old_en = read_json(BASELINE_PATH) if os.path.exists(BASELINE_PATH) else collections.OrderedDict()
    for key, first, second, name in conflicts:
        print("  ! %s defined twice with different text (kept the one from %s)" % (key, name))
    return files, new_en, old_en, tr


def cmd_check(incoming_dir):
    files, new_en, old_en, tr = load_state(incoming_dir)
    if files is None:
        print("No '*en-US.json' files in %s - drop the new dump there first." % incoming_dir)
        return 1
    added, modified, removed = diff(new_en, old_en, tr)
    report = collections.OrderedDict([
        ("meta", collections.OrderedDict([
            ("incoming_dir", os.path.relpath(incoming_dir, ROOT).replace("\\", "/")),
            ("incoming_files", len(files)),
            ("baseline_keys", len(new_en)),
            ("translated_keys", len(tr)),
            ("new", len(added)),
            ("modified", len(modified)),
            ("removed", len(removed)),
        ])),
        ("new", added),
        ("modified", modified),
        ("removed", removed),
    ])
    write_json(REPORT_PATH, report)
    print("Incoming dump : %d files, %d keys" % (len(files), len(new_en)))
    print("Translation   : %d keys" % len(tr))
    print("  new         : %d" % len(added))
    print("  modified    : %d" % len(modified))
    print("  removed     : %d" % len(removed))
    print("Report        : %s" % os.path.relpath(REPORT_PATH, ROOT))
    if added or modified:
        print("\nFill in every empty \"tr\" field of that file, then run:")
        print("  python tools/check_updates.py --merge updates/keys_to_translate.json")
        print("(a flat {key: turkish} JSON file is accepted as well)")
    elif removed:
        print("\nNothing to translate. Run '--merge' with an empty {} file to drop removed keys and roll the baseline.")
    else:
        print("\nTranslation is up to date.")
    return 0


def cmd_merge(incoming_dir, translated_path, allow_partial, keep_removed):
    files, new_en, old_en, tr = load_state(incoming_dir)
    if files is None:
        print("No '*en-US.json' files in %s - nothing to merge against." % incoming_dir)
        return 1
    translated = flatten_translations(read_json(translated_path))

    added, modified, removed = diff(new_en, old_en, tr)
    wanted = list(added) + list(modified)
    unknown = [k for k in translated if k not in new_en]
    missing = [k for k in wanted if not isinstance(translated.get(k), str) or not translated[k].strip()]
    # an empty slot is "untranslated", not "broken"
    bad = [(k, structure_problems(new_en[k], translated[k])) for k in translated
           if k in new_en and isinstance(translated[k], str) and translated[k].strip()]
    bad = [(k, p) for k, p in bad if p]

    for key in unknown:
        print("  ! ignored, not a key of the new dump: %s" % key)
    for key, problems in bad:
        print("  x %s -> %s" % (key, ", ".join(problems)))
    if bad:
        print("\n%d translated entries break tokens/tags/line breaks/casing. Fix them and run again." % len(bad))
        return 2
    if missing and not allow_partial:
        print("%d keys are still untranslated (e.g. %s)." % (len(missing), ", ".join(missing[:3])))
        print("Finish them or pass --allow-partial to merge what is there.")
        return 2

    result = collections.OrderedDict()
    for key in new_en:                       # keep the game's own key order
        value = translated.get(key)
        if isinstance(value, str) and value.strip():
            result[key] = value
        elif key in tr:
            result[key] = tr[key]
    if keep_removed:
        for key in removed:
            result[key] = tr[key]
    applied = sum(1 for k in translated if k in new_en and result.get(k) == translated[k])
    write_json(TR_PATH, result)

    if os.path.abspath(incoming_dir) != os.path.abspath(BASELINE_DIR):
        for old_file in glob.glob(os.path.join(glob.escape(BASELINE_DIR), "*.json")):
            os.remove(old_file)
        os.makedirs(BASELINE_DIR, exist_ok=True)
        for path in files:
            shutil.move(path, os.path.join(BASELINE_DIR, os.path.basename(path)))
    write_json(BASELINE_PATH, new_en)
    if os.path.exists(REPORT_PATH):
        os.remove(REPORT_PATH)

    print("Merged %d translated keys; dropped %d removed keys." % (applied, 0 if keep_removed else len(removed)))
    print("Translation : %d / %d keys (%s)" % (
        sum(1 for k in new_en if k in result), len(new_en), os.path.relpath(TR_PATH, ROOT)))
    print("Baseline    : %s (%d files + consolidated copy)" % (os.path.relpath(BASELINE_DIR, ROOT), len(files)))
    return 0


def cmd_validate():
    if not (os.path.exists(TR_PATH) and os.path.exists(BASELINE_PATH)):
        print("Missing %s or %s" % (TR_PATH, BASELINE_PATH))
        return 1
    tr, en = read_json(TR_PATH), read_json(BASELINE_PATH)
    missing = [k for k in en if k not in tr]
    extra = [k for k in tr if k not in en]
    bad = [(k, structure_problems(en[k], tr[k])) for k in en if k in tr]
    bad = [(k, p) for k, p in bad if p]
    print("Baseline %d keys | translation %d keys" % (len(en), len(tr)))
    print("  untranslated : %d" % len(missing))
    print("  obsolete     : %d" % len(extra))
    print("  broken       : %d" % len(bad))
    for key in missing[:20]:
        print("    - missing  %s" % key)
    for key, problems in bad[:40]:
        print("    x %s -> %s" % (key, ", ".join(problems)))
    return 0 if not (missing or bad) else 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("incoming", nargs="?", default=INCOMING_DIR,
                        help="folder with the new English dump (default: updates/incoming_en/)")
    parser.add_argument("--merge", metavar="TRANSLATED_FILE",
                        help="filled-in updates/keys_to_translate.json (or a flat {key: turkish} JSON) to merge")
    parser.add_argument("--allow-partial", action="store_true", help="merge even if some keys are untranslated")
    parser.add_argument("--keep-removed", action="store_true", help="keep keys the game no longer ships")
    parser.add_argument("--validate", action="store_true", help="check the current translation and exit")
    args = parser.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if args.validate:
        return cmd_validate()
    incoming = os.path.abspath(args.incoming)
    if args.merge:
        return cmd_merge(incoming, args.merge, args.allow_partial, args.keep_removed)
    return cmd_check(incoming)


if __name__ == "__main__":
    sys.exit(main())
