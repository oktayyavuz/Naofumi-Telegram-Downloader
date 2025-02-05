#!/usr/bin/env python
# -*- coding: utf-8 -*-


######################################
#        GEREKLİ KÜTÜPHANELER        #
######################################
import os
import sys
import locale
import logging
import time
import math
import signal
import asyncio
import requests

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip

try:
    from tqdm import tqdm
except ImportError:
    print("🚨 tqdm kütüphanesi bulunamadı. Lütfen 'pip install tqdm' ile yükleyin.")
    tqdm = None

try:
    from PIL import Image
except ImportError:
    print("🚨 Pillow kütüphanesi bulunamadı. Lütfen 'pip install Pillow' ile yükleyin.")
    sys.exit(1)

# UTF-8 çıktı ayarı 📝
sys.stdout.reconfigure(encoding='utf-8')

######################################
#            LOG AYARLARI            #
######################################
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

######################################
#       BOT VE GENEL AYARLAR         #
######################################
# Readme Dosyasında Bahsedilen bilgilerle doldurunuz.
api_id = 0000000
api_hash = ''
bot_token = ''

MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
CHUNK_SIZE = int(1.5 * 1024 * 1024 * 1024)  # 1.5GB

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

######################################
#          FONKSİYONLAR             #
######################################
async def send_file(client, chat_id, video_file, video_title, waiting_message, thumbnail_file=None):
    """
    📤 İndirilen video dosyasını Telegram üzerinden gönderir.
    ⏱️ Video süresi, çözünürlük vb. bilgileri otomatik tespit edilir.
    """
    try:
        start_time = time.time()
        last_update_time = start_time

        with VideoFileClip(video_file) as video:
            duration = int(video.duration)
            width = int(video.size[0])
            height = int(video.size[1])

        async def progress_callback(current, total):
            nonlocal last_update_time
            elapsed_time = time.time() - start_time
            percent_complete = current / total * 100
            eta = (total - current) / (current / elapsed_time) if current > 0 else 0

            if time.time() - last_update_time >= 5:
                try:
                    await waiting_message.edit_text(
                        f"🔄 Yükleniyor: {percent_complete:.2f}% tamamlandı\n"
                        f"⏱️ Geçen Süre: {int(elapsed_time)} saniye\n"
                        f"📅 Tahmini Süre: {int(eta)} saniye"
                    )
                    last_update_time = time.time()
                except Exception as e:
                    logger.error(f"İlerleme mesajı güncellenirken hata: {e}")

        await client.send_video(
            chat_id=chat_id,
            video=video_file,
            caption=video_title,
            duration=duration,
            width=width,
            height=height,
            thumb=thumbnail_file,
            supports_streaming=True,
            progress=progress_callback
        )
        
        await waiting_message.edit_text("✅ Video başarıyla gönderildi!")
        await waiting_message.delete()
    except Exception as e:
        await waiting_message.edit_text(f"❌ Video gönderilemedi: {e}")
    finally:
        if os.path.exists(video_file):
            os.remove(video_file)
        if thumbnail_file and os.path.exists(thumbnail_file):
            os.remove(thumbnail_file)

async def split_and_send_video(client, chat_id, video_file, video_title, callback_query, thumbnail_file=None):
    """
    🎬 Büyük dosyaları parçalara ayırarak gönderir.
    """
    try:
        with VideoFileClip(video_file) as video:
            duration = video.duration
            total_parts = math.ceil(os.path.getsize(video_file) / CHUNK_SIZE)
            segment_duration = duration / total_parts

            for part in range(total_parts):
                progress_message = await callback_query.message.reply_text(
                    f"📤 {part + 1}/{total_parts}. parça hazırlanıyor..."
                )

                start_time_part = part * segment_duration
                end_time_part = min((part + 1) * segment_duration, duration)
                part_file = f"{video_file}_part{part + 1}.mp4"
                
                segment = video.subclip(start_time_part, end_time_part)
                segment.write_videofile(
                    part_file,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True,
                    write_logfile=False
                )
                
                await send_file(
                    client,
                    chat_id,
                    part_file,
                    f"{video_title} - Parça {part + 1}/{total_parts}",
                    progress_message,
                    thumbnail_file
                )
    except Exception as e:
        await callback_query.message.reply_text(f"❌ Video parçalara ayrılırken hata oluştu: {e}")
    finally:
        if os.path.exists(video_file):
            os.remove(video_file)
        if thumbnail_file and os.path.exists(thumbnail_file):
            os.remove(thumbnail_file)

