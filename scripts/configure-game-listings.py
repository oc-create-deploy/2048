#!/usr/bin/env python3
import argparse
import os
import time

import jwt
import requests

BASE = "https://api.appstoreconnect.apple.com/v1"
SITE = "https://classic-2048-game.pages.dev/games"

GAMES = {
    "prism-stack": {
        "app": "6812284455", "name": "Prism Stack", "subtitle": "Relaxing block puzzle",
        "keywords": "block,puzzle,logic,brain,grid,tiles,offline,casual,relaxing,score",
        "promo": "Fit colorful blocks, clear complete lines, and build your best score.",
        "description": "Place colorful block pieces on the board and complete full rows or columns to clear space. Every placement matters, so plan ahead, keep the grid open, and build the highest score you can.\n\nFeatures:\n• Simple drag-and-place controls\n• Relaxing, untimed puzzle play\n• Satisfying line clears\n• High-score challenge\n• Fully offline gameplay\n• No accounts, advertising, analytics, or tracking",
        "categories": ["GAMES_PUZZLE", "GAMES_BOARD"],
        "notes": "Prism Stack is a fully offline block puzzle. No account, login, purchases, advertising, analytics, network connection, or special hardware is required. Drag pieces onto the grid and complete rows or columns to clear them."
    },
    "grandstay-manager": {
        "app": "6812284956", "name": "Grandstay Manager", "subtitle": "Build your hotel empire",
        "keywords": "hotel,manager,tycoon,simulation,business,rooms,guests,idle,upgrade,casual",
        "promo": "Welcome guests, improve rooms, and grow a thriving hotel business.",
        "description": "Take charge of a growing hotel and turn it into a thriving destination. Serve guests, improve rooms, manage the property, and expand your hospitality business step by step.\n\nFeatures:\n• Accessible hotel management gameplay\n• Room and service upgrades\n• Satisfying business progression\n• Colorful 3D presentation\n• Fully offline gameplay\n• No accounts, advertising, analytics, or tracking",
        "categories": ["GAMES_SIMULATION", "GAMES_STRATEGY"],
        "notes": "Grandstay Manager is a fully offline hotel management game. No account, login, purchases, advertising, analytics, network connection, or special hardware is required."
    },
    "chroma-pour": {
        "app": "6812285557", "name": "Chroma Pour", "subtitle": "Sort every color perfectly",
        "keywords": "water,sort,color,puzzle,tubes,logic,brain,pour,offline,casual",
        "promo": "Pour, sort, and separate every color in this satisfying logic puzzle.",
        "description": "Sort colored liquids until every tube contains a single color. Choose each pour carefully, create space for the next move, and solve increasingly tricky layouts.\n\nFeatures:\n• Easy tap-to-pour controls\n• Colorful sorting puzzles\n• Relaxing, untimed play\n• Increasing challenge\n• Fully offline gameplay\n• No accounts, advertising, analytics, or tracking",
        "categories": ["GAMES_PUZZLE", "GAMES_CASUAL"],
        "notes": "Chroma Pour is a fully offline color-sorting puzzle. No account, login, purchases, advertising, analytics, network connection, or special hardware is required."
    },
    "lexi-link": {
        "app": "6812286038", "name": "Lexi Link: Word Trails", "subtitle": "Connect letters, find words",
        "keywords": "word,letters,puzzle,vocabulary,spelling,brain,connect,offline,casual,game",
        "promo": "Swipe through letters, uncover hidden words, and complete every board.",
        "description": "Connect neighboring letters to discover hidden words and complete each puzzle. Look for every possible combination, expand your vocabulary, and enjoy satisfying word challenges.\n\nFeatures:\n• Smooth letter-linking controls\n• Engaging word puzzles\n• Vocabulary and spelling practice\n• Clean, colorful presentation\n• Offline iPhone gameplay\n• No accounts, advertising, analytics, or tracking",
        "categories": ["GAMES_WORD", "GAMES_PUZZLE"],
        "notes": "Lexi Link is an offline word puzzle. Its web-platform bridge is excluded from the iOS build. No account, login, purchases, advertising, analytics, network connection, or special hardware is required."
    },
    "rally-rush": {
        "app": "6812285914", "name": "Rally Rush", "subtitle": "Grow your crowd and race",
        "keywords": "runner,crowd,race,arcade,obstacles,gates,casual,offline,fast,3d",
        "promo": "Choose the best gates, grow your crowd, and race for the finish.",
        "description": "Lead a crowd of runners through gates and obstacles on the way to the finish. Choose the strongest route, avoid hazards, and build the biggest group you can.\n\nFeatures:\n• Quick one-touch runner gameplay\n• Crowd-growing gates\n• Obstacle-course challenges\n• Short, replayable levels\n• Fully offline gameplay\n• No accounts, advertising, analytics, or tracking",
        "categories": ["GAMES_RACING", "GAMES_CASUAL"],
        "notes": "Rally Rush is a fully offline crowd runner. No account, login, purchases, advertising, analytics, network connection, or special hardware is required."
    },
    "cubic-matchscape": {
        "app": "6812286911", "name": "Cubic Matchscape", "subtitle": "Match three objects in 3D",
        "keywords": "match,3d,puzzle,objects,triple,tiles,brain,offline,casual,sorting",
        "promo": "Find matching trios, clear the object pile, and keep your tray open.",
        "description": "Search a colorful pile of 3D objects and collect matching trios. Clear every object before the tray fills, and use careful observation to solve each board.\n\nFeatures:\n• Satisfying 3D object matching\n• Simple tap controls\n• Colorful toy-like objects\n• Observation and sorting challenges\n• Fully offline gameplay\n• No accounts, advertising, analytics, or tracking",
        "categories": ["GAMES_PUZZLE", "GAMES_CASUAL"],
        "notes": "Cubic Matchscape is a fully offline 3D matching puzzle. No account, login, purchases, advertising, analytics, network connection, or special hardware is required."
    },
    "empire-idle": {
        "app": "6812287093", "name": "Empire Idle", "subtitle": "Build and automate profits",
        "keywords": "idle,tycoon,business,empire,manager,upgrade,profit,simulation,casual,offline",
        "promo": "Build, upgrade, and automate your way to a growing business empire.",
        "description": "Start small and grow a thriving business empire. Invest your earnings, improve operations, unlock upgrades, and keep progress moving in an easygoing idle management game.\n\nFeatures:\n• Simple idle progression\n• Business and manager upgrades\n• Satisfying growth loop\n• Easy pick-up-and-play design\n• Offline gameplay\n• No accounts, advertising, analytics, or tracking",
        "categories": ["GAMES_SIMULATION", "GAMES_STRATEGY"],
        "notes": "Empire Idle is an offline idle management game. No account, login, purchases, advertising, analytics, network connection, or special hardware is required."
    },
    "metro-dash": {
        "app": "6812287453", "name": "Metro Dash: Urban Runner", "subtitle": "Run, dodge, keep moving",
        "keywords": "runner,dash,metro,obstacles,arcade,action,casual,offline,fast,3d",
        "promo": "Dash through the city, dodge every obstacle, and keep your run alive.",
        "description": "Run through a lively urban route, react to obstacles, collect rewards, and keep moving for as long as possible. Quick controls make every run easy to start and hard to put down.\n\nFeatures:\n• Fast endless-runner action\n• Responsive movement\n• Obstacles and collectibles\n• Replayable score chasing\n• Offline gameplay\n• No accounts, advertising, analytics, or tracking",
        "categories": ["GAMES_ACTION", "GAMES_CASUAL"],
        "notes": "Metro Dash is an offline endless runner. No account, login, purchases, advertising, analytics, network connection, or special hardware is required."
    },
    "merge-foundry": {
        "app": "6812287485", "name": "Merge Foundry", "subtitle": "Merge pieces, build more",
        "keywords": "merge,puzzle,combine,craft,upgrade,board,objects,offline,casual,brain",
        "promo": "Combine matching pieces, discover upgrades, and grow your merge board.",
        "description": "Combine matching pieces to create upgraded items and unlock new discoveries. Plan the board, keep useful space open, and continue building through a satisfying chain of merges.\n\nFeatures:\n• Simple drag-and-merge play\n• Discoverable item upgrades\n• Relaxing board progression\n• Colorful casual presentation\n• Offline gameplay\n• No accounts, advertising, analytics, or tracking",
        "categories": ["GAMES_PUZZLE", "GAMES_CASUAL"],
        "notes": "Merge Foundry is an offline merge puzzle. No account, login, purchases, advertising, analytics, network connection, or special hardware is required."
    },
    "velvet-solitaire": {
        "app": "6812283839", "name": "Velvet Solitaire: Calm Cards", "subtitle": "Classic cards, calm play",
        "keywords": "solitaire,cards,klondike,classic,patience,offline,relaxing,board,casual,game",
        "promo": "A clean, calming solitaire game with familiar cards and classic play.",
        "description": "Enjoy a polished solitaire experience designed for relaxing play on iPhone. Arrange cards, build the foundations, and complete the deck using familiar classic rules.\n\nFeatures:\n• Classic solitaire gameplay\n• Clear, readable cards\n• Smooth touch controls\n• Relaxing, replayable sessions\n• Fully offline play\n• No accounts, advertising, analytics, or tracking",
        "categories": ["GAMES_CARD", "GAMES_BOARD"],
        "notes": "Velvet Solitaire is a fully offline classic card game. No account, login, purchases, advertising, analytics, network connection, or special hardware is required."
    }
}

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
    "koreaAgeRatingOverride": "NONE"
}


