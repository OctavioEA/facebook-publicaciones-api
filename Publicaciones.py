import requests
import time
from flask import Flask, jsonify
import os

# ---- Tu código original, sin cambios ----
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', 'EAAIV3ZATsf2gBO7IG4dnB3bZAzBcdvjZCHLI8sLveBGnU9D6gjO2owBfvMFUoqibZCZAN1fFYqYMkB3xne5pfK2AWeug0AhRMVZCt69HzU4jMUdaT1rP6sKTF6GmAVXDhZAyG9O0Hdccs1YpVXARIBAGKNAZC8MzIn45HVEyU3ryFcqN8fjrge9ZCD8FpgUzHpxfqQQyzIVLC6D1ZCai6IvmFfo2ZCfovnGl1bLv2D2PK5pJXDGS0xggCWzfdoZD')
PAGE_ID     = '113770254142463'
API_VERSION = 'v22.0'
BASE_URL    = f'https://graph.facebook.com/{API_VERSION}'

def fetch_all(url, params):
    items = []
    while url:
        r = requests.get(url, params=params)
        r.raise_for_status()
        j = r.json()
        items.extend(j.get('data', []))
        url = j.get('paging', {}).get('next')
        params = None
        time.sleep(0.2)
    return items

def check_token_info():
    print("🔎 Verificando información del access token...")
    url = f"{BASE_URL}/me"
    params = {
        'fields': 'id,name,email',
        'access_token': ACCESS_TOKEN
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        print(f"✔️ Token válido. Info: {data}")
    else:
        print(f"⚠️ Error al verificar token: {r.status_code} - {r.text}")

def main_logic():
    # Renombré main() a main_logic() para poder exponer main() y el endpoint
    print("🔍 Obteniendo todas las publicaciones...")
    posts = fetch_all(f"{BASE_URL}/{PAGE_ID}/feed", {
        'access_token': ACCESS_TOKEN,
        'limit': 100,
        'fields': 'id,created_time,message,story'
    })
    output = []
    for i, post in enumerate(posts, start=1):
        pid = post['id']
        date = post.get('created_time', '–')
        text = post.get('message') or post.get('story') or '–'
        # Comentarios
        comments = fetch_all(f"{BASE_URL}/{pid}/comments", {
            'access_token': ACCESS_TOKEN,
            'limit': 100,
            'fields': 'from{name},message,created_time'
        })
        comments_list = [
            {
                "name": c.get('from', {}).get('name', 'Usuario desconocido'),
                "id":   c.get('from', {}).get('id', ''),
                "message": c.get('message', ''),
                "time":    c.get('created_time', '')
            }
            for c in comments
        ]
        # Reacciones
        reactions = fetch_all(f"{BASE_URL}/{pid}/reactions", {
            'access_token': ACCESS_TOKEN,
            'limit': 100,
            'fields': 'name,type'
        })
        reactions_list = [
            {
                "name": rxt.get('name', 'Usuario desconocido'),
                "type": rxt.get('type', '')
            }
            for rxt in reactions
        ]
        output.append({
            "post_id": pid,
            "created_time": date,
            "text": text,
            "comments": comments_list,
            "reactions": reactions_list
        })
    return output

# ---- Fin de tu código original ----

# ---- Código nuevo para Flask ----
app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 Servicio 'Publicaciones' en línea"

@app.route('/datos-facebook')
def datos_facebook():
    # Opcional: check_token_info() para depuración en logs
    check_token_info()
    data = main_logic()
    return jsonify(data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
