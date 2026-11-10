# Run the idea list now

1. Unzip this kit into the root of the `campus-publication` repo (it adds `.claude/agents/`, `.claude/skills/`, `schemas/`, `scripts/validate_handoff.py`, `IDEAS.md`).
2. Open Claude Code in the repo: `claude --model fable`
3. Paste this prompt:

```
Load the idea-runner skill and work through IDEAS.md wave by wave. Prepare each topic's facts.csv first as the skill says, then keep five writer subagents running at all times. Rewrite live pages instead of duplicating them, apply the entity bar, build calculators for TOOL ideas, and hold DATA ideas until their data exists (start the Ithaca apartment inventory during wave 1). Check every page with page_check.py and match_facts.py, send failures to the editor or checker once, and keep IDEAS-STATUS.md updated. Save everything to review/<topic>/. Do not publish anything. Don't stop to ask me questions; make the call the skills describe and note it in IDEAS-STATUS.md.
```

4. Keep the laptop plugged in with the lid open. Check `IDEAS-STATUS.md` whenever you want progress. If Claude Code stops for a usage limit, paste "Continue the idea list from IDEAS-STATUS.md" once it resets.
