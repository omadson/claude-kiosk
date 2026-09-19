# Contributing

Feel free to open [issues](https://github.com/omadson/claude-kiosk/issues)
for bug reports, feature requests, and use-case demonstrations, and
pull requests for code (bug fixes, new features, docs).

## Steps

1. Fork the repository and clone your fork.

   ```bash
   git clone https://github.com/<you>/claude-kiosk
   cd claude-kiosk
   ```

2. Install dependencies and the pre-commit hooks.

   ```bash
   uv sync
   uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
   ```

   The hooks run `ruff` (lint + format), `mypy`, `interrogate`, and the
   test suite before every commit, and check the commit message format.

3. Create a branch for your change, named `fix/...`, `feature/...`,
   `docs/...`, etc. to match its type.

   ```bash
   git checkout -b feature/my-change
   ```

4. Make your change. The pre-commit hooks from step 2 already run
   `ruff`, `ruff-format`, `mypy`, `interrogate` and the test suite
   before each commit, so this step is optional; it just gives you
   faster feedback than waiting for the commit to fail.

   ```bash
   uv run pytest --cov=claude_kiosk
   uv run ruff check .
   uv run ruff format --check .
   ```

5. Commit using [Conventional Commits](https://www.conventionalcommits.org/)
   (`feat:`, `fix:`, `docs:`, etc.). `python-semantic-release` reads
   these to version releases and generate the changelog automatically.

6. Push your branch.

   ```bash
   git push -u origin feature/my-change
   ```

7. Open a pull request against `main`, from your fork on GitHub or
   with `gh pr create`. Structure the description with these sections:

   - **Summary**: what changed and why.
   - **Changes**: the main points, as a short bullet list.
   - **Testing**: how you verified it (tests added/run, manual steps).
   - **Closes**: the issue it closes, if any (`Closes #123`); omit if
     none.

8. CI validates commit messages and runs the same pre-commit checks on
   every pull request; make sure they're green before requesting review.
