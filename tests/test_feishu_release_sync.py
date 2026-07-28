from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sync_feishu_full_public_data_2026_05 as full_sync  # noqa: E402
import sync_feishu_visual_assets_2026_05 as visual_sync  # noqa: E402


class FakeClient:
    def __init__(self, records: list[dict[str, object]]) -> None:
        self.records = records
        self.deleted: list[str] = []
        self.created: list[dict[str, object]] = []
        self.updated: list[dict[str, object]] = []

    def list_bitable_records(self, *args, **kwargs):  # noqa: ANN002, ANN003
        return self.records

    def delete_bitable_record(self, app_token: str, table_id: str, record_id: str):
        self.deleted.append(record_id)
        return {}

    def batch_create_bitable_records(self, app_token: str, table_id: str, records):
        self.created.extend(records)
        return {}

    def batch_update_bitable_records(self, app_token: str, table_id: str, records):
        self.updated.extend(records)
        return {}


def branded_fields(key_name: str, key: str) -> dict[str, str]:
    return {key_name: key, **full_sync.BRAND_FIELDS}


class FullDataStaleCleanupTests(unittest.TestCase):
    def test_cleanup_deletes_only_stale_duplicate_and_blank_records(self) -> None:
        client = FakeClient(
            [
                {"record_id": "keep-a", "fields": branded_fields("id", "A")},
                {"record_id": "keep-b", "fields": branded_fields("id", "B")},
                {"record_id": "duplicate-a", "fields": branded_fields("id", "A")},
                {"record_id": "old", "fields": branded_fields("id", "OLD")},
                {"record_id": "blank", "fields": {}},
            ]
        )
        asset = {
            "csv": ROOT / "unused.csv",
            "primary_key": "id",
            "title_fields": ["title"],
            "table_name": "release-table",
            "asset_key": "release",
        }
        rows = [{"id": "A", "title": "Alpha"}, {"id": "B", "title": "Beta"}]

        with (
            patch.object(full_sync, "read_csv", return_value=(rows, ["id", "title"])),
            patch.object(full_sync, "ensure_table", return_value="table-id"),
            patch.object(full_sync, "ensure_fields"),
        ):
            result = full_sync.sync_asset(
                client,
                "app-token",
                asset,
                delete_stale_records=True,
            )

        self.assertEqual(set(client.deleted), {"duplicate-a", "old", "blank"})
        self.assertNotIn("keep-a", client.deleted)
        self.assertNotIn("keep-b", client.deleted)
        self.assertEqual(client.created, [])
        self.assertEqual(client.updated, [])
        self.assertEqual(result["rows"], 2)

    def test_force_update_refreshes_existing_records(self) -> None:
        client = FakeClient(
            [
                {"record_id": "keep-a", "fields": branded_fields("id", "A")},
                {"record_id": "keep-b", "fields": branded_fields("id", "B")},
            ]
        )
        asset = {
            "csv": ROOT / "unused.csv",
            "primary_key": "id",
            "title_fields": ["title"],
            "table_name": "release-table",
            "asset_key": "release",
        }
        rows = [{"id": "A", "title": "Alpha"}, {"id": "B", "title": "Beta"}]

        with (
            patch.object(full_sync, "read_csv", return_value=(rows, ["id", "title"])),
            patch.object(full_sync, "ensure_table", return_value="table-id"),
            patch.object(full_sync, "ensure_fields"),
            patch.object(full_sync.time, "sleep"),
        ):
            full_sync.sync_asset(
                client,
                "app-token",
                asset,
                force_update=True,
            )

        self.assertEqual(client.created, [])
        self.assertEqual({item["record_id"] for item in client.updated}, {"keep-a", "keep-b"})

    def test_key_filter_updates_only_requested_current_record(self) -> None:
        client = FakeClient(
            [
                {"record_id": "keep-a", "fields": branded_fields("id", "A")},
                {"record_id": "keep-b", "fields": branded_fields("id", "B")},
            ]
        )
        asset = {
            "csv": ROOT / "unused.csv",
            "primary_key": "id",
            "title_fields": ["title"],
            "table_name": "release-table",
            "asset_key": "release",
        }
        rows = [{"id": "A", "title": "Alpha"}, {"id": "B", "title": "Beta"}]

        with (
            patch.object(full_sync, "read_csv", return_value=(rows, ["id", "title"])),
            patch.object(full_sync, "ensure_table", return_value="table-id"),
            patch.object(full_sync, "ensure_fields"),
            patch.object(full_sync.time, "sleep"),
        ):
            full_sync.sync_asset(
                client,
                "app-token",
                asset,
                force_update=True,
                only_keys={"A"},
            )

        self.assertEqual(client.created, [])
        self.assertEqual([item["record_id"] for item in client.updated], ["keep-a"])
        self.assertEqual(client.deleted, [])


class VisualStaleCleanupTests(unittest.TestCase):
    def test_upsert_keeps_current_key_and_removes_stale_rows(self) -> None:
        client = FakeClient(
            [
                {"record_id": "keep-a", "fields": {"title": "A"}},
                {"record_id": "duplicate-a", "fields": {"title": "A"}},
                {"record_id": "old", "fields": {"title": "OLD"}},
                {"record_id": "blank", "fields": {}},
            ]
        )

        with patch.object(visual_sync.time, "sleep"):
            created, updated, deleted = visual_sync.upsert_records(
                client,
                "app-token",
                "table-id",
                "title",
                [{"title": "A", "value": "one"}, {"title": "B", "value": "two"}],
                delete_stale_records=True,
            )

        self.assertEqual(set(client.deleted), {"duplicate-a", "old", "blank"})
        self.assertNotIn("keep-a", client.deleted)
        self.assertEqual(created, 1)
        self.assertEqual(updated, 1)
        self.assertEqual(deleted, 3)
        self.assertEqual(client.updated[0]["record_id"], "keep-a")


if __name__ == "__main__":
    unittest.main()
