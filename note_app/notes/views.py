# notes/views.py
import json
import time
import logging
import binascii
import requests

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from django.db.models import Q

from .models import Note, BlockchainReceipt
from .cardano_utils import (
    create_note_hash,
    build_transaction_data,
    verify_transaction_via_blockfrost,
    check_blockchain_connection,
    get_transaction_metadata,
)

logger = logging.getLogger(__name__)

# Try to import pycardano / Blockfrost; if not available, set flags so endpoints return helpful errors.
try:
    from pycardano import (
        BlockFrostChainContext,
        TransactionBuilder,
        TransactionOutput,
        Transaction,
        TransactionBody,
        TransactionWitnessSet,
        Address,
        Value,
        Network,
        AuxiliaryData
    )
    from blockfrost import BlockFrostApi, ApiError
    PY_CARDANO_AVAILABLE = True
except Exception as e:
    logger.debug("pycardano / blockfrost imports failed: %s", e)
    BlockFrostChainContext = None
    BlockFrostApi = None
    ApiError = Exception
    PY_CARDANO_AVAILABLE = False

# -----------------------
# Utility / status view
# -----------------------
def get_blockchain_status():
    try:
        return check_blockchain_connection()
    except Exception:
        return False


def landing_page(request):
    return render(request, 'account/landing.html')


# -----------------------
# List notes
# -----------------------
def list_notes(request):
    sort_by = request.GET.get("sort", "-created_at")
    search_query = request.GET.get("q", "")

    valid_sort_fields = ["created_at", "-created_at", "title", "-title"]
    if sort_by not in valid_sort_fields:
        sort_by = "-created_at"

    notes = Note.objects.filter(is_deleted=False)
    if search_query:
        notes = notes.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
    notes = notes.order_by(sort_by)

    blockchain_status = get_blockchain_status()

    return render(request, "notes/list_notes.html", {
        "notes": notes,
        "blockchain_status": blockchain_status,
        "search_query": search_query,
        "sort_by": sort_by
    })


# -----------------------
# Create / Edit / Delete
# -----------------------
@csrf_exempt
@require_http_methods(["POST"])
def create_note_view(request):
    try:
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()

        if not title or not content:
            return JsonResponse({'success': False, 'error': 'Title and content are required'})

        note = Note.objects.create(title=title, content=content)
        note_hash = create_note_hash(note.id, title, content, 'CREATE')

        transaction_data = build_transaction_data(
            note_id=note.id,
            title=title,
            content=content,
            operation='CREATE',
            from_address=getattr(settings, "CARDANO_SENDER_ADDRESS", None),
            to_address=getattr(settings, "CARDANO_RECEIVER_ADDRESS", None)
        )

        return JsonResponse({
            'success': True,
            'note_id': note.id,
            'requires_wallet': True,
            'transaction_data': transaction_data,
            'note_hash': note_hash
        })
    except Exception as e:
        logger.exception("create_note failed")
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def edit_note(request, note_id):
    try:
        note = get_object_or_404(Note, id=note_id)
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()

        if not title or not content:
            return JsonResponse({'success': False, 'error': 'Title and content are required'})

        note.title = title
        note.content = content
        note.save()

        note_hash = create_note_hash(note.id, title, content, 'UPDATE')
        transaction_data = build_transaction_data(
            note_id=note.id,
            title=title,
            content=content,
            operation='UPDATE',
            from_address=getattr(settings, "CARDANO_SENDER_ADDRESS", None),
            to_address=getattr(settings, "CARDANO_RECEIVER_ADDRESS", None)
        )

        return JsonResponse({
            'success': True,
            'note_id': note.id,
            'note': {'title': note.title, 'content': note.content},
            'requires_wallet': True,
            'transaction_data': transaction_data,
            'note_hash': note_hash,
            'operation': 'UPDATE'
        })
    except Exception as e:
        logger.exception("edit_note failed")
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def delete_note(request, note_id):
    try:
        note = get_object_or_404(Note, id=note_id)

        note_hash = create_note_hash(note.id, note.title, note.content, 'DELETE')
        transaction_data = build_transaction_data(
            note_id=note.id,
            title=note.title,
            content=note.content,
            operation='DELETE',
            from_address=getattr(settings, "CARDANO_SENDER_ADDRESS", None),
            to_address=getattr(settings, "CARDANO_RECEIVER_ADDRESS", None)
        )

        # soft delete
        note.is_deleted = True
        note.save()

        return JsonResponse({
            'success': True,
            'note_id': note.id,
            'requires_wallet': True,
            'transaction_data': transaction_data,
            'note_hash': note_hash,
            'operation': 'DELETE'
        })
    except Exception as e:
        logger.exception("delete_note failed")
        return JsonResponse({'success': False, 'error': str(e)})


