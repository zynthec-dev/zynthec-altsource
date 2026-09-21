import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (DIST / "source.json").exists():
            subprocess.run(["python3", "scripts/build.py"], cwd=ROOT, check=True)

    def test_source_contains_every_available_ipa(self):
        source = json.loads((DIST / "source.json").read_text())
        ipas = list(ROOT.glob("*.ipa"))
        import importlib.util
        spec = importlib.util.spec_from_file_location("source_build", ROOT / "scripts/build.py")
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        bundle_ids = {builder.plist_from_ipa(ipa)[0]["CFBundleIdentifier"] for ipa in ipas}
        self.assertEqual({app["bundleIdentifier"] for app in source["apps"]}, bundle_ids)
        for app in source["apps"]:
            self.assertTrue(app["versions"][0]["downloadURL"].endswith(".ipa"))
            self.assertGreater(app["versions"][0]["size"], 0)

    @unittest.skipUnless((ROOT / "miPet-0.3-beta.ipa").exists(), "miPet release asset is not available")
    def test_mipet_metadata(self):
        source = json.loads((DIST / "source.json").read_text())
        app = next(app for app in source["apps"] if app["bundleIdentifier"] == "de.renewitt.mipet")
        self.assertEqual(app["versions"][0]["version"], "0.1.0")
        self.assertEqual(app["versions"][0]["marketingVersion"], "0.3-beta")

    @unittest.skipUnless(
        (ROOT / "liveMic-1.0.8.ipa").exists() and (ROOT / "YouTube-Music-Ultimate-2.4.1_9.37.2-no-cast.ipa").exists(),
        "liveMic and YouTube Music release assets are not available",
    )
    def test_filename_versions_and_names_are_separate(self):
        source = json.loads((DIST / "source.json").read_text())
        versions = {
            app["name"]: app["versions"][0]["marketingVersion"]
            for app in source["apps"]
        }
        latest_live_mic = sorted(ROOT.glob("liveMic-*.ipa"), key=lambda p: tuple(int(n) for n in p.stem.removeprefix("liveMic-").split(".")))[-1]
        self.assertEqual(versions["liveMic"], latest_live_mic.stem.removeprefix("liveMic-"))
        self.assertEqual(versions["YouTube Music Ultimate"], "2.4.1_9.37.2-no-cast")

    def test_feed_has_no_private_origin_metadata(self):
        source = json.loads((DIST / "source.json").read_text())
        self.assertTrue(all("_origin" not in app for app in source["apps"]))

    def test_youtube_music_no_longer_declares_cast_permissions(self):
        source = json.loads((DIST / "source.json").read_text())
        app = next(app for app in source["apps"] if app["bundleIdentifier"] == "com.google.ios.youtubemusic")
        entitlements = set(app["appPermissions"]["entitlements"])
        self.assertNotIn("com.apple.developer.networking.multicast", entitlements)
        self.assertNotIn("com.apple.developer.networking.wifi-info", entitlements)
        self.assertNotIn("com.apple.developer.mediasetup", entitlements)
        self.assertIn("com.apple.developer.carplay-audio", entitlements)

    def test_configured_apps_have_valid_release_filenames(self):
        content = json.loads((ROOT / "catalog" / "content.json").read_text())
        apps = [
            *content.get("localApps", {}).values(),
            *content.get("uploadedApps", []),
        ]
        filenames = [app.get("ipaFile") for app in apps]
        self.assertTrue(all(
            isinstance(filename, str) and filename.strip().endswith(".ipa")
            for filename in filenames
        ))
        self.assertEqual(len(filenames), len(set(filenames)))

    @unittest.skipUnless((ROOT / "DeviceHubRemote-0.1.0.ipa").exists(), "Device Hub release asset is not available")
    def test_devicehub_metadata(self):
        import hashlib
        source = json.loads((DIST / "source.json").read_text())
        app = next(app for app in source["apps"] if app["bundleIdentifier"] == "com.zynthec.devicehubremote")
        self.assertEqual(app["name"], "Device Hub Remote")
        version = app["versions"][0]
        self.assertEqual(version["version"], "0.1.0")
        self.assertEqual(version["minOSVersion"], "17.2")
        self.assertEqual(version["sha256"], hashlib.sha256((ROOT / "DeviceHubRemote-0.1.0.ipa").read_bytes()).hexdigest())
        self.assertIn("NSLocalNetworkUsageDescription", app["appPermissions"]["privacy"])
        self.assertTrue((DIST / "assets/apps/com.zynthec.devicehubremote.png").is_file())

    def test_admin_is_built_without_storefront_or_installer_artifacts(self):
        self.assertTrue((DIST / "admin" / "index.html").exists())
        admin_html = (DIST / "admin" / "index.html").read_text()
        self.assertNotIn('href="/admin/', admin_html)
        self.assertNotIn('src="/admin/', admin_html)
        self.assertNotIn('href="/assets/', admin_html)
        self.assertNotIn('src="/assets/', admin_html)
        self.assertFalse((DIST / "index.html").exists())
        self.assertFalse((DIST / "app.js").exists())
        self.assertFalse((DIST / "styles.css").exists())
        self.assertFalse((DIST / "data" / "catalog.json").exists())
        self.assertFalse((DIST / "data" / "loaders.json").exists())
        self.assertFalse((DIST / "zloader.mobileconfig").exists())


if __name__ == "__main__":
    unittest.main()
