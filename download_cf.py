import urllib.request
import ssl
import os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe'
dest = r'C:\tools\cloudflared.exe'

os.makedirs(r'C:\tools', exist_ok=True)

try:
    urllib.request.urlretrieve(url, dest)
    print(f'Downloaded: {os.path.getsize(dest)} bytes')
except Exception as e:
    print(f'Error: {e}')
