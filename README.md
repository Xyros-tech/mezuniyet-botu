# Teknik Destek Botu

Discord için geliştirilmiş akıllı teknik destek botu. Gemini AI entegrasyonu ile bilinmeyen sorulara otomatik cevap verir.

## Özellikler

- 🤖 **Gemini AI Entegrasyonu**: Kayıtlı olmayan sorulara AI ile otomatik cevap
- 📚 **SSS Sistemi**: Sıkça sorulan sorular için hızlı cevaplar
- 👥 **Uzman Yönlendirme**: Soruları ilgili uzmanlara otomatik yönlendirme
- 📊 **Soru Takibi**: Kullanıcı sorularının durumunu takip etme
- 🔧 **Yönetici Paneli**: SSS yönetimi ve soru durumu güncelleme

## Kurulum

1. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

2. `config.py` dosyasında Discord bot token'ınızı ve Gemini API key'inizi ayarlayın:
```python
TOKEN = "your_discord_bot_token"
GEMINI_API_KEY = "your_gemini_api_key"
```

3. Botu çalıştırın:
```bash
python bot.py
```

## Komutlar

### Kullanıcı Komutları
- `!sss <soru>` - SSS'den cevap al veya AI'ya sor
- `!sss_liste` - SSS anahtar kelimelerini listele
- `!sss_buton` - SSS'leri butonlarla göster
- `!yardim` - Yardım mesajı
- `!soru_durumum` - Kendi sorularının durumunu gör

### Yönetici Komutları
- `!sss_ekle <anahtar> <cevap>` - Yeni SSS ekle
- `!sorulari_listele` - Kayıtlı soruları listele
- `!soru_durum_guncelle <id> <durum>` - Soru durumunu güncelle

## AI Entegrasyonu

Bot, SSS'de bulunamayan soruları otomatik olarak Gemini AI'ya yönlendirir. AI'dan gelen cevaplar:
- Kullanıcıya gösterilir
- SSS veritabanına otomatik eklenir
- Gelecekte aynı soru sorulduğunda hızlıca cevaplanır

## Dosya Yapısı

- `bot.py` - Ana bot dosyası
- `logic.py` - Veritabanı işlemleri ve AI entegrasyonu
- `config.py` - API anahtarları ve konfigürasyon
- `bot.db` - SQLite veritabanı
- `requirements.txt` - Gerekli Python kütüphaneleri
