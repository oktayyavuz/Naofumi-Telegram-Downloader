# 📹 Naofumi - Telegram Video Downloader Bot

**Naofumi**, kullanıcılara YouTube ve Instagram video linklerini göndererek videoları indirme, dönüştürme ve gönderme işlemlerini gerçekleştiren şık bir Telegram botudur. Kullanıcılar, video kalitesini seçebilir; bot, videoyu indirir, gerekirse dosyayı parçalara böler ve işlemleri otomatik olarak tamamlar.

---

## 🚀 Özellikler

- **Çoklu Kaynak Desteği:** YouTube ve Instagram (ddinstagram üzerinden reels) linklerini destekler.  
- **Farklı Format Seçenekleri:** Kullanıcılar MP3 veya MP4 formatlarında video/ekran kaydı indirebilir.  
- **Kalite Seçenekleri:** İstenilen kaliteye göre (örneğin, 1080p, 720p, 480p) video indirme.  
- **Büyük Dosya Desteği:** 2GB’den büyük videolar otomatik olarak daha küçük parçalara ayrılır.  
- **İlerleme Bilgisi:** İndirme ve yükleme süreçleri sırasında adım adım ilerleme durumu bildirimi.  
- **Otomatik Temizlik:** İşlem tamamlandığında geçici dosyalar otomatik olarak silinir.

---

## 🛠️ Kurulum

1. **Repoyu Klonlayın:**

   ```bash
   git clone https://github.com/kullanici_adiniz/naofumi.git
   cd naofumi
   ```

2. **Gerekli Python Paketlerini Yükleyin:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Ortam Değişkenlerinizi Ayarlayın:**

   Aşağıdaki bilgileri kendi API bilgilerinize göre güncelleyin:
   
   - **API_ID:** Telegram API ID'niz  
   - **API_HASH:** Telegram API Hash'iniz  
   - **BOT_TOKEN:** Telegram Bot Token'ınız  

4. **Botu Çalıştırın:**

   ```bash
   python main.py
   ```

---

## 📚 Kullanım

1. **Telegram’da Botu Başlatın:**  
   Botu aratıp `/start` komutunu göndererek başlatın.

2. **Video Linkini Gönderin:**  
   Naofumi’ye bir YouTube veya Instagram video linki gönderin.

3. **Format ve Kalite Seçimi:**  
   Bot, gönderdiğiniz linke göre uygun format (MP3/MP4) seçeneklerini sunar.  
   - **Butonlar:** İlgili emojili butonlardan istediğiniz format ve kaliteyi seçin.

4. **İşlem Süreci:**  
   Video, seçiminize göre indirilir, gerekiyorsa dönüştürülür ve size gönderilir.  
   İlerleme mesajlarında, indirme ve dönüştürme durumunu anlık olarak görebilirsiniz.

---

## 📋 Gereksinimler

- **Python 3.7** veya üzeri
- Sisteminizde yüklü olan **FFmpeg**
- **Pillow**, **pyrogram**, **yt-dlp**, **moviepy** ve tercihe bağlı olarak **tqdm** kütüphaneleri

---

## 📦 Bağımlılıklar

- [`pyrogram`](https://github.com/pyrogram/pyrogram): Telegram MTProto API İstemcisi  
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp): YouTube ve diğer sitelerden video indirme aracıdır  
- [`moviepy`](https://zulko.github.io/moviepy/): Video düzenleme ve dönüştürme için Python modülü  
- [`Pillow`](https://python-pillow.org/): Görüntü işleme için kütüphane  
- [`tqdm`](https://github.com/tqdm/tqdm): İlerleme çubuğu göstergesi (opsiyonel)

---

## 📄 Lisans

Bu proje **MIT Lisansı** altında lisanslanmıştır.

---

## ❓ Telegram Botu Oluşturma ve API Bilgileri Alma

### 1. Telegram Botu Oluşturma

1. **Telegram’ı açın** ve [@BotFather](https://t.me/botfather) ile sohbet başlatın.  
2. `/start` komutunu gönderin.  
3. `/newbot` komutunu gönderin.  
4. Botunuza **Naofumi** adını ve uygun bir kullanıcı adı verin.  
5. BotFather, size bir API Token verecek. Bu token’ı not edin; botunuzu çalıştırırken ihtiyacınız olacak.

### 2. Telegram API ID ve API Hash Alma

1. **[Telegram Developer Platformu](https://my.telegram.org/auth)** adresine gidin.  
2. **Telegram hesabınızla** giriş yapın.  
3. **API Development Tools** bölümüne gidin ve **Create new application** seçeneğini tıklayın.  
4. Uygulamanız için bir **isim** ve **kısa açıklama** girin.  
5. **Create application** butonuna tıklayın.  
6. API ID ve API Hash bilgilerinizi göreceksiniz; bunları not edin.

---

Bu adımları takip ederek **Naofumi** botunuzu başarıyla oluşturabilir ve yapılandırabilirsiniz. Daha fazla bilgi ve yardım için [Telegram Bot API Dokümantasyonu](https://core.telegram.org/bots/api) ve ilgili Python kütüphane dokümantasyonlarına göz atabilirsiniz.

---

Naofumi ile keyifli video indirme ve dönüştürme işlemlerinin tadını çıkarın! 🎥🚀