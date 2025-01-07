import logging
import os
import requests
from flask import Flask, render_template, request, send_file
import instaloader
from io import BytesIO

# Instagram için instaloader
loader = instaloader.Instaloader()

# Flask uygulaması
app = Flask(__name__)

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Instagram medya indirme fonksiyonu
def get_instagram_media_urls(url):
    try:
        # URL üzerinden shortcode çıkarıyoruz
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        # Çoklu resim veya video kontrolü
        media_urls = []
        if post.typename == 'GraphSidecar':  # Birden fazla medya içeriyor
            for node in post.get_sidecar_nodes():
                media_urls.append(node['display_url'] if not node['is_video'] else node['video_url'])
        else:
            media_urls.append(post.url if not post.is_video else post.video_url)

        return media_urls
    except Exception as e:
        logger.error(f"Medya URL'leri alınırken hata oluştu: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/media-preview', methods=['POST'])
def media_preview():
    url = request.form.get('url')
    if url and 'instagram.com' in url:
        media_urls = get_instagram_media_urls(url)
        if media_urls:
            return render_template('preview.html', media_urls=media_urls)
        else:
            return render_template('index.html', error="Medya alınamadı, doğru linki gönderdiğinizden emin olun.")
    else:
        return render_template('index.html', error="Lütfen geçerli bir Instagram linki girin.")

@app.route('/download', methods=['POST'])
def download():
    media_url = request.form.get('media_url')
    if media_url:
        try:
            response = requests.get(media_url)
            if response.status_code == 200:
                file_extension = 'mp4' if 'video' in media_url else 'jpg'
                file_name = f"media.{file_extension}"
                media_file = BytesIO(response.content)
                media_file.name = file_name
                mimetype = 'video/mp4' if file_extension == 'mp4' else 'image/jpeg'
                return send_file(media_file, as_attachment=True, download_name=file_name, mimetype=mimetype)
        except Exception as e:
            logger.error(f"Medya indirilirken hata oluştu: {e}")
            return render_template('index.html', error="Medya indirilemedi.")
    else:
        return render_template('index.html', error="Geçerli bir medya URL'si gönderilmedi.")

if __name__ == '__main__':
    app.run(debug=True)
