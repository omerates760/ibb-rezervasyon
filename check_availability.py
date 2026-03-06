#!/usr/bin/env python3
"""
İBB Sosyal Tesisler Rezervasyon Takip Botu
Belirtilen tesislerde müsaitlik varsa Telegram'dan bildirim gönderir.
"""

import os
import ssl
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode

from bs4 import BeautifulSoup

# İBB sitesi SSL sertifika zincirinde sorun çıkarabiliyor (özellikle macOS)
# SSL_VERIFY=1 ile standart doğrulamayı zorlayabilirsiniz
_SSL_CONTEXT = ssl.create_default_context()
if os.environ.get("SSL_VERIFY", "0") == "0":
    _SSL_CONTEXT.check_hostname = False
    _SSL_CONTEXT.verify_mode = ssl.CERT_NONE

# Hedef tesisler: isim -> reservation/create sayfasındaki ID
FACILITIES = {
    "ALTINBOYNUZ SOSYAL TESİSİ": 1,
    "CİHANGİR SOSYAL TESİSİ": 4,
    "ÇAMLICA SOSYAL TESİSİ": 5,
    "FETHİPAŞA SOSYAL TESİSLERİ": 7,
    "FLORYA SOSYAL TESİSLERİ": 8,
    "HALİÇ SOSYAL TESİSİ": 10,
    "KASIMPAŞA SOSYAL TESİSİ": 12,
    "KÜÇÜKÇEKMECE SOSYAL TESİSİ": 14,
}

BASE_URL = "https://tesislerrezervasyon.ibb.istanbul"


def check_facility_availability(facility_id: int) -> tuple[bool, list[str]]:
    """
    Tesis rezervasyon sayfasını çeker ve müsait tarihleri bulur.
    Returns: (has_availability, list_of_available_dates)
    """
    url = f"{BASE_URL}/reservation/create/{facility_id}"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; IBB-Rezervasyon-Bot/1.0)"})

    try:
        with urlopen(req, timeout=15, context=_SSL_CONTEXT) as response:
            html = response.read().decode("utf-8")
    except (URLError, HTTPError) as e:
        print(f"  Hata: {url} - {e}", file=sys.stderr)
        return False, []

    soup = BeautifulSoup(html, "html.parser")
    available_dates = []

    for inp in soup.find_all("input", {"name": "reservation_date"}):
        if inp.get("disabled") is not None:
            continue
        val = inp.get("value")
        if not val:
            continue
        try:
            dt = datetime.strptime(val.strip().split()[0], "%Y-%m-%d")
            available_dates.append(dt.strftime("%d.%m.%Y"))
        except (ValueError, IndexError):
            available_dates.append(val)

    return len(available_dates) > 0, available_dates


def send_telegram_message(token: str, chat_id: str, text: str) -> bool:
    """Telegram'a mesaj gönderir."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        req = Request(
            url,
            data=urlencode(data).encode(),
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urlopen(req, timeout=10, context=_SSL_CONTEXT) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Telegram gönderim hatası: {e}", file=sys.stderr)
        return False


def main():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "@SosyalTesisMyBot")

    if not token:
        print("TELEGRAM_BOT_TOKEN ortam değişkeni tanımlı değil.", file=sys.stderr)
        sys.exit(1)

    # Job başlangıç bildirimi (Türkiye saati)
    now = datetime.now(ZoneInfo("Europe/Istanbul")).strftime("%d.%m.%Y %H:%M")
    start_msg = f"🚀 <b>İBB Rezervasyon Botu</b>\n\nKontrol başladı: {now}"
    send_telegram_message(token, chat_id, start_msg)

    available_facilities = []

    for name, facility_id in FACILITIES.items():
        has_avail, dates = check_facility_availability(facility_id)
        if has_avail:
            available_facilities.append((name, dates))
            print(f"✓ {name}: Müsait - {', '.join(dates)}")
        else:
            print(f"✗ {name}: Dolu")

    if available_facilities:
        lines = ["🔔 <b>İBB Sosyal Tesis Müsaitlik Bildirimi</b>\n"]
        for name, dates in available_facilities:
            date_str = ", ".join(dates)
            lines.append(f"• <b>{name}</b>\n  Müsait: {date_str}")
            lines.append("")
        text = "\n".join(lines)
        text += f"\n📎 Rezervasyon: {BASE_URL}"

        if send_telegram_message(token, chat_id, text):
            print("\nTelegram bildirimi gönderildi.")
        else:
            print("\nTelegram bildirimi gönderilemedi.", file=sys.stderr)
            sys.exit(1)
    else:
        print("\nMüsait tesis bulunamadı.")


if __name__ == "__main__":
    main()
