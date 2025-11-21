class CardanoWalletManager {
    constructor() {
        this.api = null;
        this.walletName = null;
        this.connectedAddress = null;
        this.networkId = null;
        this.isConnected = false;
        this.wallets = [];
        this.detectWallets = this.detectWallets.bind(this);
        this.connectWallet = this.connectWallet.bind(this);
        this.disconnectWallet = this.disconnectWallet.bind(this);
        this.validatePreviewNetwork = this.validatePreviewNetwork.bind(this);
        this.getWalletAddressBech32 = this.getWalletAddressBech32.bind(this);
        this.updateUI = this.updateUI.bind(this);
        this.handleTestSendAda = this.handleTestSendAda.bind(this);
        this.init();
    }
    async init() {
        if (typeof window.cardano === 'undefined') {
            setTimeout(() => this.init(), 1000);
            return;
        }
        this.detectWallets();
        this.setupEventListeners();
    }
    detectWallets() {
        const walletStatus = document.getElementById('walletStatus');
        const walletList = document.getElementById('walletList');
        if (typeof window.cardano === 'undefined') {
            if (walletStatus) {
                walletStatus.className = 'status-indicator error';
                walletStatus.querySelector('.status-text').textContent = 'No Cardano wallets detected. Install Lace.';
            }
            if (walletList) walletList.innerHTML = '';
            return;
        }
        this.wallets = Object.keys(window.cardano);
        if (!this.wallets.length) {
            if (walletStatus) {
                walletStatus.className = 'status-indicator error';
                walletStatus.querySelector('.status-text').textContent = 'No Cardano wallets found. Install Lace.';
            }
            if (walletList) walletList.innerHTML = '';
            return;
        }
        if (walletStatus) {
            walletStatus.className = 'status-indicator';
            walletStatus.querySelector('.status-text').textContent = `${this.wallets.length} wallet(s) detected`;
        }
        this.renderWalletList();
    }
    renderWalletList() {
        const walletList = document.getElementById('walletList');
        if (!walletList) return;
        walletList.innerHTML = '';
        this.wallets.forEach(walletName => {
            const walletOption = document.createElement('div');
            walletOption.className = 'wallet-option';
            walletOption.dataset.wallet = walletName;
            walletOption.innerHTML = `
                <img src="/static/notes/img/Icon-9.svg" alt="${walletName}" class="wallet-icon">
                <div class="wallet-info">
                    <div class="wallet-name">${walletName}</div>
                    <div class="wallet-description">Click to connect ${walletName} wallet</div>
                </div>
            `;
            walletOption.addEventListener('click', () => this.connectWallet(walletName));
            walletList.appendChild(walletOption);
        });
    }
    async connectWallet(walletName) {
        const walletStatus = document.getElementById('walletStatus');
        const networkStatus = document.getElementById('networkStatus');
        try {
            console.log('Connecting to wallet:', walletName);
            if (walletStatus) {
                walletStatus.className = 'status-indicator detecting';
                walletStatus.querySelector('.status-text').textContent = `Connecting to ${walletName}...`;
            }
            const wallet = window.cardano[walletName];
            if (!wallet) throw new Error(`Wallet ${walletName} not found`);
            this.api = await wallet.enable();
            this.walletName = walletName;
            console.log('Connected to wallet API:', this.api);
            const networkId = await this.api.getNetworkId();
            this.networkId = networkId;
            if (networkId !== 0) {
                if (networkStatus) {
                    networkStatus.style.display = 'block';
                    networkStatus.querySelector('#networkText').textContent = `Warning: Connected to ${networkId === 1 ? 'Mainnet' : 'Testnet'}. Use Cardano Preview.`;
                }
                if (walletStatus) {
                    walletStatus.className = 'status-indicator connected';
                    walletStatus.querySelector('.status-text').textContent = `Connected to ${walletName} (Wrong Network)`;
                }
            } else {
                if (networkStatus) networkStatus.style.display = 'none';
                if (walletStatus) {
                    walletStatus.className = 'status-indicator connected';
                    walletStatus.querySelector('.status-text').textContent = `Connected to ${walletName} (Preview Network)`;
                }
            }
            this.connectedAddress = await this.getWalletAddressBech32();
            console.log('Wallet address (bech32 or hex-short):', this.connectedAddress);
            if (!this.connectedAddress) {
                try {
                    const hexAddr = (await this.api.getChangeAddress()) || null;
                    this.connectedAddress = hexAddr ? this.formatAddress(hexAddr) : null;
                } catch (_) {}
            }
            this.isConnected = true;
            this.updateUI();
            window.dispatchEvent(new CustomEvent('walletConnected', { detail: { walletName } }));
        } catch (error) {
            if (walletStatus) {
                walletStatus.className = 'status-indicator error';
                walletStatus.querySelector('.status-text').textContent = `Connection failed: ${error.message}`;
            }
            this.isConnected = false;
            this.api = null;
            this.walletName = null;
        }
    }
    async getWalletAddressBech32() {
        if (!this.api) return null;
        try {
            const usedAddresses = await this.api.getUsedAddresses();
            const unusedAddresses = this.api.getUnusedAddresses ? await this.api.getUnusedAddresses() : [];
            let hexAddr = null;
            if (usedAddresses && usedAddresses.length > 0) hexAddr = usedAddresses[0];
            else if (unusedAddresses && unusedAddresses.length > 0) hexAddr = unusedAddresses[0];
            else hexAddr = await this.api.getChangeAddress();
            if (!hexAddr) return null;
            console.log('Wallet address (hex):', hexAddr);
            const hasCardano = (typeof Cardano !== 'undefined' && Cardano.Address);
            const hasWasm = (typeof CardanoWasm !== 'undefined' && CardanoWasm.Address);
            if (hasCardano || hasWasm) {
                const lib = hasCardano ? Cardano : CardanoWasm;
                const bytes = this.hexToBytes(hexAddr);
                const addr = lib.Address.from_bytes(bytes).to_bech32();
                return addr;
            }
            return this.formatAddress(hexAddr);
        } catch (error) {
            console.warn('Address conversion failed:', error);
            return null;
        }
    }
    disconnectWallet() {
        this.api = null;
        this.walletName = null;
        this.connectedAddress = null;
        this.networkId = null;
        this.isConnected = false;
        this.updateUI();
        this.detectWallets();
        const walletStatus = document.getElementById('walletStatus');
        if (walletStatus) {
            walletStatus.className = 'status-indicator';
            walletStatus.querySelector('.status-text').textContent = 'Wallet disconnected';
        }
    }
    updateUI() {
        const walletInfo = document.getElementById('walletInfo');
        const networkStatus = document.getElementById('networkStatus');
        const walletButton = document.getElementById('walletConnectButton');
        if (this.isConnected) {
            if (walletInfo) walletInfo.style.display = 'block';
            const nEl = document.getElementById('connectedNetwork');
            const wEl = document.getElementById('connectedWalletName');
            const aEl = document.getElementById('connectedAddress');
            if (wEl) wEl.textContent = this.walletName;
            if (nEl) nEl.textContent = this.networkId === 0 ? 'Preview' : this.networkId === 1 ? 'Mainnet' : 'Testnet';
            if (aEl) aEl.textContent = this.connectedAddress || 'No address available';
            if (walletButton) {
                walletButton.innerHTML = '<i class="bi bi-wallet2"></i> ' + this.walletName;
                walletButton.classList.add('btn-success');
                walletButton.classList.remove('btn-outline-primary');
            }
        } else {
            if (walletInfo) walletInfo.style.display = 'none';
            if (networkStatus) networkStatus.style.display = 'none';
            if (walletButton) {
                walletButton.innerHTML = '<i class="bi bi-wallet2"></i> Connect Wallet';
                walletButton.classList.remove('btn-success');
                walletButton.classList.add('btn-outline-primary');
            }
        }
    }
    formatAddress(address) {
        if (!address) return 'No address available';
        if (address.length > 16) return address.substring(0, 8) + '...' + address.substring(address.length - 8);
        return address;
    }
    hexToBytes(hex) { return new Uint8Array(hex.match(/.{1,2}/g).map(b => parseInt(b, 16))); }
    validatePreviewNetwork() { return this.networkId === 0; }
    async checkExistingConnection() {
        const storedWallet = localStorage.getItem('connectedWallet');
        if (storedWallet && window.cardano && window.cardano[storedWallet]) {
            try { await this.connectWallet(storedWallet); }
            catch (e) { localStorage.removeItem('connectedWallet'); }
        }
    }
    async handleTestSendAda() {
        console.log('Test Send ADA button clicked - Opening modal');
        
        // Show the test send modal
        const testModal = new bootstrap.Modal(document.getElementById('testSendModal'));
        testModal.show();
        
        // Populate Blockfrost key if already saved
        const savedKey = window.BLOCKFROST_KEY || localStorage.getItem('BLOCKFROST_KEY') || '';
        if (savedKey) {
            document.getElementById('testBlockfrostKey').value = savedKey;
        }
        
        // Detect and list available wallets
        this.populateTestWalletList();
        
        // Setup submit button if not already done
        const submitBtn = document.getElementById('testSendSubmitBtn');
        if (submitBtn && !submitBtn.dataset.hasListener) {
            submitBtn.dataset.hasListener = 'true';
            submitBtn.addEventListener('click', () => this.executeTestTransaction());
        }
    }
    
    populateTestWalletList() {
        const walletList = document.getElementById('testWalletList');
        const statusDiv = document.getElementById('testWalletStatus');
        const statusText = document.getElementById('testWalletStatusText');
        
        if (!walletList) return;
        
        walletList.innerHTML = '';
        
        if (typeof window.cardano === 'undefined') {
            statusDiv.style.display = 'block';
            statusText.textContent = '❌ No Cardano wallets detected. Please install Lace wallet.';
            return;
        }
        
        const wallets = Object.keys(window.cardano);
        if (wallets.length === 0) {
            statusDiv.style.display = 'block';
            statusText.textContent = '❌ No wallets found.';
            return;
        }
        
        statusDiv.style.display = 'none';
        
        wallets.forEach(walletName => {
            const walletOption = document.createElement('div');
            walletOption.className = 'wallet-option';
            walletOption.dataset.testWallet = walletName;
            walletOption.innerHTML = `
                <img src="/static/notes/img/Icon-9.svg" alt="${walletName}" class="wallet-icon">
                <div class="wallet-info">
                    <div class="wallet-name">${walletName}</div>
                    <div class="wallet-description">Click to select ${walletName} wallet</div>
                </div>
            `;
            walletOption.addEventListener('click', () => this.selectTestWallet(walletName, walletOption));
            walletList.appendChild(walletOption);
            
            // Auto-select first wallet (usually lace)
            if (walletName === 'lace' || wallets.indexOf(walletName) === 0) {
                walletOption.click();
            }
        });
    }
    
    selectTestWallet(walletName, element) {
        console.log('Selected wallet for test:', walletName);
        
        // Remove previous selection
        document.querySelectorAll('[data-test-wallet]').forEach(el => {
            el.style.background = '';
            el.style.borderColor = '';
        });
        
        // Highlight selected wallet
        element.style.background = 'rgba(56, 75, 255, 0.2)';
        element.style.borderColor = '#384BFF';
        
        // Store selected wallet
        this.selectedTestWallet = walletName;
        
        // Update status
        const statusDiv = document.getElementById('testWalletStatus');
        const statusText = document.getElementById('testWalletStatusText');
        statusDiv.style.display = 'block';
        statusText.textContent = '✓ ' + walletName + ' selected';
    }
    
    async executeTestTransaction() {
        console.log('=== EXECUTING TEST TRANSACTION ===');
        
        const selectedWallet = this.selectedTestWallet;
        if (!selectedWallet) {
            alert('Please select a wallet first');
            return;
        }
        
        // Get form inputs
        const recipientAddress = document.getElementById('testRecipientAddress').value.trim();
        const amountAda = parseFloat(document.getElementById('testSendAmount').value.trim());
        const blockfrostKey = document.getElementById('testBlockfrostKey').value.trim();
        
        // Validate inputs
        if (!recipientAddress) {
            alert('Please enter recipient address');
            return;
        }
        if (!amountAda || amountAda <= 0) {
            alert('Please enter valid amount');
            return;
        }
        if (!blockfrostKey) {
            alert('Please enter Blockfrost Project ID');
            return;
        }
        
        // Show transaction log
        const logBox = document.getElementById('testTxLog');
        logBox.textContent = '';
        logBox.style.display = 'block';
        
        const appendLog = (label, value) => {
            logBox.textContent += `[${label}] ${value}\n`;
            logBox.scrollTop = logBox.scrollHeight;
        };
        
        try {
            appendLog('START', 'Initializing transaction...');
            console.log('Selected wallet:', selectedWallet);
            console.log('Recipient:', recipientAddress);
            console.log('Amount:', amountAda, 'ADA');
            
            // Convert ADA to lovelace (1 ADA = 1,000,000 lovelace)
            const amount = BigInt(Math.floor(amountAda * 1000000));
            
            // Check if Blaze SDK is loaded
            if (!window.Blaze || !window.Blockfrost || !window.WebWallet || !window.Core) {
                appendLog('ERROR', 'Blaze SDK not loaded');
                alert('Blaze SDK not loaded. Please refresh the page.');
                return;
            }
            
            const { Blaze, Blockfrost, WebWallet, Core } = window;
            
            // Connect to wallet
            appendLog('WALLET', 'Connecting to ' + selectedWallet + '...');
            const wallet = window.cardano[selectedWallet];
            if (!wallet) throw new Error(`Wallet ${selectedWallet} not found`);
            
            const api = await wallet.enable();
            appendLog('WALLET', 'Connected!');
            console.log('Connected to wallet API:', api);
            
            // Get wallet address
            appendLog('ADDRESS', 'Retrieving address...');
            const address = await api.getChangeAddress();
            appendLog('ADDRESS', address.substring(0, 20) + '...');
            console.log('Wallet address:', address);
            
            // Initialize Blockfrost provider
            appendLog('PROVIDER', 'Initializing Blockfrost...');
            const provider = new Blockfrost({
                network: 'cardano-preview',
                projectId: blockfrostKey,
            });
            appendLog('PROVIDER', 'Ready!');
            
            // Create wallet wrapper with UTXO cleaning
            appendLog('WRAPPER', 'Creating wallet wrapper...');
            const walletWrapper = {
                getNetworkId: async () => await api.getNetworkId(),
                getUtxos: async () => {
                    const utxos = await api.getUtxos();
                    return utxos.map(utxo => {
                        if (typeof utxo === 'string') {
                            return utxo.replace(/[\s\n\r]/g, '');
                        }
                        return utxo;
                    });
                },
                getUsedAddresses: async () => {
                    const addrs = await api.getUsedAddresses();
                    return addrs.map(a => typeof a === 'string' ? a.replace(/[\s\n\r]/g, '') : a);
                },
                getUnusedAddresses: async () => {
                    if (api.getUnusedAddresses) {
                        const addrs = await api.getUnusedAddresses();
                        return addrs.map(a => typeof a === 'string' ? a.replace(/[\s\n\r]/g, '') : a);
                    }
                    return [];
                },
                getChangeAddress: async () => {
                    const addr = await api.getChangeAddress();
                    return typeof addr === 'string' ? addr.replace(/[\s\n\r]/g, '') : addr;
                },
                getRewardAddresses: async () => {
                    const addrs = await api.getRewardAddresses();
                    return addrs.map(a => typeof a === 'string' ? a.replace(/[\s\n\r]/g, '') : a);
                },
                getCollateral: async () => {
                    if (api.getCollateral) {
                        const coll = await api.getCollateral();
                        return coll.map(c => typeof c === 'string' ? c.replace(/[\s\n\r]/g, '') : c);
                    }
                    return [];
                },
                signTx: async (tx, partialSign) => await api.signTx(tx, partialSign),
                signData: async (addr, payload) => {
                    if (api.signData) {
                        return await api.signData(addr, payload);
                    }
                    throw new Error('signData not supported');
                },
                submitTx: async (tx) => {
                    if (api.submitTx) {
                        return await api.submitTx(tx);
                    }
                    throw new Error('submitTx not supported');
                }
            };
            
            // Create WebWallet instance
            appendLog('WALLET', 'Creating WebWallet instance...');
            const webWallet = new WebWallet(walletWrapper);
            appendLog('WALLET', 'Ready!');
            
            // Create Blaze instance
            appendLog('BLAZE', 'Initializing Blaze...');
            const blaze = await Blaze.from(provider, webWallet);
            appendLog('BLAZE', 'Connected!');
            console.log('Blaze instance created:', blaze);
            
            // Parse recipient address
            appendLog('BUILD', 'Parsing recipient address...');
            const recipientAddr = Core.Address.fromBech32(recipientAddress);
            appendLog('BUILD', 'Building transaction...');
            
            // Build transaction
            const tx = await blaze
                .newTransaction()
                .payLovelace(recipientAddr, amount)
                .complete();
            
            appendLog('BUILD', 'Transaction built!');
            console.log('Transaction built');
            
            // Sign transaction
            appendLog('SIGN', 'Requesting wallet signature...');
            const signedTx = await blaze.signTransaction(tx);
            appendLog('SIGN', 'Signed!');
            console.log('Transaction signed');
            
            // Submit transaction
            appendLog('SUBMIT', 'Submitting to blockchain...');
            const txHash = await blaze.provider.postTransactionToChain(signedTx);
            
            appendLog('SUCCESS', 'Transaction submitted!');
            appendLog('HASH', txHash);
            console.log('Transaction hash:', txHash);
            
            // Save Blockfrost key
            try {
                localStorage.setItem('BLOCKFROST_KEY', blockfrostKey);
                window.BLOCKFROST_KEY = blockfrostKey;
            } catch (_) {}
            
            alert('✓ SUCCESS!\n\nTransaction Hash:\n' + txHash + '\n\nView on explorer:\nhttps://preview.cexplorer.io/tx/' + txHash);
            
        } catch (error) {
            console.error('Transaction failed:', error);
            const errorMsg = error.message || String(error);
            appendLog('ERROR', errorMsg);
            
            if (errorMsg.includes('offset') || errorMsg.includes('uint')) {
                alert('❌ CBOR Parsing Error\n\nThis is a known Blaze SDK 0.2.44 issue with Lace wallet UTXOs.\n\nTry:\n1. Refreshing the page\n2. Checking wallet balance\n3. Using a different wallet');
            } else if (errorMsg.includes('User rejected')) {
                alert('⚠ Transaction rejected by user');
            } else {
                alert('❌ Failed:\n\n' + errorMsg);
            }
        }
    }
    setupEventListeners() {
        console.log('setupEventListeners called');
        const disconnectBtn = document.getElementById('disconnectWallet');
        if (disconnectBtn) disconnectBtn.addEventListener('click', this.disconnectWallet);
        const walletButton = document.getElementById('walletConnectButton');
        if (walletButton) walletButton.addEventListener('click', () => { const m = new bootstrap.Modal(document.getElementById('walletModal')); m.show(); });
        const walletModal = document.getElementById('walletModal');
        if (walletModal) {
            walletModal.addEventListener('shown.bs.modal', () => { this.detectWallets(); });
            walletModal.addEventListener('hidden.bs.modal', () => { if (!this.isConnected) this.detectWallets(); });
        }
        window.addEventListener('walletConnected', (event) => { localStorage.setItem('connectedWallet', event.detail.walletName); });

        const sendBtn = document.getElementById('sendAdaBtn');
        const saveProviderBtn = document.getElementById('saveProviderBtn');
        const keyInput = document.getElementById('blockfrostKeyInput');
        // preload stored key into input
        try { if (keyInput) keyInput.value = (localStorage.getItem('BLOCKFROST_KEY') || window.BLOCKFROST_KEY || ''); } catch(_){}
        if (saveProviderBtn) {
            saveProviderBtn.addEventListener('click', () => {
                try {
                    const val = (keyInput && keyInput.value || '').trim();
                    if (!val) { alert('Enter a Blockfrost Project ID'); return; }
                    localStorage.setItem('BLOCKFROST_KEY', val);
                    window.BLOCKFROST_KEY = val;
                    alert('Provider settings saved');
                } catch (e) {
                    alert('Failed to save provider settings');
                }
            });
        }
        if (sendBtn) {
            sendBtn.addEventListener('click', async () => {
                if (!this.api) { alert('Connect a wallet first'); return; }
                const recipient = document.getElementById('recipientAddress').value.trim();
                // Convert ADA input to lovelace (1 ADA = 1_000_000 lovelace)
                const amountAda = parseFloat(document.getElementById('sendAmount').value.trim());
                if (!recipient || isNaN(amountAda) || amountAda <= 0) { alert('Enter recipient and amount'); return; }
                const amountLovelace = BigInt(Math.round(amountAda * 1_000_000));
                if (amountLovelace < 1_000_000n) {
                    alert('Amount is too low. Minimum is 1 ADA for a basic transfer.');
                    return;
                }
                try {
                    console.log('Recipient address (bech32):', recipient);
                    console.log('Amount (ADA):', amountAda);
                    console.log('Amount (lovelace):', amountLovelace.toString());
                    
                    const logBox = document.getElementById('txLogBox');
                    function appendLog(label, value) { if (logBox) { logBox.textContent += `${label}: ${value}\n`; } }
                    
                    const projectId = (function(){
                      try {
                        const fromWindow = (window.BLOCKFROST_KEY || '').trim();
                        const fromStorage = (localStorage.getItem('BLOCKFROST_KEY') || '').trim();
                        const chosen = fromWindow || fromStorage;
                        if (chosen) { try { localStorage.setItem('BLOCKFROST_KEY', chosen); } catch(_){} }
                        return chosen;
                      } catch(_) { return ''; }
                    })();
                    
                    if (!projectId || projectId.length < 10) {
                        alert('Please set your Blockfrost Project ID first');
                        return;
                    }
                    
                    // Check if Blaze is loaded (exactly as in React reference)
                    if (!window.Blaze || !window.Blockfrost || !window.WebWallet || !window.Core) {
                        alert('Blaze SDK not loaded. Please refresh the page.');
                        return;
                    }
                    
                    try {
                        // Exactly matching the React reference implementation
                        const { Blaze, Blockfrost, WebWallet, Core } = window;
                        
                        appendLog('Status', 'Initializing Blaze...');
                        
                        const provider = new Blockfrost({
                            network: 'cardano-preview',
                            projectId: projectId,
                        });
                        
                        // Debug: Check UTXOs format before creating wallet
                        const testUtxos = await this.api.getUtxos();
                        console.log('Raw UTXOs from wallet:', testUtxos);
                        console.log('First UTxO type:', typeof testUtxos[0]);
                        console.log('First UTxO sample:', testUtxos[0]?.substring(0, 200));
                        
                        // Create a wrapper that ensures UTXOs are valid hex strings
                        const walletWrapper = {
                            getNetworkId: async () => await this.api.getNetworkId(),
                            getUtxos: async () => {
                                const utxos = await this.api.getUtxos();
                                // Ensure each UTXO is a clean hex string
                                return utxos.map(utxo => {
                                    if (typeof utxo === 'string') {
                                        // Remove any whitespace, newlines, or invalid characters
                                        let cleaned = utxo.replace(/[\s\n\r]/g, '');
                                        // Ensure it's valid hex (only 0-9, a-f, A-F)
                                        if (!/^[0-9a-fA-F]+$/.test(cleaned)) {
                                            console.error('Invalid UTxO format:', utxo.substring(0, 100));
                                            throw new Error('Invalid UTxO hex format');
                                        }
                                        return cleaned;
                                    }
                                    return utxo;
                                });
                            },
                            getUsedAddresses: async () => {
                                const addrs = await this.api.getUsedAddresses();
                                return addrs.map(a => typeof a === 'string' ? a.replace(/[\s\n\r]/g, '') : a);
                            },
                            getUnusedAddresses: async () => {
                                if (this.api.getUnusedAddresses) {
                                    const addrs = await this.api.getUnusedAddresses();
                                    return addrs.map(a => typeof a === 'string' ? a.replace(/[\s\n\r]/g, '') : a);
                                }
                                return [];
                            },
                            getChangeAddress: async () => {
                                const addr = await this.api.getChangeAddress();
                                return typeof addr === 'string' ? addr.replace(/[\s\n\r]/g, '') : addr;
                            },
                            getRewardAddresses: async () => {
                                const addrs = await this.api.getRewardAddresses();
                                return addrs.map(a => typeof a === 'string' ? a.replace(/[\s\n\r]/g, '') : a);
                            },
                            getCollateral: async () => {
                                if (this.api.getCollateral) {
                                    const coll = await this.api.getCollateral();
                                    return coll.map(c => typeof c === 'string' ? c.replace(/[\s\n\r]/g, '') : c);
                                }
                                return [];
                            },
                            signTx: async (tx, partialSign) => await this.api.signTx(tx, partialSign),
                            signData: async (addr, payload) => {
                                if (this.api.signData) {
                                    return await this.api.signData(addr, payload);
                                }
                                throw new Error('signData not supported');
                            },
                            submitTx: async (tx) => {
                                if (this.api.submitTx) {
                                    return await this.api.submitTx(tx);
                                }
                                throw new Error('submitTx not supported');
                            }
                        };
                        
                        const wallet = new WebWallet(walletWrapper);
                        const blaze = await Blaze.from(provider, wallet);
                        
                        console.log('Blaze instance created:', blaze);
                        appendLog('Blaze', 'Connected');
                        
                        // Parse recipient address
                        const recipientAddress = Core.Address.fromBech32(recipient);
                        console.log('Recipient address parsed');
                        appendLog('Recipient', 'Parsed');
                        
                        // Build transaction (exactly as in React reference)
                        appendLog('Status', 'Building transaction...');
                        const tx = await blaze
                            .newTransaction()
                            .payLovelace(recipientAddress, amountLovelace)
                            .complete();
                        
                        console.log('Transaction built:', tx.toCbor());
                        appendLog('Build', 'Success');
                        
                        // Sign and submit using Blaze helpers
                        appendLog('Status', 'Signing transaction...');
                        const signedTx = await blaze.signTransaction(tx);
                        const signedTxHex = signedTx.toCbor();
                        appendLog('Sign', 'Success');
                        
                        const hexToBytes = (hex) => {
                            const clean = hex.startsWith('0x') ? hex.slice(2) : hex;
                            const bytes = new Uint8Array(clean.length / 2);
                            for (let i = 0; i < bytes.length; i++) {
                                bytes[i] = parseInt(clean.substr(i * 2, 2), 16);
                            }
                            return bytes;
                        };
                        
                        let txHash;
                        let submittedVia = 'wallet';
                        appendLog('Status', 'Submitting transaction via wallet...');
                        try {
                            if (!this.api.submitTx) { throw new Error('submitTx not available on wallet'); }
                            txHash = await this.api.submitTx(signedTxHex);
                        } catch (walletErr) {
                            console.warn('Wallet submission failed, falling back to Blockfrost', walletErr);
                            appendLog('Status', 'Wallet submit failed, retrying via Blockfrost...');
                            submittedVia = 'blockfrost';
                            try {
                                txHash = await blaze.submitTransaction(signedTx);
                            } catch (sdkErr) {
                                console.warn('Blaze submit failed, using manual Blockfrost call', sdkErr);
                                appendLog('Status', 'SDK submit failed, sending raw CBOR to Blockfrost...');
                                submittedVia = 'manual-blockfrost';
                                const response = await fetch('https://cardano-preview.blockfrost.io/api/v0/tx/submit', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/cbor',
                                        'project_id': projectId,
                                    },
                                    body: hexToBytes(signedTxHex)
                                });
                                if (!response.ok) {
                                    const errBody = await response.text();
                                    throw new Error(`Blockfrost submit failed (${response.status}): ${errBody}`);
                                }
                                txHash = await response.text();
                            }
                        }
                        
                        console.log(`Transaction submitted via ${submittedVia}. Hash:`, txHash);
                        appendLog('Tx Hash', `${txHash} (${submittedVia})`);
                        alert('Transaction submitted successfully!\n\nTx Hash: ' + txHash);
                        
                    } catch (error) {
                        console.error('Error submitting transaction:', error);
                        appendLog('Error', error.message || String(error));
                        alert('Transaction failed: ' + (error.message || error));
                    }
                } catch (e) {
                    console.error('Send ADA failed:', e);
                    appendLog('Error', e && e.message ? e.message : String(e));
                    alert('Send failed: ' + (e && e.message ? e.message : 'Unknown error'));
                }
            });
        }
        
        // TEST BUTTON - Use bound method
        const testButton = document.getElementById('testSendAdaButton');
        console.log('testSendAdaButton element:', testButton);
        if (testButton) {
            console.log('Test button found, attaching click listener');
            testButton.addEventListener('click', () => {
                console.log('Test button clicked!');
                this.handleTestSendAda();
            });
        } else {
            console.log('Test button NOT found in DOM');
        }
    }
}
document.addEventListener('DOMContentLoaded', () => { window.cardanoWalletManager = new CardanoWalletManager(); });