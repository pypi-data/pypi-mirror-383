# filename: login/license.py
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

def load_config(path: str = "config/config.json") -> Dict[str, Any]:
    if not os.path.exists(path):
        raise ValueError(f"Config file not found at {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e
    if "license" not in data or not isinstance(data["license"], dict):
        raise ValueError('Config must contain object "license"')
    lic = data["license"]
    required = ["url", "key", "discord_id", "product_name"]
    missing = [k for k in required if not lic.get(k)]
    if missing:
        raise ValueError(f'Missing required fields in license: {", ".join(missing)}')
    if not isinstance(lic["url"], str) or not lic["url"].startswith(("http://", "https://")):
        raise ValueError("license.url must be a valid HTTP(S) URL")
    for k in ["key", "discord_id", "product_name"]:
        if not isinstance(lic[k], str):
            raise ValueError(f"license.{k} must be a string")
    return data

def call_license_api(url: str, key: str, timeout: float = 15.0, use_body: bool = False) -> Dict[str, Any]:
    """
    Calls the license API.
    - If use_body=False: send only headers, no body.
    - If use_body=True: send JSON body {"license": key} in addition to headers.
    """
    headers = {
        "Accept": "application/json",
        "User-Agent": "LicenseCheck/1.0 (+https://example.com)",
        "LICENSE_KEY": key,
    }

    try:
        if use_body:
            resp = requests.post(url, headers=headers, json={"license": key}, timeout=timeout)
        else:
            resp = requests.post(url, headers=headers, timeout=timeout)
    except requests.RequestException as e:
        raise RuntimeError(f"Network error calling license API: {e}") from e

    if not resp.ok:
        preview = (resp.text or "")[:300]
        raise RuntimeError(f"HTTP {resp.status_code} {resp.reason}. Body: {preview}")

    if resp.status_code == 204 or not resp.content:
        raise RuntimeError("API returned no content")

    try:
        return resp.json()
    except ValueError:
        ct = resp.headers.get("Content-Type", "")
        preview = (resp.text or "")[:300]
        raise RuntimeError(f"Non-JSON response. Content-Type: {ct}. Body: {preview}")

def compare_values(cfg: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
    lic_cfg = cfg["license"]
    expected_key = lic_cfg["key"]
    expected_discord = lic_cfg["discord_id"]
    expected_product_name = lic_cfg["product_name"]

    lic = response.get("license") or {}
    cust = response.get("customer") or {}
    prod = response.get("product") or {}

    now = datetime.now(timezone.utc)

    expires_at_str = lic.get("expires_at")
    expires_dt: Optional[datetime] = None
    if isinstance(expires_at_str, str):
        try:
            expires_dt = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
        except Exception:
            expires_dt = None

    used_ips = lic.get("used_ips") or []
    max_ips = lic.get("max_ips") or 0
    used_ips_count = len(used_ips) if isinstance(used_ips, list) else 0
    remaining_ips = max(0, (max_ips if isinstance(max_ips, int) else 0) - used_ips_count)

    success_flag = response.get("success")
    status_text = response.get("status")
    api_success = (success_flag is True) or (success_flag is None and (status_text is None or status_text == "success"))

    checks = {
        "api_success": api_success,
        "license_active": lic.get("status") == "active",
        "key_matches": lic.get("license_key") == expected_key,
        "discord_matches": cust.get("discord_id") == expected_discord,
        "product_name_matches": (prod.get("name") == expected_product_name),
        "not_expired": (expires_dt is None) or (expires_dt > now),
    }

    mismatches = []
    if not checks["api_success"]:
        mismatches.append(f'API status indicates failure (status="{status_text}", success={success_flag})')
    if not checks["license_active"]:
        mismatches.append(f'License status is "{lic.get("status")}"')
    if not checks["key_matches"]:
        mismatches.append("license_key in response does not match config.key")
    if not checks["discord_matches"]:
        mismatches.append("customer.discord_id does not match config.discord_id")
    if not checks["product_name_matches"]:
        mismatches.append("product.name does not match config.product_name")
    if not checks["not_expired"]:
        mismatches.append("license is expired")

    return {
        "ok": len(mismatches) == 0,
        "checks": checks,
        "mismatches": mismatches,
        "message": response.get("message"),
        "expires_at": (expires_dt.isoformat() if expires_dt else None),
        "days_to_expiry": ((expires_dt - now).days if expires_dt else None),
        "remaining_ips": remaining_ips,
        "max_ips": max_ips if isinstance(max_ips, int) else 0,
        "used_ips_count": used_ips_count,
    }

def login(path: str = "config/config.json") -> int:
    try:
        cfg = load_config(path)
    except Exception as e:
        print(f"[CONFIG ERROR] {e}")
        sys.exit(2)

    # First try with no body; if server 500s, try once with a JSON body
    try:
        resp = call_license_api(cfg["license"]["url"], cfg["license"]["key"], use_body=False)
    except RuntimeError as e:
        msg = str(e)
        if "HTTP 500" in msg or "Internal Server Error" in msg:
            # Retry with body once
            try:
                resp = call_license_api(cfg["license"]["url"], cfg["license"]["key"], use_body=True)
            except Exception as e2:
                print(f"[API ERROR] {e2}")
                sys.exit(3)
        else:
            print(f"[API ERROR] {e}")
            sys.exit(3)

    result = compare_values(cfg, resp)

    print("License verification summary:")
    print(f" - API message: {result['message']}")
    print(f" - Active: {result['checks']['license_active']}")
    print(f" - Key matches config: {result['checks']['key_matches']}")
    print(f" - Discord matches config: {result['checks']['discord_matches']}")
    print(f" - Product name matches config: {result['checks']['product_name_matches']}")
    print(f" - Not expired: {result['checks']['not_expired']}")
    print(f" - Expires at: {result['expires_at']}")
    print(f" - Days to expiry: {result['days_to_expiry']}")
    print(f" - Remaining IP slots: {result['remaining_ips']} (max {result['max_ips']})")

    if not result["ok"]:
        print("[MISMATCHES]")
        for m in result["mismatches"]:
            print(f" - {m}")
        sys.exit(4)

    print("All checks passed.")