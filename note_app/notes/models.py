from django.db import models

class Note(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Quick Wins Features
    # Pin Notes
    is_pinned = models.BooleanField(default=False)
    pinned_at = models.DateTimeField(null=True, blank=True)
    
    # Archive
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    
    # Trash (Soft Delete)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Color Coding
    color = models.CharField(max_length=20, default='default', blank=True)
    # Choices: default, red, orange, yellow, green, blue, purple, pink

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-is_pinned', '-updated_at']  # Pinned notes first, then by date


class BlockchainReceipt(models.Model):
    note = models.OneToOneField(Note, on_delete=models.CASCADE, related_name='blockchain_receipt')
    transaction_hash = models.CharField(max_length=255)
    block_number = models.IntegerField(blank=True, null=True)
    hash_value = models.CharField(max_length=64, blank=True, null=True)  # SHA-256 hash of note data
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt for {self.note.title} (TX: {self.transaction_hash[:10]}...)"
    
    class Meta:
        verbose_name = "Blockchain Receipt"
        verbose_name_plural = "Blockchain Receipts"
