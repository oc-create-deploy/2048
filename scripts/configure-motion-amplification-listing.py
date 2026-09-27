#!/usr/bin/env python3
import os
import time
import urllib.parse

import jwt
import requests

BASE = "https://api.appstoreconnect.apple.com/v1"
BUNDLE_ID = "com.industrial.motionamplification"
VERSION = "1.0"

AGE = {
    "advertising": False,
    "alcoholTobaccoOrDrugUseOrReferences": "NONE",
    "contests": "NONE",
    "gambling": False,
    "gamblingSimulated": "NONE",
    "gunsOrOtherWeapons": "NONE",
    "healthOrWellnessTopics": False,
    "lootBox": False,
    "medicalOrTreatmentInformation": "NONE",
    "messagingAndChat": False,
    "parentalControls": False,
    "profanityOrCrudeHumor": "NONE",
    "ageAssurance": False,
    "sexualContentGraphicAndNudity": "NONE",
    "sexualContentOrNudity": "NONE",
    "socialMedia": False,
    "socialMediaAgeRestricted": False,
    "horrorOrFearThemes": "NONE",
    "matureOrSuggestiveThemes": "NONE",
    "unrestrictedWebAccess": False,
    "userGeneratedContent": False,
    "violenceCartoonOrFantasy": "NONE",
    "violenceRealisticProlongedGraphicOrSadistic": "NONE",
    "violenceRealistic": "NONE",
    "ageRatingOverrideV2": "NONE",
    "koreaAgeRatingOverride": "NONE",
}


