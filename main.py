import requests
import os
import re
import time
import threading
from queue import Queue

# Font css remote url
url = 'https://fonts.googleapis.com/css2?family=Liu+Jian+Mao+Cao&display=swap'

# Download location
local_path = './fonts/LiuJianMaoCao'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

while True:
    try:
        response = requests.get(url, headers=headers)
        break
    except Exception as e:
        print(f"An error occurred while sending the 'GET' request: {e}. Trying again in 5 seconds.")
        time.sleep(5)

if not os.path.exists(local_path):
    os.makedirs(local_path)

with open(local_path + '/index.css', 'wb') as file:
    file.write(response.content)

if not os.path.exists(local_path + '/fonts'):
    os.makedirs(local_path + '/fonts')

download_queue = Queue()


class FontDownloaderThread(threading.Thread):
    def run(self):
        while True:
            font_url = download_queue.get()
            while True:
                try:
                    font_resp = requests.get(font_url, headers=headers)
                    font_file_path = os.path.join(local_path + '/fonts', os.path.basename(font_url))
                    with open(font_file_path, 'wb') as font_file:
                        font_file.write(font_resp.content)
                    download_queue.task_done()
                    break
                except Exception as e:
                    print(f"An error occurred while downloading the file: {e}. Trying again in 5 seconds.")
                    time.sleep(5)


for _ in range(20):
    downloader = FontDownloaderThread()
    downloader.daemon = True
    downloader.start()

with open(local_path + '/index.css', 'r') as file:
    css_text = file.read()

font_urls = re.findall(r'url\((.+?)\)', css_text)
for font_url in font_urls:
    download_queue.put(font_url)

download_queue.join()

# New code to replace remote URLs with local paths.
with open(local_path + '/index.css', 'r+') as file:
    css_text = file.read()
    for font_url in font_urls:
        local_font_path = os.path.join('./fonts', os.path.basename(font_url)).replace("\\", "/")
        css_text = css_text.replace(font_url, local_font_path)

    file.seek(0)
    file.write(css_text)
    file.truncate()
