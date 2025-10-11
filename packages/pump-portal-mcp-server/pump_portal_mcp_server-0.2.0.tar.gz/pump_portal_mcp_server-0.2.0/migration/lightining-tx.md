Lightning Transaction API Docs
To buy or sell a Pump.fun token with the funds in your wallet, send a POST request to

https://pumpportal.fun/api/trade?api-key=your-api-key-here

Once the transaction passes a simulation check, a response is sent with the transaction signature or error(s).

PumpPortal will attempt to land your transaction using our dedicated Solana nodes, upstream SWQoS providers, and private and public Jito bundle relays.

Your request body must contain the following options:

action: "buy" or "sell"
mint: The contract address of the token you want to trade (this is the text after the '/' in the pump.fun url for the token.)
amount: The amount of SOL or tokens to trade. If selling, amount can be a percentage of tokens in your wallet (ex. amount: "100%")
denominatedInSol: "true" if amount is SOL, "false" if amount is tokens
slippage: The percent slippage allowed
priorityFee: Amount used to enhance transaction speed (may be distributed to multiple providers during processing)
pool: (optional) Currently 'pump', 'raydium', 'pump-amm', 'launchlab', 'raydium-cpmm', 'bonk', and 'auto' are supported options. Default is 'pump'.
skipPreflight : (optional) "false" to simulate the transaction before sending, "true" to skip simulation checks. Default is "true".
jitoOnly : (optional) "true" to only send the transaction through Jito. Default is "false".

Examples
Python


response = requests.post(url="https://pumpportal.fun/api/trade?api-key=your-api-key-here", data={
    "action": "buy",             # "buy" or "sell"
    "mint": "your CA here",      # contract address of the token you want to trade
    "amount": 100000,            # amount of SOL or tokens to trade
    "denominatedInSol": "false", # "true" if amount is amount of SOL, "false" if amount is number of tokens
    "slippage": 10,              # percent slippage allowed
    "priorityFee": 0.00005,        # amount used to enhance transaction speed
    "pool": "auto"               # exchange to trade on. "pump", "raydium", "pump-amm", "launchlab", "raydium-cpmm", "bonk" or "auto"
})

data = response.json()           # Tx signature or error(s)
