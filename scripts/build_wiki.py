"""Générer le wiki GitHub à partir des cours : python3 -m scripts.build_wiki."""
import argparse
from pathlib import Path
import re
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/khkk24/ing-nieure_logiciel"
WIKI = REPOSITORY + "/wiki"
PAGES = {
    "docs/wiki/Home.md": "Home",
    "docs/wiki/Parcours.md": "Parcours",
    "docs/wiki/Index-POC.md": "Index-POC",
    "docs/wiki/Maintenance.md": "Maintenance",
    "cours/00-fondations.md": "00-Fondations",
    "cours/01-concurrence.md": "01-Concurrence",
    "cours/02-idempotence.md": "02-Idempotence",
    "cours/03-resilience.md": "03-Resilience",
    "cours/04-scalabilite.md": "04-Scalabilite",
    "cours/05-securite.md": "05-Securite",
    "cours/06-fiabilite.md": "06-Fiabilite",
    "cours/07-deploiement.md": "07-Deploiement",
    "cours/08-synchronisation.md": "08-Synchronisation",
    "cours/09-fiabilite-ia.md": "09-Fiabilite-IA",
    "cours/10-systemes-distribues.md": "10-Systemes-distribues",
    "ressources/architecture.md": "Architecture",
    "ressources/glossaire.md": "Glossaire",
    "ressources/sources.md": "Sources",
    "ressources/projet-final.md": "Projet-final",
    "ressources/compte-rendu.md": "Compte-rendu",
    "ressources/validation.md": "Validation",
    "ateliers/README.md": "Ateliers",
    "ateliers/postgresql/README.md": "Atelier-PostgreSQL",
    "ateliers/kubernetes/README.md": "Atelier-Kubernetes",
}
ORDER = ["00-Fondations", "01-Concurrence", "02-Idempotence", "03-Resilience",
         "05-Securite", "06-Fiabilite", "04-Scalabilite", "07-Deploiement",
         "08-Synchronisation", "10-Systemes-distribues", "09-Fiabilite-IA"]
LINK = re.compile(r"(?<!!)\[([^\]\n]+)\]\(([^\s)]+)\)")


def rewrite_link(source, target):
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or target.startswith("#"):
        return target
    resolved = (ROOT / source).parent.joinpath(parsed.path).resolve()
    relative = resolved.relative_to(ROOT).as_posix()
    if not resolved.exists():
        raise ValueError(f"Lien absent dans {source} : {target}")
    if relative in PAGES:
        result = f"{WIKI}/{PAGES[relative]}"
    else:
        kind = "tree" if resolved.is_dir() else "blob"
        result = f"{REPOSITORY}/{kind}/main/{quote(relative)}"
    if parsed.query:
        result += "?" + parsed.query
    if parsed.fragment:
        result += "#" + parsed.fragment
    return result


def render(source, content):
    lines = []
    fence = None
    # Les commandes dans les blocs de code ne sont pas transformées.
    for line in content.splitlines(keepends=True):
        stripped = line.lstrip()
        marker = stripped[:3]
        if marker in ("```", "~~~"):
            fence = None if fence == marker else (marker if fence is None else fence)
            lines.append(line)
        elif fence:
            lines.append(line)
        else:
            lines.append(LINK.sub(lambda m: f"[{m[1]}]({rewrite_link(source, m[2])})", line))
    return "".join(lines)


def build(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for source, name in PAGES.items():
        content = render(source, (ROOT / source).read_text(encoding="utf-8"))
        content += f"\n---\n\n[Accueil]({WIKI}/Home) · [Parcours]({WIKI}/Parcours) · "
        content += f"[Source à modifier]({REPOSITORY}/blob/main/{quote(source)})\n"
        if name in ORDER:
            index = ORDER.index(name)
            if index:
                content += f"\n[← Étape précédente]({WIKI}/{ORDER[index - 1]})"
            if index + 1 < len(ORDER):
                content += f"\n[Étape suivante →]({WIKI}/{ORDER[index + 1]})"
            content += "\n"
        (output / f"{name}.md").write_text(content, encoding="utf-8")
    sidebar = "## Commencer\n\n"
    for name in ("Home", "Parcours", "Index-POC"):
        sidebar += f"- [{name.replace('-', ' ')}]({WIKI}/{name})\n"
    sidebar += "\n## Cours — ordre conseillé\n\n"
    for name in ORDER:
        sidebar += f"- [{name.replace('-', ' ')}]({WIKI}/{name})\n"
    sidebar += "\n## Pratiquer et approfondir\n\n"
    for name in ("Architecture", "Ateliers", "Atelier-PostgreSQL", "Atelier-Kubernetes",
                 "Projet-final", "Compte-rendu", "Glossaire", "Sources", "Validation", "Maintenance"):
        sidebar += f"- [{name.replace('-', ' ')}]({WIKI}/{name})\n"
    (output / "_Sidebar.md").write_text(sidebar, encoding="utf-8")
    (output / "_Footer.md").write_text(
        f"[Code source]({REPOSITORY}) · [Tests automatiques]({REPOSITORY}/actions) · "
        f"[Signaler un problème]({REPOSITORY}/issues)\n\n"
        "Les POC sont pédagogiques. Les simulations et ateliers non validés sont identifiés dans les cours.\n",
        encoding="utf-8",
    )
    return len(PAGES) + 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/wiki")
    args = parser.parse_args()
    print(f"{build(args.output)} pages générées dans {args.output}")


if __name__ == "__main__":
    main()
