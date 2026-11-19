#!/usr/bin/env python3
"""Generate the domain example notebooks under ``examples/notebooks/``.

Each notebook mirrors one of the runnable domain examples in ``examples/`` and
follows the same six-step workflow:

1. create a collection with a schema
2. generate and send sensor data
3. query data with domain-specific filters
4. compute statistics
5. delete a time window for one entity
6. clean up the collection

The collection schema and the data generator are extracted directly from the
example script with :mod:`ast`, so the notebook can never drift from the script
it documents. Only the queries/statistics are declarative (the example scripts
use a few legacy API shapes that the current SDK no longer exposes).

Usage::

    python scripts/generate_example_notebooks.py
"""

from __future__ import annotations

import ast
import json
import textwrap
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = ROOT / "examples" / "notebooks"

ENV_TABLE = """\
| Variable | Purpose |
|----------|---------|
| `NOSTRADAMUS_PROJECT_ID` | Target project UUID |
| `NOSTRADAMUS_MASTER_KEY` | Master key (create/delete collection, delete data) |
| `NOSTRADAMUS_WRITE_KEY` | Write key (send data) |
| `NOSTRADAMUS_READ_KEY` | Read key (query data and statistics) |
| `NOSTRADAMUS_BASE_URL` | Optional API base URL override |"""


def _source(text: str) -> list[str]:
    block = textwrap.dedent(text).strip("\n")
    lines = block.split("\n")
    return [line + "\n" for line in lines[:-1]] + [lines[-1]]


def _md(text: str) -> dict[str, Any]:
    return {"cell_type": "markdown", "metadata": {}, "source": _source(text)}


def _code(text: str) -> dict[str, Any]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": _source(text),
    }


