from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Note, BlockchainReceipt
from web3 import Web3
import hashlib
import logging

# Logging
logger = logging.getLogger(__name__)


# CREATE
def create_note_view(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            content = request.POST.get('content')

            if not title or not content:
                return JsonResponse({'success': False, 'error': 'Title and content are required'})

            # Save note in DB
            note = Note.objects.create(title=title, content=content)
            logger.info(f"Note created with ID: {note.id}")

            # Blockchain integration
            try:
                w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

                if not w3.is_connected():
                    logger.warning("Blockchain not connected")
                    return JsonResponse({
                        'success': True,
                        'note_id': note.id,
                        'message': 'Note saved (blockchain offline)'
                    })

                accounts = w3.eth.accounts
                if not accounts:
                    logger.warning("No blockchain accounts available")
                    return JsonResponse({
                        'success': True,
                        'note_id': note.id,
                        'message': 'Note saved (no blockchain accounts)'
                    })

                from_account = accounts[0]

                # Hash note
                note_string = f"{note.id}:{note.title}:{note.content}"
                note_hash = hashlib.sha256(note_string.encode('utf-8')).hexdigest()

                # Prepare txn
                txn = {
                    'from': from_account,
                    'to': from_account,
                    'value': 0,
                    'input': '0x' + note_hash.encode('utf-8').hex(),
                    'gas': 50000,
                    'gasPrice': w3.to_wei('20', 'gwei'),
                    'nonce': w3.eth.get_transaction_count(from_account),
                    'chainId': 1337,  # Ganache default
                }

                tx_hash = w3.eth.send_transaction(txn)
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

                if receipt.status == 1:
                    BlockchainReceipt.objects.create(
                        note=note,
                        transaction_hash=tx_hash.hex(),
                        block_number=receipt.blockNumber,
                        hash_value=note_hash
                    )
                    logger.info(f"Blockchain receipt created for note {note.id}")
                    return JsonResponse({'success': True, 'note_id': note.id, 'tx_hash': tx_hash.hex()})
                else:
                    logger.error(f"Blockchain transaction failed for note {note.id}")
                    return JsonResponse({'success': True, 'note_id': note.id, 'message': 'Note saved (blockchain txn failed)'})

            except Exception as blockchain_error:
                logger.error(f"Blockchain error: {str(blockchain_error)}")
                return JsonResponse({'success': True, 'note_id': note.id, 'message': 'Note saved (blockchain error)'})

        except Exception as e:
            logger.error(f"Error creating note: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'notes/create_note.html')


# LIST
def list_notes(request):
    notes = Note.objects.all().order_by('-created_at')
    return render(request, 'notes/list_notes.html', {'notes': notes})


# EDIT
def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    if request.method == 'POST':
        note.title = request.POST.get('title')
        note.content = request.POST.get('content')
        note.save()
        return JsonResponse({'success': True, 'note': {'title': note.title, 'content': note.content}})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


# DELETE
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    if request.method == 'POST':
        note.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


# VERIFY RECEIPT
def verify_receipt(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    receipt = getattr(note, 'blockchain_receipt', None)

    if not receipt:
        return JsonResponse({'error': 'No receipt found for this note'}, status=404)

    try:
        w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

        tx_hash = receipt.transaction_hash
        tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
        tx = w3.eth.get_transaction(tx_hash)

        # Recompute hash
        note_string = f"{note.id}:{note.title}:{note.content}"
        computed_hash = hashlib.sha256(note_string.encode('utf-8')).hexdigest()
        hash_match = receipt.hash_value == computed_hash

        return JsonResponse({
            'tx_hash': tx_hash,
            'status': getattr(tx_receipt, 'status', 'Unknown'),
            'gas_used': getattr(tx_receipt, 'gasUsed', 'Unknown'),
            'input_data': tx['input'][2:] if tx.get('input') else None,
            'hash_match': hash_match,
            'stored_hash': receipt.hash_value,
            'computed_hash': computed_hash,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
