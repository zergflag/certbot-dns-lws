from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


class LwsApiError(RuntimeError):
    pass


@dataclass(frozen=True)
class DnsRecord:
    record_id: str
    name: str
    record_type: str
    value: str


class LwsDnsClient:
    BASE_URL = "https://api.lws.net/v1"

    def __init__(self, login: str, api_key: str, timeout: int = 30):
        if not api_key:
            raise ValueError("The LWS API key is empty.")

        self.timeout = timeout
        self.session = requests.Session()

        self.session.headers.update(
            {
                "X-Auth-Login": login,
                "X-Auth-Pass": api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "certbot-dns-lws/0.1.0",
            }
        )

    def add_txt_record(self, fqdn: str, value: str, ttl: int = 900) -> None:
        zone = self._find_managed_zone(fqdn)
        relative_name = self._relative_name(fqdn, zone)

        payload = {
            "type": "TXT",
            "name": relative_name,
            "value": value,
            "ttl": ttl,
        }

        self._request(
            "POST",
            f"/domain/{zone}/zdns",
            json=payload,
        )

    def delete_txt_record(self, fqdn: str, value: str) -> None:
        zone = self._find_managed_zone(fqdn)
        relative_name = self._relative_name(fqdn, zone)

        records = self._list_records(zone)

        matching = [
            record
            for record in records
            if record.record_type.upper() == "TXT"
            and self._normalise_name(record.name, zone)
            == self._normalise_name(relative_name, zone)
            and self._normalise_txt(record.value)
            == self._normalise_txt(value)
        ]

        for record in matching:
            self._delete_record(zone, record.record_id)

    def _find_managed_zone(self, fqdn: str) -> str:
        labels = fqdn.rstrip(".").split(".")

        for index in range(len(labels) - 1):
            candidate = ".".join(labels[index:])

            try:
                self._list_records(candidate)
                return candidate
            except LwsApiError:
                continue

        raise LwsApiError(f"No LWS DNS zone found for {fqdn}")

    def _list_records(self, zone: str) -> list[DnsRecord]:
        data = self._request(
            "GET",
            f"/domain/{zone}/zdns",
        )

        raw_records = self._extract_records(data)

        return [
            DnsRecord(
                record_id=str(
                    raw.get("id")
                    or raw.get("record_id")
                    or raw.get("uuid")
                    or ""
                ),
                name=str(
                    raw.get("name")
                    or raw.get("host")
                    or raw.get("hostname")
                    or ""
                ),
                record_type=str(
                    raw.get("type")
                    or raw.get("record_type")
                    or ""
                ),
                value=str(
                    raw.get("value")
                    or raw.get("content")
                    or raw.get("target")
                    or ""
                ),
            )
            for raw in raw_records
        ]

    def _delete_record(self, zone: str, record_id: str) -> None:
        if not record_id:
            raise LwsApiError(
                "The LWS API response did not contain a DNS record ID."
            )

        self._request(
            "DELETE",
            f"/domain/{zone}/zdns",
            json={
                "id": int(record_id),
            },
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        response = self.session.request(
            method,
            f"{self.BASE_URL}{path}",
            timeout=self.timeout,
            **kwargs,
        )

        if not response.ok:
            raise LwsApiError(
                f"LWS API returned HTTP {response.status_code}: "
                f"{response.text[:500]}"
            )

        if not response.content:
            return None

        try:
            return response.json()
        except ValueError as exc:
            raise LwsApiError(
                "LWS API returned a non-JSON response."
            ) from exc

    @staticmethod
    def _extract_records(data: Any) -> list[dict[str, Any]]:
        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            for key in ("records", "data", "zdns", "result"):
                candidate = data.get(key)
                if isinstance(candidate, list):
                    return candidate

                if isinstance(candidate, dict):
                    nested_records = candidate.get("records")
                    if isinstance(nested_records, list):
                        return nested_records

        raise LwsApiError("Unexpected LWS DNS-zone response format.")

    @staticmethod
    def _relative_name(fqdn: str, zone: str) -> str:
        fqdn = fqdn.rstrip(".")
        zone = zone.rstrip(".")

        if fqdn == zone:
            return "@"

        suffix = f".{zone}"
        if not fqdn.endswith(suffix):
            raise LwsApiError(f"{fqdn} does not belong to zone {zone}")

        return fqdn[: -len(suffix)]

    @staticmethod
    def _normalise_txt(value: str) -> str:
        return value.strip().strip('"')

    @staticmethod
    def _normalise_name(name: str, zone: str) -> str:
        name = name.rstrip(".").lower()
        zone = zone.rstrip(".").lower()

        if name == "@":
            return zone

        if name == zone or name.endswith(f".{zone}"):
            return name

        return f"{name}.{zone}"