######################################
#        KOMUT VE MESAJLAR           #
######################################
@app.on_message(filters.command("start"))
async def start(client, message):
    """
    👋 /start komutu ile bot başlatıldığında karşılama mesajı gönderilir.
    """
    await message.reply_text("👋 Merhaba! YouTube veya Instagram video linkini gönderin, ben de indirip size göndereyim. 🎥📲")

@app.on_message(filters.text & ~filters.create(lambda _, __, message: message.text.startswith('/')))
async def send_format_buttons(client, message):
    """
    🔗 Kullanıcı metin mesajı gönderdiğinde URL kontrolü yapılır ve 
       uygun format seçenekleri sunulur.
    """
    url = message.text.strip()
    
    try:
        logger.info(f"Mesaj alındı: {url}")
        await message.delete()

        if "youtube.com" in url or "youtu.be" in url:
            keyboard = [
                [
                    InlineKeyboardButton("🎵 MP3", callback_data=f"mp3|{url}"),
                    InlineKeyboardButton("📺 MP4", callback_data=f"mp4|{url}")
                ]
            ]
            await message.reply_text("📁 Hangi formatta indirmek istersiniz?", 
                                     reply_markup=InlineKeyboardMarkup(keyboard))
        # Instagram linkleri için 📸
        elif "instagram.com" in url:
            ddinstagram_url = url.replace("instagram.com", "ddinstagram.com")
            markdown_link = f"[🎬 Reels]({ddinstagram_url})"
            await message.reply_text(f"İndirilecek link: {markdown_link}")
        else:
            await message.reply_text("❌ Geçersiz URL. Lütfen YouTube veya Instagram linki gönderin.")
    except Exception as e:
        logger.error(f"Mesaj işlenirken hata oluştu: {e}", exc_info=True)
        await message.reply_text(f"❌ Bir hata oluştu: {e}")

@app.on_callback_query()
async def handle_format_quality(client, callback_query):
    """
    🎛️ Callback sorgularını işleyerek, format ve kalite seçeneklerine göre 
       indirme işlemini başlatır.
    """
    data = callback_query.data.split('|')
    
    if len(data) == 2:
        format_choice, url = data
        if format_choice == "mp3":
            await send_mp3_quality_buttons(client, callback_query, url)
        elif format_choice == "mp4":
            await send_mp4_quality_buttons(client, callback_query, url)
    elif len(data) == 3:
        format_choice, quality, url = data
        await download_video(client, callback_query, format_choice, quality, url)

async def send_mp3_quality_buttons(client, callback_query, url):
    """
    🎵 MP3 için kalite seçeneklerini sunar.
    """
    keyboard = [
        [
            InlineKeyboardButton("128 kbps", callback_data=f"mp3|128|{url}"),
            InlineKeyboardButton("192 kbps", callback_data=f"mp3|192|{url}"),
            InlineKeyboardButton("256 kbps", callback_data=f"mp3|256|{url}")
        ]
    ]
    await callback_query.message.edit_text("🎵 MP3 kalitesini seçin:", 
                                             reply_markup=InlineKeyboardMarkup(keyboard))

