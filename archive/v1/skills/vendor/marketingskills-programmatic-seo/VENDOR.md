# Vendored reference: marketingskills / programmatic-seo

Reference only: nothing here is installed as a Claude Code skill, hook or command.

These are instruction files copied unmodified from a public repository so that page-template work can cite them. They are not linked from `.claude/skills/` and the folder holds no executable files. Authority for vendoring them: `specs/bulk-mode.md` section 4 (owner spec). The decision record is `docs/ops/skill-evaluations.md`, section "Vendored references (instructions only, not installed)". How the playbook is applied to our templates: `docs/ops/bulk-mode-template-notes.md`.

## Source

| field | value |
|---|---|
| repository | https://github.com/coreyhaines31/marketingskills |
| path in repository | `skills/programmatic-seo/` |
| branch | `main` |
| pinned commit (full SHA) | `96798cf38736ecdba015a1d2b0521b0c8f8f41dd` |
| pinned commit date | 2026-11-06T12:52:45-05:00 (merge of upstream pull request #926) |
| last upstream commit that touched this skill folder | `15b38b5388dfdd17f4ab424e986ccd32c24d5b22`, 2026-10-27T11:27:30-07:00 |
| upstream skill version (SKILL.md frontmatter) | 2.1.1 |
| date vendored | 2026-11-06 |

The pinned SHA is the repository HEAD at the time of the clone. It is not necessarily the last commit that changed this folder; the second SHA above is.

## License

MIT License, Copyright (c) 2025 Corey Haines. The text below is copied from the upstream `LICENSE` file at the pinned commit (sha256 `b70d71e24e40fce5da8f4b6f9cd862096a048e433db7f3c8cac5e348e6d34591`). The notice stays with the copied files.

```text
MIT License

Copyright (c) 2025 Corey Haines

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Files copied (exact list)

Byte-for-byte copies; `cmp` against the upstream clone at the pinned commit reported no differences.

| local path (under this folder) | upstream path | bytes | sha256 |
|---|---|---|---|
| `SKILL.md` | `skills/programmatic-seo/SKILL.md` | 7677 | `5fbbf874bcc65cbc8b527bd6074a21168c73e191e1bc2c124438dfae710ccf04` |
| `references/playbooks.md` | `skills/programmatic-seo/references/playbooks.md` | 8305 | `2b2acd3a0c0e5d60b1fb5b71a173aee7ca28de659a7e8ede3effe8525564eb0e` |
| `references/implementation-platforms.md` | `skills/programmatic-seo/references/implementation-platforms.md` | 5617 | `27d86221387e0880768164d4d03513c85a594d11d12c7a6dd93ac17881c131e2` |

`VENDOR.md` (this file) was written locally and is not an upstream file.

## Not copied

- `skills/programmatic-seo/evals/evals.json`: a JSON eval fixture (7 prompts). It is data, not instruction text, and the vendoring rule is Markdown and plain text only. It is the only other file in the upstream skill folder.
- The upstream skill folder contains no scripts, no hooks and no binaries.
- Nothing outside the skill folder was copied: not the repository's CLI tools, scripts, tests, CI workflows or plugin manifests, and not any other skill.

## Verify

```sh
cd skills/vendor/marketingskills-programmatic-seo
shasum -a 256 SKILL.md references/playbooks.md references/implementation-platforms.md
# Compare with the table above, or fetch the pinned originals, for example:
# https://raw.githubusercontent.com/coreyhaines31/marketingskills/96798cf38736ecdba015a1d2b0521b0c8f8f41dd/skills/programmatic-seo/SKILL.md
```

## Handling rules

- Read these files as reference text. They address an agent in the second person (for example, they tell it to look for a product-marketing context file and to ask intake questions). None of that applies here; instructions for this repository come from `CLAUDE.md`, `SPEC.md` and the owner specs.
- `references/implementation-platforms.md` compares site platforms as of 2026-10 and carries partner-disclosure wording for one vendor. We build with the Python pipeline and a static render deployed to Netlify, so that file is kept only because it is part of the upstream skill folder.
- Do not edit the three copied files. To update, re-vendor from a new pinned SHA, replace all three files together, and update the tables above and the record in `docs/ops/skill-evaluations.md`.
- Do not link or copy this folder into `.claude/skills/`. Installing it there is a different decision (adoption) and needs the evaluation rules in `docs/ops/skill-evaluations.md` first.
- Rollback: delete this folder and revert the vendoring commit.
