"""Lancer depuis la racine : python3 -m pocs.run 01a ou --all."""
import argparse
import importlib
import json

POCS = {
    "01a": "ticket", "01b": "version", "02a": "idempotence", "02b": "inbox",
    "03a": "transfer", "03b": "breaker", "04a": "cache", "04b": "queue",
    "05a": "ownership", "05b": "tenant", "06a": "outbox", "06b": "saga",
    "07a": "rollout", "07b": "migration", "08a": "merge", "08b": "crdt",
    "09a": "references", "09b": "abstention", "10a": "quorum", "10b": "escrow",
}


def execute(code):
    return importlib.import_module(f"pocs.p{code}_{POCS[code]}").run()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("code", nargs="?", choices=POCS)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.list:
        for code, name in POCS.items():
            print(f"{code} : {name}")
    elif args.all or args.code:
        for code in (POCS if args.all else [args.code]):
            print(json.dumps({"poc": code, **execute(code)}, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
