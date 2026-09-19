# Paradox Mods'a Yayımlama Kılavuzu / Publishing Guide

[Türkçe](#türkçe) · [English](#english)

Mod Paradox Mods'ta yayında: <https://mods.paradoxplaza.com/mods/159725/Windows> (`ModId` = **159725**).
Aşağıdaki "ilk yükleme" bölümü, modu sıfırdan başka bir hesapla yayımlamak gerekirse diye duruyor; güncellemeler için
**Sonraki güncellemeler** bölümüne bakın.

> **En önemli adım:** Yükleme bitince araç kimliği yalnızca **ekrana yazar** (`Mod published with Id=123456`),
> dosyaya **geri yazmaz**. O numarayı `PublishConfiguration.xml` içine elle yapıştırıp commit'lemezseniz
> bir sonraki güncellemeyi yayımlayamazsınız.

---

## Türkçe

### Nasıl çalışıyor?

Oyunla birlikte `ModPublisher.exe` adında küçük bir komut satırı aracı gelir. Visual Studio'daki "Publish" düğmesi de
arka planda bunu çalıştırır. Bu depo aracı **doğrudan** çağırır; Unity'yi ya da tam modlama araç zincirini kurmanız **gerekmez**.
Araç şurada durur:

```text
<oyun klasörü>\Cities2_Data\Content\Game\.ModdingToolchain\ModPublisher\ModPublisher.exe
```

Üç komutu vardır:

| Komut | Ne zaman | Ne yükler | `ModId` |
| --- | --- | --- | --- |
| `Publish` | İlk yükleme | DLL + açıklama + küçük resim | **Boş olmalı** |
| `NewVersion` | Çeviri/kod güncellemesi | DLL + açıklama + `ChangeLog` | Dolu olmalı |
| `Update` | Yalnızca sayfa bilgisi değişti | Açıklama, küçük resim, bağlantılar (DLL yüklenmez) | Dolu olmalı |

### Hazırlık (bir kez)

1. **Paradox hesabı.** [paradoxplaza.com](https://www.paradoxplaza.com) üzerinden hesap açın.
2. **Görünen ad belirleyin.** Hesabınızın bir "social profile" görünen adı olmalı; yoksa yükleme
   `No social profile exists for the account` hatasıyla reddedilir. [mods.paradoxplaza.com](https://mods.paradoxplaza.com)
   adresine girip profilinizi bir kez açmanız yeterlidir.
3. **Oyunun içinden giriş yapın.** Oyunu açın, ana menüden Paradox hesabınıza giriş yapın, sonra **oyunu kapatın**.
   ModPublisher şifre sormaz; oyunun kaydettiği oturumu kullanır. Hiç giriş yapmadıysanız şu hatayı alırsınız:
   `Could not auto log in: You were not logged in before`.
4. **.NET 6 çalışma zamanı.** ModPublisher bir .NET 6 uygulamasıdır. `dotnet --list-runtimes` çıktısında
   `Microsoft.NETCore.App 6.x` yoksa [.NET 6 Runtime](https://dotnet.microsoft.com/download/dotnet/6.0) kurun
   (ya da komuttan önce `$env:DOTNET_ROLL_FORWARD = "Major"` yazın).

### Yayımlamadan önce kontrol listesi

- [ ] Mod oyunda denendi: `dotnet build src -c Release -p:Deploy=true`, oyunu aç, `Options > Interface > Language` altında **Türkçe** görünüyor.
- [ ] `python tools/check_updates.py --validate` → `untranslated: 0`, `broken: 0`.
- [ ] Sürüm üç yerde aynı: `mod.json`, `src/TurkishLocalization.csproj` (`<Version>`), `PublishConfiguration.xml` (`<ModVersion>`).
      (Tutmuyorsa yayın hedefi zaten durur.)
- [ ] `Properties/Thumbnail.png` var. Önerilen: kare, en az 512×512, en çok 2 MB. Yeniden üretmek için: `python tools/make_thumbnail.py`.
      **Dikkat:** dosya bulunamazsa ModPublisher hata vermez, sessizce kendi varsayılan resmini yükler — bu yüzden yayın hedefi
      resmi önceden denetler.
- [ ] `<AccessLevel>`: `Public` herkese açık yayımlar. İlk denemeyi gizli yapmak isterseniz `Unlisted` (yalnızca bağlantıyla
      erişilir) yazın, her şey yolundaysa `Public` yapıp `Update` komutunu çalıştırın.
- [ ] Oyun **kapalı**.

### Adım adım: ilk yükleme

Depo kökünde bir PowerShell penceresi açın.

**1. Önce kuru çalıştırma** — hiçbir şey gönderilmez, yalnızca ne yapılacağı gösterilir:

```powershell
dotnet build src -c Release -p:ManagedPath="<oyun klasörü>\Cities2_Data\Managed" -p:PdxCommand=Publish -p:PdxDryRun=true
```

Çıktıda `Paradox Mods: Publish  v2.0.0  ModId=''` ve çalıştırılacak tam komut görünmeli.

**2. Gerçek yükleme** — aynı komut, `-p:PdxDryRun=true` olmadan:

```powershell
dotnet build src -c Release -p:ManagedPath="<oyun klasörü>\Cities2_Data\Managed" -p:PdxCommand=Publish
```

Bu komut modu derler, `src\bin\PdxContent\` altına yalnızca `TurkishLocalization.dll` içeren temiz bir klasör hazırlar
(içerik klasöründeki **her şey** yüklendiği için) ve ModPublisher'ı depo kökünden çalıştırır.

**3. Kimliği kaydedin.** Çıktının sonunda şunu arayın:

```text
Mod published with Id=123456
```

O numarayı `Properties/PublishConfiguration.xml` içine yazın ve commit'leyin:

```xml
<ModId Value="123456" />
```

```powershell
git add Properties/PublishConfiguration.xml
git commit -m "Record Paradox Mods id"
git push
```

Çıktıyı kaçırdıysanız: [mods.paradoxplaza.com/uploaded](https://mods.paradoxplaza.com/uploaded) sayfasında modunuzu açın;
adres `https://mods.paradoxplaza.com/mods/123456/Windows` biçimindedir ve ortadaki sayı `ModId`'dir.

**4. Sayfayı kontrol edin.** Küçük resim, açıklama ve etiketin (`Code Mod`) doğru göründüğüne bakın; oyunda abone olup deneyin.

### Sonraki güncellemeler

Oyun yaması gelince [DEVELOPMENT.md](DEVELOPMENT.md) içindeki adımlarla çeviriyi güncelleyin, sonra:

1. Sürümü üç dosyada artırın (ör. `2.0.1`). Paradox Mods aynı sürüm numarasını ikinci kez kabul etmez.
2. `<ChangeLog>` içeriğini yeni sürüme göre yazın (`NewVersion` için zorunludur). Metni **satır başından** başlatın;
   girintili satırlar sitede kod bloğu gibi görünür.
3. Yayımlayın:

```powershell
dotnet build src -c Release -p:ManagedPath="<oyun klasörü>\Cities2_Data\Managed" -p:PdxCommand=NewVersion
```

Yalnızca açıklamayı, küçük resmi ya da bağlantıları değiştirdiyseniz `-p:PdxCommand=Update` kullanın; DLL yüklenmez.

### Sık karşılaşılan hatalar

| Hata | Çözüm |
| --- | --- |
| `Could not auto log in: You were not logged in before` | Oyunu açıp Paradox hesabınıza giriş yapın, oyunu kapatıp tekrar deneyin. |
| `No social profile exists for the account` | mods.paradoxplaza.com'da profilinizi açıp görünen ad belirleyin. |
| `You must install .NET to run this application` / `Microsoft.NETCore.App 6.0` bulunamadı | .NET 6 Runtime kurun ya da `$env:DOTNET_ROLL_FORWARD = "Major"` yazıp yeniden deneyin. |
| `ModId is already set … Use -p:PdxCommand=NewVersion` | Mod daha önce yayımlanmış; `Publish` yerine `NewVersion` kullanın. |
| `ModId is empty` | İlk yüklemede verilen numarayı `PublishConfiguration.xml`'e yazmayı unutmuşsunuz. |
| `Version mismatch` | `<ModVersion>` ile `csproj` içindeki `<Version>` aynı olmalı. |
| `ModPublisher.exe not found` | Komuta `-p:ModPublisherExe="<tam yol>\ModPublisher.exe"` ekleyin. |
| `Content folder is empty` | Derleme başarısız olmuş; önce `-p:PdxCommand` olmadan derleyip hatayı görün. |
| Sitede yanlış/varsayılan küçük resim | Resim yolu depo köküne göredir (`Properties/Thumbnail.png`). Düzeltip `Update` çalıştırın. |
| Sürüm reddedildi | Yayımlanmış sürümle aynı numara; sürümü artırın. |

### Bilinmesi gerekenler

- **`GameVersion` her zaman joker içermeli: `1.6.*`.** Oyun içi mod tarayıcısı bu değerden bir regex kurup oyunun **tam** sürüm
  dizgesiyle (`1.6.2f1 (767.21d1) [6300.26419]`) eşleştirir. `1.6.2f1` gibi tam bir değer sondaki ek yüzünden asla eşleşmez ve mod
  "oyunun eski bir sürümü için yapılmış" uyarısıyla gösterilir (v2.0.0'da yaşandı, v2.0.1'de düzeltildi). `1.6.*` ve `1.*` eşleşir;
  `1.6.2.*` ve `1.6.2f1.*` eşleşmez. Yayın hedefi jokersiz değeri reddeder. Oyun 1.7'ye geçince alanı `1.7.*` yapıp `Update` çalıştırın.
- **Etiket:** ModPublisher her kod moduna `Code Mod` etiketini kendisi ekler. Diğer etiketleri yüklemeden sonra sitede düzenleyebilirsiniz.
- **Ekran görüntüleri:** Oyun içi görüntüleri `Properties/` altına koyup her biri için
  `<Screenshot Value="Properties/ekran1.jpg" />` satırı ekleyin (en çok 10 adet, her biri en çok 2 MB), sonra `Update` çalıştırın.
  Satırlar `<Publish>` kökünün **doğrudan** altında olmalı: `<Screenshots>` gibi bir sarmalayıcı ModPublisher tarafından yok sayılır.
  Dosyadaki liste sitedekinin **tamamının** yerine geçer.
- **Elle çalıştırmak isterseniz** (derleme hedefi olmadan), depo kökünden:

  ```powershell
  & "<oyun>\Cities2_Data\Content\Game\.ModdingToolchain\ModPublisher\ModPublisher.exe" Publish "Properties\PublishConfiguration.xml" -c "src\bin\PdxContent" -v
  ```

- **Visual Studio / resmî araç zinciri:** Oyunun `Options > Modding` ekranından kurulan tam araç zinciri (Unity dahil) ve
  şablondaki `PublishNewMod` / `PublishNewVersion` / `UpdatePublishedConfiguration` profilleri de aynı ModPublisher'ı çalıştırır.
  Bu mod ECS/Burst kodu içermediği için o kuruluma ihtiyaç duymaz; bu depo o profilleri içermez.

---

## English

This is the **first** upload of the mod to Paradox Mods, so `<ModId Value="" />` in `Properties/PublishConfiguration.xml`
is intentionally **empty**: Paradox Mods assigns a fresh id on first publication.

> **The step people forget:** the tool only **prints** the new id (`Mod published with Id=123456`); it does **not** write it
> back into the file. Paste it into `PublishConfiguration.xml` and commit it, or you will not be able to publish the next update.

### How it works

The game ships a small command-line tool, `ModPublisher.exe`; the "Publish" button of the official Visual Studio template runs the
very same tool. This repository calls it **directly**, so you do **not** need Unity or the full modding toolchain. It lives at

```text
<game folder>\Cities2_Data\Content\Game\.ModdingToolchain\ModPublisher\ModPublisher.exe
```

| Command | When | Uploads | `ModId` |
| --- | --- | --- | --- |
| `Publish` | First upload | DLL + description + thumbnail | **must be empty** |
| `NewVersion` | Translation / code update | DLL + description + `ChangeLog` | required |
| `Update` | Only the page changed | Description, thumbnail, links (no DLL) | required |

### One-time preparation

1. Create a Paradox account.
2. Give it a **social profile display name** (open your profile on [mods.paradoxplaza.com](https://mods.paradoxplaza.com) once);
   otherwise the upload fails with `No social profile exists for the account`.
3. **Log in inside the game**, then **close the game**. ModPublisher never asks for a password; it reuses the session the game cached.
   Without it: `Could not auto log in: You were not logged in before`.
4. ModPublisher is a **.NET 6** app. If `dotnet --list-runtimes` shows no `Microsoft.NETCore.App 6.x`, install the
   [.NET 6 Runtime](https://dotnet.microsoft.com/download/dotnet/6.0) or set `$env:DOTNET_ROLL_FORWARD = "Major"`.

### Pre-flight checklist

- [ ] Tested in game: `dotnet build src -c Release -p:Deploy=true`, start the game, **Türkçe** is listed under `Options > Interface > Language`.
- [ ] `python tools/check_updates.py --validate` reports `untranslated: 0` and `broken: 0`.
- [ ] Same version in `mod.json`, `src/TurkishLocalization.csproj` and `PublishConfiguration.xml` (the publish target enforces the last two).
- [ ] `Properties/Thumbnail.png` exists (square, 512×512 or larger, 2 MB max; regenerate with `python tools/make_thumbnail.py`).
      ModPublisher does **not** fail on a missing thumbnail, it silently uploads its own default image — the publish target checks for you.
- [ ] `<AccessLevel>` is what you want: `Public`, or `Unlisted` for a trial run (switch to `Public` later and run `Update`).
- [ ] The game is **closed**.

### First upload, step by step

From the repository root:

```powershell
# 1. dry run: prints the exact command, sends nothing
dotnet build src -c Release -p:ManagedPath="<game folder>\Cities2_Data\Managed" -p:PdxCommand=Publish -p:PdxDryRun=true

# 2. the real thing
dotnet build src -c Release -p:ManagedPath="<game folder>\Cities2_Data\Managed" -p:PdxCommand=Publish
```

The target builds the mod, stages a clean `src\bin\PdxContent\` folder holding only `TurkishLocalization.dll`
(ModPublisher uploads **everything** in the content folder) and runs ModPublisher from the repository root, so the relative
thumbnail path in the configuration resolves correctly.

**3. Save the id.** Find `Mod published with Id=123456` at the end of the output, then:

```xml
<ModId Value="123456" />
```

```powershell
git add Properties/PublishConfiguration.xml
git commit -m "Record Paradox Mods id"
git push
```

Missed it? Open the mod from [mods.paradoxplaza.com/uploaded](https://mods.paradoxplaza.com/uploaded); the URL is
`https://mods.paradoxplaza.com/mods/123456/Windows` and the number is the `ModId`.

### Later updates

1. Bump the version in all three files — Paradox Mods rejects a version number it has already seen.
2. Rewrite `<ChangeLog>` (mandatory for `NewVersion`). Start the text at **column zero**; indented lines render as a code block.
3. `dotnet build src -c Release -p:ManagedPath="…" -p:PdxCommand=NewVersion`

Use `-p:PdxCommand=Update` when only the description, thumbnail or links changed.

### Troubleshooting

| Error | Fix |
| --- | --- |
| `Could not auto log in: You were not logged in before` | Start the game, log in to your Paradox account, close the game, retry. |
| `No social profile exists for the account` | Set a display name on mods.paradoxplaza.com. |
| .NET 6 runtime missing | Install the .NET 6 Runtime or set `$env:DOTNET_ROLL_FORWARD = "Major"`. |
| `ModId is already set …` | Already published: use `NewVersion` instead of `Publish`. |
| `ModId is empty` | You forgot to paste the id from the first upload. |
| `Version mismatch` | `<ModVersion>` and the csproj `<Version>` must match. |
| `ModPublisher.exe not found` | Add `-p:ModPublisherExe="<full path>\ModPublisher.exe"`. |
| Wrong / default thumbnail on the site | The path is relative to the repository root. Fix it and run `Update`. |

### Good to know

- **`GameVersion` must always carry a wildcard: `1.6.*`.** The in-game mod browser turns the value into an anchored regex and tests it
  against the game's **full** version string (`1.6.2f1 (767.21d1) [6300.26419]`). An exact value such as `1.6.2f1` can never match
  because of that suffix, and the mod is shown as "made for an older version of the game" (happened in v2.0.0, fixed in v2.0.1).
  `1.6.*` and `1.*` match; `1.6.2.*` and `1.6.2f1.*` do not. The publish target rejects a value without a wildcard. When the game
  moves to 1.7, change it to `1.7.*` and run `Update`.
- ModPublisher tags every code mod `Code Mod` by itself; other tags can be edited on the website afterwards.
- Screenshots: add `<Screenshot Value="Properties/shot1.jpg" />` lines (10 max, 2 MB each) and run `Update`.
- The official IDE route (full toolchain from `Options > Modding`, Visual Studio publish profiles `PublishNewMod`,
  `PublishNewVersion`, `UpdatePublishedConfiguration`) drives the same ModPublisher. This mod has no ECS/Burst code, does not
  need that setup, and this repository does not ship those profiles.
