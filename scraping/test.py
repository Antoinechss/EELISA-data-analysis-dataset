import requests

url = "https://www.yenibiris.com/is-ilanlari?q=engineer&sayfa=1"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9,tr;q=0.8"
}

r = requests.get(url, headers=headers)
print("STATUS:", r.status_code)
print(r.text[:5000])
