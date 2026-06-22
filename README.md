<div align="center">
<img src="https://upload.wikimedia.org/wikipedia/commons/5/5f/Apple_Music_icon.svg" width="80" alt="Apple Music" />
# Apple Music Rich Presence
 
[![Python](https://img.shields.io/badge/Python-3.10--3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=flat-square&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Discord](https://img.shields.io/badge/Discord-Rich%20Presence-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
 
**🇬🇧 [English](#-english) · 🇹🇷 [Türkçe](#-türkçe)**
 
</div>
---
 
## 🇬🇧 English
 
### What does it do?
 
Shows what you're listening to on Apple Music directly on your Discord profile — song title, artist, **real album art** and a progress bar. Exactly like the built-in Spotify integration, but for Apple Music.
 
```
🎵  Listening to Apple Music
    In Your Eyes
    Inna
    ━━━━━━━━━━━━━━━━━━━━  2:34 / 5:27
```
 
### Features
 
- 🎵 **"Listening to Apple Music"** — not "Playing", exactly like Spotify
- 🖼️ **Real album art** — pulled directly from Apple Music, not guessed
- ⏱️ **Progress bar** — shows exactly where in the song you are
- 👤 **Artist name** — shows in the compact label next to your name too
- 🔗 **Apple Music profile button** — optional, one line in config
- 🔄 **Zero manual effort** — set up once, runs forever
- 🪶 **Lightweight** — ~60 MB RAM, silent background process
### Requirements
 
| | |
|---|---|
| OS | Windows 10 or 11 |
| Python | 3.10, 3.11 or 3.12 |
| Apple Music | Microsoft Store version |
| Discord | Desktop app (not browser) |
 
> **Python version matters.** `winsdk` only ships pre-built wheels for 3.10–3.12. If you're on 3.13+, create a separate environment with `py -3.12 -m venv venv`.
 
### Installation
 
**1. Clone the repo**
 
```bash
git clone https://github.com/yourusername/applemusic-discord-presence.git
cd applemusic-discord-presence
```
 
**2. Install dependencies**
 
```bash
pip install -r requirements.txt
```
 
**3. Get a Discord Application ID**
 
This is required for any Rich Presence app — Discord's rule, not ours. Only done once, ever.
 
1. Go to [discord.com/developers/applications](https://discord.com/developers/applications) → **New Application**
2. Name it anything (e.g. `"Apple Music"`) — this name won't appear on your profile
3. Copy the **Application ID** from the General Information page
**4. Create the config**
 
```bash
python main.py
```
 
The script auto-creates `config.json` on first run and stops. Open it, paste your ID:
 
```json
{
  "discord_client_id": "PASTE_HERE",
  ...
}
```
 
**5. Run**
 
```bash
python main.py
```
 
Play something in Apple Music. Discord updates within a few seconds.
 
### Auto-start (no manual launching, ever)
 
1. Open `start_hidden.vbs` in a text editor and replace the placeholder path with this folder's real path
2. Press `Win + R`, type `shell:startup`, hit Enter — your Startup folder opens
3. Right-click `start_hidden.vbs` → **Create shortcut** → move that shortcut into the Startup folder
The script now starts silently at every login — no console window, no manual step.
 
**To stop permanently:** delete the shortcut from the Startup folder.
 
### Configuration
 
```json
{
  "discord_client_id": "YOUR_APPLICATION_ID",
  "app_id_match": "applemusic",
  "show_profile_button": false,
  "profile_button_label": "Show Apple Music Profile",
  "profile_url": "",
  "poll_interval_seconds": 5
}
```
 
| Field | Description | Default |
|---|---|---|
| `discord_client_id` | ID from Discord Developer Portal | — |
| `app_id_match` | Substring used to identify Apple Music's media session | `"applemusic"` |
| `show_profile_button` | Show/hide the profile button | `false` |
| `profile_button_label` | Button text | `"Show Apple Music Profile"` |
| `profile_url` | Your Apple Music profile link | `""` |
| `poll_interval_seconds` | How often to check for changes | `5` |
 
**Profile button:**
```json
"show_profile_button": true,
"profile_url": "https://music.apple.com/profile/yourusername"
```
 
> **Note:** Discord only shows Rich Presence buttons to *other* people viewing your profile — you won't see your own button. This is a Discord platform limitation, not a bug.
 
### How it works
 
```
Apple Music
    │  album art + track info
    ▼
Windows SMTC API  ──────────────────────────────┐
(GlobalSystemMediaTransportControls)             │
    │                                            │
    │  text: title / artist / album              │  image: raw bytes
    ▼                                            ▼
 Artist                                    catbox.moe
 cleanup                                (anonymous upload)
    │                                            │
    │                                            │  URL
    ▼                                            ▼
Discord RPC  ◄──────────────────────────────────┘
(pypresence)
    │
    ▼
Shows on your Discord profile
```
 
**Artwork priority:**
 
1. **Apple Music's own image** — the exact bytes Apple Music hands to Windows (same as the volume flyout). Uploaded to `catbox.moe` to get a URL Discord can use.
2. **iTunes Search API** — fallback. Song title, artist and album are each scored independently. If none clear the confidence floor, **no image is shown rather than a wrong one**.
Both results are cached per track — network calls happen once per song change, not every poll.
 
### Troubleshooting
 
<details>
<summary><b>Nothing shows up</b></summary>
- Discord desktop app must be open (not the browser)
- Apple Music must be **playing**, not paused
- Double-check `discord_client_id` in `config.json`
- Make sure `app_id_match` is `"applemusic"` (lowercase)
</details>
<details>
<summary><b>Shows "Playing" instead of "Listening to"</b></summary>
Update `pypresence` — older versions don't support `activity_type`:
 
```bash
pip install -U pypresence
```
 
</details>
<details>
<summary><b>winsdk fails to install (build error)</b></summary>
`winsdk` only has pre-built wheels for Python 3.10–3.12. On 3.13+, pip tries to compile from source which requires Visual Studio's C++ build tools.
 
Solution — use a 3.12 virtual environment:
 
```bash
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
 
</details>
<details>
<summary><b>Artwork missing for some tracks</b></summary>
For local files or rare releases, Apple Music sometimes doesn't provide a thumbnail to Windows, and iTunes Search finds no match either. In that case, no image is shown intentionally — a blank space is better than the wrong cover.
 
</details>
### Dependencies
 
| Package | Version | Purpose |
|---|---|---|
| [pypresence](https://github.com/qwertyquerty/pypresence) | ≥ 4.6.1 | Discord RPC connection |
| [winsdk](https://github.com/pywinrt/python-winsdk) | ≥ 1.0.0 | Windows media API bindings |
| [requests](https://docs.python-requests.org/) | ≥ 2.31.0 | Album art upload |
 
---
 
## 🇹🇷 Türkçe
 
### Ne Yapar?
 
Apple Music'te ne dinlediğiniz, Discord profilinizde **gerçek zamanlı** olarak görünür — şarkı adı, sanatçı, **gerçek kapak resmi** ve ilerleme çubuğuyla birlikte. Spotify entegrasyonundan hiçbir farkı yok. Hatta bir üstünlüğü var: kapak resmini doğrudan Apple Music'in kendisinden çekiyor, tahmin etmiyor.
 
```
🎵  Listening to Apple Music
    In Your Eyes
    Inna
    ━━━━━━━━━━━━━━━━━━━━  2:34 / 5:27
```
 
### Özellikler
 
- 🎵 **"Listening to Apple Music"** — Spotify gibi, "Playing" değil
- 🖼️ **Gerçek kapak resmi** — Apple Music'in verdiği tam resim, tahmin değil
- ⏱️ **İlerleme çubuğu** — şarkının nerede olduğunu gösterir
- 👤 **Sanatçı adı** — Discord'daki o küçük etikette de görünür
- 🔗 **Apple Music profil butonu** — isteğe bağlı, tek satırla açılır
- 🔄 **Sıfır manuel müdahale** — bir kez kur, her zaman çalışır
- 🪶 **Hafif** — ~60 MB RAM, arka planda sessizce çalışır
### Gereksinimler
 
| | |
|---|---|
| İşletim Sistemi | Windows 10 veya 11 |
| Python | 3.10, 3.11 veya 3.12 |
| Apple Music | Microsoft Store versiyonu |
| Discord | Masaüstü uygulaması (tarayıcı değil) |
 
> **Python sürümü önemli.** `winsdk` yalnızca 3.10–3.12 için derlenmiş paket sunuyor. 3.13+ kullanıyorsanız `py -3.12 -m venv venv` ile ayrı bir ortam oluşturun.
 
### Kurulum
 
**1. Repoyu klonla**
 
```bash
git clone https://github.com/kullaniciadin/applemusic-discord-presence.git
cd applemusic-discord-presence
```
 
**2. Bağımlılıkları kur**
 
```bash
pip install -r requirements.txt
```
 
**3. Discord Application ID al**
 
Bu adım, herhangi bir Rich Presence uygulaması için zorunlu — Discord'un kuralı. Yalnızca **bir kez** yapılır.
 
1. [discord.com/developers/applications](https://discord.com/developers/applications) → **New Application**
2. İsim ver (örn. `"Apple Music"`) — bu isim profilinde görünmez
3. **General Information** sayfasından **Application ID**'yi kopyala
**4. Config dosyasını oluştur**
 
```bash
python main.py
```
 
Script ilk çalışmada `config.json` dosyasını otomatik oluşturur ve durur. Dosyayı aç, ID'yi yapıştır:
 
```json
{
  "discord_client_id": "BURAYA_YAPISTIR",
  ...
}
```
 
**5. Çalıştır**
 
```bash
python main.py
```
 
Apple Music'te bir şey çal. Discord birkaç saniye içinde güncellenir.
 
### Otomatik Başlatma
 
Her açılışta manuel çalıştırmamak için:
 
1. `start_hidden.vbs` dosyasını bir metin editörüyle aç, placeholder yolu gerçek yolla değiştir
2. `Win + R` → `shell:startup` → Enter — Başlangıç klasörü açılır
3. `start_hidden.vbs` dosyasına sağ tık → **Kısayol oluştur** → kısayolu o klasöre taşı
Artık Windows her açıldığında script arka planda, sessizce çalışır. Konsol penceresi çıkmaz.
 
**Durdurmak için:** Başlangıç klasöründeki kısayolu sil.
 
### Yapılandırma
 
```json
{
  "discord_client_id": "APPLICATION_ID_BURAYA",
  "app_id_match": "applemusic",
  "show_profile_button": false,
  "profile_button_label": "Show Apple Music Profile",
  "profile_url": "",
  "poll_interval_seconds": 5
}
```
 
| Alan | Açıklama | Varsayılan |
|---|---|---|
| `discord_client_id` | Discord Developer Portal'dan alınan ID | — |
| `app_id_match` | Apple Music oturumunu bulmak için eşleşme metni | `"applemusic"` |
| `show_profile_button` | Profil butonunu göster/gizle | `false` |
| `profile_button_label` | Buton yazısı | `"Show Apple Music Profile"` |
| `profile_url` | Apple Music profil linki | `""` |
| `poll_interval_seconds` | Kaç saniyede bir kontrol etsin | `5` |
 
**Profil butonu:**
```json
"show_profile_button": true,
"profile_url": "https://music.apple.com/profile/kullaniciadin"
```
 
> **Not:** Discord, Rich Presence butonlarını kendi profilinde göstermez — başkaları görür. Bu Discord'un kısıtlaması, hata değil.
 
### Nasıl Çalışır?
 
```
Apple Music
    │  kapak resmi + şarkı bilgisi
    ▼
Windows SMTC API  ──────────────────────────────┐
(GlobalSystemMediaTransportControls)             │
    │                                            │
    │  metin: şarkı / sanatçı / albüm            │  görsel: ham resim baytları
    ▼                                            ▼
 Sanatçı                                   catbox.moe
 temizleme                               (anonim yükleme)
    │                                            │
    │                                            │  URL
    ▼                                            ▼
Discord RPC  ◄──────────────────────────────────┘
(pypresence)
    │
    ▼
Discord profilinizde görünür
```
 
**Kapak resmi önceliği:**
 
1. **Apple Music'in verdiği resim** — Apple Music'in Windows'a ilettiği tam resim (ses seviyesi tuşunda görünenle aynı). `catbox.moe`'ya yüklenerek Discord'un okuyabileceği bir URL'e dönüştürülüyor.
2. **iTunes Search API eşleştirmesi** — yedek plan. Şarkı adı, sanatçı ve albüm üç ayrı güven skoru üzerinden değerlendiriliyor; hiçbiri eşiği geçemezse **yanlış resim göstermek yerine resim gösterilmiyor**.
Her iki sonuç da önbellekleniyor — ağ çağrıları her polling'de değil, şarkı değiştiğinde bir kez yapılıyor.
 
### Sorun Giderme
 
<details>
<summary><b>Hiçbir şey görünmüyor</b></summary>
- Discord masaüstü uygulaması açık olmalı (tarayıcı değil)
- Apple Music çalıyor olmalı (duraklatılmış değil)
- `config.json` içinde `discord_client_id` doğru yapıştırılmış olmalı
- `app_id_match` değerinin `"applemusic"` (küçük harf) olduğunu kontrol et
</details>
<details>
<summary><b>"Listening to" yerine "Playing" yazıyor</b></summary>
`pypresence` güncelle — eski sürümler `activity_type` parametresini desteklemiyor:
 
```bash
pip install -U pypresence
```
 
</details>
<details>
<summary><b>winsdk kurulmuyor, derleme hatası veriyor</b></summary>
`winsdk` yalnızca Python 3.10–3.12 için hazır paket sunuyor. 3.13+ kullanıyorsanız pip kaynaktan derlemeye çalışıyor, bu da Visual Studio C++ araçları gerektiriyor.
 
Çözüm — Python 3.12 ile sanal ortam oluştur:
 
```bash
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
 
</details>
<details>
<summary><b>Kapak resmi bazı şarkılarda çıkmıyor</b></summary>
Yerel dosyalar veya nadir baskılar için Apple Music bazen Windows'a resim vermiyor, iTunes Search da sonuç bulamıyor. Bu durumda resim kasıtlı olarak gösterilmiyor — yanlış bir kapak göstermek tercih edilmiyor.
 
</details>
### Bağımlılıklar
 
| Kütüphane | Sürüm | Amaç |
|---|---|---|
| [pypresence](https://github.com/qwertyquerty/pypresence) | ≥ 4.6.1 | Discord RPC bağlantısı |
| [winsdk](https://github.com/pywinrt/python-winsdk) | ≥ 1.0.0 | Windows medya API bağlamaları |
| [requests](https://docs.python-requests.org/) | ≥ 2.31.0 | Kapak resmi yükleme |
 
---
 
<div align="center">
**Projeyi beğendiysen ⭐ bırakmayı unutma**
 
*Made with ♥ and way too many edge cases*
 
</div>
