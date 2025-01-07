import logging
import os
import requests
from flask import Flask, render_template, request, send_file
import instaloader
from io import BytesIO

# Instagram video ve fotoğraf indirmek için instaloader
loader = instaloader.Instaloader()

# Flask uygulaması
app = Flask(__name__)

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Tekil medya indirme fonksiyonu
def download_instagram_media(url):
    try:
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        if post.is_video:
            media_url = post.video_url
            response = requests.get(media_url)
            if response.status_code == 200:
                video_file = BytesIO(response.content)
                video_file.name = "video.mp4"
                return "video", video_file
        else:
            media_url = post.url
            response = requests.get(media_url)
            if response.status_code == 200:
                image_file = BytesIO(response.content)
                image_file.name = "photo.jpg"
                return "photo", image_file

    except Exception as e:
        logger.error(f"Medya indirilirken hata oluştu: {e}")
        return None, None

# Albümdeki tüm medya öğelerini indirme fonksiyonu
def download_instagram_album(url):
    try:
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        media_files = []
        for node in post.get_sidecar_nodes():
            if node.is_video:
                media_files.append({"type": "video", "url": node.video_url})
            else:
                media_files.append({"type": "photo", "url": node.display_url})

        return media_files

    except Exception as e:
        logger.error(f"Albüm indirilirken hata oluştu: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if url and 'instagram.com' in url:
        if '/p/' in url:  # Tek gönderi veya albüm URL'si
            try:
                album_media = download_instagram_album(url)

                if album_media:
                    # Albüm modalında göstermek için medya URL'lerini gönder
                    return render_template('index.html', album_media=album_media)
                else:
                    return render_template('index.html', error="Medya indirilemedi, doğru linki gönderdiğinizden emin olun.")
            except Exception as e:
                logger.error(f"Hata: {e}")
                return render_template('index.html', error="Beklenmeyen bir hata oluştu.")
        else:
            return render_template('index.html', error="Lütfen geçerli bir Instagram gönderi linki girin.")
    else:
        return render_template('index.html', error="Lütfen geçerli bir Instagram linki girin.")

if __name__ == '__main__':
    app.run(debug=True)
