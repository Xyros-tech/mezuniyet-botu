import json
import os
from datetime import datetime
import sqlite3

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
