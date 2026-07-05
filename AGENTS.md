# SDD Enterprise Policy

This repository MUST use the installed SDD Enterprise workflow.

Never implement features directly.

For every development request, use the installed Speckit skills in this order:

1. speckit-clarify (only if requirements are ambiguous)
2. speckit-constitution
3. speckit-specify
4. speckit-plan
5. speckit-tasks
6. speckit-implement

Rules:

- Never skip a phase.
- Never generate implementation before specification and planning.
- Always use the installed project Skills under `.agents/skills/`.
- Follow the repository constitution and project memory.
- Keep every artifact synchronized with SDD Enterprise.