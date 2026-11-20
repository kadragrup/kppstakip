# İlan Takip

KPSS P94 (lise) + İHA / ticari pilot ilanlarını belirli aralıklarla tarar,
yeni ve uygun ilan bulursa e-postana gönderir. GitHub Actions üzerinde ücretsiz çalışır.

## Kurulum

1. GitHub'da yeni bir **özel (private)** repo aç, bu klasörün içeriğini yükle
   (`.github` klasörü dahil).
2. Gmail'de 2 adımlı doğrulamayı aç, sonra
   https://myaccount.google.com/apppasswords adresinden bir **uygulama şifresi** oluştur.
3. Repo → Settings → Secrets and variables → Actions → New repository secret:
   - `GMAIL_USER`: gmail adresin
   - `GMAIL_APP_PASSWORD`: 16 haneli uygulama şifresi (boşluksuz)
   - `MAIL_TO`: bildirimin gideceği adres (aynıysa yine yaz)
4. Actions sekmesi → **Ilan Takip** → **Run workflow** ile ilk testi yap.
   İlk çalışmada geçmiş eşleşmelerin hepsi bir kerede gelir, sonra yalnızca yeniler gelir.

## Ayarlar

`config.json` içinde:
- `anahtar_kelimeler`: başlıkta bunlardan biri geçerse bildirilir
- `haric_kelimeler`: bunlar geçerse bildirilmez
- `kaynaklar`: taranacak RSS/HTML adresleri. Yeni kurum sayfası eklemek için
  `{"ad": "...", "tur": "html", "url": "..."}` satırı ekle.

## Notlar

- Zamanlama saati UTC'dir; 3 saatte bir çalışır. Sıklığı `takip.yml` içindeki cron'dan değiştir.
- Repoda 60 gün hiç etkinlik olmazsa GitHub zamanlanmış çalışmayı durdurabilir;
  Actions sekmesinden ara sıra kontrol et.
- Kariyer Kapısı gibi JavaScript ile yüklenen siteler bu yöntemle taranamaz;
  orada kendi bildirim özelliğini kullan.
- Bazı siteler otomatik erişimi engelleyebilir; böyle bir kaynak log'da [UYARI] verir, diğerleri devam eder.
