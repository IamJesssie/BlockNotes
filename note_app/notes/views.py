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
from django.contrib.auth.decorators import login_required
import json

logger = logging.getLogger(__name__)


def get_blockchain_status():
    """
    Checks if Blockfrost API is accessible.
    """
    return check_blockchain_connection()


def landing_page(request):
    return render(request, 'account/landing.html')


# LIST
@login_required
def list_notes(request):
    sort_by = request.GET.get("sort", "-created_at")  
    search_query = request.GET.get("q", "")

    valid_sort_fields = ["created_at", "-created_at", "title", "-title"]
    if sort_by not in valid_sort_fields:
        sort_by = "-created_at"

    notes = Note.objects.all()
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
    """
    Create a note and prepare transaction data for wallet signing.
    The frontend wallet will sign and submit the transaction, then call confirm_transaction.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
    try:
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()

        if not title or not content:
            return JsonResponse({'success': False, 'error': 'Title and content are required'})

        # Create note in database first
        note = Note.objects.create(title=title, content=content)
        logger.info(f"Note created with ID: {note.id}")

        # Prepare transaction data for wallet
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
            'note_hash': note_hash,
            'message': 'Note created. Please sign transaction with your wallet to record it on blockchain.'
        })

    except Exception as e:
        logger.error(f"Error creating note: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def confirm_transaction(request):
    """
    Endpoint called by frontend after wallet submits transaction.
    Receives tx_hash and verifies it via Blockfrost, then creates BlockchainReceipt.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
    
    try:
        data = json.loads(request.body) if request.body else {}
        tx_hash = data.get('tx_hash', '').strip()
        note_id = data.get('note_id')
        operation = data.get('operation', 'CREATE')
        signature_data = data.get('signature_data')  # Optional signature data from wallet
        
        if not tx_hash or not note_id:
            return JsonResponse({'success': False, 'error': 'Transaction hash and note ID are required'})
        
        # If tx_hash starts with 'pending_', it's a placeholder
        # Store it but mark as pending
        is_pending = tx_hash.startswith('pending_')
        
        note = get_object_or_404(Note, id=note_id)
        
        # If transaction is pending (placeholder), just store the signature data
        if is_pending:
            # Store pending transaction with signature for later verification
            BlockchainReceipt.objects.update_or_create(
                note=note,
                defaults={
                    'transaction_hash': tx_hash,
                    'block_number': None,  # Will be set when transaction is confirmed
                    'hash_value': create_note_hash(note.id, note.title, note.content, operation)
                }
            )
            return JsonResponse({
                'success': True,
                'tx_hash': tx_hash,
                'status': 'pending',
                'message': 'Transaction signature recorded. Full transaction will be created later.'
            })
        
        # Verify transaction via Blockfrost
        tx_info = verify_transaction_via_blockfrost(tx_hash)
        
        if not tx_info:
            return JsonResponse({
                'success': False,
                'error': 'Transaction not found or verification failed'
            })
        
        # Compute hash for verification
        note_hash = create_note_hash(note.id, note.title, note.content, operation)
        
        # Create or update receipt
        receipt, created = BlockchainReceipt.objects.update_or_create(
            note=note,
            defaults={
                'transaction_hash': tx_hash,
                'block_number': tx_info.get('block_height'),
                'hash_value': note_hash
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
    """
    Update a note and prepare transaction data for wallet signing.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
    
    note = get_object_or_404(Note, id=note_id)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        
        if not title or not content:
            return JsonResponse({'success': False, 'error': 'Title and content are required'})
        
        # Update note in database
        note.title = title
        note.content = content
        note.save()
        
        # Prepare transaction data for wallet
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
            'operation': 'UPDATE',
            'message': 'Note updated. Please sign transaction with your wallet to record it on blockchain.'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


# DELETE
@csrf_exempt
@require_http_methods(["POST"])
def delete_note(request, note_id):
    """
    Delete a note and prepare transaction data for wallet signing.
    Note is marked for deletion but actual deletion happens after transaction confirmation.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
    
    note = get_object_or_404(Note, id=note_id)
    
    if request.method == 'POST':
        # Store note data before deletion for transaction
        note_title = note.title
        note_content = note.content
        
        # Prepare transaction data before deletion
        note_hash = create_note_hash(note.id, note_title, note_content, 'DELETE')
        transaction_data = build_transaction_data(
            note_id=note.id,
            title=note_title,
            content=note_content,
            operation='DELETE',
            from_address=settings.CARDANO_SENDER_ADDRESS,
            to_address=settings.CARDANO_RECEIVER_ADDRESS
        )
        
        # Store note ID before deletion
        deleted_note_id = note.id
        
        # Delete note from database
        note.delete()
        
        return JsonResponse({
            'success': True,
            'note_id': deleted_note_id,
            'requires_wallet': True,
            'transaction_data': transaction_data,
            'note_hash': note_hash,
            'operation': 'DELETE',
            'message': 'Note deleted. Please sign transaction with your wallet to record it on blockchain.'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


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
@login_required
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