def token():
    now = int(time.time())
    with open(os.environ["ASC_KEY_PATH"]) as handle:
        key = handle.read()
    return jwt.encode(
        {"iss": os.environ["ASC_ISSUER_ID"], "iat": now, "exp": now + 900, "aud": "appstoreconnect-v1"},
        key, algorithm="ES256", headers={"kid": os.environ["ASC_KEY_ID"], "typ": "JWT"})


class API:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {token()}", "Content-Type": "application/json"}

    def request(self, method, path, payload=None, ok=(200, 201, 204)):
        response = requests.request(method, BASE + path, headers=self.headers, json=payload, timeout=60)
        if response.status_code not in ok:
            raise RuntimeError(f"{method} {path}: {response.status_code} {response.text}")
        return response.json() if response.content else None

    def get_data(self, path):
        return self.request("GET", path)["data"]


def configure(api, slug, game):
    app_id = game["app"]
    app_info = api.get_data(f"/apps/{app_id}/appInfos")[0]
    info_id = app_info["id"]
    versions = api.get_data(f"/apps/{app_id}/appStoreVersions?filter[platform]=IOS&limit=10")
    version = next(item for item in versions if item["attributes"]["versionString"] == "1.0")
    version_id = version["id"]
    base_url = f"{SITE}/{slug}"

    api.request("PATCH", f"/apps/{app_id}", {"data": {"type": "apps", "id": app_id,
        "attributes": {"contentRightsDeclaration": "USES_THIRD_PARTY_CONTENT"}}})

    api.request("PATCH", f"/appInfos/{info_id}", {"data": {"type": "appInfos", "id": info_id,
        "relationships": {
            "primaryCategory": {"data": {"type": "appCategories", "id": "GAMES"}},
            "primarySubcategoryOne": {"data": {"type": "appCategories", "id": game["categories"][0]}},
            "primarySubcategoryTwo": {"data": {"type": "appCategories", "id": game["categories"][1]}},
            "secondaryCategory": {"data": {"type": "appCategories", "id": "ENTERTAINMENT"}}
        }}})

    info_locs = api.get_data(f"/appInfos/{info_id}/appInfoLocalizations")
    info_attrs = {"name": game["name"], "subtitle": game["subtitle"],
                  "privacyPolicyUrl": f"{base_url}/privacy/"}
    if info_locs:
        loc_id = info_locs[0]["id"]
        api.request("PATCH", f"/appInfoLocalizations/{loc_id}", {"data": {
            "type": "appInfoLocalizations", "id": loc_id, "attributes": info_attrs}})
    else:
        api.request("POST", "/appInfoLocalizations", {"data": {
            "type": "appInfoLocalizations", "attributes": {"locale": "en-US", **info_attrs},
            "relationships": {"appInfo": {"data": {"type": "appInfos", "id": info_id}}}}})

    api.request("PATCH", f"/ageRatingDeclarations/{info_id}", {"data": {
        "type": "ageRatingDeclarations", "id": info_id, "attributes": AGE}})

    api.request("PATCH", f"/appStoreVersions/{version_id}", {"data": {
        "type": "appStoreVersions", "id": version_id,
        "attributes": {"copyright": "2026 Playable Games", "releaseType": "MANUAL"}}})

    version_locs = api.get_data(f"/appStoreVersions/{version_id}/appStoreVersionLocalizations")
    version_attrs = {
        "description": game["description"], "keywords": game["keywords"],
        "marketingUrl": f"{base_url}/", "promotionalText": game["promo"],
        "supportUrl": f"{base_url}/support/"
    }
    if version_locs:
        loc_id = version_locs[0]["id"]
        api.request("PATCH", f"/appStoreVersionLocalizations/{loc_id}", {"data": {
            "type": "appStoreVersionLocalizations", "id": loc_id, "attributes": version_attrs}})
    else:
        api.request("POST", "/appStoreVersionLocalizations", {"data": {
            "type": "appStoreVersionLocalizations", "attributes": {"locale": "en-US", **version_attrs},
            "relationships": {"appStoreVersion": {"data": {"type": "appStoreVersions", "id": version_id}}}}})

    review = api.request("GET", f"/appStoreVersions/{version_id}/appStoreReviewDetail", ok=(200, 404))
    review_attrs = {
        "contactFirstName": "Alex", "contactLastName": "Lobanov",
        "contactPhone": "+35797439757", "contactEmail": "boltorez@icloud.com",
        "demoAccountRequired": False, "notes": game["notes"]
    }
    if review and review.get("data"):
        review_id = review["data"]["id"]
        api.request("PATCH", f"/appStoreReviewDetails/{review_id}", {"data": {
            "type": "appStoreReviewDetails", "id": review_id, "attributes": review_attrs}})
    else:
        api.request("POST", "/appStoreReviewDetails", {"data": {
            "type": "appStoreReviewDetails", "attributes": review_attrs,
            "relationships": {"appStoreVersion": {"data": {"type": "appStoreVersions", "id": version_id}}}}})

    builds = api.get_data(f"/builds?filter[app]={app_id}&filter[processingState]=VALID&sort=-uploadedDate&limit=1")
    if builds:
        build_id = builds[0]["id"]
        api.request("PATCH", f"/appStoreVersions/{version_id}", {"data": {
            "type": "appStoreVersions", "id": version_id,
            "relationships": {"build": {"data": {"type": "builds", "id": build_id}}}}})
        build_number = builds[0]["attributes"]["version"]
    else:
        build_number = None

    print(f"{game['name']}: metadata complete; build {build_number or 'pending'}; manual release")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=GAMES)
    args = parser.parse_args()
    api = API()
    items = [(args.only, GAMES[args.only])] if args.only else GAMES.items()
    for slug, game in items:
        configure(api, slug, game)


if __name__ == "__main__":
    main()
