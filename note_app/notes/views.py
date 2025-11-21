from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Note, BlockchainReceipt
from .cardano_utils import (
    create_note_hash,
    build_transaction_data,
    verify_transaction_via_blockfrost,
    check_blockchain_connection,
    get_transaction_metadata,
)
from django.conf import settings
import hashlib
import logging
from django.db.models import Q
import json
from django.db import transaction


logger = logging.getLogger(__name__)


def get_blockchain_status():
    """
    Checks if Blockfrost API is accessible.
    """
    return check_blockchain_connection()


def landing_page(request):
    return render(request, 'account/landing.html')


# LIST
def list_notes(request):
    sort_by = request.GET.get("sort", "-created_at")
    search_query = request.GET.get("q", "")

    valid_sort_fields = ["created_at", "-created_at", "title", "-title"]
    if sort_by not in valid_sort_fields:
        sort_by = "-created_at"

    # Exclude notes that have been marked deleted
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



@csrf_exempt
@require_http_methods(["POST"])
def create_note_view(request):
    try:
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()

        if not title or not content:
            return JsonResponse({'success': False, 'error': 'Title and content are required'})

        # Create note in database
        note = Note.objects.create(title=title, content=content)

        note_hash = create_note_hash(note.id, title, content, 'CREATE')
        transaction_data = build_transaction_data(
            note_id=note.id,
            title=title,
            content=content,
            operation='CREATE',
            from_address=settings.CARDANO_SENDER_ADDRESS,
            to_address=settings.CARDANO_RECEIVER_ADDRESS
        )

        return JsonResponse({
            'success': True,
            'note_id': note.id,
            'requires_wallet': True,
            'transaction_data': transaction_data,
            'note_hash': note_hash
        })

    except Exception as e:
        logger.error(f"Error creating note: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def confirm_transaction(request):
    try:
        data = json.loads(request.body) if request.body else {}
        tx_hash = data.get('tx_hash', '').strip()
        note_id = data.get('note_id')
        operation = data.get('operation', 'CREATE')
        signature_data = data.get('signature_data')
        # NEW: default metadata label if frontend didn't send one
        metadata_label = data.get('metadata_label', '674')

        if not tx_hash or not note_id:
            return JsonResponse({'success': False, 'error': 'Transaction hash and note ID are required'})

        # NOTE: the note may be soft-deleted (is_deleted=True) but still exists
        note = get_object_or_404(Note, id=note_id)

        # signature_data (optional)
        signature_data = data.get('signature_data') or {}
        wallet_sig = signature_data.get('signature') or None
        wallet_key = signature_data.get('key') or signature_data.get('publicKey') or None
        wallet_addr = signature_data.get('address') or None
        signed_payload = signature_data.get('payload') or None

        # Pending placeholder tx
        is_pending = tx_hash.startswith("pending_")
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
                    'signed_payload': signed_payload
                }
            )

            return JsonResponse({'success': True, 'tx_hash': tx_hash, 'status': 'pending'})

        # Verify transaction via Blockfrost
        tx_info = verify_transaction_via_blockfrost(tx_hash)
        if not tx_info:
            return JsonResponse({'success': False, 'error': 'Transaction verification failed'})

        note_hash = create_note_hash(note.id, note.title, note.content, operation)

        BlockchainReceipt.objects.update_or_create(
            note=note,
            defaults={
                'transaction_hash': tx_hash,
                'block_number': tx_info.get('block_height'),
                'hash_value': note_hash,
                'action': operation,
                'wallet_signature': wallet_sig,
                'wallet_public_key': wallet_key,
                'wallet_address': wallet_addr,
                'signed_payload': signed_payload
            }
        )

        return JsonResponse({
            'success': True,
            'tx_hash': tx_hash,
            'block_height': tx_info.get('block_height'),
            'message': 'Transaction confirmed and receipt saved'
        })

    except Exception as e:
        logger.error(f"Error confirming transaction: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})




# EDIT
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
            from_address=settings.CARDANO_SENDER_ADDRESS,
            to_address=settings.CARDANO_RECEIVER_ADDRESS
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
        logger.error(f"Error updating note: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})



# DELETE
@csrf_exempt
@require_http_methods(["POST"])
def delete_note(request, note_id):
    try:
        note = get_object_or_404(Note, id=note_id)

        # prepare transaction data BEFORE marking deleted
        note_hash = create_note_hash(note.id, note.title, note.content, 'DELETE')
        transaction_data = build_transaction_data(
            note_id=note.id,
            title=note.title,
            content=note.content,
            operation='DELETE',
            from_address=settings.CARDANO_SENDER_ADDRESS,
            to_address=settings.CARDANO_RECEIVER_ADDRESS
        )

        # Soft-delete: mark deleted but keep DB row so receipt can be attached
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
        logger.error(f"Error deleting note: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})




# VERIFY RECEIPT (JSON API)
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
        
        # Compute hash for verification
        note_hash = create_note_hash(note.id, note.title, note.content, 'CREATE')
        hash_match = receipt.hash_value == note_hash
        
        # Get metadata
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
        logger.error(f"Error verifying receipt: {str(e)}")
        return JsonResponse({'error': f'Verification failed: {str(e)}'}, status=500)


# BLOCKCHAIN PROOF PAGE
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
        
        # Compute hash for verification
        note_hash = create_note_hash(note.id, note.title, note.content, 'CREATE')
        hash_match = receipt.hash_value == note_hash
        
        # Get metadata
        metadata = get_transaction_metadata(tx_hash) or {}
        
        # Convert fees from lovelace to ADA (1 ADA = 1,000,000 lovelace)
        fees_lovelace = int(tx_info.get('fees', 0))
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
        logger.error(f"Error loading blockchain proof: {str(e)}")
        return render(request, 'notes/blockchain_proof.html', {
            'note': note,
            'error': f'Failed to load blockchain data: {str(e)}'
        })


# API Views
@require_http_methods(["GET"])
def api_blockchain_status(request):
    status = get_blockchain_status()
    return JsonResponse({'is_connected': status})

@csrf_exempt
@require_http_methods(["POST"])
def prepare_transaction_view(request):
    """
    Backend helper to prepare a transaction record. The frontend will build/sign/submit.
    This endpoint creates a pending receipt record (placeholder) if note exists,
    and returns tx template info.
    """
    try:
        data = json.loads(request.body.decode('utf-8') if request.body else '{}')
        tx_data = data.get('transaction_data') or {}
        metadata_label = data.get('metadata_label', '721')
        metadata = data.get('metadata', {})
        receiver_address = data.get('receiver_address')
        min_lovelace = int(data.get('min_lovelace', 1))
        network = data.get('network', 'testnet')

        note_id = tx_data.get('note_id')
        if not note_id:
            return JsonResponse({'success': False, 'error': 'note_id required'}, status=400)

        note = None
        try:
            note = Note.objects.get(id=note_id)
        except Note.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No Note matches the given query.'}, status=404)

        # Create a pending tx_hash placeholder
        tx_hash = f"pending_{int(time.time()*1000)}_{(tx_data.get('note_hash') or '')[:16]}"

        # Persist pending receipt (safe defaults) so frontend can continue
        # Use update_or_create to avoid duplicates
        defaults = {
            'transaction_hash': tx_hash,
            'block_number': None,
            'hash_value': tx_data.get('note_hash') or '',
            'metadata_label': metadata_label,
            'action': tx_data.get('operation', 'CREATE'),
            'signed_payload': tx_data.get('note_hash') or '',
            'wallet_address': None,
            'wallet_public_key': None,
            'wallet_signature': None,
            'timestamp': timezone.now()
        }
        BlockchainReceipt.objects.update_or_create(note=note, defaults=defaults)

        # Return prepared info the frontend expects
        return JsonResponse({
            'success': True,
            'tx_hash': tx_hash,
            'network': network,
            'metadata_label': metadata_label,
            'metadata': metadata,
            'min_lovelace': min_lovelace,
            'message': 'Prepared pending transaction placeholder. Sign on frontend and call confirm_transaction.'
        })
    except Exception as e:
        logger.exception("prepare_transaction failed")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def confirm_transaction(request):
    """
    Confirm transaction (called after frontend signs and/or submits tx).
    Accepts signature_data and metadata info.
    """
    try:
        data = json.loads(request.body.decode('utf-8') if request.body else '{}')
        tx_hash = data.get('tx_hash', '').strip()
        note_id = data.get('note_id')
        operation = data.get('operation', 'CREATE')
        signature_data = data.get('signature_data') or {}
        metadata_label = data.get('metadata_label', None)
        metadata = data.get('metadata', None)
        network = data.get('network', 'testnet')

        if not tx_hash or not note_id:
            return JsonResponse({'success': False, 'error': 'Transaction hash and note ID are required'}, status=400)

        note = get_object_or_404(Note, id=note_id)

        # Try to verify transaction on-chain if tx_hash isn't placeholder
        is_pending = str(tx_hash).startswith('pending_')

        if is_pending:
            # Update existing pending receipt with signature info
            receipt, created = BlockchainReceipt.objects.update_or_create(
                note=note,
                defaults={
                    'transaction_hash': tx_hash,
                    'block_number': None,
                    'hash_value': create_note_hash(note.id, note.title, note.content, operation),
                    'metadata_label': metadata_label or getattr(receipt, 'metadata_label', '721'),
                    'action': operation,
                    'wallet_signature': signature_data.get('signature') if signature_data else None,
                    'wallet_public_key': signature_data.get('key') if signature_data else None,
                    'wallet_address': signature_data.get('address') if signature_data else None,
                    'signed_payload': signature_data.get('payload') if signature_data else None,
                    'network': network,
                }
            )
            return JsonResponse({
                'success': True,
                'tx_hash': tx_hash,
                'status': 'pending',
                'message': 'Signature recorded; transaction pending.'
            })

        # If not pending, attempt on-chain verification (you had verify_transaction_via_blockfrost)
        tx_info = verify_transaction_via_blockfrost(tx_hash)
        if not tx_info:
            return JsonResponse({'success': False, 'error': 'Transaction not found or verification failed'}, status=404)

        note_hash = create_note_hash(note.id, note.title, note.content, operation)

        # Save receipt details
        receipt, created = BlockchainReceipt.objects.update_or_create(
            note=note,
            defaults={
                'transaction_hash': tx_hash,
                'block_number': tx_info.get('block_height'),
                'hash_value': note_hash,
                'metadata_label': metadata_label or '721',
                'action': operation,
                'wallet_signature': signature_data.get('signature') if signature_data else None,
                'wallet_public_key': signature_data.get('key') if signature_data else None,
                'wallet_address': signature_data.get('address') if signature_data else None,
                'signed_payload': signature_data.get('payload') if signature_data else None,
                'network': network,
            }
        )

        return JsonResponse({
            'success': True,
            'tx_hash': tx_hash,
            'block_height': tx_info.get('block_height'),
            'message': 'Transaction confirmed and receipt saved'
        })
    except Exception as e:
        logger.exception("confirm_transaction failed")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
