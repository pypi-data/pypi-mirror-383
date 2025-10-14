"""Tests for pointr_cloud_common migration DTOs preserving new flags."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure tests import the local package rather than an installed distribution.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pointr_cloud_common.dto.v9.migration_request_dto import MigrationOptionsDTO
from pointr_cloud_common.dto.v9.building_migration_dto import BuildingMigrationRequestDTO


def test_common_migration_options_round_trip_preserves_map_objects() -> None:
    options_payload = {
        "migrate_map_objects": True,
    }

    options = MigrationOptionsDTO.from_api_json(options_payload)
    assert options.migrate_map_objects is True
    assert options.to_api_json()["migrate_map_objects"] is True


def test_common_building_migration_request_preserves_map_objects() -> None:
    request_payload = {
        "source": {
            "api_url": "https://source",
            "version": "v9",
            "client_identifier": "source-client",
        },
        "target": {
            "api_url": "https://target",
            "version": "v9",
            "client_identifier": "target-client",
        },
        "building_id": "building-123",
        "site_id": "site-abc",
        "options": {
            "migrate_map_objects": True,
        },
    }

    dto = BuildingMigrationRequestDTO.from_api_json(request_payload)
    assert dto.migrate_map_objects is True
    assert dto.to_api_json()["options"]["migrate_map_objects"] is True