async def send_mp4_quality_buttons(client, callback_query, url):
    """
    📺 MP4 için uygun çözünürlük seçeneklerini YouTube üzerinden alarak sunar.
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
            'retries': 5,
            'fragment_retries': 5,
            'retry_sleep_functions': {
                'http': lambda retry_count, n=None: 5,
                'fragment': lambda retry_count, n=None: 5
            }
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])

        available_resolutions = sorted(
            {fmt.get('height') for fmt in formats if fmt.get('height')},
            reverse=True
        )
        limited_resolutions = available_resolutions[:4]

        keyboard = [
            [InlineKeyboardButton(f"{res}p", callback_data=f"mp4|{res}|{url}")]
            for res in limited_resolutions
        ]
        
        await callback_query.message.edit_text("📺 MP4 kalitesini seçin:", 
                                                 reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        await callback_query.message.edit_text(f"❌ Kalite bilgisi alınamadı: {e}")

async def download_video(client, callback_query, format_choice, quality, url):
    """
    🎥 İstenen format ve kalitede videoyu indirir, gerekirse dönüştürür ve gönderir.
    """
    chat_id = callback_query.message.chat.id

    try:
        logger.info(f"Video indirme başladı: {url}")
        
        ydl_opts = {
            'socket_timeout': 30,
            'retries': 5,
            'fragment_retries': 5,
            'retry_sleep_functions': {
                'http': lambda retry_count, n=None: 5,
                'fragment': lambda retry_count, n=None: 5
            }
        }

        if format_choice == "mp3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }],
                'outtmpl': '%(title)s.%(ext)s',
                'noplaylist': True,
            })
        else:  
            ydl_opts.update({
                'format': f'bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=m4a]/best[ext=mp4][height<={quality}]',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }],
                'ffmpeg_args': ['-c:v', 'libx264', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart'],
                'outtmpl': '%(title)s.%(ext)s',
                'noplaylist': True,
                'merge_output_format': 'mp4'
            })

        await callback_query.message.edit_text("📥 Video indiriliyor, lütfen bekleyin...")
        
        start_time = time.time()
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info_dict)
            if format_choice == "mp3":
                file_name = file_name.rsplit(".", 1)[0] + ".mp3"
            
            thumbnail_url = info_dict.get('thumbnail')
            thumbnail_file = None
            if thumbnail_url:
                try:
                    thumbnail_file = f"{file_name}_thumb.jpg"
                    response = requests.get(thumbnail_url)
                    with open(thumbnail_file, 'wb') as f:
                        f.write(response.content)
                except Exception as e:
                    logger.warning(f"Thumbnail indirilemedi: {e}")
                    thumbnail_file = None

            title = f"{info_dict.get('title', 'Video')} - {url}"

            file_size = os.path.getsize(file_name)
            elapsed_time = time.time() - start_time
            await callback_query.message.edit_text(
                f"📥 Dosya indirildi. Geçen süre: {int(elapsed_time)} saniye. Gönderiliyor..."
            )

            if file_size > MAX_FILE_SIZE:
                await split_and_send_video(client, chat_id, file_name, title, callback_query, thumbnail_file)
            else:
                await send_file(client, chat_id, file_name, title, callback_query.message, thumbnail_file)

    except Exception as e:
        logger.error(f"Video indirme hatası: {e}", exc_info=True)
        await callback_query.message.edit_text(f"❌ Bir hata oluştu: {e}")

######################################
#     İLETİLEN (FORWARDED) VIDEO     #
######################################
@app.on_message(filters.forwarded & filters.video)
async def handle_forwarded_video(client, message):
    """
    🔁 İletilen video mesajlarını kontrol eder, indirir, 
       gerekiyorsa 480p'ye dönüştürür ve tekrar gönderir.
    """
    try:
        logger.info("İletilen video alındı")
        status_msg = await message.reply_text("📥 Video kontrol ediliyor...")

        file_id = message.video.file_id
        file_name = message.video.file_name or f"{file_id}.mp4"
        download_dir = "downloads"
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        download_path = os.path.join(download_dir, file_name)

        if os.path.exists(download_path):
            logger.info(f"Video zaten indirildi: {download_path}")
            await status_msg.edit_text("📥 Video zaten indirildi, işleniyor...")
        else:
            await status_msg.edit_text("📥 Video indiriliyor...")
            start_time = time.time()
            last_update_time = start_time

            async def progress(current, total):
                nonlocal last_update_time
                if total == 0:
                    return
                now = time.time()
                if now - last_update_time < 2:
                    return
                percentage = current * 100 / total
                elapsed_time = int(now - start_time)
                speed = current / elapsed_time if elapsed_time > 0 else 0
                speed_text = f"{speed / 1024 / 1024:.1f} MB/s" if speed > 0 else "Hesaplanıyor..."
                try:
                    await status_msg.edit_text(
                        f"📥 Video indiriliyor...\n"
                        f"İlerleme: {percentage:.1f}%\n"
                        f"⚡ Hız: {speed_text}\n"
                        f"⏱️ Geçen süre: {elapsed_time} saniye"
                    )
                    last_update_time = now
                except Exception as e:
                    logger.error(f"İlerleme mesajı güncellenirken hata: {e}")

            await message.download(file_name=download_path, progress=progress)
            logger.info(f"Video indirildi: {download_path}")

        await status_msg.edit_text("🔄 Video işleniyor...")

        try:
            with VideoFileClip(download_path) as clip:
                real_width = int(clip.size[0])
                real_height = int(clip.size[1])
                logger.info(f"Gerçek video boyutları: {real_width}x{real_height}")

                if real_height > 480:
                    await status_msg.edit_text("🔄 Video 480p'ye dönüştürülüyor...")
                    width_new = int((480 * real_width) / real_height)
                    resized_path = f"{download_path}_480p.mp4"

                    if tqdm:
                        with tqdm(total=clip.duration, desc="Video Dönüştürülüyor", unit="s") as pbar:
                            def callback(t):
                                pbar.update(1)
                                time.sleep(1)
                            try:
                                resized = clip.resize(
                                    height=480,
                                    resample=Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS
                                )
                                resized.write_videofile(
                                    resized_path,
                                    codec='libx264',
                                    audio_codec='aac',
                                    threads=2,
                                    audio_bitrate="192k",
                                    progress_callback=callback
                                )
                            except Exception as e:
                                logger.error(f"Video dönüştürme hatası: {e}")
                                await message.reply_text(f"❌ Video dönüştürülürken hata oluştu: {str(e)}")
                                return
                    else:
                        try:
                            resized = clip.resize(
                                height=480,
                                resample=Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS
                            )
                            resized.write_videofile(
                                resized_path,
                                codec='libx264',
                                audio_codec='aac',
                                threads=2,
                                audio_bitrate="192k"
                            )
                        except Exception as e:
                            logger.error(f"Video dönüştürme hatası: {e}")
                            await message.reply_text(f"❌ Video dönüştürülürken hata oluştu: {str(e)}")
                            return
                    os.remove(download_path)
                    await message.reply_video(
                        video=resized_path,
                        caption=f"✅ 480p'ye dönüştürüldü!\n\nOrijinal Çözünürlük: {real_width}x{real_height}",
                        duration=int(clip.duration),
                        width=width_new,
                        height=480
                    )
                    os.remove(resized_path)
                    await status_msg.delete()
                    logger.info("🎉 Video işleme tamamlandı.")
                else:
                    logger.info(f"Video zaten 480p veya daha düşük ({real_height}p).")
                    await message.forward(message.chat.id)
                    await status_msg.delete()

        except (IOError, OSError) as e:
            logger.error(f"Video dosyası hatası: {e}", exc_info=True)
            await message.reply_text(f"❌ Video dosyası işlenirken hata oluştu: {str(e)}")
        except Exception as e:
            logger.error(f"Video işleme hatası: {e}", exc_info=True)
            await message.reply_text(f"❌ Video işlenirken hata oluştu: {str(e)}")

    except Exception as e:
        logger.error(f"Genel Hata: {e}", exc_info=True)
        await message.reply_text(f"❌ Beklenmedik bir hata oluştu: {str(e)}")
    finally:
        if 'status_msg' in locals():
            try:
                await status_msg.delete()
            except Exception:
                pass

######################################
#           SIGNAL HANDLER           #
######################################
def signal_handler(sig, frame):
    """
    🔔 Kapatma sinyalleri alındığında botu düzgün şekilde sonlandırır.
    """
    print("\n🚪 Kapat komutu alındı. Bot durduruluyor...")
    if app:
        try:
            asyncio.run(app.stop())
        except Exception as e:
            print(f"❌ Durdurma sırasında hata: {e}")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        logger.info("🚀 Bot başlatılıyor...")
        app.run()
    except Exception as e:
        logger.critical(f"🚨 Bot çalıştırılırken kritik hata: {e}", exc_info=True)
        sys.exit(1)
