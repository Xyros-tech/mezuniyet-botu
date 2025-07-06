import discord
from discord.ext import commands
import logic
import json
import sqlite3
from datetime import datetime
import socket
from config import TOKEN
import difflib
import logging

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

logic.veritabani_olustur()

sss = logic.sss_yukle()

uzmanlar = {
    "programcı": "@ProgramciRolü",
    "satış": "@SatisRolü"
}

logging.basicConfig(filename='bot_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

@bot.event
async def on_ready():
    print(f'Bot hazır! Giriş yapan kullanıcı: {bot.user}')

@bot.command(name='sss')
async def sss_cevapla(ctx, *, soru: str = None):
    """Kullanıcıdan gelen soruya SSS'den otomatik cevap verir."""
    if not soru:
        embed = discord.Embed(title="Soru Girmediniz", description="Lütfen bir soru yazın.\nÖrnek: `!sss kargo`", color=0xf1c40f)
        await ctx.send(embed=embed)
        return
    anahtarlar = logic.sss_liste()
    for anahtar in anahtarlar:
        if anahtar in soru.lower():
            cevap = logic.sss_cevap(anahtar)
            embed = discord.Embed(title=f"🔎 SSS: {anahtar}", description=cevap, color=0x2ecc71)
            embed.set_footer(text="Daha fazla anahtar için !sss_liste veya !sss_buton kullanabilirsiniz.")
            await ctx.send(embed=embed)
            return

    yakinlar = difflib.get_close_matches(soru.lower(), anahtarlar, n=1, cutoff=0.5)
    if yakinlar:
        cevap = logic.sss_cevap(yakinlar[0])
        embed = discord.Embed(title=f"❓ SSS (Benzer Soru): {yakinlar[0]}", description=cevap, color=0x3498db)
        embed.set_footer(text="Tam eşleşme bulamadım, en yakın sonucu gösterdim.")
        await ctx.send(embed=embed)
        return
    logic.soru_kaydet(str(ctx.author), soru, str(ctx.channel), datetime.now().isoformat())
    embed = discord.Embed(title="Cevap Bulunamadı", description="Bu soruya henüz otomatik bir cevabım yok. Sorunuz kaydedildi ve ilgili uzmana iletilecek.", color=0xe74c3c)
    await ctx.send(embed=embed)
    try:
        await ctx.author.send("Sorunuz kaydedildi ve uzmanlara iletildi. En kısa sürede dönüş yapılacaktır.")
    except Exception:
        pass
    if any(k in soru.lower() for k in ["site", "ödeme", "hata"]):
        await ctx.send(f"Sorunuz teknik bir konuya benziyor. {uzmanlar['programcı']} sizinle ilgilenecek.")
    else:
        await ctx.send(f"Sorunuz ürün veya satışla ilgili olabilir. {uzmanlar['satış']} sizinle ilgilenecek.")

@bot.command(name='sss_ekle')
@commands.has_permissions(administrator=True)
async def sss_ekle(ctx, anahtar: str, *, cevap: str):
    logic.sss_ekle(anahtar.lower(), cevap)
    await ctx.send(f"'{anahtar}' anahtarı ile yeni SSS eklendi.")

@bot.command(name='yardim')
async def yardim(ctx):
    if ctx.author.guild_permissions.administrator:
        mesaj = (
            "**Yönetici Komutları**\n"
            "- !sss <soru>: SSS'den otomatik cevap al\n"
            "- !sss_liste: SSS anahtar kelimelerini gör\n"
            "- !sss_buton: SSS anahtarlarını butonlarla gör\n"
            "- !sss_ekle <anahtar> <cevap>: Yeni SSS ekle\n"
            "- !sss_yukle: JSON dosyasından toplu SSS yükle\n"
            "- !sss_indir: SSS listesini indir\n"
            "- !sorulari_listele: Kayıtlı soruları listele\n"
            "- !sorulari_indir: Soruları indir\n"
            "- !soru_durum_guncelle <id> <yeni_durum>: Soru durumunu güncelle\n"
            "- !dokumantasyon: Tüm komutlar ve açıklamaları\n"
            "\nKullanıcı komutları da kullanılabilir."
        )
    else:
        mesaj = (
            "**Kullanıcı Komutları**\n"
            "- !sss <soru>: SSS'den otomatik cevap al\n"
            "- !sss_liste: SSS anahtar kelimelerini gör\n"
            "- !sss_buton: SSS anahtarlarını butonlarla gör\n"
            "- !kullanim: Kullanım kılavuzu\n"
            "- !soru_durumum: Kendi sorularının durumunu gör\n"
            "- !ping: Botun gecikmesini gör\n"
            "- !sunucu_bilgi: Sunucu bilgilerini gör\n"
            "- !komutlar_nasil: Komutların nasıl kullanılacağını öğren\n"
            "- !dokumantasyon: Tüm komutlar ve açıklamaları\n"
        )
    await ctx.send(mesaj)

@bot.command(name='sss_liste')
async def sss_liste(ctx):
    """Mevcut SSS anahtar kelimelerini listeler."""
    anahtarlar = logic.sss_liste()
    anahtarlar_str = '\n'.join(f"• {a}" for a in anahtarlar)
    embed = discord.Embed(title="Sıkça Sorulan Konular", description=anahtarlar_str, color=0x1abc9c)
    embed.set_footer(text="Detay için: !sss <konu> veya !sss_buton kullanabilirsiniz.")
    await ctx.send(embed=embed)

@bot.command(name='kullanim')
async def kullanim(ctx):
    mesaj = (
        "**Teknik Destek Botu Kullanım Kılavuzu**\n"
        "1. SSS'den otomatik cevap almak için: `!sss <sorunuz veya anahtar kelime>`\n"
        "   Örnek: `!sss kargo`\n"
        "2. SSS anahtar kelimelerini görmek için: `!sss_liste`\n"
        "3. Yardım mesajı için: `!yardim`\n"
        "4. Sorunuz karmaşıksa, bot sizi ilgili uzmana yönlendirir ve sorunuz kaydedilir.\n"
        "5. (Yönetici) Yeni SSS eklemek için: `!sss_ekle <anahtar> <cevap>`\n"
        "\nDaha fazla bilgi veya öneri için yöneticilere ulaşabilirsiniz."
    )
    await ctx.send(mesaj)

@bot.command(name='sorulari_listele')
@commands.has_permissions(administrator=True)
async def sorulari_listele(ctx):
    """Yöneticiler için: Kayıtlı soruları listeler."""
    try:
        sorular = logic.sorulari_listele()
        if not sorular:
            await ctx.send("Kayıtlı soru yok.")
            return
        mesaj = "\n".join([f"{s[0]}. {s[1]} - {s[2]} (Durum: {s[3]})" for s in sorular])
        await ctx.send(mesaj[:2000])
    except Exception:
        await ctx.send("Soru kaydı bulunamadı.")

@bot.command(name='soru_durum_guncelle')
@commands.has_permissions(administrator=True)
async def soru_durum_guncelle(ctx, soru_id: int, yeni_durum: str):
    """Yöneticiler için: Soru durumunu günceller."""
    try:
        logic.soru_durum_guncelle(soru_id, yeni_durum)
        await ctx.send(f"{soru_id}. sorunun durumu '{yeni_durum}' olarak güncellendi.")
        
        if yeni_durum.lower() == 'cevaplandı':
            sorular = logic.sorulari_listele()
            for s in sorular:
                if s[0] == soru_id:
                    kullanici_adi = s[1]
                    break
            else:
                kullanici_adi = None
            if kullanici_adi:
                for member in ctx.guild.members:
                    if str(member) == kullanici_adi:
                        try:
                            await member.send(f"Sorduğunuz {soru_id}. numaralı soruya cevap verildi! Lütfen sunucudan kontrol edin.")
                        except Exception:
                            pass
                        break
    except Exception:
        await ctx.send("Güncelleme başarısız.")

@bot.command(name='soru_durumum')
async def soru_durumum(ctx):
    """Kullanıcıya kendi sorduğu soruların durumunu gösterir."""
    try:
        sorular = logic.kullanici_sorulari(str(ctx.author))
        if not sorular:
            await ctx.send("Kayıtlı sorunuz yok.")
            return
        mesaj = "\n".join([f"{i+1}. {s[0]} (Durum: {s[1]})" for i, s in enumerate(sorular)])
        await ctx.send(mesaj[:2000])
    except Exception:
        await ctx.send("Soru kaydı bulunamadı.")

@bot.command(name='ping')
async def ping(ctx):
    """Botun gecikmesini gösterir."""
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command(name='sunucu_bilgi')
async def sunucu_bilgi(ctx):
    sunucu = ctx.guild
    mesaj = (
        f"Sunucu adı: {sunucu.name}\n"
        f"Üye sayısı: {sunucu.member_count}\n"
        f"Oluşturulma tarihi: {sunucu.created_at.strftime('%d.%m.%Y')}"
    )
    await ctx.send(mesaj)

@bot.command(name='komutlar_nasil')
async def komutlar_nasil(ctx):
    mesaj = (
        "**Komutları Nasıl Kullanırım?**\n"
        "Tüm komutlar ünlem (!) ile başlar.\n"
        "Örnekler:\n"
        "- !sss kargo\n"
        "- !sss_liste\n"
        "- !kullanim\n"
        "- !ping\n"
        "- !sunucu_bilgi\n"
        "- !soru_durumum\n"
        "- (Yönetici) !sss_ekle anahtar cevap\n"
        "- (Yönetici) !sorulari_listele\n"
        "- (Yönetici) !soru_durum_guncelle index yeni_durum\n"
        "\nKomutları yazdıktan sonra Enter'a basmanız yeterli!"
    )
    await ctx.send(mesaj)

@bot.command(name='sss_yukle')
@commands.has_permissions(administrator=True)
async def sss_yukle(ctx):
    """Yöneticiler için: JSON dosyasından toplu SSS yükler."""
    if not ctx.message.attachments:
        await ctx.send("Lütfen bir JSON dosyası ekleyin. Örnek kullanım: !sss_yukle ile birlikte dosya yükleyin.")
        return
    dosya = ctx.message.attachments[0]
    if not dosya.filename.endswith('.json'):
        await ctx.send("Sadece .json uzantılı dosya kabul edilir.")
        return
    icerik = await dosya.read()
    try:
        sss_dict = json.loads(icerik.decode('utf-8'))
        for anahtar, cevap in sss_dict.items():
            logic.sss_ekle(anahtar.lower(), cevap)
        await ctx.send(f"{len(sss_dict)} adet SSS başarıyla yüklendi.")
    except Exception as e:
        await ctx.send(f"Yükleme başarısız: {e}")

@bot.command(name='sss_indir')
@commands.has_permissions(administrator=True)
async def sss_indir(ctx):
    """Yöneticiler için: SSS listesini JSON dosyası olarak indirir."""
    try:
        sss_list = [(anahtar, logic.sss_cevap(anahtar)) for anahtar in logic.sss_liste()]
        sss_dict = {k: v for k, v in sss_list}
        with open('sss_export.json', 'w', encoding='utf-8') as f:
            json.dump(sss_dict, f, ensure_ascii=False, indent=2)
        await ctx.send(file=discord.File('sss_export.json'))
    except Exception as e:
        await ctx.send(f"İndirme başarısız: {e}")

@bot.command(name='sorulari_indir')
@commands.has_permissions(administrator=True)
async def sorulari_indir(ctx):
    """Yöneticiler için: Kayıtlı soruları JSON dosyası olarak indirir."""
    try:
        sorular = logic.sorulari_listele()
        sorular_list = [
            {"id": s[0], "kullanici": s[1], "soru": s[2], "durum": s[3]} for s in sorular
        ]
        with open('sorular_export.json', 'w', encoding='utf-8') as f:
            json.dump(sorular_list, f, ensure_ascii=False, indent=2)
        await ctx.send(file=discord.File('sorular_export.json'))
    except Exception as e:
        await ctx.send(f"İndirme başarısız: {e}")

class SSSButtonView(discord.ui.View):
    def __init__(self, sss_list):
        super().__init__(timeout=60)
        for anahtar in sss_list:
            self.add_item(SSSButton(label=anahtar))

class SSSButton(discord.ui.Button):
    def __init__(self, label):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.anahtar = label

    async def callback(self, interaction: discord.Interaction):
        cevap = logic.sss_cevap(self.anahtar)
        embed = discord.Embed(title=f"SSS: {self.anahtar}", description=cevap or "Cevap bulunamadı.", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command(name='sss_buton')
async def sss_buton(ctx):
    """SSS anahtar kelimelerini butonlarla ve şık bir arayüzle gösterir."""
    sss_list = logic.sss_liste()
    if not sss_list:
        await ctx.send("SSS verisi bulunamadı.")
        return
    view = SSSButtonView(sss_list)
    embed = discord.Embed(
        title="Sıkça Sorulan Konular (Butonlu)",
        description="Aşağıdaki butonlardan birini seçerek ilgili cevabı hızlıca görebilirsiniz.",
        color=0x9b59b6
    )
    embed.set_footer(text="SSS veritabanı sürekli güncellenmektedir.")
    await ctx.send(embed=embed, view=view)

@bot.command(name='dokumantasyon')
async def dokumantasyon(ctx):
    mesaj = (
        "**Teknik Destek Botu Dokümantasyonu**\n"
        "\n"
        "**Kullanıcı Komutları:**\n"
        "- !sss <soru>: SSS'den otomatik cevap alır veya uzmanlara iletir.\n"
        "- !sss_liste: SSS anahtar kelimelerini listeler.\n"
        "- !sss_buton: SSS anahtarlarını butonlarla gösterir.\n"
        "- !yardim: Kısa yardım mesajı.\n"
        "- !kullanim: Kullanım kılavuzu.\n"
        "- !soru_durumum: Kendi sorduğunuz soruların durumunu gösterir.\n"
        "- !ping: Botun gecikmesini gösterir.\n"
        "- !sunucu_bilgi: Sunucu bilgilerini gösterir.\n"
        "- !komutlar_nasil: Komutların nasıl kullanılacağını açıklar.\n"
        "\n"
        "**Yönetici Komutları:**\n"
        "- !sss_ekle <anahtar> <cevap>: Yeni SSS ekler.\n"
        "- !sss_yukle: JSON dosyasından toplu SSS yükler (dosya ekleyin).\n"
        "- !sss_indir: SSS listesini JSON olarak indirir.\n"
        "- !sorulari_listele: Kayıtlı soruları listeler.\n"
        "- !sorulari_indir: Kayıtlı soruları JSON olarak indirir.\n"
        "- !soru_durum_guncelle <id> <yeni_durum>: Soru durumunu günceller.\n"
        "\n"
        "**Notlar:**\n"
        "- SSS dosyası örneği: { 'kargo': 'Kargo 2-3 gün içinde gelir.', ... }\n"
        "- SSS ve sorular veritabanında saklanır.\n"
        "- Sorularınız otomatik cevaplanmazsa ilgili uzmana iletilir.\n"
        "\nDaha fazla bilgi için yöneticilere ulaşabilirsiniz."
    )
    await ctx.send(mesaj)

@bot.command(name='sss_ornek')
@commands.has_permissions(administrator=True)
async def sss_ornek(ctx):
    """Yöneticiler için: Örnek SSS JSON dosyası ve açıklaması gönderir."""
    ornek_json = '{\n  "kargo": "Kargo 2-3 gün içinde gelir.",\n  "ödeme": "Ödeme kredi kartı veya havale ile yapılabilir.",\n  "iade": "İade süresi 14 gündür."\n}'
    with open('sss_ornek.json', 'w', encoding='utf-8') as f:
        f.write(ornek_json)
    mesaj = (
        "**SSS JSON Dosyası Örneği**\n"
        "Aşağıdaki gibi bir dosya yükleyebilirsiniz.\n"
        "Anahtarlar küçük harf ve Türkçe karakter içerebilir.\n"
        "Her anahtar bir konu, her değer ise cevaptır.\n"
        "\nKod örneği:\n"
        f"```json\n{ornek_json}\n```"
    )
    await ctx.send(mesaj)
    await ctx.send(file=discord.File('sss_ornek.json'))

@bot.command(name='sss_toplu_ekle')
@commands.has_permissions(administrator=True)
async def sss_toplu_ekle(ctx):
    """Yöneticiler için: Mesaj olarak gönderilen JSON formatındaki SSS listesini veritabanına topluca ekler."""
    await ctx.send("Lütfen eklemek istediğiniz SSS listesini JSON formatında bu komuta cevap olarak gönderin. (Örnek: !sss_ornek ile alınabilir)")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        cevap = await bot.wait_for('message', check=check, timeout=120)
        sss_dict = json.loads(cevap.content)
        sayac = 0
        for anahtar, cevap in sss_dict.items():
            logic.sss_ekle(anahtar.lower(), cevap)
            sayac += 1
        await ctx.author.send(f"Toplam {sayac} adet SSS başarıyla eklendi!")
        await ctx.send("SSS'ler başarıyla eklendi. Detaylar özel mesaj olarak gönderildi.")
    except Exception as e:
        await ctx.send(f"Bir hata oluştu: {e}\nLütfen JSON formatını kontrol edin.")

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

def sss_ekle(anahtar, cevap):
    with db_baglanti() as conn:
        conn.execute("INSERT OR REPLACE INTO sss (anahtar, cevap) VALUES (?, ?)", (anahtar, cevap))
    logging.info(f"SSS eklendi/güncellendi: {anahtar}")

def sss_liste():
    with db_baglanti() as conn:
        return [row[1] for row in conn.execute("SELECT id, anahtar FROM sss").fetchall()]

def sss_cevap(anahtar):
    with db_baglanti() as conn:
        row = conn.execute("SELECT cevap FROM sss WHERE anahtar=?", (anahtar,)).fetchone()
        return row[0] if row else None

def soru_kaydet(kullanici, soru, kanal, tarih, durum='beklemede'):
    with db_baglanti() as conn:
        conn.execute("INSERT INTO sorular (kullanici, soru, kanal, tarih, durum) VALUES (?, ?, ?, ?, ?)",
                     (kullanici, soru, kanal, tarih, durum))
    logging.info(f"Soru kaydedildi: {kullanici} - {soru}")

def sorulari_listele():
    with db_baglanti() as conn:
        return conn.execute("SELECT id, kullanici, soru, durum FROM sorular").fetchall()

def soru_durum_guncelle(soru_id, yeni_durum):
    with db_baglanti() as conn:
        conn.execute("UPDATE sorular SET durum=? WHERE id=?", (yeni_durum, soru_id))
    logging.info(f"Soru durumu güncellendi: {soru_id} -> {yeni_durum}")

def kullanici_sorulari(kullanici):
    with db_baglanti() as conn:
        return conn.execute("SELECT soru, durum FROM sorular WHERE kullanici=?", (kullanici,)).fetchall()

def sss_otomatik_yukle():
    """Google Dokümanındaki SSS'leri ve örnek SSS'leri veritabanına yükler."""
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
            logic.sss_ekle(anahtar.lower(), cevap)
            sayac += 1
        except Exception as e:
            logging.error(f"SSS eklenirken hata: {anahtar} - {e}")
    
    logging.info(f"Toplam {sayac} adet SSS otomatik olarak yüklendi.")
    return sayac

sss_otomatik_yukle()

bot.run(TOKEN)