def _notebook(cells: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def _parse(path: Path) -> tuple[str, ast.Module]:
    source = path.read_text(encoding="utf-8")
    return source, ast.parse(source)


def _module_constant(source: str, name: str) -> str:
    _, tree = _parse(ROOT / source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == name for t in node.targets
        ):
            segment = ast.get_source_segment(_parse(ROOT / source)[0], node)
            return textwrap.dedent(segment)
    raise LookupError(f"{name} not found at module level in {source}")


def _generator(source: str) -> tuple[str, str]:
    text, tree = _parse(ROOT / source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("generate_"):
            segment = ast.get_source_segment(text, node)
            return node.name, textwrap.dedent(segment)
    raise LookupError(f"no generate_* function in {source}")


def _collection_kwargs(source: str) -> dict[str, Any]:
    text, tree = _parse(ROOT / source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "create"):
            continue
        kwargs = {kw.arg: kw.value for kw in node.keywords if kw.arg}
        if "collection_schema" not in kwargs:
            continue

        def resolve_node(value):
            if isinstance(value, ast.Name):
                return next(
                    n.value
                    for n in tree.body
                    if isinstance(n, ast.Assign)
                    and any(
                        isinstance(t, ast.Name) and t.id == value.id for t in n.targets
                    )
                )
            return value

        def resolve(value):
            return ast.literal_eval(resolve_node(value))

        return {
            "name": resolve(kwargs["name"]),
            "description": resolve(kwargs["description"]),
            "tags": resolve(kwargs["tags"]),
            "schema": textwrap.dedent(
                ast.get_source_segment(text, resolve_node(kwargs["collection_schema"]))
            ),
        }
    raise LookupError(f"no collections.create call in {source}")


def _fmt(value: Any) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "True" if value else "False"
    return repr(value)


def _header(spec: dict[str, Any]) -> str:
    highlights = "\n".join(f"- {item}" for item in spec["highlights"])
    workflow = "\n".join(f"{i}. {step}" for i, step in enumerate(spec["workflow"], 1))
    return f"""\
# {spec["emoji"]} {spec["title"]} — Nostradamus IoTO SDK

{spec["intro"]}

This notebook mirrors `{spec["source"]}` using only `nostradamus_ioto_sdk.NostradamusClient`.
It sends **{spec["volume"]}** ({spec["records"]} records) to the collection
`{spec["collection"]}`, then queries, aggregates and deletes part of it.

## Workflow

{workflow}

## What this notebook highlights

{highlights}

## Prerequisites

```bash
pip install -e ../..          # from the repository root
pip install python-dotenv
```

{ENV_TABLE}

> The notebook is idempotent: if the collection already exists the SDK raises
> `APIError` with status `409`, and Step 1 falls back to reusing it."""


def _config(spec: dict[str, Any]) -> str:
    straight_imports = ["import os", "import random"]
    straight_imports += [
        extra for extra in spec.get("extra_imports", []) if extra.startswith("import ")
    ]
    imports = sorted(straight_imports)
    imports += [
        "from collections import Counter",
        "from datetime import datetime, timedelta, timezone",
        "",
        "from dotenv import load_dotenv",
        "",
        "from nostradamus_ioto_sdk import NostradamusClient, StatOperation",
        "from nostradamus_ioto_sdk.exceptions import APIError",
    ]
    missing = "\n".join(
        f'    "{name}": {name},'
        for name in (
            "PROJECT_ID",
            "MASTER_KEY",
            "WRITE_KEY",
            "READ_KEY",
        )
    )
    return f"""\
{chr(10).join(imports)}

load_dotenv()

BASE_URL = os.getenv("NOSTRADAMUS_BASE_URL", "https://nostradamus-ioto.issel.ee.auth.gr")
PROJECT_ID = os.getenv("NOSTRADAMUS_PROJECT_ID", "")
MASTER_KEY = os.getenv("NOSTRADAMUS_MASTER_KEY", "")
WRITE_KEY = os.getenv("NOSTRADAMUS_WRITE_KEY", "")
READ_KEY = os.getenv("NOSTRADAMUS_READ_KEY", "")

_missing = [
    name
    for name, value in {{
{missing}
    }}.items()
    if not value
]
if _missing:
    raise RuntimeError(
        "Missing required environment variables: " + ", ".join(_missing)
    )

print("{spec["emoji"]} Nostradamus IoTO SDK — {spec["title"]}")
print(f"base_url={{BASE_URL}} project_id={{PROJECT_ID}}")"""


def _create(spec: dict[str, Any]) -> str:
    tags = "[" + ", ".join(json.dumps(t) for t in spec["tags"]) + "]"
    return f"""\
COLLECTION_NAME = {json.dumps(spec["collection"])}

COLLECTION_SCHEMA = {spec["schema"]}

with NostradamusClient(api_key=MASTER_KEY, base_url=BASE_URL) as master_client:
    try:
        collection = master_client.collections.create(
            project_id=PROJECT_ID,
            name=COLLECTION_NAME,
            description={json.dumps(spec["description"])},
            tags={tags},
            collection_schema=COLLECTION_SCHEMA,
        )
        print("✅ Collection created")
    except APIError as exc:
        if exc.status_code != 409:
            raise
        collection = next(
            (
                coll
                for coll in master_client.collections.list(PROJECT_ID)
                if coll.collection_name == COLLECTION_NAME
            ),
            None,
        )
        if collection is None:
            raise
        print("⚠️  Collection already exists — reusing it")

collection_id = str(collection.collection_id)
print(f"collection_id={{collection_id}}")
collection.model_dump()"""


def _send(spec: dict[str, Any]) -> str:
    parts = []
    if spec["constants"]:
        parts.append(spec["constants"])
    parts.append(spec["generator"])
    parts.append(f"""\
data = {spec["generator_name"]}({spec["call_args"]})
print(f"Generated {{len(data)}} records")

with NostradamusClient(api_key=WRITE_KEY, base_url=BASE_URL) as write_client:
    write_client.data.send(
        project_id=PROJECT_ID,
        collection_id=collection_id,
        data=data,
    )
print(f"✅ Sent {{len(data)}} records to {{COLLECTION_NAME}}")""")
    return "\n\n".join(parts)


def _query_cell(spec: dict[str, Any]) -> str:
    lines = [
        "def summary(result, label):",
        '    """Print a compact view of a DataListResponse."""',
        '    print(f"{label}: {len(result.data)} of {result.total_count} record(s)")',
        "    if result.data:",
        '        print("  example:", result.data[0])',
        "",
        "",
        "with NostradamusClient(api_key=READ_KEY, base_url=BASE_URL) as read_client:",
        "    # All records, grouped per key",
        "    result = read_client.data.get(",
        "        project_id=PROJECT_ID,",
        "        collection_id=collection_id,",
        "    )",
        '    summary(result, "📥 All records")',
        '    counts = Counter(row["key"] for row in result.data)',
        '    print("   per key:", dict(sorted(counts.items())))',
        "",
    ]

    for query in spec["queries"]:
        label = query["label"]
        expr = [
            f"    # {label}",
            "    result = read_client.data.get(",
            "        project_id=PROJECT_ID,",
            "        collection_id=collection_id,",
        ]
        if query.get("attributes"):
            attrs = ", ".join(json.dumps(a) for a in query["attributes"])
            expr.append(f"        attributes=[{attrs}],")
        if query.get("filters"):
            expr.append("        filters=[")
            for flt in query["filters"]:
                rendered = ", ".join(f'"{k}": {_fmt(v)}' for k, v in flt.items())
                expr.append(f"            {{{rendered}}},")
            expr.append("        ],")
        if query.get("order_by"):
            field, order = query["order_by"]
            expr.append(
                f"""        order_by='{{"field": "{field}", "order": "{order}"}}',"""
            )
        if query.get("limit"):
            expr.append(f"        limit={query['limit']},")
        expr.append("    )")

        if query.get("ranked"):
            expr.append(f'    print("🏆 {label}")')
            expr.append("    for row in result.data:")
            expr.append('        print("   >", row)')
        else:
            expr.append(f'    summary(result, "{label}")')
        lines.append("\n".join(expr))
        lines.append("")

    return "\n".join(lines).rstrip("\n")


def _statistics(spec: dict[str, Any]) -> str:
    entries = "\n".join(
        f"        ({json.dumps(label, ensure_ascii=False)}, {json.dumps(attribute, ensure_ascii=False)}, StatOperation.{stat}),"
        for label, attribute, stat in spec["stats"]
    )
    return f"""\
with NostradamusClient(api_key=READ_KEY, base_url=BASE_URL) as read_client:
    for label, attribute, stat in [
{entries}
    ]:
        result = read_client.data.statistics(
            project_id=PROJECT_ID,
            collection_id=collection_id,
            stat=stat,
            attribute=attribute,
        )
        print(f"📈 {{label}}: {{result.get('value', result)}}")"""


def _delete(spec: dict[str, Any]) -> str:
    key = json.dumps(spec["delete_key"])
    return f"""\
timestamp_from = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime(
    "%Y-%m-%dT%H:%M:%SZ"
)
timestamp_to = (datetime.now(timezone.utc) - timedelta(hours=12)).strftime(
    "%Y-%m-%dT%H:%M:%SZ"
)

DELETE_KEY = {key}


with NostradamusClient(api_key=MASTER_KEY, base_url=BASE_URL) as master_client:

    def count_for(key):
        result = master_client.data.get(
            project_id=PROJECT_ID,
            collection_id=collection_id,
            filters=[{{"property_name": "key", "operator": "eq", "property_value": key}}],
        )
        return result.total_count

    before = count_for(DELETE_KEY)
    result = master_client.data.delete(
        project_id=PROJECT_ID,
        collection_id=collection_id,
        key=DELETE_KEY,
        timestamp_from=timestamp_from,
        timestamp_to=timestamp_to,
    )
    after = count_for(DELETE_KEY)

print(f"🗑️  {{result.message}} (criteria={{result.criteria}})")
print(f"   {{DELETE_KEY}}: {{before}} → {{after}} record(s)")"""


def _cleanup(spec: dict[str, Any]) -> str:
    return """\
with NostradamusClient(api_key=MASTER_KEY, base_url=BASE_URL) as master_client:
    master_client.collections.delete(
        project_id=PROJECT_ID,
        collection_id=collection_id,
    )
print(f"🧹 Collection {collection_id} deleted")
print("✨ Demo complete!")"""


def _build(spec: dict[str, Any]) -> dict[str, Any]:
    step1 = f"""\
## Step 1: Create the {spec["entity"]} collection

`collections.create()` returns a `CollectionResponse`, so the collection ID comes
straight from the model. The schema declares one sample record and is copied
verbatim from `{spec["source"]}`."""

    step2 = f"""\
## Step 2: Generate and send {spec["entity_plural"]} data

`data.send()` accepts a single dict or a list of dicts — the SDK serialises and
authenticates the batch with the write key. `{spec["generator_name"]}()` is the
same generator used by the script."""

    bullets = "\n".join(f"- **{q['label']}**" for q in spec["queries"])
    step3 = f"""\
## Step 3: Query data with domain filters

`data.get()` returns a `DataListResponse` with `.data` (records) and
`.total_count`. Filters are plain dicts combined as an AND. The queries below
mirror the alert conditions from the script:

{bullets}"""

    step4 = """\
## Step 4: Statistics

`data.statistics()` takes `stat`, `attribute` and optional `group_by` /
`interval` / `limit`. Use the `StatOperation` enum instead of raw strings."""

    step5 = f"""\
## Step 5: Delete a 12-hour window for one {spec["entity"]}

`data.delete()` accepts `key`, `timestamp_from` and `timestamp_to` (at least one
required). Here we remove the first half of the 24-hour window for
`{spec["delete_key"]}` and compare the record count before and after."""

    step6 = """\
## Step 6: Clean up

Remove the demo collection so the notebook can be re-run from scratch."""

    return _notebook(
        [
            _md(_header(spec)),
            _code("%pip install -q -e ../.. python-dotenv"),
            _md("""\
## Configuration

Each permission level gets its own `NostradamusClient` instance — the SDK injects
the `X-API-Key` header, so there is no manual header handling."""),
            _code(_config(spec)),
            _md(step1),
            _code(_create(spec)),
            _md(step2),
            _code(_send(spec)),
            _md(step3),
            _code(_query_cell(spec)),
            _md(step4),
            _code(_statistics(spec)),
            _md(step5),
            _code(_delete(spec)),
            _md(step6),
            _code(_cleanup(spec)),
        ]
    )


SPECS: list[dict[str, Any]] = [
    {
        "slug": "agriculture_precision_farming",
        "emoji": "🌾",
        "title": "Precision Farming",
        "source": "examples/agriculture/precision_farming.py",
        "entity": "zone",
        "entity_plural": "crop-zone",
        "intro": (
            "Multi-zone crop monitoring: each field reports soil moisture, soil and "
            "ambient temperature, humidity, light, NDVI, leaf wetness, wind and "
            "rainfall, plus the sensor battery level."
        ),
        "volume": "4 zones × 24 hourly readings",
        "records": 96,
        "constants": ["ZONES"],
        "call_args": "ZONES",
        "extra_imports": [],
        "delete_key": "ZONE_A_FIELD_01",
        "workflow": [
            "Create the `precision_farming_data` collection with a schema",
            "Generate and send 4 zones × 24 hourly readings",
            "Query by zone, drought stress, disease risk and NDVI ranking",
            "Aggregate soil moisture, ambient temperature and battery statistics",
            "Delete a 12-hour window for `ZONE_A_FIELD_01`",
            "Delete the collection",
        ],
        "highlights": [
            "Drought stress detection (low moisture + high temperature)",
            "Disease risk detection (high leaf wetness + high humidity)",
            "NDVI ranking across zones",
        ],
        "queries": [
            {
                "label": "🔍 Zone A readings (limit 5)",
                "filters": [
                    {
                        "property_name": "key",
                        "operator": "eq",
                        "property_value": "ZONE_A_FIELD_01",
                    }
                ],
                "limit": 5,
            },
            {
                "label": "🏜️ Drought stress (moisture < 25 % and temp > 30 °C)",
                "filters": [
                    {
                        "property_name": "soil_moisture_pct",
                        "operator": "lt",
                        "property_value": 25.0,
                    },
                    {
                        "property_name": "ambient_temperature_c",
                        "operator": "gt",
                        "property_value": 30.0,
                    },
                ],
                "limit": 10,
            },
            {
                "label": "🍄 Disease risk (leaf wetness > 120 min and humidity > 80 %)",
                "filters": [
                    {
                        "property_name": "leaf_wetness_duration_min",
                        "operator": "gt",
                        "property_value": 120,
                    },
                    {
                        "property_name": "ambient_humidity_pct",
                        "operator": "gt",
                        "property_value": 80.0,
                    },
                ],
                "limit": 10,
            },
            {
                "label": "Top 3 healthiest readings (NDVI)",
                "attributes": ["key", "ndvi", "timestamp"],
                "order_by": ("ndvi", "desc"),
                "limit": 3,
                "ranked": True,
            },
        ],
        "stats": [
            ("Average soil moisture (%)", "soil_moisture_pct", "AVG"),
            ("Maximum ambient temperature (°C)", "ambient_temperature_c", "MAX"),
            ("Minimum battery level (%)", "battery_pct", "MIN"),
            ("Distinct zones", "key", "DISTINCT"),
        ],
    },
    {
        "slug": "agriculture_greenhouse_automation",
        "emoji": "🏡",
        "title": "Greenhouse Automation",
        "source": "examples/agriculture/greenhouse_automation.py",
        "entity": "greenhouse zone",
        "entity_plural": "greenhouse climate",
        "intro": (
            "Greenhouse climate control with actuator feedback: air temperature, "
            "humidity, CO2, PAR light, substrate moisture/EC/pH, VPD and the state of "
            "the vent, heating, irrigation and fogger actuators."
        ),
        "volume": "3 zones × 48 half-hourly readings",
        "records": 144,
        "constants": [],
        "call_args": "",
        "extra_imports": [],
        "delete_key": "GH_01_ZONE_A",
        "workflow": [
            "Create the `greenhouse_sensors` collection with a schema",
            "Generate and send 3 zones × 48 half-hourly readings",
            "Query heat stress, low CO2, active irrigation and VPD ranking",
            "Aggregate air temperature, CO2 and substrate moisture statistics",
            "Delete a 12-hour window for `GH_01_ZONE_A`",
            "Delete the collection",
        ],
        "highlights": [
            "Heat stress detection (air temp > 35 °C with vents barely open)",
            "CO2 depletion detection (below 400 ppm)",
            "Actuator auditing (vent / heating / irrigation / fogger flags)",
        ],
        "queries": [
            {
                "label": "🔥 Heat stress (air temp > 35 °C and vents < 50 %)",
                "filters": [
                    {
                        "property_name": "air_temperature_c",
                        "operator": "gt",
                        "property_value": 35,
                    },
                    {
                        "property_name": "vent_position_pct",
                        "operator": "lt",
                        "property_value": 50,
                    },
                ],
            },
            {
                "label": "🫁 Low CO2 (< 400 ppm)",
                "filters": [
                    {
                        "property_name": "co2_ppm",
                        "operator": "lt",
                        "property_value": 400,
                    }
                ],
            },
            {
                "label": "💧 Irrigation active",
                "filters": [
                    {
                        "property_name": "irrigation_active",
                        "operator": "eq",
                        "property_value": 1,
                    }
                ],
            },
            {
                "label": "Top 5 highest VPD",
                "attributes": ["key", "vpd_kpa", "air_temperature_c"],
                "order_by": ("vpd_kpa", "desc"),
                "limit": 5,
                "ranked": True,
            },
        ],
        "stats": [
            ("Average air temperature (°C)", "air_temperature_c", "AVG"),
            ("Maximum CO2 (ppm)", "co2_ppm", "MAX"),
            ("Minimum substrate moisture (%)", "substrate_moisture_pct", "MIN"),
            ("Distinct zones", "key", "DISTINCT"),
        ],
    },
    {
        "slug": "agriculture_livestock_tracking",
        "emoji": "🐄",
        "title": "Livestock Tracking",
        "source": "examples/agriculture/livestock_tracking.py",
        "entity": "animal",
        "entity_plural": "cattle health",
        "intro": (
            "Cattle health and GPS tracking: body temperature, heart rate, activity "
            "level, rumination, step count, ambient temperature, position and collar "
            "battery."
        ),
        "volume": "5 animals × 24 hourly readings",
        "records": 120,
        "constants": [],
        "call_args": "",
        "extra_imports": [],
        "delete_key": "CATTLE_001",
        "workflow": [
            "Create the `livestock_sensors` collection with a schema",
            "Generate and send 5 animals × 24 hourly readings",
            "Query fever, illness, heat stress and body-temperature ranking",
            "Aggregate body temperature, heart rate and rumination statistics",
            "Delete a 12-hour window for `CATTLE_001`",
            "Delete the collection",
        ],
        "highlights": [
            "Fever detection (body temperature > 39.5 °C)",
            "Illness detection (low activity + low rumination)",
            "Heat stress alerts (ambient > 30 °C with elevated heart rate)",
        ],
        "queries": [
            {
                "label": "🔍 CATTLE_001 readings",
                "filters": [
                    {
                        "property_name": "key",
                        "operator": "eq",
                        "property_value": "CATTLE_001",
                    }
                ],
            },
            {
                "label": "🌡️ Fever (body temp > 39.5 °C)",
                "filters": [
                    {
                        "property_name": "body_temperature_c",
                        "operator": "gt",
                        "property_value": 39.5,
                    }
                ],
            },
            {
                "label": "😴 Illness risk (activity < 2 and rumination < 10 min)",
                "filters": [
                    {
                        "property_name": "activity_level",
                        "operator": "lt",
                        "property_value": 2,
                    },
                    {
                        "property_name": "rumination_min",
                        "operator": "lt",
                        "property_value": 10,
                    },
                ],
            },
            {
                "label": "🥵 Heat stress (ambient > 30 °C and heart rate > 80 bpm)",
                "filters": [
                    {
                        "property_name": "ambient_temperature_c",
                        "operator": "gt",
                        "property_value": 30,
                    },
                    {
                        "property_name": "heart_rate_bpm",
                        "operator": "gt",
                        "property_value": 80,
                    },
                ],
            },
            {
                "label": "Top 5 body temperatures",
                "attributes": ["key", "body_temperature_c"],
                "order_by": ("body_temperature_c", "desc"),
                "limit": 5,
                "ranked": True,
            },
        ],
        "stats": [
            ("Average body temperature (°C)", "body_temperature_c", "AVG"),
            ("Maximum heart rate (bpm)", "heart_rate_bpm", "MAX"),
            ("Minimum rumination (min)", "rumination_min", "MIN"),
            ("Distinct animals", "key", "DISTINCT"),
        ],
    },
    {
        "slug": "smart_city_air_quality_monitoring",
        "emoji": "🏙️",
        "title": "Air Quality Monitoring",
        "source": "examples/smart_city/air_quality_monitoring.py",
        "entity": "station",
        "entity_plural": "air-quality",
        "intro": (
            "Urban air-quality network: four stations (downtown, industrial, highway "
            "and park) with distinct pollution profiles report PM2.5, PM10, NO2, O3, "
            "CO, SO2, meteorology and a derived AQI index."
        ),
        "volume": "4 stations × 48 half-hourly readings",
        "records": 192,
        "constants": ["STATION_PROFILES"],
        "call_args": "",
        "extra_imports": [],
        "delete_key": "AQ_STATION_DOWNTOWN",
        "workflow": [
            "Create the `air_quality_stations` collection with a schema",
            "Generate and send 4 stations × 48 half-hourly readings",
            "Query unhealthy PM2.5, ozone peaks, stagnation events and AQI ranking",
            "Aggregate PM2.5, AQI and wind-speed statistics",
            "Delete a 12-hour window for `AQ_STATION_DOWNTOWN`",
            "Delete the collection",
        ],
        "highlights": [
            "Station-specific pollution profiles",
            "Rush-hour traffic multipliers on PM/NO2/CO",
            "Stagnation detection (high PM10 with low wind)",
        ],
        "queries": [
            {
                "label": "🏭 Industrial station readings",
                "filters": [
                    {
                        "property_name": "key",
                        "operator": "eq",
                        "property_value": "AQ_STATION_INDUSTRIAL",
                    }
                ],
            },
            {
                "label": "😷 Unhealthy PM2.5 (> 55 µg/m³)",
                "filters": [
                    {
                        "property_name": "pm25_ugm3",
                        "operator": "gt",
                        "property_value": 55,
                    }
                ],
            },
            {
                "label": "🌫️ Ozone peak (> 60 ppb)",
                "filters": [
                    {"property_name": "o3_ppb", "operator": "gt", "property_value": 60}
                ],
            },
            {
                "label": "🌬️ Stagnation (PM10 > 80 µg/m³ and wind < 3 m/s)",
                "filters": [
                    {
                        "property_name": "pm10_ugm3",
                        "operator": "gt",
                        "property_value": 80,
                    },
                    {
                        "property_name": "wind_speed_ms",
                        "operator": "lt",
                        "property_value": 3,
                    },
                ],
            },
            {
                "label": "Top 5 AQI readings",
                "attributes": ["key", "aqi_index", "pm25_ugm3"],
                "order_by": ("aqi_index", "desc"),
                "limit": 5,
                "ranked": True,
            },
        ],
        "stats": [
            ("Average PM2.5 (µg/m³)", "pm25_ugm3", "AVG"),
            ("Maximum AQI", "aqi_index", "MAX"),
            ("Minimum wind speed (m/s)", "wind_speed_ms", "MIN"),
            ("Distinct stations", "key", "DISTINCT"),
        ],
    },
    {
        "slug": "smart_energy_microgrid_monitoring",
        "emoji": "⚡",
        "title": "Microgrid Monitoring",
        "source": "examples/smart_energy/microgrid_monitoring.py",
        "entity": "asset",
        "entity_plural": "solar/wind/battery",
        "intro": (
            "Solar/wind/battery microgrid: two solar arrays, a wind turbine and a "
            "battery bank report power output, cumulative energy, voltage, current, "
            "temperature, efficiency, grid frequency and status."
        ),
        "volume": "4 assets × 48 half-hourly readings",
        "records": 192,
        "constants": [],
        "call_args": "",
        "extra_imports": ["import math"],
        "delete_key": "SOLAR_ARRAY_01",
        "workflow": [
            "Create the `microgrid_assets` collection with a schema",
            "Generate and send 4 assets × 48 half-hourly readings",
            "Query solar output, low battery SOC, faults and peak production",
            "Aggregate power output, temperature and battery SOC statistics",
            "Delete a 12-hour window for `SOLAR_ARRAY_01`",
            "Delete the collection",
        ],
        "highlights": [
            "Realistic day/night solar curves and wind gusts",
            "Battery charge/discharge cycles with SOC tracking",
            "Fault detection via the `status` flag",
        ],
        "queries": [
            {
                "label": "☀️ SOLAR_ARRAY_01 readings",
                "filters": [
                    {
                        "property_name": "key",
                        "operator": "eq",
                        "property_value": "SOLAR_ARRAY_01",
                    }
                ],
            },
            {
                "label": "🔋 Low battery SOC (< 30 %)",
                "filters": [
                    {
                        "property_name": "battery_soc_pct",
                        "operator": "lt",
                        "property_value": 30,
                    }
                ],
            },
            {
                "label": "🚨 Faults (status == 0)",
                "filters": [
                    {"property_name": "status", "operator": "eq", "property_value": 0}
                ],
            },
            {
                "label": "🌞 Peak production (irradiance > 700 W/m² and power > 35 kW)",
                "filters": [
                    {
                        "property_name": "solar_irradiance_wm2",
                        "operator": "gt",
                        "property_value": 700,
                    },
                    {
                        "property_name": "power_output_kw",
                        "operator": "gt",
                        "property_value": 35,
                    },
                ],
            },
            {
                "label": "Top 5 power output readings",
                "attributes": ["key", "power_output_kw"],
                "order_by": ("power_output_kw", "desc"),
                "limit": 5,
                "ranked": True,
            },
        ],
        "stats": [
            ("Average power output (kW)", "power_output_kw", "AVG"),
            ("Maximum temperature (°C)", "temperature_c", "MAX"),
            ("Minimum battery SOC (%)", "battery_soc_pct", "MIN"),
            ("Distinct assets", "key", "DISTINCT"),
        ],
    },
    {
        "slug": "smart_transportation_fleet_management",
        "emoji": "🚛",
        "title": "Fleet Management",
        "source": "examples/smart_transportation/fleet_management.py",
        "entity": "vehicle",
        "entity_plural": "fleet telemetry",
        "intro": (
            "Vehicle fleet telemetry: trucks, vans and buses report GPS position, "
            "speed, heading, fuel level and consumption, engine RPM and temperature, "
            "odometer, tyre pressure, harsh-braking counts and cargo weight."
        ),
        "volume": "5 vehicles × 24 hourly readings",
        "records": 120,
        "constants": ["VEHICLE_PROFILES"],
        "call_args": "",
        "extra_imports": [],
        "delete_key": "TRUCK_001",
        "workflow": [
            "Create the `fleet_telemetry` collection with a schema",
            "Generate and send 5 vehicles × 24 hourly readings",
            "Query speeding, overheating, low fuel and fuel-consumption ranking",
            "Aggregate speed, engine temperature and fuel-level statistics",
            "Delete a 12-hour window for `TRUCK_001`",
            "Delete the collection",
        ],
        "highlights": [
            "Vehicle-type-specific speed and cargo profiles",
            "Speeding (> 90 km/h) and overheating (> 100 °C) detection",
            "Driver-behaviour signals (harsh braking, idle time)",
        ],
        "queries": [
            {
                "label": "🚚 TRUCK_001 readings",
                "filters": [
                    {
                        "property_name": "key",
                        "operator": "eq",
                        "property_value": "TRUCK_001",
                    }
                ],
            },
            {
                "label": "💨 Speeding (> 90 km/h)",
                "filters": [
                    {
                        "property_name": "speed_kmh",
                        "operator": "gt",
                        "property_value": 90,
                    }
                ],
            },
            {
                "label": "🔥 Overheating (engine temp > 100 °C)",
                "filters": [
                    {
                        "property_name": "engine_temperature_c",
                        "operator": "gt",
                        "property_value": 100,
                    }
                ],
            },
            {
                "label": "⛽ Low fuel (< 20 %)",
                "filters": [
                    {
                        "property_name": "fuel_level_pct",
                        "operator": "lt",
                        "property_value": 20,
                    }
                ],
            },
            {
                "label": "Top 5 fuel consumption",
                "attributes": ["key", "fuel_consumption_lph"],
                "order_by": ("fuel_consumption_lph", "desc"),
                "limit": 5,
                "ranked": True,
            },
        ],
        "stats": [
            ("Average speed (km/h)", "speed_kmh", "AVG"),
            ("Maximum engine temperature (°C)", "engine_temperature_c", "MAX"),
            ("Minimum fuel level (%)", "fuel_level_pct", "MIN"),
            ("Distinct vehicles", "key", "DISTINCT"),
        ],
    },
    {
        "slug": "cyber_physical_robot_fleet_monitoring",
        "emoji": "🤖",
        "title": "Robot Fleet Monitoring",
        "source": "examples/cyber_physical/robot_fleet_monitoring.py",
        "entity": "robot",
        "entity_plural": "robot fleet",
        "intro": (
            "Warehouse robot fleet: AGVs, robotic arms and an inspection drone report "
            "position, velocity, orientation, battery, motor temperature, payload, "
            "task status, LiDAR point count, network latency, CPU usage and error codes."
        ),
        "volume": "5 robots × 24 hourly readings",
        "records": 120,
        "constants": ["ROBOT_PROFILES", "TASK_PREFIXES"],
        "call_args": "",
        "extra_imports": [],
        "delete_key": "AGV_001",
        "workflow": [
            "Create the `robot_fleet` collection with a schema",
            "Generate and send 5 robots × 24 hourly readings",
            "Query errors, low battery, performance bottlenecks and battery ranking",
            "Aggregate battery, motor temperature and obstacle-distance statistics",
            "Delete a 12-hour window for `AGV_001`",
            "Delete the collection",
        ],
        "highlights": [
            "Mixed robot types (AGV, robotic arm, inspection drone)",
            "Error detection (`error_code > 0`) and task-status inspection",
            "Performance bottlenecks (high CPU with high network latency)",
        ],
        "queries": [
            {
                "label": "🤖 AGV_001 readings",
                "filters": [
                    {
                        "property_name": "key",
                        "operator": "eq",
                        "property_value": "AGV_001",
                    }
                ],
            },
            {
                "label": "🚨 Errors (error_code > 0)",
                "filters": [
                    {
                        "property_name": "error_code",
                        "operator": "gt",
                        "property_value": 0,
                    }
                ],
            },
            {
                "label": "🔋 Low battery (< 30 %)",
                "filters": [
                    {
                        "property_name": "battery_pct",
                        "operator": "lt",
                        "property_value": 30,
                    }
                ],
            },
            {
                "label": "🐌 Bottlenecks (CPU > 80 % and latency > 50 ms)",
                "filters": [
                    {
                        "property_name": "cpu_usage_pct",
                        "operator": "gt",
                        "property_value": 80,
                    },
                    {
                        "property_name": "network_latency_ms",
                        "operator": "gt",
                        "property_value": 50,
                    },
                ],
            },
            {
                "label": "Lowest 5 battery levels",
                "attributes": ["key", "battery_pct", "robot_type"],
                "order_by": ("battery_pct", "asc"),
                "limit": 5,
                "ranked": True,
            },
        ],
        "stats": [
            ("Average battery (%)", "battery_pct", "AVG"),
            ("Maximum motor temperature (°C)", "motor_temperature_c", "MAX"),
            ("Minimum obstacle distance (m)", "obstacle_distance_m", "MIN"),
            ("Distinct robots", "key", "DISTINCT"),
        ],
    },
]


def main() -> None:
    NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
    for spec in SPECS:
        kwargs = _collection_kwargs(spec["source"])
        generator_name, generator_source = _generator(spec["source"])
        spec = {
            **spec,
            "collection": kwargs["name"],
            "description": kwargs["description"],
            "tags": kwargs["tags"],
            "schema": kwargs["schema"],
            "generator_name": generator_name,
            "generator": generator_source,
            "constants": "\n\n".join(
                _module_constant(spec["source"], name) for name in spec["constants"]
            ),
        }
        notebook = _build(spec)
        destination = NOTEBOOKS_DIR / f"{spec['slug']}.ipynb"
        destination.write_text(
            json.dumps(notebook, indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {destination.relative_to(ROOT)} ({len(notebook['cells'])} cells)")


if __name__ == "__main__":
    main()
