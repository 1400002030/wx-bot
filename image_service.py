import time

import requests
from PIL import Image

t = time.time()
for i in range(10):
    print(i)
    pos = {"x": 0, "y": 24.018691588785043, "width": 100, "height": 51.96261682242992}
    poster = "https://leuan.top/files/2023/05/05/poster17696177997926719647.png"
    resp = requests.get(poster, stream=True).raw
    qr = requests.get("https://leuan.top/files/2023/05/09/831599a7-03bb-4981-bc62-e83c5d43340d1438630822518088301.jpg",
                      stream=True).raw
    img = Image.open(resp)
    img.save('./img.png')
    img_size = img.size
    w = int(img_size[0] * pos['width'] / 100)
    h = int(img_size[1] * pos['height'] / 100)
    x = int(img_size[0] * pos['x'] / 100)
    y = int(img_size[1] * pos['y'] / 100)
    qr = Image.open(qr)
    qr = qr.resize((w, h))
    img.paste(qr, (x, y))
    img.save('./test.png')
print(f'处理:{time.time() - t} {(time.time() - t)/10}')
