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

# Instagram video veya fotoğraf indirme fonksiyonu
def download_instagram_media(url):
    try:
        # URL üzerinden medya (fotoğraf, video) indirme
        shortcode = url.split("/")[-2]  # URL'den shortcode'u alıyoruz
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        # Medya tipi fotoğraf mı, video mu?
        if post.is_video:
            media_url = post.video_url
            # Video indir
            response = requests.get(media_url)
            if response.status_code == 200:
                video_file = BytesIO(response.content)  # Geçici video dosyasını bellek üzerinde oluşturuyoruz
                video_file.name = "video.mp4"  # Dosya adını belirtiyoruz
                return "video", video_file
        else:
            media_url = post.url
            # Fotoğraf indir
            response = requests.get(media_url)
            if response.status_code == 200:
                image_file = BytesIO(response.content)  # Geçici fotoğraf dosyasını bellek üzerinde oluşturuyoruz
                image_file.name = "photo.jpg"  # Dosya adını belirtiyoruz
                return "photo", image_file

    except Exception as e:
        logger.error(f"Medya indirilirken hata oluştu: {e}")
        return None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if url and 'instagram.com' in url:
        media_type, media_file, media_filename = download_instagram_media(url)  # media_filename ekleniyor

        if media_type == "photo":
            # Fotoğrafı indir
            return send_file(media_file, as_attachment=True, download_name=media_filename, mimetype='image/jpeg')
        elif media_type == "video":
            # Video'yu indir
            return send_file(media_file, as_attachment=True, download_name=media_filename, mimetype='video/mp4')
        else:
            return render_template('index.html', error="Medya indirilemedi, doğru linki gönderdiğinizden emin olun.")
    else:
        return render_template('index.html', error="Lütfen geçerli bir Instagram linki girin.")

if __name__ == '__main__':
    app.run(debug=True)
