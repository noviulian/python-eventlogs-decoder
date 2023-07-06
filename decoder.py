import eth_abi
from web3 import Web3
import json

abi = [
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "string",
                "name": "ipfs_hash",
                "type": "string",
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "token_id",
                "type": "uint256",
            },
        ],
        "name": "URI",
        "type": "event",
    },
]

webhook_data = {
    "confirmed": True,
    "chainId": "0x1",
    "abi": [
        {
            "anonymous": False,
            "inputs": [
                {
                    "indexed": False,
                    "internalType": "string",
                    "name": "ipfs_hash",
                    "type": "string",
                },
                {
                    "indexed": True,
                    "internalType": "uint256",
                    "name": "token_id",
                    "type": "uint256",
                },
            ],
            "name": "URI",
            "type": "event",
        },
    ],
    "streamId": "b4dbc80e-8161-43d8-9c5a-05a8a4bba988",
    "tag": "URI-listener",
    "retries": 0,
    "block": {
        "number": "15933519",
        "hash": "0x192357541e97093ebdf99b4a04e7e33726b6eb01f88f7ab3df3ab2dc5242147c",
        "timestamp": "1668009611",
    },
    "logs": [
        {
            "logIndex": "475",
            "transactionHash": "0x55125fa34ce16c295c222d48fc3efe210864dc2fb017f5965b4e3743d72342d5",
            "address": "0x495f947276749ce646f68ac8c248420045cb7b5e",
            "data": "0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000042697066733a2f2f6261666b726569687366326568636c78796d793467366836697163627361346c6961637a6f716b7373666b6e70787535796a356f67696a6f667175000000000000000000000000000000000000000000000000000000000000",
            "topic0": "0x6bb7ff708619ba0610cba295a58592e0451dee2622938c8755667688daf3529b",
            "topic1": "0xab6953e647a36018fc48d6223583597b84c755a0000000000000010000000001",
            "topic2": None,
            "topic3": None,
        }
    ],
    "txs": [],
    "txsInternal": [],
    "erc20Transfers": [],
    "erc20Approvals": [],
    "nftApprovals": {"ERC1155": [], "ERC721": []},
    "nftTransfers": [],
}


def check_abi_matches_log(abi, log):
    # Get the event name from the ABI
    abi_event_name = abi[0]["name"]

    # Generate the signature hash for the event
    event_signature = (
        abi_event_name + "(" + ",".join(i["type"] for i in abi[0]["inputs"]) + ")"
    )
    event_signature_hash = Web3.keccak(text=event_signature).hex()

    # Check if the event signature hash matches the topic0 in the log
    if event_signature_hash != log["topic0"]:
        return False

    # Check if the number of inputs in the ABI matches the length of the data in the log
    num_inputs = len(abi[0]["inputs"])
    num_data_items = len(
        eth_abi.decode(
            [i["type"] for i in abi[0]["inputs"]], bytes.fromhex(log["data"][2:])
        )
    )
    if num_inputs != num_data_items:
        return False

    return True


def decode_webhook_data(abi, webhook_data):
    # Check if the logs are empty
    if not webhook_data["logs"]:
        return None

    # Check if the abi is empty
    if not abi:
        return None

    # Check if the abi matches the log
    if not check_abi_matches_log(abi, webhook_data["logs"][0]):
        return None

    # Get the log data
    log = webhook_data["logs"][0]

    # ABI for the event
    event_abi = abi[0]

    # Get the data types and names from the abi
    types = [i["type"] for i in event_abi["inputs"]]
    names = [i["name"] for i in event_abi["inputs"]]

    # Get the data from the log
    data = log["data"]

    # Skip '0x' at the beginning of the data
    bb = bytes.fromhex(data[2:])

    # Decode the values
    values = eth_abi.decode(types, bb)

    # Zip together the names and values
    result = dict(zip(names, values))

    return result


decoded_logs = decode_webhook_data(abi, webhook_data)

print(json.dumps(decoded_logs, indent=4))

# Output:
# {
#     "ipfs_hash": "ipfs://bafkreihsf2ehclxymy4g6h6iqcbsa4liaczoqkssfknpxu5yj5ogijofqu",
#     "token_id": 66,
# }
