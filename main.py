import requests

url =  "https://blockstream.info/api/block-height/900000"

response = requests.get(url)

print(response.text)