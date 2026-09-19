# zynthec Apps

Eine schlanke AltStore-/SideStore-Source für eigene IPA-Dateien mit browserbasierter Admin-Seite.

## Enthalten

- `https://altsource.zynthec.com/source.json`: kompatibler AltSource-Feed.
- `https://altsource.zynthec.com/admin`: Apps hochladen, entfernen und ihre Metadaten gestalten.
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
gh release create apps --title "App downloads" --notes "Binary releases used by zynthec Apps."
gh release upload apps miPet-0.3-beta.ipa
```

Der Workflow **Publish IPA** kann eine IPA alternativ von einer direkten HTTPS-Adresse übernehmen, in das Release laden und danach den Store neu deployen.

## Admin-Zugang

Für `/admin` wird ein Fine-grained Personal Access Token benötigt, beschränkt auf `zynthec-dev/zynthec-altsource` mit:

- Repository permission `Contents: Read and write`
- möglichst kurzer Laufzeit

Das Token bleibt in `sessionStorage` des aktuellen Browser-Tabs und wird nur direkt an `api.github.com` übertragen. Es wird nicht in Website, Repository oder Build gespeichert.

Die App-Verwaltung ermöglicht:

- IPA-Dateien in das GitHub Release `apps` hochzuladen und daraus zu entfernen,
- Namen, Versionstexte, Beschreibungen und Farben zu ändern,
- eigene Icons und Screenshot-URLs zu hinterlegen.

## Deployment

GitHub Actions baut und testet die Source bei jedem Push. Für `altsource.zynthec.com` kann GitHub Pages oder Cloudflare Pages verwendet werden.

Der aktuelle Live-Stand wird über den Cloudflare Worker `zynthec-altsource` unter `https://altsource.zynthec.com` ausgeliefert.

- Build command bei Cloudflare Pages: `python3 scripts/build.py`
- Output directory: `dist`
- Custom domain: `altsource.zynthec.com`
