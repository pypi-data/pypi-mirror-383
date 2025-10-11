Claiming Token Creator Fees

Pump.fun rewards token creators by allowing them to collect a fraction of the fees generated from trading activity on their token. You can use the PumpPortal Lightning or Local Transaction APIs to claim any creator fees from Pump.fun. The Lightning Transaction API can now also be used to claim creator fees from Meteora Dynamic Bonding Curves.

Examples below:

Lightning Transaction Examples:
Python


import requests

response = requests.post(url="https://pumpportal.fun/api/trade?api-key=your-api-key-here", data={
    "action": "collectCreatorFee",
    "priorityFee": 0.000001,
    "pool": "meteora-dbc" # "pump" or "meteora-dbc"
    "mint": "token CA" # the token for which you are claiming fees
    # Note: pump.fun claims creator fees all at once, so you do not need to specify "mint"
})

data = response.json()           # Tx signature or error(s)
