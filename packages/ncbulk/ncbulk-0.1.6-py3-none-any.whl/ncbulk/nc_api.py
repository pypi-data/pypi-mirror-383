from __future__ import annotations

import os
import time
from typing import Any, Dict, Iterable, Optional, Tuple

import requests
import logging


OCS_HEADERS = {"OCS-APIRequest": "true"}


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Environment variable {name} is required but not set. "
            "Set it via .env or export before running."
        )
    return value


def http_request_with_retries(
    method: str,
    url: str,
    *,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 15,
    retries: int = 2,
    verbose: bool = False,
):
    logger = logging.getLogger("ncbulk.nc_api")
    last_exc: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            if verbose:
                logger.debug(
                    "HTTP %s %s (attempt %s/%s)",
                    method,
                    url,
                    attempt + 1,
                    retries + 1,
                )
            resp = requests.request(
                method,
                url,
                auth=(
                    _require_env("NEXTCLOUD_ADMIN_USERNAME"),
                    _require_env("NEXTCLOUD_ADMIN_PASSWORD"),
                ),
                headers=OCS_HEADERS,
                data=data,
                params=params,
                timeout=timeout,
            )
            return resp
        except requests.RequestException as exc:  # type: ignore[name-defined]
            last_exc = exc
            if attempt < retries:
                time.sleep(1.0 * (attempt + 1))
    if last_exc:
        raise last_exc


def is_user_absent(
    username: str, *, timeout: int = 15, retries: int = 2, verbose: bool = False
) -> bool:
    resp = http_request_with_retries(
        "GET",
        f"{_require_env('NEXTCLOUD_URL')}/ocs/v2.php/cloud/users/{username}",
        timeout=timeout,
        retries=retries,
        verbose=verbose,
    )
    if resp.status_code == 404:
        return True
    if resp.status_code == 200:
        try:
            data = resp.json()
            ocs = data.get("ocs", {})
            # If data payload present, treat as exists
            if "data" in ocs:
                return False
            meta = ocs.get("meta", {})
            # Nextcloud OCS success usually has ocs/meta/statuscode == 200
            code = int(meta.get("statuscode", 0))
            return code != 200
        except Exception:
            # Fall back to considering user present on any 200 without parseable body
            return False
    # For other 2xx codes treat as present; otherwise absent
    return resp.status_code >= 400


def check_ocs_availability(
    *, timeout: int = 15, retries: int = 2, verbose: bool = False
) -> Tuple[bool, Optional[str]]:
    """Quick health check of Nextcloud OCS and credentials.

    Returns (ok, reason). On success, (True, None). On failure, (False, message).
    """
    logger = logging.getLogger("ncbulk.nc_api")
    try:
        base_url = _require_env("NEXTCLOUD_URL")
        _ = _require_env("NEXTCLOUD_ADMIN_USERNAME")
        _ = _require_env("NEXTCLOUD_ADMIN_PASSWORD")
    except Exception as exc:
        return False, str(exc)

    # Basic reachability: capabilities endpoint
    try:
        cap_resp = http_request_with_retries(
            "GET",
            f"{base_url}/ocs/v2.php/cloud/capabilities",
            timeout=timeout,
            retries=retries,
            verbose=verbose,
        )
    except Exception as exc:
        return False, f"Failed to reach OCS capabilities: {exc}"

    if cap_resp.status_code >= 400:
        return (
            False,
            f"OCS capabilities returned HTTP {cap_resp.status_code}: {cap_resp.text[:200]}",
        )

    # Privilege/credentials check: list users (admin required)
    try:
        users_resp = http_request_with_retries(
            "GET",
            f"{base_url}/ocs/v2.php/cloud/users",
            params={"search": "", "limit": 1},
            timeout=timeout,
            retries=retries,
            verbose=verbose,
        )
    except Exception as exc:
        return False, f"Failed to query users: {exc}"

    if users_resp.status_code in (401, 403):
        return False, (
            "Invalid credentials or insufficient privileges for provisioning API. "
            "Tip: create an App Password in Nextcloud and use it instead of the main password."
        )
    if users_resp.status_code >= 400:
        # Other server/client errors
        return (
            False,
            f"Users endpoint returned HTTP {users_resp.status_code}: {users_resp.text[:200]}",
        )

    # HTTP 2xx considered OK
    if verbose:
        logger.debug(
            "OCS health check passed: capabilities and users endpoints reachable"
        )
    return True, None


def update_user_field(
    username: str,
    key: str,
    value: str,
    *,
    timeout: int = 15,
    retries: int = 2,
    verbose: bool = False,
):
    return http_request_with_retries(
        "PUT",
        f"{_require_env('NEXTCLOUD_URL')}/ocs/v2.php/cloud/users/{username}",
        data={"key": key, "value": value},
        timeout=timeout,
        retries=retries,
        verbose=verbose,
    )


def create_nextcloud_user(
    username: str,
    password: Optional[str],
    groups: Iterable[str],
    *,
    email: Optional[str] = None,
    displayname: Optional[str] = None,
    language: Optional[str] = None,
    timeout: int = 15,
    retries: int = 2,
    verbose: bool = False,
):
    data: Dict[str, Any] = {"userid": username}
    if password:
        data["password"] = password
    for i, g in enumerate(groups):
        data[f"groups[{i}]"] = g
    if language:
        data["language"] = language
    # Pass email/displayname at creation time if present to support welcome mode
    if email:
        # Nextcloud API expects key 'email'
        data["email"] = email
    if displayname:
        data["displayname"] = displayname

    resp = http_request_with_retries(
        "POST",
        f"{_require_env('NEXTCLOUD_URL')}/ocs/v2.php/cloud/users",
        data=data,
        timeout=timeout,
        retries=retries,
        verbose=verbose,
    )
    if resp.status_code == 200:
        return True
    return resp.text


def assign_user_to_group(
    username: str,
    group: str,
    *,
    timeout: int = 15,
    retries: int = 2,
    verbose: bool = False,
):
    return http_request_with_retries(
        "POST",
        f"{_require_env('NEXTCLOUD_URL')}/ocs/v2.php/cloud/users/{username}/groups",
        data={"groupid": group},
        timeout=timeout,
        retries=retries,
        verbose=verbose,
    )
