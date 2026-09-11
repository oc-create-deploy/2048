# App Store release

## App configuration

- Product name: `2048`
- App Store Connect name: `2048 Classic — Number Merge` (Apple ID `6811016385`)
- Bundle ID: `com.gamedevplayable.ttte`
- Marketing version: `1.0.0`
- Current production candidate: App Store version `1.0`, binary version `1.0.0`, build `2`
- Minimum iOS version: 13.0
- Supported device family and orientation: iPhone only, portrait
- Network access, tracking, advertising, analytics, accounts, and sensitive-device permissions: none
- Local data: current board and best score are stored only on the device with Hive

The app includes a full-size opaque 1024×1024 App Store icon and a static, lightweight launch screen. It does not request camera, microphone, photo, location, contacts, Bluetooth, tracking, or notification permissions.

## App Store Connect listing

- Subtitle: `Slide, merge, reach 2048`
- Primary category: Games → Puzzle, Board
- Secondary category: Entertainment
- Age rating: 4+
- Price: Free
- Availability: all 175 current App Store territories, including future territories
- Release method: manual release after approval
- Build: `2` (VALID; export compliance cleared)
- App privacy source-of-truth: no data collected and no tracking
- Third-party content: declared (the original game source is MIT licensed)

## Public product pages

- Product page: `https://classic-2048-game.pages.dev/`
- Support: `https://classic-2048-game.pages.dev/support/`
- Privacy policy: `https://classic-2048-game.pages.dev/privacy/`

## Validation

On Linux, run:

```sh
flutter pub get
dart format --output=none --set-exit-if-changed lib test
flutter analyze
flutter test
flutter build web --release
```

An Android debug build can also be used as a cross-platform compile check when an Android SDK is installed: `flutter build apk --debug`.

## TestFlight workflow

The manual **TestFlight** GitHub Actions workflow validates the app, creates a signed IPA on macOS, and uploads it with an App Store Connect API key. Configure these GitHub Actions repository secrets:

- `ASC_KEY_ID`
- `ASC_ISSUER_ID`
- `ASC_PRIVATE_KEY` (the complete `.p8` text)
- `BUILD_CERTIFICATE_BASE64` (base64-encoded Apple Distribution `.p12`)
- `P12_PASSWORD`
- `BUILD_PROVISION_PROFILE_BASE64` (base64-encoded App Store provisioning profile named `2048 App Store`)

Run **Actions → TestFlight → Run workflow** and enter a build number higher than every build previously uploaded for version 1.0.0. The workflow derives the Apple team identifier and provisioning UUID from the profile; neither value nor any signing credential is committed.

## macOS-only verification before first upload

1. Confirm the bundle ID exists in the intended Apple Developer team and the App Store Connect app record uses it.
2. Open `ios/Runner.xcworkspace` in the current stable Xcode and verify the Release signing identity/profile.
3. Run `flutter build ipa --release --build-name 1.0.0 --build-number 1` with the distribution profile installed, or run the TestFlight workflow.
4. Inspect the archive with Xcode Organizer and validate it with App Store Connect.
5. Complete App Store Connect metadata, screenshots, age rating, content rights, category, support/privacy URLs, and the privacy questionnaire. Based on the current source, the app collects no data and does not track users; re-review this answer whenever dependencies or features change.
