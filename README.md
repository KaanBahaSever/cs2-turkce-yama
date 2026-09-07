# Cities: Skylines II — Türkçe Yama

Oyunun tamamı için Türkçe yerelleştirme. **24.194 satır** çevrilmiştir: arayüz, ekonomi ve istatistik panelleri, öğreticiler, sözlük, politikalar, Chirper gönderileri, tüm yapı adları ve açıklamaları.

- **Oyun sürümü:** 1.6.0f1
- **Kapsam:** temel oyun + tüm DLC'ler ve yaratıcı paketleri
- **Gereksinim:** [I18N Everywhere](https://mods.paradoxplaza.com/mods/75426/Windows) modu

---

## Kurulum

PowerShell'i açıp şu satırı yapıştırın:

```powershell
irm https://raw.githubusercontent.com/KULLANICI/DEPO/main/install.ps1 | iex
```

Betik oyun klasörünü bulur, çakışan eski çevirileri yedekleyip kaldırır ve yamayı yerine koyar.

<details>
<summary>Elle kurmak isterseniz</summary>

`en-US.json` dosyasını indirip şu klasöre koyun:

```
%LOCALAPPDATA%Low\Colossal Order\Cities Skylines II\Mods\TurkishLang\lang\en-US.json
```

Klasörler yoksa oluşturun. Adres çubuğuna `%LOCALAPPDATA%Low\Colossal Order\Cities Skylines II` yazarak da gidebilirsiniz.
</details>

Kurduktan sonra:

1. Oyunu başlatın (açıksa yeniden başlatın).
2. I18N Everywhere modunun etkin olduğundan emin olun.
3. **Options / Seçenekler** ekranına girip çıkın — çeviri o anda devreye girer.

## Önemli

> **Daha önce başka bir Türkçe çeviri kurduysanız (örn. Calypso) tamamen kaldırın.**
> İki çeviri aynı anda yüklüyken metinler karışır. Kurulum betiği bunları otomatik bulup
> `Cities Skylines II\TurkishLang-Yedek\` altına taşır; isterseniz oradan geri alabilirsiniz.

Dosyanın adı neden `en-US.json`? Oyunda Türkçe dil seçeneği yok. I18N Everywhere, İngilizce metinlerin
üzerine yazarak çalışır — bu yüzden dosya İngilizce yerel adıyla durur, oyun dili İngilizce kalmalıdır.

## Kaldırma

```powershell
irm https://raw.githubusercontent.com/KULLANICI/DEPO/main/uninstall.ps1 | iex
```

Ya da `Mods\TurkishLang` klasörünü silin.

## Hata bildirimi

Yanlış veya eksik bir çeviri görürseniz [issue açın](../../issues). Şunları eklerseniz çok hızlı düzelir:
ekran görüntüsü ve metnin geçtiği yer (hangi panel/menü).

## Katkı

`en-US.json` düz bir `anahtar: değer` JSON dosyasıdır. **Yalnızca sağdaki değerleri** düzenleyin;
anahtarlara, `{DEĞİŞKEN}` yer tutucularına ve `<icon:...>` / `<inputAction:...>` etiketlerine dokunmayın.

## Terimler

| İngilizce | Türkçe |
|---|---|
| Zoning | İmar |
| Low / Medium / High Density | Düşük / Orta / Yüksek Yoğunluklu |
| Mixed-Use | Karma Kullanım |
| Sewage | Atık Su |
| Landfill | Katı Atık Depolama Sahası |
| Grid (elektrik/su) | Şebeke |
| Roundabout | Döner Kavşak |
| Deathcare | Defin ve Cenaze Hizmetleri |
| Commuter | Banliyö Yolcusu |
| Upkeep | Bakım Gideri |
| Milestone | Gelişim Seviyesi |
| Signature Building | İmza Yapı |
