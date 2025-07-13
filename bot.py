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
            yeni_rutbe = logic.soru_sonrasi_rutbe_guncelle(str(ctx.author))
            if yeni_rutbe:
                await ctx.send(f"🎉 Tebrikler! Yeni rütbeniz: **{yeni_rutbe}**")
            return
    yakinlar = difflib.get_close_matches(soru.lower(), anahtarlar, n=1, cutoff=0.5)
    if yakinlar:
        cevap = logic.sss_cevap(yakinlar[0])
        embed = discord.Embed(title=f"❓ SSS (Benzer Soru): {yakinlar[0]}", description=cevap, color=0x3498db)
        embed.set_footer(text="Tam eşleşme bulamadım, en yakın sonucu gösterdim.")
        await ctx.send(embed=embed)
        yeni_rutbe = logic.soru_sonrasi_rutbe_guncelle(str(ctx.author))
        if yeni_rutbe:
            await ctx.send(f"🎉 Tebrikler! Yeni rütbeniz: **{yeni_rutbe}**")
        return
    gemini_cevap = logic.gemini_soru_sor(soru)
    if gemini_cevap:
        logic.sss_ekle(soru.lower()[:50], gemini_cevap)
        embed = discord.Embed(title="🤖 AI Cevabı", description=gemini_cevap, color=0x9b59b6)
        embed.set_footer(text="Bu cevap AI tarafından oluşturuldu ve SSS'ye eklendi.")
        await ctx.send(embed=embed)
        yeni_rutbe = logic.soru_sonrasi_rutbe_guncelle(str(ctx.author))
        if yeni_rutbe:
            await ctx.send(f"🎉 Tebrikler! Yeni rütbeniz: **{yeni_rutbe}**")
    else:
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
        yeni_rutbe = logic.soru_sonrasi_rutbe_guncelle(str(ctx.author))
        if yeni_rutbe:
            await ctx.send(f"🎉 Tebrikler! Yeni rütbeniz: **{yeni_rutbe}**")

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
            "- !sorulari_listele: Kayıtlı soruları listele\n"
            "- !soru_durum_guncelle <id> <yeni_durum>: Soru durumunu güncelle\n"
            "\nKullanıcı komutları da kullanılabilir."
        )
    else:
        mesaj = (
            "**Kullanıcı Komutları**\n"
            "- !sss <soru>: SSS'den otomatik cevap al\n"
            "- !sss_liste: SSS anahtar kelimelerini gör\n"
            "- !sss_buton: SSS anahtarlarını butonlarla gör\n"
            "- !soru_durumum: Kendi sorularının durumunu gör\n"
            "- !yardim: Bu yardım mesajı\n"
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

logic.sss_otomatik_yukle()

bot.run(TOKEN)