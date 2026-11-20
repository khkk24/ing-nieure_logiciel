"""Vérifier les liens locaux et les destinations des pages générées, sans réseau."""
from pathlib import Path
import re
import tempfile
from urllib.parse import unquote, urlsplit
from .build_wiki import ROOT, PAGES, WIKI, build


def main():
    errors = []
    count = 0
    for base in (ROOT / "cours", ROOT / "ressources", ROOT / "ateliers", ROOT / "docs"):
        for path in base.rglob("*.md"):
            count += 1
            check_file(path, errors)
    for path in (ROOT / "README.md", ROOT / "CONTRIBUTING.md"):
        count += 1
        check_file(path, errors)
    known = set(PAGES.values()) | {"_Sidebar", "_Footer"}
    with tempfile.TemporaryDirectory(prefix="wiki-check-") as folder:
        generated = build(folder)
        for path in Path(folder).glob("*.md"):
            for target in re.findall(r"\]\(([^\s)]+)\)", path.read_text(encoding="utf-8")):
                if target.startswith(WIKI + "/"):
                    page = urlsplit(target).path.rsplit("/", 1)[-1]
                    if page not in known:
                        errors.append(f"Page wiki absente : {page}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"OK : {count} sources Markdown et {generated} pages wiki ; liens locaux valides.")


def check_file(path, errors):
    text = path.read_text(encoding="utf-8")
    if sum(line.startswith("```") for line in text.splitlines()) % 2:
        errors.append(f"Bloc de code non fermé : {path.relative_to(ROOT)}")
    for target in re.findall(r"\]\(([^\s)]+)\)", text):
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or target.startswith("#"):
            continue
        destination = (path.parent / unquote(parsed.path)).resolve()
        if not destination.is_relative_to(ROOT) or not destination.exists():
            errors.append(f"Lien local absent ou hors dépôt : {path.relative_to(ROOT)} -> {target}")


if __name__ == "__main__":
    main()
