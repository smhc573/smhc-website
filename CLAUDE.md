# St Matthews Healthcare website

This `main` branch is exactly what is live on https://smhc.uk.com. Blue Moon Solutions sync it
to the web host. Never edit or commit to `main` by hand.

All work happens on the `source` branch, which holds the content, build scripts, photographs,
brochures and the full instructions in its own CLAUDE.md:

    git fetch origin source
    git checkout -b source origin/source

Then follow CLAUDE.md on that branch. Changes are published with
`python3 source/publish.py "what changed"`, which rebuilds the site, updates `main` and pushes.
