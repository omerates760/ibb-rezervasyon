# İBB Sosyal Tesis Rezervasyon Takip Botu

Altınboynuz, Cihangir, Çamlıca, Fethipaşa, Florya, Haliç, Kasımpaşa ve Küçükçekmece sosyal tesislerinde müsaitlik olduğunda Telegram bildirimi gönderir.

## Kurulum

```bash
cd ibb-rezervasyon
pip install -r requirements.txt
```

> **Not:** İBB sitesi SSL sertifikasında sorun çıkabilir. Varsayılan olarak bu durum yönetilir. Sorun yaşarsanız `SSL_VERIFY=1` ile deneyebilirsiniz.

## Yapılandırma

`.env` dosyası oluşturun (veya `.env.example`'ı kopyalayıp düzenleyin):

```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=@SosyalTesisMyBot
```

**Chat ID notu:** `@SosyalTesisMyBot` bir kanal/kullanıcı adıdır. Botun mesaj gönderebilmesi için:
- **Kanal:** Botu kanala admin olarak ekleyin
- **Özel mesaj:** Sayısal chat ID kullanın (örn. `123456789`). [@userinfobot](https://t.me/userinfobot) ile ID'nizi öğrenebilirsiniz

## Yerel çalıştırma

```bash
python check_availability.py
```

## GitHub Actions ile (6 saatte bir)

1. Bu projeyi GitHub'a push edin
2. Repo → **Settings** → **Secrets and variables** → **Actions**
3. Şu secret'ları ekleyin:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. Workflow her 6 saatte bir otomatik çalışır (UTC: 00:00, 06:00, 12:00, 18:00)
5. Manuel çalıştırma: **Actions** → **İBB Rezervasyon Kontrolü** → **Run workflow**

## İzlenecek tesisler

| Tesis | ID |
|-------|-----|
| Altınboynuz | 1 |
| Cihangir | 4 |
| Çamlıca | 5 |
| Fethipaşa | 7 |
| Florya | 8 |
| Haliç | 10 |
| Kasımpaşa | 12 |
| Küçükçekmece | 14 |
