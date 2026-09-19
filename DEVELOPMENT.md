# Geliştirici Rehberi

Modu derlemek, oyun yaması gelince çeviriyi güncellemek ve yayımlamak için gerekenler.
Paradox Mods adımları ayrı dosyada: [PUBLISHING.md](PUBLISHING.md).

## Derleme

[.NET SDK](https://dotnet.microsoft.com/download) 6 veya üzeri yeterlidir. Oyunun derlemelerinin yerini gösterin:

```powershell
dotnet build src -c Release -p:ManagedPath="<oyun klasörü>\Cities2_Data\Managed"
```

Çıktı: `src\bin\Release\TurkishLocalization.dll`

- Oyun varsayılan Steam/Xbox klasöründeyse ya da `CSII_MANAGEDPATH` tanımlıysa `-p:ManagedPath` gerekmez.
- `-p:Deploy=true` eklerseniz DLL doğrudan oyunun `Mods\TurkishLocalization` klasörüne kopyalanır.

## Oyun yaması gelince

1. **Dökümü bırakın.** Yeni İngilizce parça dosyalarını (`[A]0- en-US.json`, `[A]1- en-US.json`, … kaç dosya olursa olsun)
   `updates/incoming_en/` klasörüne kopyalayın.
2. **Farkı çıkarın.**

   ```powershell
   python tools/check_updates.py
   ```

   Sonuç `updates/keys_to_translate.json` dosyasına yazılır: **new** (yeni), **modified** (İngilizcesi değişmiş; eski
   İngilizce ve eski Türkçe yanında verilir) ve **removed** (oyundan kaldırılmış) anahtarlar.
3. **Çevirin.** Her girdinin boş `"tr"` alanını doldurun:

   ```json
   "Assets.NAME[FoodTruck01]": { "en": "Food truck 01", "tr": "Yemek Kamyoneti 01" }
   ```

4. **Birleştirin.**

   ```powershell
   python tools/check_updates.py --merge updates/keys_to_translate.json
   ```

   Eksik çeviri, bozulmuş `{DEĞİŞKEN}` / `<etiket>` / satır sonu ya da "HESABı" türü büyük harf hatası varsa araç
   **hiçbir şeyi değiştirmeden** durur. Sorun yoksa `src/Localization/tr-TR.json` güncellenir, kaldırılan anahtarlar düşülür,
   `originals/en-US/` yeni taban olur ve korunan özel ad listesi yenilenir.
5. **Doğrulayın, derleyin, oyunda deneyin.**

   ```powershell
   python tools/check_updates.py --validate
   dotnet build src -c Release -p:ManagedPath="<oyun klasörü>\Cities2_Data\Managed" -p:Deploy=true
   ```

6. **Yayımlayın.** Sürümü `mod.json`, `src/TurkishLocalization.csproj` ve `Properties/PublishConfiguration.xml` içinde artırın,
   `GameVersion` ile `ChangeLog`'u güncelleyin ve [PUBLISHING.md](PUBLISHING.md) içindeki `NewVersion` adımını izleyin.

## Çeviri kuralları

- `src/Localization/tr-TR.json` düz bir `anahtar: değer` dosyasıdır. **Yalnızca değerleri** düzenleyin; anahtarlara,
  `{DEĞİŞKEN}` yer tutucularına ve `<icon:…>` / `<inputAction:…>` etiketlerine dokunmayın.
- Metinleri **normal yazımıyla** tutun ("Paradox Hesabı"). Oyun başlıkları kendisi büyük harfe çevirir ve bunu dilden bağımsız
  kurallarla yaptığı için `ı` küçük kalır, `i` de `I` olurdu; mod bu adımı çalışma anında düzeltir (`src/TurkishCasing.cs`).
- İki istisna dosyada bilerek büyük harfle yazılıdır: ayarlar sekmeleri (`HAKKINDA`, `OYNANIŞ`) ve JavaScript'in büyüttüğü
  hata penceresi düğmeleri (`Common.ERROR_ACTION[...]`).

## Mod nasıl çalışır

- `Mod.cs` gerçek bir `tr-TR` dili kaydeder; oyun dil listesini modlardan önce dondurduğu için Arayüz ayar sayfasını yeniden
  kurdurur, oyun dil listesini sıfırladığında kendini tekrar kaydeder.
- `TurkishCaseMapper.cs` oyunun büyük harf geri çağrısının önüne geçer; `TurkishCasing.cs` Türkçe `i/İ`, `ı/I` kurallarını
  uygular. Yabancı özel adlar (`Localization/protected-words.txt`) uluslararası yazımını korur: CITIES: SKYLINES, CHRISTINA.
- Bu iki kanca da korumalıdır: bir oyun güncellemesi bozarsa mod günlüğe uyarı yazar, çeviri yine yüklenir.
  Günlük: `%LOCALAPPDATA%Low\Colossal Order\Cities Skylines II\Logs\TurkishLocalization.log`

## Depo yapısı

```text
src/                              C# modu
  Mod.cs                          IMod: tr-TR dilini kaydeder
  TurkishCasing.cs                Türkçe i/ı büyük harf kuralları
  TurkishCaseMapper.cs            Oyunun büyük harf geri çağrısına takılan sarmalayıcı
  Localization/tr-TR.json         Türkçe çeviri (DLL'e gömülür)
  Localization/protected-words.txt  Korunan özel adlar (üretilir)
originals/en-US/                  Çevirinin dayandığı İngilizce taban (parça dosyalar + en-US.json)
updates/incoming_en/              Yeni yama dökümleri buraya
tools/check_updates.py            Fark çıkarma, doğrulama, birleştirme
tools/fix_upper_i.py              "HESABı" türü bozuk büyük harfli sözcükleri bulur/onarır
tools/build_protected_words.py    Korunan özel ad listesini üretir
tools/make_thumbnail.py           Properties/Thumbnail.png üretir
Properties/                       Paradox Mods yayın ayarları ve küçük resim
mod.json                          Mod kimlik bilgileri
```
