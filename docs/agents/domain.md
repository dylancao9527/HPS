# Domain Docs

This repo uses a single-context domain documentation layout.

## Before exploring, read these

- `CONTEXT.md` at the repo root, if it exists.
- `docs/adr/`, if it exists.
- `docs/architecture/ARCHITECTURE.md` for the current system architecture.

If any of these files do not exist, proceed silently. Do not suggest creating them upfront unless the task is specifically about clarifying domain language or architectural decisions.

## Current domain summary

This is a high blood pressure risk prediction and health management system. It uses a Flask API, MySQL persistence, React frontend, Prophet for blood pressure trend prediction, and LightGBM for risk classification.

The system is a health-management aid, not a clinical diagnosis system.

## Expected layout

```text
/
├── CONTEXT.md
└── docs/
    ├── adr/
    └── architecture/
        └── ARCHITECTURE.md
```

## Vocabulary rule

When naming domain concepts in issues, tests, refactors, or diagnosis notes, prefer the project vocabulary from `CONTEXT.md` and `docs/architecture/ARCHITECTURE.md`.
