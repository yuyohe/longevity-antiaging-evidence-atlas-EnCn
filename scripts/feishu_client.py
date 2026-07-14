"""Minimal Feishu OpenAPI client for 长寿抗衰与健康寿命证据图谱.

This client intentionally implements only the operations needed for the first MVP:
- get tenant_access_token
- list/create/update bitable records

Environment variables:
- FEISHU_APP_ID
- FEISHU_APP_SECRET
- FEISHU_BASE_URL, default https://open.feishu.cn
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests


class FeishuError(RuntimeError):
    pass


class FeishuClient:
    def __init__(self, app_id: Optional[str] = None, app_secret: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.app_id = app_id or os.getenv("FEISHU_APP_ID", "")
        self.app_secret = app_secret or os.getenv("FEISHU_APP_SECRET", "")
        self.base_url = (base_url or os.getenv("FEISHU_BASE_URL", "https://open.feishu.cn")).rstrip("/")
        self._tenant_token: Optional[str] = None
        self._tenant_token_expire_at = 0.0

        if not self.app_id or not self.app_secret:
            raise FeishuError("Missing FEISHU_APP_ID or FEISHU_APP_SECRET.")

    def tenant_access_token(self) -> str:
        if self._tenant_token and time.time() < self._tenant_token_expire_at - 60:
            return self._tenant_token

        url = f"{self.base_url}/open-apis/auth/v3/tenant_access_token/internal"
        resp = requests.post(
            url,
            json={"app_id": self.app_id, "app_secret": self.app_secret},
            timeout=30,
        )
        data = self._json(resp)
        token = data.get("tenant_access_token")
        if not token:
            raise FeishuError(f"Failed to get tenant_access_token: {data}")
        self._tenant_token = token
        self._tenant_token_expire_at = time.time() + int(data.get("expire", 7200))
        return token

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.tenant_access_token()}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _json(resp: requests.Response) -> Dict[str, Any]:
        try:
            data = resp.json()
        except Exception as exc:
            raise FeishuError(f"Feishu response is not JSON: {resp.status_code} {resp.text[:500]}") from exc
        if resp.status_code >= 400:
            raise FeishuError(f"Feishu HTTP error {resp.status_code}: {data}")
        if data.get("code", 0) not in (0, None):
            raise FeishuError(f"Feishu API error: {data}")
        return data

    def list_bitable_records(self, app_token: str, table_id: str, page_size: int = 500) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        page_token: Optional[str] = None
        while True:
            params: Dict[str, Any] = {"page_size": page_size}
            if page_token:
                params["page_token"] = page_token
            url = f"{self.base_url}/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
            resp = requests.get(url, headers=self._headers(), params=params, timeout=30)
            data = self._json(resp)
            payload = data.get("data", {})
            records.extend(payload.get("items", []))
            page_token = payload.get("page_token")
            if not payload.get("has_more") or not page_token:
                break
        return records

    def list_bitable_fields(self, app_token: str, table_id: str, page_size: int = 100) -> List[Dict[str, Any]]:
        fields: List[Dict[str, Any]] = []
        page_token: Optional[str] = None
        while True:
            params: Dict[str, Any] = {"page_size": page_size}
            if page_token:
                params["page_token"] = page_token
            url = f"{self.base_url}/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
            resp = requests.get(url, headers=self._headers(), params=params, timeout=30)
            data = self._json(resp)
            payload = data.get("data", {})
            fields.extend(payload.get("items", []))
            page_token = payload.get("page_token")
            if not payload.get("has_more") or not page_token:
                break
        return fields

    def list_bitable_tables(self, app_token: str, page_size: int = 100) -> List[Dict[str, Any]]:
        tables: List[Dict[str, Any]] = []
        page_token: Optional[str] = None
        while True:
            params: Dict[str, Any] = {"page_size": page_size}
            if page_token:
                params["page_token"] = page_token
            url = f"{self.base_url}/open-apis/bitable/v1/apps/{app_token}/tables"
            resp = requests.get(url, headers=self._headers(), params=params, timeout=30)
            data = self._json(resp)
            payload = data.get("data", {})
            tables.extend(payload.get("items", []))
            page_token = payload.get("page_token")
            if not payload.get("has_more") or not page_token:
                break
        return tables

    def create_bitable_table(
        self,
        app_token: str,
        table_name: str,
        default_view_name: str,
        fields: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{app_token}/tables"
        resp = requests.post(
            url,
            headers=self._headers(),
            json={"table": {"name": table_name, "default_view_name": default_view_name, "fields": fields}},
            timeout=30,
        )
        return self._json(resp)

    def create_bitable_text_field(self, app_token: str, table_id: str, field_name: str) -> Dict[str, Any]:
        return self.create_bitable_field(app_token, table_id, field_name, 1)

    def create_bitable_field(self, app_token: str, table_id: str, field_name: str, field_type: int) -> Dict[str, Any]:
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
        resp = requests.post(
            url,
            headers=self._headers(),
            json={"field_name": field_name, "type": field_type},
            timeout=30,
        )
        return self._json(resp)

    def delete_bitable_table(self, app_token: str, table_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}"
        resp = requests.delete(url, headers=self._headers(), timeout=30)
        return self._json(resp)

    def create_bitable_view(self, app_token: str, table_id: str, view_name: str, view_type: str = "grid") -> Dict[str, Any]:
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/views"
        resp = requests.post(
            url,
            headers=self._headers(),
            json={"view_name": view_name, "view_type": view_type},
            timeout=30,
        )
        return self._json(resp)

    def list_bitable_views(self, app_token: str, table_id: str, page_size: int = 100) -> List[Dict[str, Any]]:
        views: List[Dict[str, Any]] = []
        page_token: Optional[str] = None
        while True:
            params: Dict[str, Any] = {"page_size": page_size}
            if page_token:
                params["page_token"] = page_token
            url = f"{self.base_url}/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/views"
            resp = requests.get(url, headers=self._headers(), params=params, timeout=30)
            data = self._json(resp)
            payload = data.get("data", {})
            views.extend(payload.get("items", []))
            page_token = payload.get("page_token")
            if not payload.get("has_more") or not page_token:
                break
        return views

    def upload_bitable_file(self, app_token: str, file_path: str | Path, parent_type: str = "bitable_file") -> str:
        path = Path(file_path)
        url = f"{self.base_url}/open-apis/drive/v1/medias/upload_all"
        headers = {"Authorization": f"Bearer {self.tenant_access_token()}"}
        with path.open("rb") as f:
            files = {"file": (path.name, f)}
            data = {
                "file_name": path.name,
                "parent_type": parent_type,
                "parent_node": app_token,
                "size": str(path.stat().st_size),
            }
            resp = requests.post(url, headers=headers, data=data, files=files, timeout=90)
        payload = self._json(resp)
        data_out = payload.get("data", {})
        token = data_out.get("file_token") or data_out.get("media_token")
        if not token:
            raise FeishuError(f"Upload response missing file token: {payload}")
        return token

    def create_bitable_record(self, app_token: str, table_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        resp = requests.post(url, headers=self._headers(), json={"fields": fields}, timeout=30)
        return self._json(resp)

    def batch_create_bitable_records(self, app_token: str, table_id: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"
        resp = requests.post(url, headers=self._headers(), json={"records": records}, timeout=60)
        return self._json(resp)

    def update_bitable_record(self, app_token: str, table_id: str, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        resp = requests.put(url, headers=self._headers(), json={"fields": fields}, timeout=30)
        return self._json(resp)

    def batch_update_bitable_records(self, app_token: str, table_id: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update"
        resp = requests.post(url, headers=self._headers(), json={"records": records}, timeout=60)
        return self._json(resp)

    def delete_bitable_record(self, app_token: str, table_id: str, record_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        resp = requests.delete(url, headers=self._headers(), timeout=30)
        return self._json(resp)

    def get_wiki_node(self, node_token: str) -> Dict[str, Any]:
        url = f"{self.base_url}/open-apis/wiki/v2/spaces/get_node"
        resp = requests.get(url, headers=self._headers(), params={"token": node_token}, timeout=30)
        return self._json(resp)

    def resolve_bitable_app_token(self, app_token: str = "", wiki_node_token: str = "") -> str:
        if app_token:
            return app_token
        if not wiki_node_token:
            raise FeishuError("Missing FEISHU_BITABLE_APP_TOKEN or FEISHU_BITABLE_WIKI_NODE_TOKEN.")
        data = self.get_wiki_node(wiki_node_token)
        node = data.get("data", {}).get("node", {})
        if node.get("obj_type") != "bitable":
            raise FeishuError(f"Wiki node is not a bitable: {node.get('obj_type')}")
        obj_token = node.get("obj_token", "")
        if not obj_token:
            raise FeishuError(f"Wiki node response missing obj_token: {data}")
        return obj_token
