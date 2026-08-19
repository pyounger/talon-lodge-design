# Talon Lodge — Design & Mockups

Interactive HTML mockups for the new Talon Lodge & Spa platform, plus the
design/spec documents behind them. This is the **design & collaboration** repo;
the running system is split across:

- **talon-lodge-api** — Laravel backend (the real data model + engine)
- **talon-lodge-ui** — Angular front end
- **talon-lodge-design** — *this repo:* mockups + design docs

## Start here

Open **[test-hub.html](test-hub.html)** in a browser — it's the launcher for all
~37 prototype tools (guest profiles & flights, fish processing, room and boat
assignments, meal/beverage orders, the evening display, massage scheduling,
booking engine, and more). Everything runs client-side (localStorage +
IndexedDB), no server needed.

## Design docs

Schema and rules that the api implements: `DB_SCHEMA.md`,
`DATABASE_DESIGN.md`, `MATCHING_RULES.md`, `MERGE_RULES.md`,
`RECORD_MANAGEMENT.md`, `UI_MAPPING.md`, `MODULE_ROADMAP.md`,
`DEVELOPER_TASKS.md`, `PROTOTYPE_BUILD_LOG.md`.

> These mockups are the reference for behavior and screens; when the prototype
> and the docs disagree, the prototype is the source of truth for intended UX.
