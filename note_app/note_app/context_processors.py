import os

def blockfrost(request):
    return {
        'BLOCKFROST_PROJECT_ID': os.environ.get('BLOCKFROST_PROJECT_ID', ''),
    }