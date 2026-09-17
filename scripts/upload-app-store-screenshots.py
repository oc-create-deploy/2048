#!/usr/bin/env python3
import argparse
import hashlib
import os
import time
from pathlib import Path

import jwt
import requests

BASE = "https://api.appstoreconnect.apple.com/v1"


def make_token():
    now = int(time.time())
    with open(os.environ["ASC_KEY_PATH"]) as source:
        private_key = source.read()
    return jwt.encode(
        {"iss": os.environ["ASC_ISSUER_ID"], "iat": now, "exp": now + 900,
         "aud": "appstoreconnect-v1"},
        private_key,
        algorithm="ES256",
        headers={"kid": os.environ["ASC_KEY_ID"], "typ": "JWT"},
    )


class API:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {make_token()}",
                        "Content-Type": "application/json"}

    def request(self, method, path, payload=None, ok=(200, 201, 204)):
        response = requests.request(method, BASE + path, headers=self.headers,
                                    json=payload, timeout=90)
        if response.status_code not in ok:
            raise RuntimeError(f"{method} {path}: {response.status_code} {response.text}")
        return response.json() if response.content else None

    def data(self, path):
        return self.request("GET", path)["data"]


def localization_for_version(api, app_id, version_string):
    versions = api.data(
        f"/apps/{app_id}/appStoreVersions?filter[platform]=IOS&limit=50")
    version = next(item for item in versions
                   if item["attributes"]["versionString"] == version_string)
    localizations = api.data(
        f"/appStoreVersions/{version['id']}/appStoreVersionLocalizations")
    return next((item for item in localizations
                 if item["attributes"]["locale"] == "en-US"), localizations[0])


def screenshot_set(api, localization_id, display_type):
    sets = api.data(
        f"/appStoreVersionLocalizations/{localization_id}/appScreenshotSets?limit=50")
    found = next((item for item in sets
                  if item["attributes"]["screenshotDisplayType"] == display_type), None)
    if found:
        return found
    payload = {"data": {"type": "appScreenshotSets",
                         "attributes": {"screenshotDisplayType": display_type},
                         "relationships": {"appStoreVersionLocalization": {
                             "data": {"type": "appStoreVersionLocalizations",
                                      "id": localization_id}}}}}
    return api.request("POST", "/appScreenshotSets", payload)["data"]


def clear_set(api, set_id):
    for item in api.data(f"/appScreenshotSets/{set_id}/appScreenshots?limit=50"):
        api.request("DELETE", f"/appScreenshots/{item['id']}")


def reserve(api, set_id, path):
    payload = {"data": {"type": "appScreenshots",
                         "attributes": {"fileName": path.name,
                                        "fileSize": path.stat().st_size},
                         "relationships": {"appScreenshotSet": {
                             "data": {"type": "appScreenshotSets", "id": set_id}}}}}
    return api.request("POST", "/appScreenshots", payload)["data"]


def upload_file(reservation, path):
    content = path.read_bytes()
    operations = reservation["attributes"]["uploadOperations"]
    for operation in operations:
        start = operation["offset"]
        length = operation["length"]
        headers = {item["name"]: item["value"]
                   for item in operation.get("requestHeaders", [])}
        response = requests.request(operation["method"], operation["url"],
                                    headers=headers, data=content[start:start + length],
                                    timeout=180)
        if response.status_code not in (200, 201):
            raise RuntimeError(
                f"Screenshot upload failed: {response.status_code} {response.text}")
    return hashlib.md5(content).hexdigest()


def commit_upload(api, screenshot_id, checksum):
    payload = {"data": {"type": "appScreenshots", "id": screenshot_id,
                         "attributes": {"uploaded": True,
                                        "sourceFileChecksum": checksum}}}
    api.request("PATCH", f"/appScreenshots/{screenshot_id}", payload)


def wait_until_complete(api, screenshot_id):
    deadline = time.time() + 300
    while time.time() < deadline:
        item = api.request("GET", f"/appScreenshots/{screenshot_id}")["data"]
        state = item["attributes"].get("assetDeliveryState", {}).get("state")
        if state == "COMPLETE":
            return
        if state in {"FAILED", "COMPLETE_WITH_ERRORS"}:
            raise RuntimeError(f"Screenshot processing failed: {item['attributes']}")
        time.sleep(5)
    raise TimeoutError(f"Screenshot {screenshot_id} did not finish processing")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app-id", required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--version", default="1.0")
    parser.add_argument("--display-type", default="APP_IPHONE_69")
    args = parser.parse_args()

    paths = sorted(args.directory.glob("*.png"))
    if not paths:
        raise SystemExit("No PNG screenshots found")

    api = API()
    localization = localization_for_version(api, args.app_id, args.version)
    target_set = screenshot_set(api, localization["id"], args.display_type)
    clear_set(api, target_set["id"])
    for path in paths:
        reservation = reserve(api, target_set["id"], path)
        commit_upload(api, reservation["id"], upload_file(reservation, path))
        wait_until_complete(api, reservation["id"])
        print(f"Uploaded {path.name}")
    print(f"Uploaded {len(paths)} screenshots to {args.display_type}")

