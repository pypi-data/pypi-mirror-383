Create a New Wallet and API Key
You can programmatically create new Lightning wallets and linked api keys by sending a GET request to:

https://pumpportal.fun/api/create-wallet

Examples
Python

import requests

response = requests.get(url="https://pumpportal.fun/api/create-wallet")

# JSON with keys for a newly generated wallet and the linked API key
data = response.json()

Example response:

{
    "apiKey": "f99ppca5b5qk0eaqe9anccunb962pku1b1wkct1bed55ewhk95w5akkjcn878rvgb5832rk6agtp6vkuednmwmu46xvqewvu8thk0p9pdrrqcta591170tunf5wkawva9htmucuba4ykudmqm4yk9e176rau5ct46gh3ff86d35ekau613murk4ctjp2uk18dum6rhbdt8kuf8",
    "walletPublicKey": "944j4DPvHh1UtrkPUzcpqoLrTXmkierWX2tMh22sJTYy",
    "privateKey": "3XFhWeQhPYqTsiZFLZ9G26qSYqyKaGK5AfqPyf52uKQdUJRxUxLB33Bs86QRUHRZXXoKHpp6pKkid7R2QbPPQcz1"
}
