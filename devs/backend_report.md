# Backend Report

`yasched` is a YAML-first scheduling backend. Its job is to take a set of human-written YAML files describing `topics`, `tasks`, `events`, and `layouts`, turn them into a consistent in-memory model, and expose a clean query API that other interfaces can use.

At a big-picture level, the backend is a pipeline with four stages:

1. `XymlLoader` reads YAML from disk and supports splitting one database across multiple files.
2. `DatabaseParser` converts the raw YAML data into plain domain objects.
3. `DatabaseManager` validates the data, checks references and consistency, and resolves links between objects.
4. `DatabaseInterface` provides a read-only service layer for queries like schedules, deadlines, topic trees, blocked tasks, and conflicts.

## Important actors

- `Database`
  The raw container after parsing. It holds plain lists of `Layout`, `Topic`, `Event`, and `Task`, and is still close to the YAML structure.
- `ResolvedDatabase`
  The enriched version produced after validation and reference resolution. It replaces string references with real linked objects and adds computed data.
- `DatabaseLoader`
  The main file I/O entry point. It loads from YAML into a `Database`, and can save a database back to YAML.
- `DatabaseParser`
  The component that understands the YAML schema and builds the core scheduling objects from raw dictionaries.
- `DatabaseManager`
  The integrity gatekeeper. It detects duplicate IDs, missing references, invalid time logic, and cycles, and computes inherited or effective values like layout, tags, and deadlines.
- `DatabaseInterface`
  The backend API used by CLI and UI layers. It answers higher-level questions such as what happens on a given day or week, which tasks are overdue or blocked, which events fall in a range, and how topics and tasks are organized.

## Core domain model

The backend revolves around four main business entities:

- `Topic`
  Organizes the knowledge and work hierarchy, with parent-child relationships.
- `Task`
  Represents work to do. Tasks can belong to topics, link to events, depend on other tasks, and inherit metadata.
- `Event`
  Represents scheduled items with time information. Events belong to a topic and can affect tasks.
- `Layout`
  Stores visual and styling metadata shared by tasks, events, and topics. It is part of the stored model, but not the main business logic.

## How the backend works conceptually

The backend separates data into two layers:

- Raw objects: simple parsed records from YAML.
- Resolved objects: connected, validated, query-ready objects.

That separation keeps parsing simple and moves all smart behavior to the validation and resolution stage. Once data is resolved, the rest of the system can work with reliable linked objects instead of manually chasing IDs.

## Main responsibility

The backend is responsible for:

- loading structured schedule data from YAML,
- validating that the database makes sense,
- resolving relationships across tasks, topics, and events,
- computing useful derived values,
- serving as the source of truth for higher-level consumers.

## Short framing for another AI

`yasched` backend is a YAML-driven data engine for scheduling. It loads human-authored schedule files, parses them into domain objects, validates and resolves all references, and exposes a query layer that powers tools like the CLI and UI.
