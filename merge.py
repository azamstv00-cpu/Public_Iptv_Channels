#!/usr/bin/env python3
"""Merge multiple IPTV M3U/M3U8 playlists into a single deduplicated file.

Reads source URLs from sources.txt plus a local personal.m3u8 file,
deduplicates channels by URL, groups them by group-title, and writes
playlist.m3u8.
"""

import argparse
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCES_FILE = os.path.join(ROOT, "sources.txt")
PERSONAL_FILE = os.path.join(ROOT, "personal.m3u8")
OUTPUT_FILE = os.path.join(ROOT, "playlist.m3u8")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
)

EXTINF_RE = re.compile(r"^#EXTINF:(?P<duration>-?\d+(?:\.\d+)?)(?P<attrs>.*)")


class Channel:
    __slots__ = ("name", "url", "attrs", "directives")

    def __init__(self, name, url, attrs, directives):
        self.name = name
        self.url = url
        self.attrs = attrs
        self.directives = directives

    def attrs_dict(self):
        parsed = {}
        for match in re.finditer(r'([\w-]+)="([^"]*)"', self.attrs):
            parsed[match.group(1)] = match.group(2)
        return parsed


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return data.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode("utf-8", errors="replace")


def parse_playlist(text):
    channels = []
    pending = None
    directives = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if line.startswith("#EXTINF:"):
            if pending:
                channels.append(pending)
            match = EXTINF_RE.match(line)
            attrs = match.group("attrs").strip() if match else ""
            name = (attrs.split(",")[-1]).strip() if attrs else line
            pending = Channel(name=name, url=None, attrs=attrs, directives=[])
            directives = []
        elif line.startswith("#EXTM3U"):
            continue
        elif line.startswith("#") and pending:
            directives.append(line)
        elif pending:
            pending.url = line.strip()
            pending.directives = list(directives)
            channels.append(pending)
            pending = None
    if pending:
        channels.append(pending)
    return [c for c in channels if c.url]


def normalize_label(label):
    return re.sub(r"\s*\(\d+\)\s*$", "", label).strip() or label


def combined_attrs(attrs, source_name):
    if "," in attrs:
        attr_part, _, name_part = attrs.partition(",")
    else:
        attr_part, name_part = attrs, ""
    parsed = {}
    for match in re.finditer(r'([\w-]+)="([^"]*)"', attr_part):
        parsed[match.group(1)] = match.group(2)
    original = parsed.get("group-title")
    combined = f"{source_name}-{original}" if original else source_name
    if "group-title=" in attr_part:
        attr_part = re.sub(
            r'group-title="[^"]*"', f'group-title="{combined}"', attr_part, count=1
        )
    else:
        attr_part = (attr_part.rstrip() + f' group-title="{combined}"').strip()
    if name_part:
        return f"{attr_part},{name_part}"
    return attr_part


def build_merged(sources, personal_text, labels=None):
    labels = labels or {}
    merged = {}
    source_order = {}

    def add_channels(channels, source_name, priority, is_personal=False):
        for ch in channels:
            key = ch.url
            if key in merged:
                continue
            merged[key] = ch
            source_order[key] = (priority, source_name, is_personal)

    add_channels(parse_playlist(personal_text), "Personal", 0, is_personal=True)

    seen = set()
    for source in sources:
        if source in seen:
            continue
        seen.add(source)
        try:
            text = fetch(source)
        except Exception as exc:
            print(f"  [skip] {source}: {exc}", file=sys.stderr)
            continue
        channels = parse_playlist(text)
        if not channels:
            print(f"  [warn] {source}: no channels found", file=sys.stderr)
        label = labels.get(source, source)
        add_channels(channels, label, len(seen))

    groups = {}
    for key, ch in merged.items():
        priority, source_name, is_personal = source_order[key]
        if is_personal:
            group = ch.attrs_dict().get("group-title") or "Personal"
        else:
            group = source_name
        groups.setdefault(group, []).append((priority, ch, is_personal))

    return groups


def render_m3u8(groups):
    lines = ["#EXTM3U", ""]
    for group, items in groups.items():
        channels = sorted(items, key=lambda item: item[1].name.lower())
        lines.append(f"#GROUP-TITLE:{group}")
        for _, ch, is_personal in channels:
            attrs = ch.attrs if is_personal else combined_attrs(ch.attrs, group)
            lines.append(f"#EXTINF:-1{(' ' + attrs).rstrip()}")
            for directive in ch.directives:
                lines.append(directive)
            lines.append(ch.url)
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Merge IPTV playlists")
    parser.add_argument(
        "--sources", default=SOURCES_FILE, help="path to sources.txt"
    )
    parser.add_argument("--personal", default=PERSONAL_FILE, help="path to personal.m3u8")
    parser.add_argument("--output", default=OUTPUT_FILE, help="path to output file")
    args = parser.parse_args()

    with open(args.sources, encoding="utf-8") as fh:
        raw_lines = [line.strip() for line in fh if line.strip()]

    sources = []
    labels = {}
    current_label = None
    for line in raw_lines:
        if line.lstrip().startswith("#"):
            current_label = line.lstrip()[1:].strip() or current_label
        else:
            sources.append(line)
            labels[line] = normalize_label(current_label or os.path.basename(line))

    personal_text = ""
    if os.path.exists(args.personal):
        with open(args.personal, encoding="utf-8") as fh:
            personal_text = fh.read()

    print(f"Merging {len(sources)} sources...")
    groups = build_merged(sources, personal_text, labels=labels)

    total = sum(len(v) for v in groups.values())
    lines = [
        "#EXTM3U",
        f"# Merged by ChannelMerger",
        f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"# Sources: {len(sources)} | Channels: {total} | Groups: {len(groups)}",
        "",
    ]
    lines.extend(render_m3u8(groups).splitlines()[1:])

    with open(args.output, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"Done: {total} channels in {len(groups)} groups -> {args.output}")
    for group in groups:
        print(f"  {group}: {len(groups[group])} channels")


if __name__ == "__main__":
    main()