# -----------------------
# Receipt / Proof / Verify
# -----------------------
@require_http_methods(["GET"])
def verify_receipt(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    receipt = getattr(note, 'blockchain_receipt', None)
    if not receipt:
        return JsonResponse({'error': 'No receipt found for this note'}, status=404)
    try:
        tx_hash = receipt.transaction_hash
        tx_info = verify_transaction_via_blockfrost(tx_hash)
        if not tx_info:
            return JsonResponse({'error': 'Transaction not found on blockchain'}, status=404)
        note_hash = create_note_hash(note.id, note.title, note.content, 'CREATE')
        hash_match = receipt.hash_value == note_hash
        metadata = get_transaction_metadata(tx_hash) or {}

        response_data = {
            'tx_hash': tx_hash,
            'status': tx_info.get('status', 'unknown'),
            'block_height': tx_info.get('block_height'),
            'block_time': tx_info.get('block_time'),
            'fees': tx_info.get('fees', '0'),
            'hash_match': hash_match,
            'stored_hash': receipt.hash_value,
            'computed_hash': note_hash,
            'note_title': note.title,
            'note_id': note.id,
            'metadata': metadata
        }
        return JsonResponse(response_data)
    except Exception as e:
        logger.exception("verify_receipt failed")
        return JsonResponse({'error': f'Verification failed: {str(e)}'}, status=500)


def blockchain_proof(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    receipt = getattr(note, 'blockchain_receipt', None)
    if not receipt:
        return render(request, 'notes/blockchain_proof.html', {
            'note': note,
            'error': 'No blockchain receipt found for this note'
        })
    try:
        tx_hash = receipt.transaction_hash
        tx_info = verify_transaction_via_blockfrost(tx_hash)
        if not tx_info:
            return render(request, 'notes/blockchain_proof.html', {
                'note': note,
                'error': 'Transaction not found on blockchain'
            })
        note_hash = create_note_hash(note.id, note.title, note.content, 'CREATE')
        hash_match = receipt.hash_value == note_hash
        metadata = get_transaction_metadata(tx_hash) or {}
        fees_lovelace = int(tx_info.get('fees', 0) or 0)
        fees_ada = fees_lovelace / 1_000_000 if fees_lovelace else 0
        proof_data = {
            'tx_hash': tx_hash,
            'status': 'Success' if tx_info.get('status') == 'confirmed' else 'Pending',
            'fees_lovelace': fees_lovelace,
            'fees_ada': fees_ada,
            'block_height': tx_info.get('block_height'),
            'block_time': tx_info.get('block_time'),
            'slot': tx_info.get('slot'),
            'hash_match': hash_match,
            'stored_hash': receipt.hash_value,
            'computed_hash': note_hash,
            'note_title': note.title,
            'note_id': note.id,
            'timestamp': receipt.timestamp,
            'metadata': metadata
        }
        return render(request, 'notes/blockchain_proof.html', {
            'note': note,
            'proof_data': proof_data
        })
    except Exception as e:
        logger.exception("blockchain_proof failed")
        return render(request, 'notes/blockchain_proof.html', {
            'note': note,
            'error': f'Failed to load blockchain data: {str(e)}'
        })


# -----------------------
# API: blockchain status
# -----------------------
@require_http_methods(["GET"])
def api_blockchain_status(request):
    return JsonResponse({'is_connected': get_blockchain_status()})


# ---------------------
# prepare_transaction_view
# ---------------------
# ---------- prepare_transaction_view ----------
@csrf_exempt
@require_http_methods(["POST"])
def prepare_transaction_view(request):
    """
    Build an unsigned transaction CBOR (for preview/testnet) using pycardano+Blockfrost.
    Returns JSON: { success, transaction_cbor (hex), tx_hash (placeholder), network }
    """
    try:
        data = json.loads(request.body.decode('utf-8') if request.body else '{}')
        tx_data = data.get('transaction_data') or {}
        receiver_address = data.get('receiver_address')
        min_lovelace = int(data.get('min_lovelace', 1))
        metadata_label = data.get('metadata_label', '721')
        metadata = data.get('metadata', {})

        note_id = tx_data.get('note_id')
        wallet_addr = tx_data.get('wallet_address') or tx_data.get('from_address') or tx_data.get('sender') or tx_data.get('wallet')

        if not note_id or not wallet_addr:
            return JsonResponse({'success': False, 'error': 'note_id and wallet_address required'}, status=400)
        if not receiver_address:
            return JsonResponse({'success': False, 'error': 'receiver_address required'}, status=400)

        if BlockFrostChainContext is None:
            return JsonResponse({'success': False, 'error': 'pycardano / blockfrost libs not available on server'}, status=500)

        # create chain context (uses your settings: BLOCKFROST_PROJECT_ID and BLOCKFROST_API_URL)
        ctx = BlockFrostChainContext(
            project_id=settings.BLOCKFROST_PROJECT_ID,
            base_url=settings.BLOCKFROST_API_URL
        )

        sender_addr = Address.from_primitive(wallet_addr)
        receiver_addr = Address.from_primitive(receiver_address)

        # Build transaction: send min_lovelace to receiver, let pycardano pick inputs + change
        builder = TransactionBuilder(ctx)
        builder.add_output(TransactionOutput(receiver_addr, Value(min_lovelace)))

        # Attach metadata if provided (pycardano expects AuxiliaryData or similar)
        if metadata:
            try:
                # AuxiliaryData expects metadata as python primitives; this will attach it
                builder.auxiliary_data = AuxiliaryData(metadata)
            except Exception:
                # fallback: attach raw dict to builder.auxiliary_data
                try:
                    builder.auxiliary_data = AuxiliaryData(metadata)
                except Exception:
                    logger.exception("Couldn't attach metadata as AuxiliaryData; continuing without metadata")

        unsigned_tx = builder.build(change_address=sender_addr)

        # Convert to CBOR hex
        cbor_bytes = unsigned_tx.to_cbor()
        cbor_hex = binascii.hexlify(cbor_bytes).decode()

        tx_hash_placeholder = f"pending_{int(time.time()*1000)}_{(tx_data.get('note_hash') or '')[:16]}"

        # Save pending receipt (non-fatal if this fails)
        try:
            note = Note.objects.get(id=note_id)
            BlockchainReceipt.objects.update_or_create(
                note=note,
                defaults={
                    'transaction_hash': tx_hash_placeholder,
                    'block_number': None,
                    'hash_value': tx_data.get('note_hash') or '',
                    'metadata_label': metadata_label,
                    'action': tx_data.get('operation', 'CREATE'),
                    'signed_payload': tx_data.get('note_hash') or '',
                    'wallet_address': wallet_addr,
                    'wallet_public_key': None,
                    'wallet_signature': None,
                    'timestamp': timezone.now(),
                    'network': getattr(settings, 'CARDANO_NETWORK', 'preview')
                }
            )
        except Exception:
            logger.exception("Failed to save pending receipt (non-fatal)")

        return JsonResponse({
            'success': True,
            'transaction_cbor': cbor_hex,
            'tx_hash': tx_hash_placeholder,
            'network': getattr(settings, 'CARDANO_NETWORK', 'preview'),
            'message': 'Unsigned transaction ready'
        })
    except Exception as e:
        logger.exception("prepare_transaction failed")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ---------- assemble_signed_tx ----------
@csrf_exempt
@require_http_methods(["POST"])
def assemble_signed_tx(request):
    """
    Wallet returned a witness set (not a fully signed tx). Assembling witness sets server-side
    requires precise pycardano object handling. Implementing a generic assembler is error-prone
    because wallets return different formats. For now we return a clear error that instructs
    frontend to return a full signed tx CBOR after signTx, or to POST the witness hex and we will try.
    """
    try:
        data = json.loads(request.body.decode('utf-8') if request.body else '{}')
        # If frontend already provided final signed tx CBOR, accept it:
        if data.get('signed_tx_cbor'):
            return JsonResponse({'success': True, 'signed_tx_cbor': data.get('signed_tx_cbor')})

        # Otherwise advise the frontend to send the full signed tx (preferred)
        return JsonResponse({
            "success": False,
            "error": "assemble_signed_tx not implemented for witness-only responses. "
                     "Please have your wallet return a full signed transaction CBOR from signTx, "
                     "or use the submit_signed_tx endpoint with 'signed_tx_cbor'."
        })
    except Exception as e:
        logger.exception("assemble_signed_tx failed")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# ---------- submit_signed_tx ----------
@csrf_exempt
@require_http_methods(["POST"])
def submit_signed_tx(request):
    """
    Accepts a fully-signed transaction CBOR hex and submits to Blockfrost.
    Returns { success, tx_hash }.
    """
    try:
        data = json.loads(request.body.decode('utf-8') if request.body else '{}')
        signed = data.get('signed_tx_cbor')
        if not signed:
            return JsonResponse({'success': False, 'error': 'No signed_tx_cbor provided'}, status=400)

        try:
            tx_bytes = binascii.unhexlify(signed)
        except Exception:
            return JsonResponse({'success': False, 'error': 'Invalid hex for signed_tx_cbor'}, status=400)

        url = settings.BLOCKFROST_API_URL.rstrip('/') + "/tx/submit"
        headers = {
            "project_id": settings.BLOCKFROST_PROJECT_ID,
            "Content-Type": "application/cbor"
        }

        res = requests.post(url, headers=headers, data=tx_bytes)
        if res.status_code not in (200, 202):
            logger.error("Blockfrost submit failed: %s %s", res.status_code, res.text)
            return JsonResponse({"success": False, "error": f"Blockfrost submit failed: {res.status_code} - {res.text}"}, status=502)

        # Blockfrost returns tx hash in body
        tx_hash = res.text.strip().replace('"', '')
        return JsonResponse({'success': True, 'tx_hash': tx_hash})
    except Exception as e:
        logger.exception("submit_signed_tx failed")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# -----------------------
# Confirm transaction
# -----------------------
@csrf_exempt
@require_http_methods(["POST"])
def confirm_transaction(request):
    try:
        data = json.loads(request.body.decode('utf-8') if request.body else '{}')
        tx_hash = (data.get('tx_hash') or '').strip()
        note_id = data.get('note_id')
        operation = data.get('operation', 'CREATE')
        signature_data = data.get('signature_data') or {}
        metadata_label = data.get('metadata_label', '721')
        metadata = data.get('metadata', None)
        network = data.get('network', getattr(settings, "CARDANO_NETWORK", "preview"))

        if not tx_hash or not note_id:
            return JsonResponse({'success': False, 'error': 'Transaction hash and note ID required'}, status=400)

        note = get_object_or_404(Note, id=note_id)

        wallet_sig = signature_data.get('signature') or None
        wallet_key = signature_data.get('key') or signature_data.get('publicKey') or None
        wallet_addr = signature_data.get('address') or None
        signed_payload = signature_data.get('payload') or None

        is_pending = str(tx_hash).startswith('pending_')
        if is_pending:
            BlockchainReceipt.objects.update_or_create(
                note=note,
                defaults={
                    'transaction_hash': tx_hash,
                    'block_number': None,
                    'hash_value': create_note_hash(note.id, note.title, note.content, operation),
                    'metadata_label': metadata_label,
                    'action': operation,
                    'wallet_signature': wallet_sig,
                    'wallet_public_key': wallet_key,
                    'wallet_address': wallet_addr,
                    'signed_payload': signed_payload,
                    'network': network,
                    'timestamp': timezone.now()
                }
            )
            return JsonResponse({'success': True, 'tx_hash': tx_hash, 'status': 'pending', 'message': 'Signature recorded; transaction pending.'})

        # verify on-chain
        tx_info = verify_transaction_via_blockfrost(tx_hash)
        if not tx_info:
            return JsonResponse({'success': False, 'error': 'Transaction not found or verification failed'}, status=404)

        note_hash = create_note_hash(note.id, note.title, note.content, operation)
        BlockchainReceipt.objects.update_or_create(
            note=note,
            defaults={
                'transaction_hash': tx_hash,
                'block_number': tx_info.get('block_height'),
                'hash_value': note_hash,
                'metadata_label': metadata_label,
                'action': operation,
                'wallet_signature': wallet_sig,
                'wallet_public_key': wallet_key,
                'wallet_address': wallet_addr,
                'signed_payload': signed_payload,
                'network': network,
                'timestamp': timezone.now()
            }
        )

        return JsonResponse({'success': True, 'tx_hash': tx_hash, 'block_height': tx_info.get('block_height'), 'message': 'Transaction confirmed and receipt saved'})

    except Exception as e:
        logger.exception("confirm_transaction failed")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

