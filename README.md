# zynthec Source

Eine schlanke AltStore-/SideStore-Source für eigene IPA-Dateien mit browserbasierter Admin-Seite.

## Enthalten

- `https://source.zynthec.com`: kompatibler AltSource-Feed direkt an der Domainwurzel.
- `https://source.zynthec.com/admin/`: Apps hochladen, entfernen und ihre Metadaten gestalten.
- Automatische Metadaten- und Icon-Erkennung für IPA-Dateien im Projektordner.
- GitHub Release `apps` als Speicherort für die IPA-Downloads.

Es gibt bewusst keine Installationsseite, keine Loader-Downloads, kein Konfigurationsprofil und keine Zusammenführung fremder Sources.

## Lokal bauen

```bash
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 -m http.server 8080 --directory dist
```

Der fertige statische Build liegt in `dist/`.

## Erste IPA

`miPet-0.3-beta.ipa` enthält laut eingebetteter `Info.plist` die Version **0.1.0 (Build 1)**. Diese echten Metadaten werden im Feed verwendet.

IPAs werden nicht in Git eingecheckt. Sie gehören in das GitHub Release mit dem Tag `apps`:

```bash
gh release create apps --title "App downloads" --notes "Binary releases used by zynthec Source."
gh release upload apps miPet-0.3-beta.ipa
```

Der Workflow **Publish IPA** kann eine IPA alternativ von einer direkten HTTPS-Adresse übernehmen, in das Release laden und danach den Store neu deployen.

## Admin-Zugang

Für `/admin/` wird ein Fine-grained Personal Access Token benötigt, beschränkt auf `zynthec-dev/zynthec-source` mit:

- Repository permission `Contents: Read and write`
- möglichst kurzer Laufzeit

Das Token bleibt in `sessionStorage` des aktuellen Browser-Tabs und wird nur direkt an `api.github.com` übertragen. Es wird nicht in Website, Repository oder Build gespeichert.

Die App-Verwaltung ermöglicht:

- IPA-Dateien in das GitHub Release `apps` hochzuladen und daraus zu entfernen,
- Namen, Versionstexte, Beschreibungen und Farben zu ändern,
- eigene Icons und Screenshot-URLs zu hinterlegen.

## Deployment

GitHub Actions baut und testet die Source bei jedem Push. GitHub Pages stellt das Build-Artefakt bereit; Cloudflare liefert den Feed unter der eigenen Domain aus.

Der aktuelle Live-Stand wird über einen Cloudflare Worker unter `https://source.zynthec.com` ausgeliefert. Die Domainwurzel wird dabei auf das intern erzeugte `source.json` abgebildet.

- Build command bei Cloudflare Pages: `python3 scripts/build.py`
- Output directory: `dist`
- Custom domain: `source.zynthec.com`


## Violette Gestaltung und feste Reihenfolge

Die Source verwendet `#7045B8` und das gemeinsame neutrale Glas-Icon. zLoader (`com.zynthec.zloader`) steht in `apps`, `featuredApps` und im Admin-Panel immer zuerst, sofern der Eintrag vorhanden ist. Andere Apps behalten ihre relative Reihenfolge. Clients mit eigener Sortierung können die Feed-Reihenfolge überschreiben.

Das Admin-Panel unterstützt System/Hell/Dunkel, speichert ausschließlich die Darstellungspräferenz in localStorage und bleibt per Tastatur bedienbar. Dezente CSS-Transparenz ist eine Webannäherung; Apples native Liquid-Glass-Materialien werden nur im iOS-Icon verwendet. Reduzierte Bewegung, erhöhter Kontrast und reduzierte Transparenz werden berücksichtigt, soweit der Browser die entsprechenden Medienabfragen unterstützt.

Der isolierte Browsertest `tests/admin-ui.mjs` benötigt Playwright und Chrome. Mit `ADMIN_TEST_URL` lässt sich eine lokale Preview auswählen; `ADMIN_TEST_ROOT` kann alternativ die generierten `dist`-Dateien direkt bereitstellen. `PLAYWRIGHT_MODULE`, `CHROME_PATH` und `ADMIN_SCREENSHOTS` sind optional konfigurierbar. Der Test fängt sämtliche GitHub-Anfragen ab und verwendet ausschließlich Testdaten. Er prüft Reihenfolge, Tastaturbedienung, Abbrechen ohne Schreibzugriff, Theme-Persistenz, mobile Breite und Reduce Motion.
