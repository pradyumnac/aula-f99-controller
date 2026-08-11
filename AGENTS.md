# AGENTS.md

Custom control terminal ui software for the AULA F99 keyboard: replicate as much of the OEM software's customization as possible, targeting Windows now and Linux in the future.

## Mandatory invariants

- **STE100 (Simplified Technical English)**: all documentation, comments, commit messages, README content, CHANGELOG entries -- must follow the STE100 standard (simple English: short sentences, one instruction per sentence, approved/consistent vocabulary, active voice, no unnecessary jargon).
- **Documentation structure**: documentation must follow the Diataxis framework skill at [.agents/skills/docs-diataxis/SKILL.md](.agents/skills/docs-diataxis/SKILL.md). Follow it strictly -- classify new docs into the correct quadrant (tutorial/how-to/reference/explanation) before writing them.
- **Spec and feature decisions**: when reconciling specs or scoping features, ask one question at a time and wait for each answer -- do not batch multiple open decisions into one multi-question prompt.
