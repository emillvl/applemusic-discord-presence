<div align="center">
<img src="https://upload.wikimedia.org/wikipedia/commons/5/5f/Apple_Music_icon.svg" width="80" alt="Apple Music" />

# Apple Music Rich Presence
 
[![Python](https://img.shields.io/badge/Python-3.10--3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=flat-square&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Discord](https://img.shields.io/badge/Discord-Rich%20Presence-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](../../LICENSE)
 
**🇬🇧 [English](#-english) · 🇹🇷 [Türkçe](#-türkçe)**
 
</div>
---
 
## 🇬🇧 English
 
### What does it do?
 
Shows the track currently playing in the Windows Apple Music app on your Discord profile, including the song title, artist, album art when available, and playback progress. It uses Windows media-session data for playback metadata and Discord Rich Presence for display.
 
```
🎵  Listening to Apple Music
    In Your Eyes
    Inna
    ━━━━━━━━━━━━━━━━━━━━  2:34 / 5:27
```
 
### Features
 
- Shows a "Listening to Apple Music" activity on Discord.
- Uses Apple Music's artwork when available, with iTunes Search as a fallback.
- Sets a playback progress indicator when the track changes.
- Includes the artist in the activity details.
- Can show a button linking to your Apple Music profile.
- Includes an optional helper for starting in the background when you sign in to Windows.

### Requirements
 
| | |
|---|---|
| OS | Windows 10 or 11 |
| Python | 3.10, 3.11 or 3.12 |
| Apple Music | Microsoft Store version |
| Discord | Desktop app (not browser) |
 
> **Python version matters.** `winsdk` only ships pre-built wheels for 3.10-3.12. If you're on 3.13+, create a separate environment with `py -3.12 -m venv venv`.
 
### Installation
 
**1. Clone the repo**
 
```bash
git clone https://github.com/emillvl/applemusic-discord-presence.git
cd applemusic-discord-presence
cd "AppleMusic Discord Presence"
```
 
**2. Install dependencies**
 
```bash
python -m pip install -r "Description/requirements.txt"
```
 
**3. Get a Discord Application ID**
 
Discord Rich Presence requires an Application ID. You only need to create it once for this setup.
 
1. Go to [discord.com/developers/applications](https://discord.com/developers/applications) → **New Application**
2. Name it anything (e.g. `"Apple Music"`): this name won't appear on your profile
3. Copy the **Application ID** from the General Information page

**4. Configure your Application ID**
 
```bash
python main.py
```
 
Open `config.json` in the `AppleMusic Discord Presence` folder and replace `discord_client_id` with your own Application ID, keeping the other fields. If the file is missing, the command above creates it and exits; edit it before running again.

Example field (keep the rest of your JSON file):
 
```json
{
  "discord_client_id": "PASTE_HERE"
}
```
 
**5. Run**
 
```bash
python main.py
```
 
Play something in Apple Music. Discord updates within a few seconds.
 
### Auto-start on Windows
 
1. Open `start_hidden.vbs` in a text editor. Set both `pythonwPath` and `scriptPath` to quoted absolute paths: the first to `pythonw.exe`, the second to `main.py`. If you use a virtual environment, choose its `Scripts\pythonw.exe`.
2. Press `Win + R`, type `shell:startup`, and press Enter to open your Startup folder.
3. Right-click `start_hidden.vbs` → **Create shortcut** → move that shortcut into the Startup folder

The shortcut starts the script at login without a console window. Test `python main.py` in a terminal first so you can see setup errors.
 
To disable future automatic starts, delete the shortcut from the Startup folder. This does not stop a copy that is already running.
 
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
| `discord_client_id` | ID from Discord Developer Portal | - |
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
 
> **Note:** Discord only shows Rich Presence buttons to *other* people viewing your profile: you won't see your own button. This is a Discord platform limitation, not a bug.
 
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
 
1. **Apple Music's own image**: the exact bytes Apple Music hands to Windows (same as the volume flyout). Uploaded to `catbox.moe` to get a URL Discord can use.
2. If the upload fails or no thumbnail is available, the script searches iTunes. It scores the title, artist, and album, then accepts a cover only if the match meets the individual and combined thresholds. Otherwise, it leaves the artwork blank.

Artwork results, including failed lookups, are cached by title, artist, and album for the life of the process. Polling does not repeat those lookups. Restart the script to retry a failed artwork lookup.

### Privacy and playback limits

The script sends track details to Discord. It uploads artwork supplied by Windows to `catbox.moe`; fallback searches send the artist and track title to Apple's iTunes Search API. These requests happen automatically when artwork is needed, including for local tracks that expose a thumbnail. There is no configuration switch to disable artwork uploads.

Playback timestamps update when the detected track changes, not after every seek within the same track. Pausing clears the activity on the next poll.
 
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

Update `pypresence`: older versions don't support `activity_type`:
 
```bash
pip install -U pypresence
```

</details>

<details>
<summary><b>winsdk fails to install (build error)</b></summary>

`winsdk` only has pre-built wheels for Python 3.10-3.12. On 3.13+, pip tries to compile from source which requires Visual Studio's C++ build tools.
 
From the `AppleMusic Discord Presence` folder, use a 3.12 virtual environment in Command Prompt:
 
```bash
py -3.12 -m venv venv
venv\Scripts\activate
python -m pip install -r "Description/requirements.txt"
python main.py
```

</details>

<details>
<summary><b>Artwork missing for some tracks</b></summary>

For local files or rare releases, Apple Music may provide no thumbnail and iTunes Search may find no match above the confidence threshold. The script then leaves the artwork blank.

</details>

### Dependencies
 
| Package | Version | Purpose |
|---|---|---|
| [pypresence](https://github.com/qwertyquerty/pypresence) | ≥ 4.6.1 | Discord RPC connection |
| [winsdk](https://github.com/pywinrt/python-winsdk) | ≥ 1.0.0 | Windows media API bindings |
| [requests](https://docs.python-requests.org/) | ≥ 2.31.0 | Album art upload |
 
---
 
## 🇹🇷 Türkçe
 
### Ne yapar?
 
Windows'taki Apple Music uygulamasında çalan parçayı Discord profilinizde gösterir. Şarkı adı, sanatçı, mevcutsa albüm kapağı ve oynatma ilerlemesi Discord Rich Presence üzerinden güncellenir.
 
```
🎵  Listening to Apple Music
    In Your Eyes
    Inna
    ━━━━━━━━━━━━━━━━━━━━  2:34 / 5:27
```
 
### Özellikler
 
- Discord'da "Listening to Apple Music" etkinliğini gösterir.
- Varsa Apple Music'in kapak görselini, yoksa iTunes Search sonuçlarını kullanır.
- Parça değiştiğinde oynatma ilerlemesini ayarlar.
- Etkinlik ayrıntılarına sanatçı adını ekler.
- Apple Music profiline giden bir buton gösterebilir.
- Windows oturumu açıldığında arka planda çalışması için isteğe bağlı bir yardımcı dosya içerir.

### Gereksinimler
 
| | |
|---|---|
| İşletim Sistemi | Windows 10 veya 11 |
| Python | 3.10, 3.11 veya 3.12 |
| Apple Music | Microsoft Store versiyonu |
| Discord | Masaüstü uygulaması (tarayıcı değil) |
 
> **Python sürümü önemli.** `winsdk` yalnızca 3.10-3.12 için derlenmiş paket sunuyor. 3.13+ kullanıyorsanız `py -3.12 -m venv venv` ile ayrı bir ortam oluşturun.
 
### Kurulum
 
**1. Repoyu klonla**
 
```bash
git clone https://github.com/emillvl/applemusic-discord-presence.git
cd applemusic-discord-presence
cd "AppleMusic Discord Presence"
```
 
**2. Bağımlılıkları kur**
 
```bash
python -m pip install -r "Description/requirements.txt"
```
 
**3. Discord Application ID al**
 
Discord Rich Presence için bir Application ID gerekir. Bu kurulum için bir kez oluşturmanız yeterlidir.
 
1. [discord.com/developers/applications](https://discord.com/developers/applications) → **New Application**
2. İsim ver (örn. `"Apple Music"`): bu isim profilinde görünmez
3. **General Information** sayfasından **Application ID**'yi kopyala

**4. Application ID değerini ayarla**
 
```bash
python main.py
```
 
`AppleMusic Discord Presence` klasöründeki `config.json` dosyasını aç ve diğer alanları koruyarak `discord_client_id` değerini kendi Application ID değerinle değiştir. Dosya yoksa yukarıdaki komut dosyayı oluşturur ve kapanır; tekrar çalıştırmadan önce düzenle.

Örnek alan (JSON dosyandaki diğer alanları koru):
 
```json
{
  "discord_client_id": "BURAYA_YAPISTIR"
}
```
 
**5. Çalıştır**
 
```bash
python main.py
```
 
Apple Music'te bir şey çal. Discord birkaç saniye içinde güncellenir.
 
### Otomatik başlatma
 
Her açılışta manuel çalıştırmamak için:
 
1. `start_hidden.vbs` dosyasını bir metin editörüyle aç. `pythonwPath` ve `scriptPath` alanlarına çift tırnak içinde tam dosya yollarını yaz: ilki `pythonw.exe`, ikincisi `main.py` için. Sanal ortam kullanıyorsan o ortamın `Scripts\pythonw.exe` dosyasını seç.
2. `Win + R` ile Çalıştır penceresini aç, `shell:startup` yaz ve Enter'a bas.
3. `start_hidden.vbs` dosyasına sağ tık → **Kısayol oluştur** → kısayolu o klasöre taşı

Kısayol, oturum açıldığında scripti konsol penceresi olmadan başlatır. Kurulum hatalarını görebilmek için önce terminalde `python main.py` komutuyla dene.
 
Otomatik başlatmayı kapatmak için Başlangıç klasöründeki kısayolu sil. Bu işlem, zaten çalışan bir kopyayı durdurmaz.
 
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
| `discord_client_id` | Discord Developer Portal'dan alınan ID | - |
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
 
> **Not:** Discord, Rich Presence butonlarını kendi profilinde göstermez: başkaları görür. Bu Discord'un kısıtlaması, hata değil.
 
### Nasıl çalışır?
 
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
 
1. **Apple Music'in verdiği resim**: Apple Music'in Windows'a ilettiği tam resim (ses seviyesi tuşunda görünenle aynı). `catbox.moe`'ya yüklenerek Discord'un okuyabileceği bir URL'e dönüştürülüyor.
2. Küçük resim yoksa veya yüklenemezse script iTunes'ta arama yapar. Parça adı, sanatçı ve albüm için ayrı puanlar hesaplar. Kapak, yalnızca bu puanlar ve toplam puan gerekli eşikleri geçerse kullanılır; aksi halde kapak alanı boş kalır.

Kapak arama sonuçları, başarısız aramalar dahil, program açık kaldığı sürece parça adı, sanatçı ve albüme göre önbellekte tutulur. Her kontrolde yeniden istek gönderilmez. Başarısız bir aramayı tekrarlamak için scripti yeniden başlat.

### Gizlilik ve oynatma sınırları

Script, parça bilgilerini Discord'a gönderir. Windows'un sağladığı kapak görsellerini `catbox.moe`'ya yükler; yedek arama için sanatçı ve parça adını Apple'ın iTunes Search API'sine gönderir. Kapak gerektiğinde bu istekler otomatik yapılır. Bu durum, küçük resim sağlayan yerel parçalar için de geçerlidir. Yapılandırmada kapak yüklemelerini kapatan bir seçenek yoktur.

Oynatma zamanları, aynı parça içinde her ileri veya geri sarma işleminde değil, algılanan parça değiştiğinde güncellenir. Oynatmayı duraklatınca etkinlik bir sonraki kontrolde temizlenir.
 
### Sorun giderme
 
<details>
<summary><b>Hiçbir şey görünmüyor</b></summary>

- Discord masaüstü uygulaması açık olmalı (tarayıcı değil)
- Apple Music çalıyor olmalı (duraklatılmış değil)
- `config.json` içinde `discord_client_id` doğru yapıştırılmış olmalı
- `app_id_match` değerinin `"applemusic"` (küçük harf) olduğunu kontrol et

</details>

<details>
<summary><b>"Listening to" yerine "Playing" yazıyor</b></summary>

`pypresence` güncelle: eski sürümler `activity_type` parametresini desteklemiyor:
 
```bash
pip install -U pypresence
```

</details>

<details>
<summary><b>winsdk kurulmuyor, derleme hatası veriyor</b></summary>

`winsdk` yalnızca Python 3.10-3.12 için hazır paket sunuyor. 3.13+ kullanıyorsanız pip kaynaktan derlemeye çalışıyor, bu da Visual Studio C++ araçları gerektiriyor.
 
`AppleMusic Discord Presence` klasöründe, Komut İstemi (CMD) ile Python 3.12 sanal ortamı oluştur:
 
```bash
py -3.12 -m venv venv
venv\Scripts\activate
python -m pip install -r "Description/requirements.txt"
python main.py
```

</details>

<details>
<summary><b>Kapak resmi bazı şarkılarda çıkmıyor</b></summary>

Yerel dosyalar veya nadir baskılar için Apple Music küçük resim sağlamayabilir. iTunes Search de güven eşiğini geçen bir eşleşme bulamazsa kapak alanı boş kalır.

</details>

### Bağımlılıklar
 
| Kütüphane | Sürüm | Amaç |
|---|---|---|
| [pypresence](https://github.com/qwertyquerty/pypresence) | ≥ 4.6.1 | Discord RPC bağlantısı |
| [winsdk](https://github.com/pywinrt/python-winsdk) | ≥ 1.0.0 | Windows medya API bağlamaları |
| [requests](https://docs.python-requests.org/) | ≥ 2.31.0 | Kapak resmi yükleme |
 
---
 
<div align="center">
*Made with ♥ and way too many edge cases*
 
</div>
