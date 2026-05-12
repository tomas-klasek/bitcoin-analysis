import requests

block_height = 900000

url =  "https://blockstream.info/api/block-height/" + str(block_height)

block_hash = requests.get(url).text.strip()

hash_url = "https://blockstream.info/api/block/" + block_hash

block_json = requests.get(hash_url)

print(block_json.json())