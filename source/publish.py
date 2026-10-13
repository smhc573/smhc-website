"""Rebuild the St Matthews Healthcare website and publish it.

The repository has two branches:
  source  the content, build scripts, photographs and brochures (this branch)
  main    exactly the files that are live on smhc.uk.com. The web host syncs this branch.

Run from anywhere inside the repository, on the source branch:
  python3 source/publish.py "What changed, in a few words"

It rebuilds site/ from source/data.py, commits the source branch, copies site/ into the
main branch, commits and pushes both. Add --no-push to try it without publishing.
"""
import os, sys, shutil, subprocess, tempfile

KEEP = {".git", "README.md"}   # files on main that are not part of the website build


def run(*cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if check and r.returncode != 0:
        sys.exit(f"{' '.join(cmd)} failed:\n{r.stdout}{r.stderr}")
    return r.stdout.strip()


def mirror(src, dst):
    """Make dst hold exactly what src holds, apart from the KEEP items at the top level."""
    for root, dirs, files in os.walk(dst, topdown=True):
        rel = os.path.relpath(root, dst)
        if rel == ".":
            dirs[:] = [d for d in dirs if d not in KEEP]
            files = [f for f in files if f not in KEEP]
        for f in files:
            if not os.path.exists(os.path.join(src, rel, f)):
                os.remove(os.path.join(root, f))
        for d in list(dirs):
            if not os.path.isdir(os.path.join(src, rel, d)):
                shutil.rmtree(os.path.join(root, d))
                dirs.remove(d)
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        target = dst if rel == "." else os.path.join(dst, rel)
        os.makedirs(target, exist_ok=True)
        for f in files:
            shutil.copy2(os.path.join(root, f), os.path.join(target, f))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    push = "--no-push" not in sys.argv
    message = args[0] if args else "Website update"
    top = run("git", "rev-parse", "--show-toplevel")
    if run("git", "rev-parse", "--abbrev-ref", "HEAD", cwd=top) != "source":
        sys.exit("Switch to the source branch first: git checkout source")
    print("Rebuilding the website...")
    print(run(sys.executable, os.path.join(top, "source", "launch.py"), cwd=top))
    run("git", "add", "-A", cwd=top)
    if run("git", "status", "--porcelain", cwd=top):
        run("git", "commit", "-m", message, cwd=top)
    work = tempfile.mkdtemp(prefix="smhc-main-")
    run("git", "worktree", "add", "--force", work, "main", cwd=top)
    try:
        mirror(os.path.join(top, "site"), work)
        run("git", "add", "-A", cwd=work)
        if run("git", "status", "--porcelain", cwd=work):
            src = run("git", "rev-parse", "--short", "HEAD", cwd=top)
            run("git", "commit", "-m", f"Publish: {message} (from source {src})", cwd=work)
            print("main updated.")
        else:
            print("The live files have not changed, so there is nothing new to publish.")
    finally:
        run("git", "worktree", "remove", "--force", work, cwd=top, check=False)
    if push:
        run("git", "push", "origin", "main", "source", cwd=top)
        print("Pushed. The web host picks up main and the change goes live.")


if __name__ == "__main__":
    main()
