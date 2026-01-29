# Architecture YAML Protocols

Core protocols for Value-Continuous AI Development (VCAD).
This repository defines the decisions, boundaries, and connections that enable AI-driven coding while maintaining human governance.

## Core Protocols

The repository is organized into 5 main components:

| Protocol | Description | Links |
| :--- | :--- | :--- |
| **Decisions** | **Why / What**. Architectural decisions, policies, and tech stacks. | [README](decisions/README.md) |
| **Boundaries** | **Must / Must Not**. Invariant constraints, ownership boundaries, and strict rules. | [README](boundaries/README.md) |
| **Connections** | **How / Interface**. Inter-component connections, data flows, and API contracts. | [README](connections/README.md) |
| **Closures** | **If fails**. Error handling, recovery procedures, and responsibility closures. | [README](closures/README.md) |
| **Components** | **Where**. Maps the above rules to the actual codebase (file paths). | [README](components/README.md) |

## Legacy Collections

Previous design pattern collections (Logger design, API design, etc.) have been moved to `legacy/collection`.

- [Legacy Collections](legacy/collection/)

## Usage

When using AI agents for development:

1. **Decide**: Check `decisions` for architectural direction.
2. **Define**: Define specific rules in `boundaries`, `connections`, and `closures`.
3. **Assign**: Map these rules to file paths in `components`.

This allows AI to understand "where" and "under what rules" code should be written.
