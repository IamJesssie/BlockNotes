"""
Cardano blockchain utilities for BlockNotes
Handles transaction building, Blockfrost API integration, and transaction verification
"""
import hashlib
import logging
import requests
from typing import Optional, Dict, Any
from django.conf import settings

try:
    from pycardano import Network
    from pycardano.backends.blockfrost import BlockfrostChainContext
    from blockfrost import BlockFrostApi, ApiUrls
    CARDANO_AVAILABLE = True
except ImportError:
    CARDANO_AVAILABLE = False
    logging.warning("Cardano libraries not available. Install pycardano and blockfrost-python.")

logger = logging.getLogger(__name__)


def get_network():
    """Get Cardano network based on settings"""
    if not CARDANO_AVAILABLE:
        return None
    network_map = {
        'mainnet': Network.MAINNET,
        'preview': Network.TESTNET,
        'preprod': Network.TESTNET,
    }
    return network_map.get(settings.CARDANO_NETWORK, Network.TESTNET)


def get_blockfrost_context():
    """Initialize Blockfrost chain context"""
    if not CARDANO_AVAILABLE:
        return None
    try:
        network = get_network()
        if network is None:
            return None
        context = BlockfrostChainContext(
            project_id=settings.BLOCKFROST_PROJECT_ID,
            network=network,
        )
        return context
    except Exception as e:
        logger.error(f"Failed to initialize Blockfrost context: {e}")
        return None


def get_blockfrost_api():
    """Get Blockfrost API client"""
    if not CARDANO_AVAILABLE:
        return None
    try:
        api_url = ApiUrls.preview.value if settings.CARDANO_NETWORK == 'preview' else ApiUrls.mainnet.value
        return BlockFrostApi(
            project_id=settings.BLOCKFROST_PROJECT_ID,
            base_url=api_url
        )
    except Exception as e:
        logger.error(f"Failed to initialize Blockfrost API: {e}")
        return None


def create_note_hash(note_id: int, title: str, content: str, operation: str = 'CREATE') -> str:
    """
    Create a SHA-256 hash of note data for blockchain storage
    
    Args:
        note_id: Note database ID
        title: Note title
        content: Note content
        operation: Operation type (CREATE, UPDATE, DELETE)
    
    Returns:
        Hex string of the hash
    """
    note_string = f"{operation}:{note_id}:{title}:{content}"
    return hashlib.sha256(note_string.encode('utf-8')).hexdigest()


def build_transaction_data(note_id: int, title: str, content: str, operation: str, 
                           from_address: str, to_address: str) -> Dict[str, Any]:
    """
    Build transaction data structure that will be used by the frontend wallet
    to construct and sign the transaction.
    
    This returns metadata that will be embedded in the transaction metadata.
    """
    note_hash = create_note_hash(note_id, title, content, operation)
    
    return {
        'operation': operation,
        'note_id': note_id,
        'note_hash': note_hash,
        'title': title[:100],  # Limit title length
        'content_length': len(content),
        'from_address': from_address,
        'to_address': to_address,
    }


def verify_transaction_via_blockfrost(tx_hash: str) -> Optional[Dict[str, Any]]:
    """
    Verify a transaction using Blockfrost API
    
    Args:
        tx_hash: Transaction hash (hex string)
    
    Returns:
        Dictionary with transaction details or None if not found
    """
    if not CARDANO_AVAILABLE:
        return None
    try:
        api = get_blockfrost_api()
        if api is None:
            return None
        tx = api.transaction(tx_hash)
        tx_utxos = api.transaction_utxos(tx_hash)
        
        # Extract metadata if present
        metadata = {}
        if hasattr(tx, 'metadata') and tx.metadata:
            metadata = tx.metadata
        
        return {
            'tx_hash': tx_hash,
            'block_height': tx.block_height if hasattr(tx, 'block_height') else None,
            'block_time': tx.block_time if hasattr(tx, 'block_time') else None,
            'slot': tx.slot if hasattr(tx, 'slot') else None,
            'fees': tx.fees if hasattr(tx, 'fees') else '0',
            'metadata': metadata,
            'utxos': tx_utxos if tx_utxos else [],
            'status': 'confirmed' if tx.block_height else 'pending',
        }
    except Exception as e:
        logger.error(f"Error verifying transaction {tx_hash} via Blockfrost: {e}")
        return None


def check_blockchain_connection() -> bool:
    """
    Check if Blockfrost API is accessible
    
    Returns:
        True if connection is successful, False otherwise
    """
    if not CARDANO_AVAILABLE:
        return False
    try:
        api = get_blockfrost_api()
        if api is None:
            return False
        # Try to get network info
        health = api.health()
        return health is not None
    except Exception as e:
        logger.debug(f"Blockfrost connection check failed: {e}")
        return False


def get_transaction_metadata(tx_hash: str) -> Optional[Dict[str, Any]]:
    """
    Get transaction metadata from Blockfrost
    
    Args:
        tx_hash: Transaction hash
    
    Returns:
        Metadata dictionary or None
    """
    if not CARDANO_AVAILABLE:
        return None
    try:
        api = get_blockfrost_api()
        if api is None:
            return None
        tx = api.transaction(tx_hash)
        if hasattr(tx, 'metadata') and tx.metadata:
            return tx.metadata
        return {}
    except Exception as e:
        logger.error(f"Error getting transaction metadata: {e}")
        return None

