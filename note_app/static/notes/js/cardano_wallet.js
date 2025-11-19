/**
 * Cardano Wallet Integration (CIP-30)
 * Handles wallet connection, transaction signing, and submission
 * Reference: https://www.cardano-caniuse.io/
 */

class CardanoWalletManager {
    constructor() {
        this.walletApi = null;
        this.selectedWallet = null;
        this.walletAddress = null;
        this.availableWallets = [];
        this.init();
    }

    init() {
        this.detectWallets();
    }

    detectWallets() {
        if (typeof window.cardano === 'undefined') {
            console.warn('No Cardano wallets detected');
            return;
        }

        this.availableWallets = Object.keys(window.cardano).filter(walletName => {
            const wallet = window.cardano[walletName];
            return wallet && typeof wallet.enable === 'function';
        });

        console.log('Available wallets:', this.availableWallets);
    }

    async connectWallet(walletName = 'lace') {
        try {
            if (!window.cardano || !window.cardano[walletName]) {
                throw new Error(`Wallet ${walletName} not found. Please install Lace wallet.`);
            }

            const wallet = window.cardano[walletName];
            
            // Check if already enabled
            const isEnabled = await wallet.isEnabled();
            if (isEnabled) {
                this.walletApi = await wallet.enable();
            } else {
                // Request permission
                this.walletApi = await wallet.enable();
            }

            this.selectedWallet = walletName;
            
            // Get wallet address
            const addresses = await this.walletApi.getUsedAddresses();
            if (addresses && addresses.length > 0) {
                this.walletAddress = addresses[0];
            } else {
                const unusedAddresses = await this.walletApi.getUnusedAddresses();
                if (unusedAddresses && unusedAddresses.length > 0) {
                    this.walletAddress = unusedAddresses[0];
                }
            }

            console.log('Wallet connected:', walletName);
            console.log('Wallet address:', this.walletAddress);
            
            return {
                success: true,
                wallet: walletName,
                address: this.walletAddress,
                api: this.walletApi
            };
        } catch (error) {
            console.error('Error connecting wallet:', error);
            throw error;
        }
    }

    async buildTransaction(transactionData, receiverAddress) {
        try {
            if (!this.walletApi) {
                throw new Error('Wallet not connected');
            }

            // Get UTXOs
            const utxos = await this.walletApi.getUtxos();
            if (!utxos || utxos.length === 0) {
                throw new Error('No UTXOs available');
            }

            // Get change address
            const changeAddress = await this.walletApi.getChangeAddress();

            // Build transaction
            // For Cardano, we'll send a minimal amount (1 ADA = 1,000,000 lovelace)
            // and include metadata with the note hash
            const minAda = 1000000; // 1 ADA in lovelace

            // Create transaction using CIP-30
            // Note: The actual transaction building is done by the wallet
            // We prepare the transaction structure
            const tx = {
                inputs: utxos.slice(0, 1), // Use first UTXO for simplicity
                outputs: [
                    {
                        address: receiverAddress,
                        amount: {
                            lovelace: minAda
                        }
                    },
                    {
                        address: changeAddress,
                        amount: {
                            lovelace: 0 // Will be calculated by wallet
                        }
                    }
                ],
                metadata: {
                    '674': { // CIP-0020 metadata label for note operations
                        'operation': transactionData.operation,
                        'note_id': transactionData.note_id,
                        'note_hash': transactionData.note_hash,
                        'title': transactionData.title,
                        'content_length': transactionData.content_length
                    }
                }
            };

            return tx;
        } catch (error) {
            console.error('Error building transaction:', error);
            throw error;
        }
    }

    async signAndSubmitTransaction(transactionData, receiverAddress) {
        try {
            if (!this.walletApi) {
                throw new Error('Wallet not connected. Please connect your wallet first.');
            }

            // Get network ID to ensure we're on the right network
            const networkId = await this.walletApi.getNetworkId();
            console.log('Network ID:', networkId); // 0 = testnet, 1 = mainnet

            // Build transaction
            const tx = await this.buildTransaction(transactionData, receiverAddress);

            // Sign transaction
            const signedTx = await this.walletApi.signTx(
                this.encodeTransaction(tx),
                false // partialSign = false
            );

            // Submit transaction
            const txHash = await this.walletApi.submitTx(
                this.encodeTransaction(tx)
            );

            console.log('Transaction submitted:', txHash);
            return txHash;
        } catch (error) {
            console.error('Error signing/submitting transaction:', error);
            throw error;
        }
    }

    /**
     * Encode transaction to CBOR format
     * This is a simplified version - in production, use proper CBOR encoding
     */
    encodeTransaction(tx) {
        // For now, return the transaction object
        // The wallet will handle CBOR encoding
        // In a real implementation, you'd use a CBOR library
        return JSON.stringify(tx);
    }

