"""Settings migrations for schema version upgrades."""

from typing import Dict, Any


def migrate_v1_to_v2(data: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate from schema version 1 to 2 (placeholder for future)."""
    data["schema_version"] = 2
    return data


MIGRATIONS = {
    1: migrate_v1_to_v2,
}


def migrate_settings(data: Dict[str, Any], target_version: int) -> Dict[str, Any]:
    """Apply migrations to reach target version."""
    current_version = data.get("schema_version", 1)

    for version in range(current_version, target_version):
        migrator = MIGRATIONS.get(version)
        if migrator:
            data = migrator(data)
        else:
            # No migration needed or available
            data["schema_version"] = version + 1

    return data