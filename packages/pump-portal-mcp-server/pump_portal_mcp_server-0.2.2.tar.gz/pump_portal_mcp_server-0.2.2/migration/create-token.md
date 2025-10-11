Pump.fun Token Creation
You can create tokens via the pump.fun API.

There is no additional fee for token creation. The standard trading fee is applied to the initial dev buy.

Examples below:

Python

import requests
import json
from solders.keypair import Keypair

def send_create_tx():
    # Generate a random keypair for token
    mint_keypair = Keypair()

    # Define token metadata
    form_data = {
        'name': 'PPTest',
        'symbol': 'TEST',
        'description': 'This is an example token created via PumpPortal.fun',
        'twitter': 'https://x.com/a1lon9/status/1812970586420994083',
        'telegram': 'https://x.com/a1lon9/status/1812970586420994083',
        'website': 'https://pumpportal.fun',
        'showName': 'true'
    }

    # Read the image file
    with open('./example.png', 'rb') as f:
        file_content = f.read()

    files = {
        'file': ('example.png', file_content, 'image/png')
    }

    # Create IPFS metadata storage
    metadata_response = requests.post("https://pump.fun/api/ipfs", data=form_data, files=files)
    metadata_response_json = metadata_response.json()

    # Token metadata
    token_metadata = {
        'name': form_data['name'],
        'symbol': form_data['symbol'],
        'uri': metadata_response_json['metadataUri']
    }

    # Send the create transaction
    response = requests.post(
        "https://pumpportal.fun/api/trade?api-key=your-api-key",
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            'action': 'create',
            'tokenMetadata': token_metadata,
            'mint': str(mint_keypair),
            'denominatedInSol': 'true',
            'amount': 1, # Dev buy of 1 SOL
            'slippage': 10,
            'priorityFee': 0.0005,
            'pool': 'pump'
        })
    )

    if response.status_code == 200:  # successfully generated transaction
        data = response.json()
        print(f"Transaction: https://solscan.io/tx/{data['signature']}")
    else:
        print(response.reason)  # log error

send_create_tx()
