import json
import os
from datetime import datetime
import sqlite3
import requests
import logging
from config import GEMINI_API_KEY

SSS_DOSYA = 'sss.json'
SORULAR_DOSYA = 'sorular.json'

def db_baglanti():
    return sqlite3.connect('bot.db')

def veritabani_olustur():
    with db_baglanti() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sss (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anahtar TEXT UNIQUE,
                cevap TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sorular (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici TEXT,
                soru TEXT,
                kanal TEXT,
                tarih TEXT,
                durum TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rutbeler (
                kullanici TEXT PRIMARY KEY,
                rutbe TEXT
            )
        """)

def sss_ekle(anahtar, cevap):
    with db_baglanti() as conn:
        conn.execute("INSERT OR REPLACE INTO sss (anahtar, cevap) VALUES (?, ?)", (anahtar, cevap))

def sss_liste():
    with db_baglanti() as conn:
        return [row[0] for row in conn.execute("SELECT anahtar FROM sss").fetchall()]

def sss_cevap(anahtar):
    with db_baglanti() as conn:
        row = conn.execute("SELECT cevap FROM sss WHERE anahtar=?", (anahtar,)).fetchone()
        return row[0] if row else None

def sss_yukle():
    if not os.path.exists(SSS_DOSYA):
        return {}
    with open(SSS_DOSYA, 'r', encoding='utf-8') as f:
        return json.load(f)

def sss_kaydet(sss_dict):
    with open(SSS_DOSYA, 'w', encoding='utf-8') as f:
        json.dump(sss_dict, f, ensure_ascii=False, indent=2)

def soru_kaydet(kullanici, soru, kanal, tarih, durum='beklemede'):
    with db_baglanti() as conn:
        conn.execute("INSERT INTO sorular (kullanici, soru, kanal, tarih, durum) VALUES (?, ?, ?, ?, ?)",
                     (kullanici, soru, kanal, tarih, durum))

def sorulari_listele():
    with db_baglanti() as conn:
        return conn.execute("SELECT id, kullanici, soru, durum FROM sorular").fetchall()

def soru_durum_guncelle(soru_id, yeni_durum):
    with db_baglanti() as conn:
        conn.execute("UPDATE sorular SET durum=? WHERE id=?", (yeni_durum, soru_id))

def kullanici_sorulari(kullanici):
    with db_baglanti() as conn:
        return conn.execute("SELECT soru, durum FROM sorular WHERE kullanici=?", (kullanici,)).fetchall()

def kullanici_soru_sayisi(kullanici):
    with db_baglanti() as conn:
        row = conn.execute("SELECT COUNT(*) FROM sorular WHERE kullanici=?", (kullanici,)).fetchone()
        return row[0] if row else 0

def kullanici_rutbe(soru_sayisi):
    if soru_sayisi >= 21:
        return "Usta Soran"
    elif soru_sayisi >= 6:
        return "Aktif Üye"
    elif soru_sayisi >= 1:
        return "Yeni Üye"
    else:
        return "Hiç Soru Sormamış"

def gemini_soru_sor(soru):
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{
                "parts": [{
                    "text": f"Sen bir müşteri hizmetleri temsilcisisin. Aşağıdaki soruya kısa, net ve yardımcı bir cevap ver. Cevabın Türkçe olmalı ve 100 kelimeden az olmalı: {soru}"
                }]
            }]
        }
        response = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                cevap = result['candidates'][0]['content']['parts'][0]['text']
                return cevap.strip()
        return None
    except Exception as e:
        logging.error(f"Gemini API hatası: {e}")
        return None

def sss_otomatik_yukle():
    sss_verileri = {
        "kargo": "Kargo 2-3 iş günü içinde adresinize teslim edilir. Kargo takip numarası SMS ile gönderilir.",
        "ödeme": "Kredi kartı, havale/EFT ve kapıda ödeme seçenekleri mevcuttur. Tüm ödemeler güvenli şekilde işlenir.",
        "iade": "Ürün tesliminden itibaren 14 gün içinde iade yapabilirsiniz. Ürün orijinal ambalajında olmalıdır.",
        "değişim": "Ürün hatası durumunda ücretsiz değişim yapılır. Müşteri hizmetlerimizle iletişime geçin.",
        "garanti": "Tüm ürünlerimiz 2 yıl garanti kapsamındadır. Garanti belgesi kargo ile birlikte gönderilir.",
        "stok": "Stok durumu anlık olarak güncellenir. Stokta olmayan ürünler için ön sipariş alınabilir.",
        "fiyat": "Fiyatlarımız KDV dahildir. Kampanya ve indirimler için sosyal medya hesaplarımızı takip edin.",
        "kargo ücreti": "150 TL üzeri alışverişlerde kargo ücretsizdir. Alt tutarlarda 15 TL kargo ücreti alınır.",
        "sipariş takip": "Siparişinizi 'Sipariş Takip' bölümünden takip edebilirsiniz. Kargo numarası SMS ile gönderilir.",
        "müşteri hizmetleri": "7/24 müşteri hizmetlerimiz hizmetinizdedir. WhatsApp: 0555 123 45 67",
        "güvenlik": "Tüm ödeme işlemleriniz SSL sertifikası ile korunmaktadır. Kredi kartı bilgileriniz saklanmaz.",
        "kampanya": "Güncel kampanyalar için ana sayfamızı ziyaret edin. Özel indirimler sosyal medya hesaplarımızda duyurulur.",
        "ürün bilgisi": "Ürün detay sayfalarında tüm teknik özellikler ve kullanım kılavuzları bulunmaktadır.",
        "şifre sıfırlama": "Şifrenizi unuttuysanız 'Şifremi Unuttum' linkini kullanarak yeni şifre alabilirsiniz.",
        "hesap oluşturma": "Ücretsiz hesap oluşturmak için 'Üye Ol' butonunu kullanabilirsiniz.",
        "adres değişikliği": "Sipariş verildikten sonra adres değişikliği için müşteri hizmetlerimizle iletişime geçin.",
        "fatura": "Faturanız kargo ile birlikte gönderilir. E-fatura için hesap ayarlarınızdan talep edebilirsiniz.",
        "kupon kodu": "Kupon kodlarınızı ödeme sayfasında 'Kupon Kodu' bölümüne girerek kullanabilirsiniz.",
        "puan sistemi": "Her alışverişinizde puan kazanırsınız. 1000 puan = 10 TL indirim olarak kullanılabilir.",
        "yorum yapma": "Ürün yorumları için üye girişi yapmanız gerekmektedir. Yorumlar moderasyon sonrası yayınlanır.",
        "kargo firması": "Anlaşmalı kargo firmalarımız: Yurtiçi Kargo, Aras Kargo ve MNG Kargo. Teslimat süresi 2-3 iş günüdür.",
        "kargo takip": "Kargo takip numaranızı SMS ile alacaksınız. Takip için kargo firmasının web sitesini kullanabilirsiniz.",
        "kapıda ödeme": "Kapıda ödeme seçeneği mevcuttur. Ek ücret 5 TL'dir. Sadece nakit ödeme kabul edilir.",
        "kredi kartı taksit": "3, 6, 9 ve 12 taksit seçenekleri mevcuttur. Taksit ücreti yoktur.",
        "havale bilgileri": "Havale bilgileri: Banka: X Bankası, IBAN: TR00 0000 0000 0000 0000 0000 00, Alıcı: Şirket Adı",
        "sipariş iptal": "Siparişinizi kargo firmasına teslim edilmeden önce iptal edebilirsiniz. Müşteri hizmetlerimizle iletişime geçin.",
        "ürün hasarı": "Kargo sırasında hasar gören ürünler için fotoğraf çekip müşteri hizmetlerimizle iletişime geçin.",
        "eksik ürün": "Eksik ürün durumunda kargo paketini açmadan fotoğraf çekip müşteri hizmetlerimizle iletişime geçin.",
        "yanlış ürün": "Yanlış ürün gönderilmesi durumunda ücretsiz değişim yapılır. Müşteri hizmetlerimizle iletişime geçin.",
        "ürün arızası": "Ürün arızası durumunda garanti kapsamında ücretsiz tamir veya değişim yapılır.",
        "teknik destek": "Teknik destek için WhatsApp: 0555 123 45 67 veya e-posta: destek@sirket.com adresini kullanabilirsiniz.",
        "ürün kullanım kılavuzu": "Ürün kullanım kılavuzları ürün detay sayfalarında PDF formatında bulunmaktadır.",
        "aksesuar": "Ürün aksesuarları ayrı satılır. Aksesuar listesi ürün detay sayfalarında bulunmaktadır.",
        "yedek parça": "Yedek parça talepleri için müşteri hizmetlerimizle iletişime geçin. Garanti kapsamında ücretsizdir.",
        "ürün videosu": "Ürün tanıtım videoları ürün detay sayfalarında ve YouTube kanalımızda bulunmaktadır.",
        "canlı destek": "Canlı destek hizmetimiz hafta içi 09:00-18:00 saatleri arasında mevcuttur."
    }
    sayac = 0
    for anahtar, cevap in sss_verileri.items():
        try:
            sss_ekle(anahtar.lower(), cevap)
            sayac += 1
        except Exception as e:
            logging.error(f"SSS eklenirken hata: {anahtar} - {e}")
    logging.info(f"Toplam {sayac} adet SSS otomatik olarak yüklendi.")
    return sayac

# Kullanıcıya rütbe ver
def rutbe_ver(kullanici, rutbe):
    with db_baglanti() as conn:
        conn.execute("INSERT OR REPLACE INTO rutbeler (kullanici, rutbe) VALUES (?, ?)", (kullanici, rutbe))

# Kullanıcının rütbesini getir
def kullanici_rutbe_db(kullanici):
    with db_baglanti() as conn:
        row = conn.execute("SELECT rutbe FROM rutbeler WHERE kullanici=?", (kullanici,)).fetchone()
        return row[0] if row else None

# Soru sorunca rütbe ver (ilk soruda Bronz, 5. soruda Gümüş, 15. soruda Altın, 30. soruda Elmas)
def soru_sonrasi_rutbe_guncelle(kullanici):
    sayi = kullanici_soru_sayisi(kullanici)
    mevcut = kullanici_rutbe_db(kullanici)
    yeni = None
    if sayi == 1 and mevcut != "Bronz":
        yeni = "Bronz"
    elif sayi == 5 and mevcut != "Gümüş":
        yeni = "Gümüş"
    elif sayi == 15 and mevcut != "Altın":
        yeni = "Altın"
    elif sayi == 30 and mevcut != "Elmas":
        yeni = "Elmas"
    if yeni:
        rutbe_ver(kullanici, yeni)
        return yeni
    return None