def make_token():
    now = int(time.time())
    with open(os.environ["ASC_KEY_PATH"], encoding="utf-8") as source:
        key = source.read()
    return jwt.encode(
        {"iss": os.environ["ASC_ISSUER_ID"], "iat": now, "exp": now + 900,
         "aud": "appstoreconnect-v1"},
        key, algorithm="ES256",
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

    def request_v2(self, method, path, payload=None, ok=(200, 201, 204)):
        response = requests.request(
            method, "https://api.appstoreconnect.apple.com/v2" + path,
            headers=self.headers, json=payload, timeout=90)
        if response.status_code not in ok:
            raise RuntimeError(f"{method} /v2{path}: {response.status_code} {response.text}")
        return response.json() if response.content else None


def ensure_free_price(api, app_id):
    current = api.request("GET", f"/apps/{app_id}/appPriceSchedule",
                          ok=(200, 404))
    if current and current.get("data"):
        return
    points = api.data(
        f"/apps/{app_id}/appPricePoints?filter[territory]=USA&include=territory&limit=200")
    free = next((item for item in points
                 if item.get("attributes", {}).get("customerPrice") == "0.0"), None)
    if free is None:
        raise RuntimeError("The free USA App Store price point was not found")
    inline_id = "${free-price}"
    api.request("POST", "/appPriceSchedules", {"data": {
        "type": "appPriceSchedules",
        "relationships": {
            "app": {"data": {"type": "apps", "id": app_id}},
            "baseTerritory": {"data": {"type": "territories", "id": "USA"}},
            "manualPrices": {"data": [{"type": "appPrices", "id": inline_id}]},
        }}, "included": [{
            "type": "appPrices", "id": inline_id,
            "attributes": {"startDate": None, "endDate": None},
            "relationships": {"appPricePoint": {"data": {
                "type": "appPricePoints", "id": free["id"]}}},
        }]})
    print("Created free App Store price schedule with USA as the base territory")


def ensure_worldwide_availability(api, app_id):
    current = api.request("GET", f"/apps/{app_id}/appAvailabilityV2",
                          ok=(200, 404))
    if current and current.get("data"):
        return
    territories = api.data("/territories?limit=200")
    linkages = []
    included = []
    for index, territory in enumerate(territories):
        inline_id = f"${{availability-{index}}}"
        linkages.append({"type": "territoryAvailabilities", "id": inline_id})
        included.append({
            "type": "territoryAvailabilities", "id": inline_id,
            "attributes": {"available": True, "preOrderEnabled": False,
                           "releaseDate": None},
            "relationships": {"territory": {"data": {
                "type": "territories", "id": territory["id"]}}},
        })
    api.request_v2("POST", "/appAvailabilities", {"data": {
        "type": "appAvailabilities",
        "attributes": {"availableInNewTerritories": True},
        "relationships": {
            "app": {"data": {"type": "apps", "id": app_id}},
            "territoryAvailabilities": {"data": linkages},
        }}, "included": included})
    print(f"Created App Store availability for all {len(territories)} territories")


def upsert_info_localization(api, info_id):
    items = api.data(f"/appInfos/{info_id}/appInfoLocalizations")
    attrs = {
        "name": "Motion Amplification Camera",
        "subtitle": "Reveal subtle machine motion",
        "privacyPolicyUrl": "https://globalistallc.com/motion-amplification-camera-privacy.html",
    }
    current = next((item for item in items
                    if item["attributes"]["locale"] == "en-US"), None)
    if current:
        api.request("PATCH", f"/appInfoLocalizations/{current['id']}", {"data": {
            "type": "appInfoLocalizations", "id": current["id"], "attributes": attrs}})
    else:
        api.request("POST", "/appInfoLocalizations", {"data": {
            "type": "appInfoLocalizations", "attributes": {"locale": "en-US", **attrs},
            "relationships": {"appInfo": {"data": {"type": "appInfos", "id": info_id}}}}})


def upsert_version_localization(api, version_id):
    items = api.data(f"/appStoreVersions/{version_id}/appStoreVersionLocalizations")
    attrs = {
        "description": (
            "Motion Amplification Camera helps engineers, technicians, and maintenance teams "
            "visualize subtle machine movement using an iPhone camera.\n\n"
            "Capture a stable view of equipment, select the motion band and gain, then process "
            "the recording on device. The app exports an accelerated, high-fidelity video that "
            "makes slow or slight visual changes easier to review.\n\n"
            "Features:\n"
            "• On-device motion visualization\n"
            "• Selectable frequency band and analysis gain\n"
            "• 1×, 2×, 4×, or 8× export playback\n"
            "• High-fidelity ProRes video export\n"
            "• Focus, exposure, and white-balance locks\n"
            "• Live horizon guidance\n"
            "• Calibrated visible-length measurement\n"
            "• Automatic center-point distance on supported devices\n"
            "• CSV session export\n"
            "• No accounts, advertising, analytics, or cloud uploads\n\n"
            "Results depend on camera stability, lighting, recording duration, target texture, "
            "device capability, and selected settings. This app is an inspection and visualization "
            "aid; it does not replace calibrated vibration instrumentation, engineering judgment, "
            "or required safety procedures."
        ),
        "keywords": "vibration,motion,camera,inspection,machinery,maintenance,frequency,video,industrial,analysis",
        "marketingUrl": "https://globalistallc.com/motion-amplification-camera.html",
        "promotionalText": (
            "Visualize subtle machine movement, estimate distance, and export accelerated "
            "high-fidelity inspection video—all on device."
        ),
        "supportUrl": "https://globalistallc.com/motion-amplification-camera-support.html",
    }
    current = next((item for item in items
                    if item["attributes"]["locale"] == "en-US"), None)
    if current:
        api.request("PATCH", f"/appStoreVersionLocalizations/{current['id']}", {"data": {
            "type": "appStoreVersionLocalizations", "id": current["id"], "attributes": attrs}})
    else:
        api.request("POST", "/appStoreVersionLocalizations", {"data": {
            "type": "appStoreVersionLocalizations", "attributes": {"locale": "en-US", **attrs},
            "relationships": {"appStoreVersion": {"data": {
                "type": "appStoreVersions", "id": version_id}}}}})


def review_details(api, version_id):
    attrs = {
        "contactFirstName": "Alex",
        "contactLastName": "Lobanov",
        "contactPhone": "+35797439757",
        "contactEmail": "contact@globalistallc.com",
        "demoAccountRequired": False,
        "notes": (
            "No account or demo credentials are required. The app needs a physical iPhone camera; "
            "please grant Camera and Photos access. Mount or brace the phone, aim at a well-lit "
            "textured object, tap Start analysis, record for 10–15 seconds, then stop and wait for "
            "on-device processing. The result can be reviewed, saved, or shared. Automatic distance "
            "uses available depth/AR tracking and may correctly show unavailable on unsupported "
            "hardware or unsuitable scenes. The app has no purchases, ads, analytics, account system, "
            "or cloud upload."
        ),
    }
    response = api.request("GET", f"/appStoreVersions/{version_id}/appStoreReviewDetail",
                           ok=(200, 404))
    if response and response.get("data"):
        item_id = response["data"]["id"]
        api.request("PATCH", f"/appStoreReviewDetails/{item_id}", {"data": {
            "type": "appStoreReviewDetails", "id": item_id, "attributes": attrs}})
    else:
        api.request("POST", "/appStoreReviewDetails", {"data": {
            "type": "appStoreReviewDetails", "attributes": attrs,
            "relationships": {"appStoreVersion": {"data": {
                "type": "appStoreVersions", "id": version_id}}}}})


def main():
    api = API()
    encoded = urllib.parse.quote(BUNDLE_ID, safe="")
    apps = api.data(f"/apps?filter[bundleId]={encoded}&limit=2")
    if len(apps) != 1:
        raise RuntimeError(f"Expected one app for {BUNDLE_ID}; found {len(apps)}")
    app = apps[0]
    app_id = app["id"]
    print(f"App: {app['attributes']['name']} ({app_id})")

    api.request("PATCH", f"/apps/{app_id}", {"data": {
        "type": "apps", "id": app_id,
        "attributes": {"contentRightsDeclaration": "DOES_NOT_USE_THIRD_PARTY_CONTENT"}}})

    info = api.data(f"/apps/{app_id}/appInfos")[0]
    info_id = info["id"]
    api.request("PATCH", f"/appInfos/{info_id}", {"data": {
        "type": "appInfos", "id": info_id,
        "relationships": {
            "primaryCategory": {"data": {"type": "appCategories", "id": "UTILITIES"}},
            "secondaryCategory": {"data": {"type": "appCategories", "id": "PHOTO_AND_VIDEO"}},
        }}})
    upsert_info_localization(api, info_id)
    api.request("PATCH", f"/ageRatingDeclarations/{info_id}", {"data": {
        "type": "ageRatingDeclarations", "id": info_id, "attributes": AGE}})

    versions = api.data(f"/apps/{app_id}/appStoreVersions?filter[platform]=IOS&limit=20")
    version = next((item for item in versions
                    if item["attributes"]["versionString"] == VERSION), None)
    if version is None:
        version = api.request("POST", "/appStoreVersions", {"data": {
            "type": "appStoreVersions",
            "attributes": {"platform": "IOS", "versionString": VERSION,
                           "releaseType": "MANUAL"},
            "relationships": {"app": {"data": {"type": "apps", "id": app_id}}}}})["data"]
    version_id = version["id"]
    api.request("PATCH", f"/appStoreVersions/{version_id}", {"data": {
        "type": "appStoreVersions", "id": version_id,
        "attributes": {"copyright": "2026 Globalista LLC", "releaseType": "MANUAL"}}})
    upsert_version_localization(api, version_id)
    review_details(api, version_id)

    builds = api.data(f"/builds?filter[app]={app_id}&filter[processingState]=VALID&sort=-uploadedDate&limit=10")
    build = next((item for item in builds if item["attributes"]["version"] == "17"),
                 builds[0] if builds else None)
    if build is None:
        raise RuntimeError("No VALID build is available")
    api.request("PATCH", f"/appStoreVersions/{version_id}", {"data": {
        "type": "appStoreVersions", "id": version_id,
        "relationships": {"build": {"data": {"type": "builds", "id": build["id"]}}}}})

    ensure_free_price(api, app_id)
    ensure_worldwide_availability(api, app_id)

    prices = api.request(
        "GET", f"/appPriceSchedules/{app_id}/manualPrices?include=appPricePoint&limit=200")
    is_free = any(item.get("attributes", {}).get("customerPrice") == "0.0"
                  for item in prices.get("included", []))

    availability = api.request("GET", f"/apps/{app_id}/appAvailabilityV2")
    availability_id = availability["data"]["id"]
    territory_response = requests.get(
        f"https://api.appstoreconnect.apple.com/v2/appAvailabilities/{availability_id}/territoryAvailabilities?limit=200",
        headers=api.headers, timeout=90)
    territory_response.raise_for_status()
    territories = territory_response.json()["data"]
    unavailable = [item["id"] for item in territories
                   if not item.get("attributes", {}).get("available", False)]
    new_territories = availability["data"]["attributes"]["availableInNewTerritories"]

    print(f"Configured version {VERSION} with build {build['attributes']['version']}")
    print("Release type: MANUAL")
    print(f"Pricing: {'FREE' if is_free else 'NOT_VERIFIED_FREE'}")
    print(f"Availability: {len(territories) - len(unavailable)}/{len(territories)} territories; "
          f"availableInNewTerritories={new_territories}")
    if not is_free or unavailable or not new_territories:
        raise RuntimeError("Pricing or worldwide availability is incomplete")


if __name__ == "__main__":
    main()