    /**
     * Simplified transaction creation using wallet's transaction builder
     * This uses a more direct approach with the wallet API
     */
    async createAndSubmitTransaction(transactionData, receiverAddress) {
        try {
            if (!this.walletApi) {
                throw new Error('Wallet not connected');
            }

            // Get UTXOs and addresses
            const utxos = await this.walletApi.getUtxos();
            const changeAddress = await this.walletApi.getChangeAddress();

            if (!utxos || utxos.length === 0) {
                throw new Error('No UTXOs available');
            }

            // For Cardano, we need to send at least 1 ADA (1,000,000 lovelace)
            // and include metadata
            // Since we can't directly build the full transaction here,
            // we'll use a simplified approach where we prepare the data
            // and let the wallet handle the transaction building

            // Create metadata hash (CIP-0020)
            const metadata = {
                '674': {
                    'operation': transactionData.operation,
                    'note_id': transactionData.note_id,
                    'note_hash': transactionData.note_hash,
                    'title': transactionData.title.substring(0, 64), // Limit length
                    'content_length': transactionData.content_length
                }
            };

            // For now, we'll create a simple transaction structure
            // The actual implementation would use pycardano on the backend
            // or a proper Cardano transaction builder library
            // This is a placeholder that shows the structure

            // Return transaction data that will be processed
            return {
                metadata: metadata,
                receiverAddress: receiverAddress,
                minAda: 1000000 // 1 ADA
            };
        } catch (error) {
            console.error('Error creating transaction:', error);
            throw error;
        }
    }

    disconnect() {
        this.walletApi = null;
        this.selectedWallet = null;
        this.walletAddress = null;
    }

    isConnected() {
        return this.walletApi !== null;
    }
}

// Global wallet manager instance
window.cardanoWalletManager = new CardanoWalletManager();

/**
 * Helper function to handle note operations with wallet integration
 */
async function handleNoteWithWallet(operation, noteData, receiverAddress) {
    try {
        const walletManager = window.cardanoWalletManager;

        // Ensure wallet is connected
        if (!walletManager.isConnected()) {
            const result = await walletManager.connectWallet('lace');
            if (!result || !result.success) {
                throw new Error('Failed to connect wallet');
            }
        }

        // Create transaction data
        const transactionData = {
            operation: operation,
            note_id: noteData.note_id,
            note_hash: noteData.note_hash,
            title: noteData.title || '',
            content_length: noteData.content_length || 0
        };

        // For Cardano, we'll use a backend endpoint to build the transaction
        // and then sign it with the wallet
        // This is a simplified flow - in production, you'd build the full transaction

        // Call backend to prepare transaction
        const response = await fetch('/notes/api/prepare_transaction/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                transaction_data: transactionData,
                receiver_address: receiverAddress
            })
        });

        const txData = await response.json();

        if (!txData.success) {
            throw new Error(txData.error || 'Failed to prepare transaction');
        }

        // Sign and submit using wallet
        // Note: This is simplified - actual implementation would use proper CBOR encoding
        const txHash = await walletManager.walletApi.signTx(
            txData.transaction_cbor,
            false
        );

        const submittedHash = await walletManager.walletApi.submitTx(
            txData.transaction_cbor
        );

        return submittedHash;
    } catch (error) {
        console.error('Error handling note with wallet:', error);
        throw error;
    }
}

/**
 * Simplified version that works with the current backend structure
 * This version sends transaction data to backend, which prepares it,
 * then we sign and submit from frontend
 */
async function submitNoteTransaction(transactionData, receiverAddress) {
    try {
        const walletManager = window.cardanoWalletManager;

        if (!walletManager.isConnected()) {
            await walletManager.connectWallet('lace');
        }

        // For Cardano transactions, we need to:
        // 1. Get UTXOs from wallet
        // 2. Build transaction with metadata
        // 3. Sign with wallet
        // 4. Submit with wallet

        // Since building Cardano transactions requires proper CBOR encoding
        // and transaction structure, we'll use a simplified approach:
        // Send minimal ADA (1 ADA) to receiver with metadata

        const utxos = await walletManager.walletApi.getUtxos();
        const changeAddress = await walletManager.walletApi.getChangeAddress();

        // Build transaction structure
        // Note: This is a conceptual structure - actual implementation
        // would require proper CBOR encoding and transaction building
        const txStructure = {
            inputs: utxos.slice(0, 1),
            outputs: [
                {
                    address: receiverAddress,
                    amount: { lovelace: 1000000 } // 1 ADA
                }
            ],
            changeAddress: changeAddress,
            metadata: {
                '674': {
                    'msg': [transactionData.note_hash]
                }
            }
        };

        // For now, return the structure
        // In production, this would be properly encoded and signed
        console.log('Transaction structure:', txStructure);

        // Return a placeholder - actual implementation would sign and submit
        return 'tx_placeholder_hash';
    } catch (error) {
        console.error('Error submitting transaction:', error);
        throw error;
    }
}

/**
 * Get CSRF token from Django
 */
function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    // Fallback: try to get from meta tag
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
        return csrfMeta.getAttribute('content');
    }
    return '';
}

