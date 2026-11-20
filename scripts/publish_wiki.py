"""Publier les pages générées, sans supprimer les pages supplémentaires du wiki."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from .build_wiki import ROOT, REPOSITORY, build


def run(command, cwd=None, capture=False):
    return subprocess.run(command, cwd=cwd, check=True, text=True,
                          capture_output=capture, timeout=120)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--use-gh", action="store_true", help="Utiliser l'authentification existante de gh")
    args = parser.parse_args()
    auth = ["git"]
    if args.use_gh:
        auth += ["-c", "credential.helper=", "-c", "credential.helper=!gh auth git-credential"]
    revision = run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture=True).stdout.strip()
    if run(["git", "status", "--porcelain"], cwd=ROOT, capture=True).stdout.strip():
        raise SystemExit("Créer d'abord un commit des changements à publier : le dépôt doit être propre.")
    with tempfile.TemporaryDirectory(prefix="defis-wiki-") as folder:
        root = Path(folder)
        generated, checkout = root / "generated", root / "wiki"
        count = build(generated)
        run([*auth, "clone", REPOSITORY + ".wiki.git", str(checkout)])
        for source in generated.glob("*.md"):
            shutil.copy2(source, checkout / source.name)
        names = sorted(p.name for p in generated.glob("*.md"))
        run(["git", "add", "--", *names], cwd=checkout)
        changes = run(["git", "diff", "--cached", "--name-only"], cwd=checkout, capture=True).stdout
        if not changes.strip():
            print("Le wiki est déjà à jour.")
            return
        identity = ["git", "-c", "user.name=khkk24", "-c", "user.email=74632942+khkk24@users.noreply.github.com"]
        run([*identity, "commit", "-m", f"docs: publier le parcours depuis {revision[:12]}"], cwd=checkout)
        run([*auth, "push", "origin", "HEAD"], cwd=checkout)
        print(f"Wiki publié : {count} pages, source {revision}.")


if __name__ == "__main__":
    main()
