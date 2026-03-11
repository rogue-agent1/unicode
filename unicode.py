#!/usr/bin/env python3
"""unicode - Unicode character lookup and inspection tool.

Single-file, zero-dependency CLI for exploring Unicode.
"""

import sys
import unicodedata
import argparse


def lookup_char(char):
    """Get info about a single character."""
    cp = ord(char)
    try:
        name = unicodedata.name(char)
    except ValueError:
        name = "<unnamed>"
    cat = unicodedata.category(char)
    block = f"U+{cp:04X}"
    bidi = unicodedata.bidirectional(char)
    combining = unicodedata.combining(char)
    decomp = unicodedata.decomposition(char)
    return {
        "char": char,
        "codepoint": block,
        "decimal": cp,
        "name": name,
        "category": cat,
        "bidirectional": bidi,
        "combining": combining,
        "decomposition": decomp or "none",
        "utf8": char.encode("utf-8").hex(" "),
        "utf16": char.encode("utf-16-be").hex(" "),
    }


def cmd_inspect(args):
    """Inspect characters in a string."""
    text = " ".join(args.text)
    for ch in text:
        info = lookup_char(ch)
        print(f"  {info['char']}  {info['codepoint']}  {info['name']}")
        if args.verbose:
            print(f"     Category: {info['category']}")
            print(f"     UTF-8: {info['utf8']}")
            print(f"     UTF-16: {info['utf16']}")
            if info['decomposition'] != 'none':
                print(f"     Decomposition: {info['decomposition']}")
            print()


def cmd_search(args):
    """Search Unicode characters by name."""
    query = " ".join(args.query).upper()
    count = 0
    for cp in range(0x110000):
        if count >= args.limit:
            break
        try:
            ch = chr(cp)
            name = unicodedata.name(ch)
        except ValueError:
            continue
        if query in name:
            print(f"  {ch}  U+{cp:04X}  {name}")
            count += 1
    if count == 0:
        print(f"No characters matching '{query}'")


def cmd_codepoint(args):
    """Look up by codepoint (U+XXXX or decimal)."""
    for spec in args.codepoints:
        try:
            if spec.upper().startswith("U+"):
                cp = int(spec[2:], 16)
            elif spec.startswith("0x"):
                cp = int(spec, 16)
            else:
                cp = int(spec)
            ch = chr(cp)
            info = lookup_char(ch)
            print(f"  {info['char']}  {info['codepoint']}  {info['name']}")
        except (ValueError, OverflowError) as e:
            print(f"  Invalid codepoint: {spec} ({e})")


def cmd_encode(args):
    """Show encoding of text."""
    text = " ".join(args.text)
    encodings = ["utf-8", "utf-16-be", "utf-32-be", "ascii", "latin-1"]
    for enc in encodings:
        try:
            data = text.encode(enc)
            hex_str = data.hex(" ")
            print(f"  {enc:12s}  {hex_str}  ({len(data)} bytes)")
        except (UnicodeEncodeError, UnicodeDecodeError):
            print(f"  {enc:12s}  <cannot encode>")


def main():
    parser = argparse.ArgumentParser(prog="unicode", description="Unicode character lookup tool")
    sub = parser.add_subparsers(dest="command")

    p_inspect = sub.add_parser("inspect", help="Inspect characters in text")
    p_inspect.add_argument("text", nargs="+")
    p_inspect.add_argument("-v", "--verbose", action="store_true")

    p_search = sub.add_parser("search", help="Search by character name")
    p_search.add_argument("query", nargs="+")
    p_search.add_argument("-l", "--limit", type=int, default=20)

    p_cp = sub.add_parser("codepoint", help="Look up by codepoint")
    p_cp.add_argument("codepoints", nargs="+", help="U+XXXX or decimal")

    p_enc = sub.add_parser("encode", help="Show text encoding")
    p_enc.add_argument("text", nargs="+")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1

    cmds = {"inspect": cmd_inspect, "search": cmd_search, "codepoint": cmd_codepoint, "encode": cmd_encode}
    return cmds[args.command](args) or 0


if __name__ == "__main__":
    sys.exit(main())
