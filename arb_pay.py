"""
Anchor de trails on-chain via GiskardPayments.markUsed(action_ref).

Usa action_ref (SHA-256 hex, 32 bytes) como payload bytes32 —
ancla el trail en Arbitrum One con timestamp inmutable.

USE_SIGNER=0  (default): firma con OWNER_PRIVATE_KEY directo.
USE_SIGNER=1: firma via giskard-signer socket (para entornos con vault).
"""
import os
from web3 import Web3

ARBITRUM_RPC     = os.getenv("ARBITRUM_RPC", "https://arb1.arbitrum.io/rpc")
CONTRACT_ADDRESS = os.getenv("GISKARD_CONTRACT_ADDRESS", "0xe40E376cD32b03E3084F9E0d646155D0Ba0A63ae")
USE_SIGNER       = os.getenv("USE_SIGNER", "0") == "1"
SIGNER_WALLET_ID = os.getenv("SIGNER_WALLET_ID", "owner")
SIGNER_CHAIN_ID  = int(os.getenv("SIGNER_CHAIN_ID", "42161"))

ABI = [
    {
        "inputs": [{"name": "paymentId", "type": "bytes32"}],
        "name": "markUsed", "outputs": [],
        "stateMutability": "nonpayable", "type": "function",
    },
    {
        "inputs": [{"name": "paymentId", "type": "bytes32"}],
        "name": "isUsed", "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "view", "type": "function",
    },
]

_w3            = None
_contract      = None
_owner         = None
_owner_addr    = None
_signer_client = None


def _setup():
    global _w3, _contract, _owner, _owner_addr, _signer_client
    if _w3 is not None:
        return
    _w3 = Web3(Web3.HTTPProvider(ARBITRUM_RPC))
    _contract = _w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=ABI,
    )
    key = os.getenv("OWNER_PRIVATE_KEY", "")
    if USE_SIGNER:
        import sys
        signer_path = "/home/dell7568/giskard-signer"
        if signer_path not in sys.path:
            sys.path.insert(0, signer_path)
        from signer.client import SignerClient
        _signer_client = SignerClient.from_env()
        _owner_addr = _signer_client.get_address(SIGNER_WALLET_ID)
    elif key:
        _owner = _w3.eth.account.from_key(key)
        _owner_addr = _owner.address


def anchor_action_ref(action_ref_hex: str) -> str | None:
    """Ancla action_ref en Arbitrum One via markUsed. Retorna tx_hash o None si falla.

    action_ref_hex: SHA-256 hex string de 64 chars (32 bytes).
    El tx_hash resultante es la prueba on-chain inmutable del trail.
    """
    _setup()
    if not _owner_addr:
        return None
    try:
        payload = bytes.fromhex(action_ref_hex)
        if len(payload) != 32:
            return None
        tx = _contract.functions.markUsed(payload).build_transaction({
            "from":  _owner_addr,
            "nonce": _w3.eth.get_transaction_count(_owner_addr),
            "gas":   120_000,
        })
        if USE_SIGNER:
            if "gasPrice" not in tx and "maxFeePerGas" not in tx:
                tx["gasPrice"] = _w3.eth.gas_price
            tx.setdefault("chainId", SIGNER_CHAIN_ID)
            raw = _signer_client.sign_transaction(SIGNER_WALLET_ID, tx)["raw_transaction"]
            if not raw.startswith("0x"):
                raw = "0x" + raw
            tx_hash = _w3.eth.send_raw_transaction(bytes.fromhex(raw[2:]))
        else:
            signed = _w3.eth.account.sign_transaction(tx, os.getenv("OWNER_PRIVATE_KEY", ""))
            tx_hash = _w3.eth.send_raw_transaction(signed.raw_transaction)
        return tx_hash.hex() if isinstance(tx_hash, bytes) else str(tx_hash)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error("anchor_action_ref failed: %s", exc)
        return None
