"""Generated with Anthropic Claude Sonnet 5.5

Utility: extend type_fields.json with the fields of composite data types.

Connects to a Zurich Instruments device, subscribes to all readable nodes
whose type is composite (ZIDemodSample, ZIVectorData, ...) and records the
keys of the data that actually arrives. Only types that are NOT yet in the
JSON file are added. Existing entries are never modified or removed.

Sources that are inactive while polling (disabled demodulator, scope without
trigger, ...) deliver nothing and stay unknown. Enable them and run the
script again.

Usage:
    python update_type_fields.py --device dev3206
    python update_type_fields.py --device dev3206 --seconds 2 --dry-run
"""

import argparse
import json
import sys
from pathlib import Path

import zhinst.core as zi

DEFAULT_CACHE = Path(__file__).with_name("type_fields.json")


def flatten(d: dict, prefix: str = "") -> dict:
    """{'time': {'dataloss': False}} -> {'time/dataloss': False}"""
    out = {}
    for key, value in d.items():
        if isinstance(value, dict):
            out.update(flatten(value, f"{prefix}{key}/"))
        else:
            out[f"{prefix}{key}"] = value
    return out


def load_cache(path: Path) -> dict[str, list[str]]:
    """Load the JSON file; an unreadable file aborts instead of being overwritten."""
    if not path.exists():
        return {}
    try:
        cache = json.loads(path.read_text())
    except json.JSONDecodeError as err:
        sys.exit(f"{path} is not valid JSON ({err}). Nothing was changed.")
    if not isinstance(cache, dict):
        sys.exit(f"{path} does not contain a JSON object. Nothing was changed.")
    return cache


def composite_nodes(daq: zi.ziDAQServer, dev: str) -> dict[str, list[str]]:
    """Readable nodes with a composite type, grouped by type name."""
    paths = daq.listNodes(f"/{dev}/*", 7)  # recursive | absolute | leaves only
    info = json.loads(daq.listNodesJSON(f"/{dev}/*"))  # keys are lowercase
    by_type: dict[str, list[str]] = {}
    for path in paths:
        path = path.lower()  # poll() returns lowercase paths as well
        props = info.get(path, {})
        node_type = props.get("Type", "")
        if node_type.startswith("ZI") and "Read" in props.get("Properties", ""):
            by_type.setdefault(node_type, []).append(path)
    return by_type


def learn(
    daq: zi.ziDAQServer, candidates: dict[str, list[str]], seconds: float
) -> dict[str, list[str]]:
    """Subscribe to all candidate nodes at once and read the keys of the data."""
    paths = [p for plist in candidates.values() for p in plist]
    for path in paths:
        daq.subscribe(path)
    try:
        data = daq.poll(seconds, 500, 0, True)
    finally:
        for path in paths:
            daq.unsubscribe(path)

    learned: dict[str, list[str]] = {}
    for node_type, plist in candidates.items():
        for path in plist:  # first node of this type that delivered data wins
            sample = data.get(path)
            if isinstance(sample, list):  # some types arrive as a list of chunks
                sample = sample[0] if sample else None
            if isinstance(sample, dict):
                learned[node_type] = list(flatten(sample))
                break
    return learned


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--device", default="dev3206", help="device serial, e.g. dev3206")
    parser.add_argument("--host", default="localhost", help="Data Server host")
    parser.add_argument("--port", type=int, default=8004, help="Data Server port")
    parser.add_argument("--api-level", type=int, default=6)
    parser.add_argument("--seconds", type=float, default=1.0, help="poll duration")
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE, help="JSON file")
    parser.add_argument("--dry-run", action="store_true", help="report only, do not write")
    args = parser.parse_args()

    cache = load_cache(args.cache)

    daq = zi.ziDAQServer(args.host, args.port, args.api_level)
    by_type = composite_nodes(daq, args.device)
    if not by_type:
        sys.exit("No readable composite nodes found on this device.")

    known = sorted(t for t in by_type if t in cache)
    candidates = {t: p for t, p in by_type.items() if t not in cache}
    print(f"Composite types on device : {', '.join(sorted(by_type))}")
    print(f"Already in {args.cache.name:<14}: {', '.join(known) or '-'} (left untouched)")

    if not candidates:
        print("Nothing to learn.")
        return

    learned = learn(daq, candidates, args.seconds)
    missing = sorted(set(candidates) - set(learned))

    for node_type, fields in learned.items():
        print(f"\nNEW {node_type} ({len(fields)} fields): {', '.join(fields)}")
    if missing:
        print(
            "\nNo data received for: " + ", ".join(missing)
            + "\n -> enable the sources (e.g. demods/n/enable) and run again."
        )

    if not learned:
        return
    if args.dry_run:
        print("\nDry run: file not written.")
        return

    merged = dict(cache)  # existing entries stay exactly as they are
    for node_type, fields in learned.items():
        merged.setdefault(node_type, fields)
    args.cache.write_text(json.dumps(merged, indent=2))
    print(f"\nAdded {len(learned)} type(s) to {args.cache}")


if __name__ == "__main__":
    main()
