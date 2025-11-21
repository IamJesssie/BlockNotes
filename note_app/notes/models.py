from django.db import models

class Note(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # New: soft-delete flag so we can keep note records until blockchain receipt confirmed
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class BlockchainReceipt(models.Model):
    note = models.OneToOneField(Note, on_delete=models.CASCADE, related_name='blockchain_receipt')
    transaction_hash = models.CharField(max_length=128)
    block_number = models.IntegerField(null=True, blank=True)
    hash_value = models.CharField(max_length=66, null=True, blank=True)


    metadata_label = models.CharField(max_length=32, default="721")
    network = models.CharField(max_length=32, default="testnet")   # NEW - default "testnet"

    action = models.CharField(max_length=16, null=True, blank=True)

    signed_payload = models.CharField(max_length=256, null=True, blank=True)
    wallet_address = models.CharField(max_length=512, null=True, blank=True)
    wallet_public_key = models.TextField(null=True, blank=True)
    wallet_signature = models.TextField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt for Note {self.note.id}"

