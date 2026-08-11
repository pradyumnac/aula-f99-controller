# AGENTS.md

Custom control terminal ui software for the AULA F99 keyboard: replicate as much of the OEM software's customization as possible, targeting Windows now and Linux in the future.

## Mandatory invariants

- **STE100 (Simplified Technical English)**: all documentation, comments, commit messages, README content, CHANGELOG entries -- must follow the STE100 standard (simple English: short sentences, one instruction per sentence, approved/consistent vocabulary, active voice, no unnecessary jargon).
- **Documentation structure**: documentation must follow the Diataxis framework skill at [.agents/skills/docs-diataxis/SKILL.md](.agents/skills/docs-diataxis/SKILL.md). Follow it strictly -- classify new docs into the correct quadrant (tutorial/how-to/reference/explanation) before writing them.
- **Spec and feature decisions**: when reconciling specs or scoping features, ask one question at a time and wait for each answer -- do not batch multiple open decisions into one multi-question prompt.
- **Document roles (DRY)**: each doc below owns one kind of content. State a fact once, in its owning doc, and link to it from everywhere else -- never copy the fact across files. If you find existing duplication, propose the fix and get it approved change by change; do not clean it up silently.
- **No history in the repo**: never track history or migrations in code, comments, or docs. When a file, module, or process is retired, purge it completely -- delete it, remove every reference. No "formerly X", "replaces old Y", "used to be Z" notes. Comments and docs capture only the current state of the system; `git log` is where change history belongs.
- **Concise code comments**: comments must be terse and state only what can't be inferred from the code. Only public functions/interfaces get a comment at all, and it's mandatory-minimum: what it does, non-obvious conditions. Never detailed prose or narrative docstrings.
- **Advisor review before commit**: before every commit, ask the user whether they want the code reviewed by an advisor (code review) first, and wait for their answer -- do not commit until asked. This rule is not skippable. The only exception: the user explicitly says not to use the advisor and to commit directly -- then commit without review.

| Document | Owns |
| --- | --- |
| `README.md` | User-facing introduction only |
| `docs/spec.md` | Project facts: modules, CLI reference, mise tasks, toolchain |
| `docs/tui-spec.md` | TUI structure and design: layout, sections list, modals, theme, key-binding mechanics, slices |
| `docs/feature-tracking.md` | Per-feature status, write-need, TUI location, and CLI switch -- one row per feature |
| `docs/reference/f99/hardware.md` | Physical device facts: layout, switch, ports, indicators, battery |
| `docs/reference/f99/keybindings.md` | The keyboard's own factory `FN` shortcuts |
| `docs/reference/f99/protocol.md` | USB protocol: device IDs, packet format, captured commands |
| `docs/reference/f99/gui-features.md` | OEM software feature baseline |
| `docs/unresolved.md` | Known bugs and gaps not fixed yet, and why |
| `CHANGELOG.md` | Change history |
