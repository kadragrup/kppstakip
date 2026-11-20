#!/usr/bin/env python3
"""Kamu ilan takipçisi: yeni ve uygun ilanları e-posta ile bildirir."""
import json, os, smtplib, ssl, sys, hashlib
import xml.etree.ElementTree as ET
from email.mime.text import MIMEText
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (ilan-takip)"}
SEEN_FILE = "seen.json"
MAX_MAIL = 40


def tr_lower(s: str) -> str:
    return s.replace("İ", "i").replace("I", "ı").lower()


def eslesir(baslik, cfg):
    t = tr_lower(baslik)
    if any(tr_lower(x) in t for x in cfg["haric_kelimeler"]):
        return False
    return any(tr_lower(x) in t for x in cfg["anahtar_kelimeler"])


def rss_oku(src):
    r = requests.get(src["url"], headers=HEADERS, timeout=30)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    for it in root.iter("item"):
        baslik = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        if baslik and link:
            yield baslik, link


def html_oku(src):
    r = requests.get(src["url"], headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all("a", href=True):
        baslik = " ".join(a.get_text(" ", strip=True).split())
        if len(baslik) < 15:
            continue
        yield baslik, urljoin(src["url"], a["href"])


def mail_gonder(konu, govde):
    kullanici = os.environ["GMAIL_USER"]
    sifre = os.environ["GMAIL_APP_PASSWORD"]
    alici = os.environ.get("MAIL_TO", kullanici)
    msg = MIMEText(govde, "plain", "utf-8")
    msg["Subject"], msg["From"], msg["To"] = konu, kullanici, alici
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
        s.login(kullanici, sifre)
        s.send_message(msg)


def main():
    cfg = json.load(open("config.json", encoding="utf-8"))
    seen = set(json.load(open(SEEN_FILE))) if os.path.exists(SEEN_FILE) else set()
    yeni = []

    for src in cfg["kaynaklar"]:
        okuyucu = rss_oku if src["tur"] == "rss" else html_oku
        try:
            for baslik, link in okuyucu(src):
                anahtar = hashlib.sha1(link.encode()).hexdigest()
                if anahtar in seen or not eslesir(baslik, cfg):
                    continue
                seen.add(anahtar)
                yeni.append((src["ad"], baslik, link))
        except Exception as e:  # bir kaynak hata verirse diğerleri devam etsin
            print(f"[UYARI] {src['ad']}: {e}", file=sys.stderr)

    print(f"{len(yeni)} yeni ilan bulundu.")
    if yeni:
        satirlar = [f"• {b}\n  {k}\n  (Kaynak: {ad})\n" for ad, b, k in yeni[:MAX_MAIL]]
        if len(yeni) > MAX_MAIL:
            satirlar.append(f"... ve {len(yeni) - MAX_MAIL} ilan daha.")
        mail_gonder(f"Yeni ilan bildirimi ({len(yeni)})", "\n".join(satirlar))

    json.dump(sorted(seen), open(SEEN_FILE, "w"))


if __name__ == "__main__":
    main()
