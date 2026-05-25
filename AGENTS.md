# AGENTS.md

## Project Profile

`mapck` is a lightweight browser-based geography quiz app. It is currently a static frontend with no build system and no backend.

The app focuses on map knowledge practice through:

- country identification from pointed map images
- numbered-map identification questions
- capital city recall
- reverse-capital questions
- region-based quiz sets
- score history stored in browser `localStorage`

Current content is driven by `data/index.json` plus one JSON file per region under `data/regions/`, with a legacy fallback to `data/regions.json`. Map assets live under `maps/`.

## Tech Stack

- `index.html`: single-page app shell
- `css/styles.css`: all styling
- `js/app.js`: UI orchestration and event wiring
- `js/quizEngine.js`: question generation and answer validation
- `js/regionManager.js`: region data loading and lookup
- `js/scoreTracker.js`: score persistence, import/export, timer helpers
- `data/index.json`: manifest of available region files
- `data/regions/*.json`: source of truth for individual region content
- `data/regions.json`: legacy fallback format

This repo uses native ES modules in the browser. There is no bundler, framework, package manager, or automated test setup at the moment.

## Run Instructions

Use a local HTTP server so `fetch(...)` works for region manifests and JSON files:

```bash
cd /Users/allenlsy/project/mapck
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

Opening `index.html` directly may fail or behave inconsistently because region data is loaded through `fetch`.

## How The App Works

1. `App.init()` loads saved scores, fetches region data, binds DOM events, and enables quiz setup.
2. Starting a quiz calls `QuizEngine.initQuiz(regionId, mode, questionCount)`.
3. `RegionManager` loads regions from `data/index.json` and `data/regions/*.json`, falling back to `data/regions.json` if needed.
4. The engine generates question types from each region's `questionTypes` config.
   Common supported types:
   - `pointed_country`
   - `capital`
   - `reverse_capital`
   - `numbered_region`
5. Answers are scored through `ScoreTracker`.
6. Results and quiz history are persisted in browser storage under the key `mapck_scores`.

## Content Model

Region manifests live under `data/index.json` as:

```json
{
  "regions": [
    {
      "id": "region_id",
      "file": "regions/region_id.json"
    }
  ]
}
```

Each region file under `data/regions/` contains a single region object:

```json
{
  "id": "region_id",
  "name": "Region Name",
  "mapImage": "maps/region.jpg",
  "entityLabel": "country",
  "numberedMapImage": "maps/region/numbered_map.png",
  "questionTypes": ["pointed_country", "capital", "reverse_capital"],
  "countries": []
}
```

Country objects currently support:

- `id`
- `name`
- `capital`
- `alternateNames`
- `alternateCapitals`
- optional `mapNumber`
- `pointed_country`
- optional `questionImages`

Important: the current code prefers `country.pointed_country` for pointed-country questions. `questionImages` is supported as a fallback/backward-compatible structure, not the primary structure used in the current dataset.

## Current Conventions

- Default map image for capital-based questions comes from `region.mapImage`.
- Pointed-country questions usually use a country-specific image.
- Answer matching is case-insensitive and punctuation-insensitive.
- Fuzzy matching exists, but the current threshold is strict in code despite comments suggesting otherwise. If changing answer validation, verify behavior carefully in the browser.
- Score import/export format is JSON shaped like `{ "scores": [...] }`.

## Guidance For Future Work

Prefer small, data-driven additions over hardcoding quiz content into JavaScript.

Good next extensions for this project:

- add more regions and world subregions
- add US states and capitals as a separate region family
- add more question types without breaking existing JSON
- improve image organization and naming consistency
- add lightweight browser-based tests for quiz generation and answer validation

When adding new quiz datasets:

- prefer one file per region under `data/regions/` and keep `data/index.json` in sync
- reuse the existing region/country schema where possible
- preserve alternate-name support for accepted answers
- prefer stable asset paths and consistent file naming

## Guidance For Coding Agents

- Preserve the no-build static-app workflow unless there is a strong reason to introduce tooling.
- Keep dependencies to zero or near-zero unless the user explicitly wants a more complex stack.
- Verify UI behavior in a browser after meaningful frontend or quiz-logic changes.
- If you change the data schema or manifest layout, update both the code and the documentation in `README.md`.
- Be careful not to break existing regions when adding new content types such as US states.
- Treat `data/index.json`, `data/regions/*.json`, and asset paths as user-maintained content; avoid mass reformatting unless requested.

## Known Code Notes

- `js/quizEngine.js` currently contains the core question-generation rules and answer matching logic.
- The app assumes browser APIs such as `fetch`, `localStorage`, `Blob`, and `FileReader`.
- There is no formal linting or test command yet, so manual verification is important.

## File Choice

For this repo, `AGENTS.md` is the right place for Codex/OpenAI coding-agent instructions.

`CLAUDE.md` is commonly used for Claude-specific repo guidance, but it is separate rather than universal. If you want to support multiple coding assistants, it is reasonable to keep:

- `AGENTS.md` for Codex/OpenAI-style agents
- `CLAUDE.md` for Claude

with mostly shared content adapted to each tool's conventions.
