# Cities: Skylines II — Türkçe Çeviri / Turkish Localization

[Türkçe](#türkçe) · [English](#english)

Oyunun tamamı için Türkçe yerelleştirme — **24.267 satır, %100 kapsam**, temel oyun + tüm DLC ve yaratıcı paketleri.

**v2.0.0 ile baştan yazıldı:** artık bağımsız bir C# modu. **Başka hiçbir mod gerektirmez.**

| | |
| --- | --- |
| Mod sürümü | 2.0.0 |
| Test edilen oyun sürümü | 1.6.2f1 |
| Bağımlılık | Yok |

---

## Türkçe

### v2.0.0'da ne değişti?

v1, I18N Everywhere modunun okuduğu JSON dosyalarını bir PowerShell betiğiyle yerine kopyalayan geçici bir çözümdü.
**v2.0.0 bunun yerini tamamen alıyor:**

| | v1 (eski) | v2.0.0 |
| --- | --- | --- |
| Biçim | PowerShell betiği + açıkta JSON dosyası | Tek bir DLL, çeviri içine gömülü |
| Gereken ek mod | I18N Everywhere | **Yok** |
| Oyundaki görünümü | İngilizce dilinin üzerine yazardı | Dil listesinde gerçek bir **Türkçe** seçeneği |
| Oyun yaması | 1.6.0f1 (24.194 satır) | **1.6.2f1 (24.267 satır)** |
| Büyük harf hataları | "GRAFıK", "HAKKıNDA" | **GRAFİK**, **HAKKINDA** |

### Özellikler

- **Tamamen bağımsız.** Çevirinin tamamı DLL'in içine gömülüdür. I18N Everywhere dahil hiçbir ek mod gerekmez.
- **Gerçek bir dil seçeneği.** `Seçenekler > Arayüz > Dil` listesine yerleşik diller gibi **Türkçe** eklenir.
  İngilizce metinlerin üzerine yazmaz; istediğiniz an başka bir dile dönebilirsiniz.
- **İlk açılışta otomatik Türkçe.** Sonrasında seçiminize dokunmaz.
- **Çakışmaya dayanıklı.** Başka bir mod `tr-TR` dilini zaten eklediyse hata vermez; anahtarlar birleştirilir, bu modun metinleri öncelik alır.
- **Doğru Türkçe büyük harfler.** Oyun, BÜYÜK HARFLE gösterdiği başlıkları dilden bağımsız kurallarla büyütür
  ("PARADOX HESABı", "GRAFIK"). Mod bu adımı Türkçe etkinken düzeltir: **PARADOX HESABI**, **GRAFİK**, **AYARLARI**.
  Yabancı özel adlar (CITIES: SKYLINES, CHRISTINA, PELICAN BIOFUEL) uluslararası yazımını korur.
- **Dil listesinde Türkçe.** Oyun dil listesini modlar yüklenmeden önce dondurur; mod sayfayı yeniden kurdurur.
- **Çökmeye karşı güvenli kültür ayarı.** `tr-TR` kültürü yalnızca Türkçe etkinken uygulanır, sayı biçimi değişmez tutulur
  (başka modlardaki `float.Parse("1.5")` bozulmaz) ve dil değişince eski kültür geri yüklenir.
- **Tutarlı terminoloji.** İmar, Atık Su, Döner Kavşak, Şebeke, Karma Kullanım, Gelişim Seviyesi…

### Kurulum

**1. Paradox Mods (önerilen, tek tık):** Oyunda `Paradox Mods` ekranını açın, *Turkish Localization (Türkçe Çeviri)* modunu bulun,
**Subscribe / Abone ol**'a basın, etkinleştirin ve oyunu yeniden başlatın.

**2. Elle kurulum:** [Releases](../../releases) sayfasından `TurkishLocalization.dll` dosyasını indirin ve şu klasöre koyun
(klasörler yoksa oluşturun):

```text
%LOCALAPPDATA%Low\Colossal Order\Cities Skylines II\Mods\TurkishLocalization\TurkishLocalization.dll
```

İpucu: Windows Gezgini'nin adres çubuğuna `%LOCALAPPDATA%Low\Colossal Order\Cities Skylines II\Mods` yazıp Enter'a basın.

Oyunu başlatın; dil kendiliğinden Türkçe olur. Olmazsa `Options > Interface > Language > Türkçe`.

> **v1'den geçiyorsanız** eski yamanın klasörünü silin: `...\Cities Skylines II\Mods\TurkishLang`.
> Artık gerekmiyor; durduğu sürece İngilizce dilini de Türkçe gösterir. I18N Everywhere'i yalnızca bu yama için
> kurduysanız onu da kaldırabilirsiniz. Calypso gibi başka bir Türkçe çeviri varsa kaldırmanız önerilir.

### Derleme

[.NET SDK](https://dotnet.microsoft.com/download) 6 veya üzeri yeterlidir. Oyunun derlemelerinin yerini gösterin:

```powershell
dotnet build src -c Release -p:ManagedPath="<oyun klasörü>\Cities2_Data\Managed"
```

Çıktı: `src\bin\Release\TurkishLocalization.dll`

- Resmî modlama araç zinciri kuruluysa (`CSII_MANAGEDPATH` tanımlıysa) ya da oyun varsayılan Steam klasöründeyse `-p:ManagedPath` gerekmez.
- `-p:Deploy=true` eklerseniz DLL doğrudan oyunun `Mods` klasörüne kopyalanır.
- Paradox Mods'a yayımlama adımları: [PUBLISHING.md](PUBLISHING.md)

### Bakımcılar için: oyun yaması gelince

Yeni bir CS2 yaması çıktığında çeviriyi güncellemenin adımları:

1. **Dökümü bırakın.** Oyundan alınan yeni İngilizce parça dosyalarını (`[A]0- en-US.json`, `[A]1- en-US.json`, … kaç dosya olursa olsun)
   `updates/incoming_en/` klasörüne kopyalayın.
2. **Farkı çıkarın.**

   ```powershell
   python tools/check_updates.py
   ```

   Araç parçaları birleştirir, `src/Localization/tr-TR.json` ve `originals/en-US/en-US.json` ile karşılaştırır ve sonucu
   `updates/keys_to_translate.json` dosyasına yazar. Üç liste çıkar: **new** (yeni anahtarlar), **modified** (İngilizcesi
   değişmiş anahtarlar — eski İngilizce ve eski Türkçe yanında verilir) ve **removed** (oyundan kaldırılanlar).
3. **Çevirin.** O dosyadaki her girdinin boş `"tr"` alanını doldurun:

   ```json
   "Assets.NAME[FoodTruck01]": { "en": "Food truck 01", "tr": "Yemek Kamyoneti 01" }
   ```

   `{DEĞİŞKEN}` yer tutucularına, `<etiket>`lere ve `\n` satır sonlarına dokunmayın.
4. **Birleştirin.**

   ```powershell
   python tools/check_updates.py --merge updates/keys_to_translate.json
   ```

   Araç önce denetler: eksik çeviri, bozulmuş yer tutucu/etiket/satır sonu ya da "GRAFıK" türü büyük harf hatası varsa
   **hiçbir şeyi değiştirmeden** durur ve sorunlu anahtarları listeler. Her şey yolundaysa `src/Localization/tr-TR.json`
   güncellenir, kaldırılan anahtarlar düşülür, `originals/en-US/` yeni taban olur ve `updates/incoming_en/` boşaltılır.
5. **Doğrulayın ve derleyin.**

   ```powershell
   python tools/check_updates.py --validate
   dotnet build src -c Release -p:ManagedPath="<oyun klasörü>\Cities2_Data\Managed"
   ```

6. **Sürümü yükseltin ve yayımlayın.** `mod.json`, `src/TurkishLocalization.csproj` ve `Properties/PublishConfiguration.xml`
   içindeki sürümü artırın, `ChangeLog`'u yazın, ardından [PUBLISHING.md](PUBLISHING.md) adımlarını izleyin.

### Katkı

`src/Localization/tr-TR.json` düz bir `anahtar: değer` dosyasıdır. **Yalnızca sağdaki değerleri** düzenleyin;
anahtarlara, `{DEĞİŞKEN}` yer tutucularına ve `<icon:…>` / `<inputAction:…>` etiketlerine dokunmayın.
Yanlış ya da eksik çeviri için [issue açın](../../issues) — ekran görüntüsü ve metnin geçtiği panel çok yardımcı olur.

Not: Metinleri dosyada **normal yazımıyla** tutun ("Paradox Hesabı"). Oyun bunları kendisi büyük harfe çevirir ve bunu
`ToUpperInvariant()` ile yaptığı için `ı` küçük kalır, `i` de `I` olurdu; mod bu adımı çalışma anında düzeltir
(`src/TurkishCasing.cs`). İki istisna dosyada bilerek büyük harfle yazılıdır: ayarlar sekmeleri (`HAKKINDA`, `OYNANIŞ` —
düzeltme devre dışı kalırsa yedek) ve JavaScript'in büyüttüğü hata penceresi düğmeleri (`Common.ERROR_ACTION[...]`).
`python tools/fix_upper_i.py` dosyada "HESABı" türü bozuk sözcük kalıp kalmadığını denetler.

### Depo yapısı

```text
src/                        C# modu
  Mod.cs                    IMod: tr-TR dilini kaydeder
  TurkishLocalization.csproj
  TurkishCasing.cs          Türkçe i/ı büyük harf kuralları
  TurkishCaseMapper.cs      Oyunun büyük harf geri çağrısına takılan sarmalayıcı
  Localization/tr-TR.json   Türkçe çeviri (DLL'e gömülür)
  Localization/protected-words.txt  Korunan özel adlar (üretilir)
originals/en-US/            Çevirinin dayandığı İngilizce taban (parça dosyalar + en-US.json)
updates/incoming_en/        Yeni yama dökümleri buraya
tools/check_updates.py      Güncelleme aracı
tools/fix_upper_i.py        "HESABı" türü bozuk büyük harfli sözcükleri bulur/onarır
tools/build_protected_words.py  Büyük harfte korunacak yabancı özel ad listesini üretir
tools/make_thumbnail.py     Properties/Thumbnail.png üretir
Properties/                 Paradox Mods yayın ayarları ve küçük resim
mod.json                    Mod kimlik bilgileri
PUBLISHING.md               Paradox Mods'a yayımlama kılavuzu
```

---

## English

Complete Turkish localization for Cities: Skylines II — **24,267 strings, 100% coverage**, base game plus every DLC and creator pack.

### What changed in v2.0.0

v1 was a stop-gap: a PowerShell script that copied loose JSON files into place for the I18N Everywhere mod.
**v2.0.0 replaces it entirely** with a standalone C# mod:

| | v1 (legacy) | v2.0.0 |
| --- | --- | --- |
| Form | PowerShell script + loose JSON | One DLL with the translation embedded |
| Required mods | I18N Everywhere | **None** |
| In game | Overwrote the English locale | A native **Türkçe** entry in the language list |
| Game patch | 1.6.0f1 (24,194 strings) | **1.6.2f1 (24,267 strings)** |
| Casing bugs | "GRAFıK", "HAKKıNDA" | **GRAFİK**, **HAKKINDA** |

### Features

- **Fully standalone.** The translation is embedded in the DLL. No I18N Everywhere, no other mod.
- **A real language entry.** Registers the `tr-TR` locale, so **Türkçe** appears under `Options > Interface > Language`
  like any built-in language. English is left untouched and you can switch back at any time.
- **Turkish on first launch**, then your choice is respected.
- **Conflict safe.** If another mod already registered `tr-TR`, nothing throws: entries are merged and this mod's take precedence (logged at info level).
- **Survives locale reloads.** The game drops mod-added locales on a bulk asset reload; the mod registers itself again.
- **Crash-safe culture handling.** The thread culture becomes `tr-TR` only while Turkish is active, keeps invariant number
  formatting (culture-blind `float.Parse("1.5")` calls in other mods keep working) and is restored when you switch language.
- **Correct Turkish capitals.** The game upper-cases headings with culture-invariant rules ("PARADOX HESABı", "GRAFIK").
  While Turkish is active the mod corrects that step: **PARADOX HESABI**, **GRAFİK**. Foreign proper nouns
  (CITIES: SKYLINES, CHRISTINA, PELICAN BIOFUEL) keep their international spelling.
- **Türkçe in the language list.** The game freezes that list before mods load; the mod has the page rebuilt.
- Consistent city-planning terminology.

### Installation

**1. Paradox Mods (recommended, one click):** open `Paradox Mods` in game, find *Turkish Localization (Türkçe Çeviri)*,
press **Subscribe**, enable it and restart the game.

**2. Manual:** download `TurkishLocalization.dll` from [Releases](../../releases) and place it at (create the folders if needed)

```text
%LOCALAPPDATA%Low\Colossal Order\Cities Skylines II\Mods\TurkishLocalization\TurkishLocalization.dll
```

The game switches to Turkish on its own. If it does not: `Options > Interface > Language > Türkçe`.

> **Coming from v1?** Delete `...\Cities Skylines II\Mods\TurkishLang`. It is obsolete and keeps turning the *English*
> locale Turkish for as long as it exists.

### Building

Requires the [.NET SDK](https://dotnet.microsoft.com/download) (6+) and an installed copy of the game.

```powershell
dotnet build src -c Release -p:ManagedPath="<game folder>\Cities2_Data\Managed"
```

`-p:ManagedPath` can be omitted when `CSII_MANAGEDPATH` is set (official modding toolchain) or the game lives in the default Steam library.
Add `-p:Deploy=true` to copy the DLL into the game's `Mods` folder. Publishing to Paradox Mods: see [PUBLISHING.md](PUBLISHING.md).

### Patch update guide for maintainers

When a new CS2 patch drops:

1. **Drop the dump.** Copy the freshly dumped split files (`[A]0- en-US.json`, `[A]1- en-US.json`, … any number of them)
   into `updates/incoming_en/`.
2. **Extract the diff.**

   ```powershell
   python tools/check_updates.py
   ```

   The tool merges the split files, compares them with `src/Localization/tr-TR.json` and `originals/en-US/en-US.json`, and writes
   `updates/keys_to_translate.json` with three lists: **new** keys, **modified** keys (English source changed — the old English
   and the old Turkish are included) and **removed** keys.
3. **Translate.** Fill in the empty `"tr"` field of every entry in that file:

   ```json
   "Assets.NAME[FoodTruck01]": { "en": "Food truck 01", "tr": "Yemek Kamyoneti 01" }
   ```

   Leave `{TOKENS}`, `<tags>` and `\n` line breaks exactly as they are.
4. **Merge.**

   ```powershell
   python tools/check_updates.py --merge updates/keys_to_translate.json
   ```

   The tool validates first: a missing translation, a broken token/tag/line break or a casing error such as "GRAFıK" makes it
   stop **without changing anything** and list the offending keys. Otherwise it updates `src/Localization/tr-TR.json`, drops
   removed keys, rolls `originals/en-US/` forward to the new baseline and empties `updates/incoming_en/`.
   (A flat `{ "key": "Turkish" }` file is accepted as well.)
5. **Validate and build.**

   ```powershell
   python tools/check_updates.py --validate
   dotnet build src -c Release -p:ManagedPath="<game folder>\Cities2_Data\Managed"
   ```

6. **Bump the version and publish.** Raise the version in `mod.json`, `src/TurkishLocalization.csproj` and
   `Properties/PublishConfiguration.xml`, write the `ChangeLog`, then follow [PUBLISHING.md](PUBLISHING.md).

### License and credits

Translation and mod by Kaan Baha Sever. Cities: Skylines II is a trademark of Paradox Interactive / Colossal Order;
the English source strings under `originals/` belong to them and are included only as a translation reference.
