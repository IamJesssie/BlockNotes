// cardano_wallet.js - improved wallet manager
(function(global) {
  const RETRY_ATTEMPTS = 20;
  const RETRY_DELAY_MS = 150; // total ~3s
  const MIN_LOVELACE = 1; // 1 lovelace as requested

  class CardanoWalletManager {
    constructor() {
      this.walletApi = null;
      this.selectedWallet = null;
      this.walletAddress = null;
      this.availableWallets = [];
      this.status = 'not-detected'; // 'not-detected'|'available'|'connected'|'error'
      this._listeners = { status: [] };
      this._init();
    }

    // observable status
    on(event, cb) {
      if (!this._listeners[event]) this._listeners[event] = [];
      this._listeners[event].push(cb);
    }
    _emit(event, payload) {
      (this._listeners[event] || []).forEach(cb => {
        try { cb(payload); } catch(e){ console.error(e); }
      });
    }

    // backwards-compatible alias for old UI code
    async connectWallet(walletName = 'lace') {
        return await this.connect(walletName);
    }


    async _init() {
      // wait a little for wallets to inject themselves
      for (let i=0;i<RETRY_ATTEMPTS;i++){
        if (typeof window.cardano !== 'undefined') break;
        await new Promise(r => setTimeout(r, RETRY_DELAY_MS));
      }
      this.detectWallets();
      // watch for dynamic injection (some wallets inject after page load)
      if (typeof window.cardano !== 'undefined' && typeof window.cardano.on === 'function') {
        try {
          window.cardano.on('cardano#connected', () => this.detectWallets());
        } catch(e) { /* ignore */ }
      }
    }

    detectWallets() {
      if (typeof window.cardano === 'undefined') {
        console.warn('Cardano object not present');
        this.availableWallets = [];
        this.status = 'not-detected';
        this._emit('status', this.status);
        return;
      }
      // List wallet keys that have enable()
      this.availableWallets = Object.keys(window.cardano).filter(k => {
        try {
          const w = window.cardano[k];
          return w && typeof w.enable === 'function';
        } catch(e) { return false; }
      });
      console.log('Available wallets:', this.availableWallets);
      this.status = this.availableWallets.length ? 'available' : 'not-detected';
      this._emit('status', this.status);
    }

    getAvailableWallets() {
      return this.availableWallets.slice();
    }

    async connect(walletName = 'lace') {
      if (this.status === 'not-detected') {
        this.detectWallets();
        if (this.status === 'not-detected') {
          throw new Error('No Cardano wallets detected');
        }
      }
      if (!window.cardano || !window.cardano[walletName]) {
        throw new Error(`Wallet ${walletName} not found`);
      }
      try {
        const provider = window.cardano[walletName];
        // prefer isEnabled if exists
        if (typeof provider.isEnabled === 'function') {
          const already = await provider.isEnabled();
          this.walletApi = already ? await provider.enable() : await provider.enable();
        } else {
          this.walletApi = await provider.enable();
        }
        this.selectedWallet = walletName;

        // get addresses (CBOR or bech32 strings depending on wallet)
        const used = (await this.walletApi.getUsedAddresses()) || [];
        const unused = (await this.walletApi.getUnusedAddresses()) || [];
        const change = await (this.walletApi.getChangeAddress ? this.walletApi.getChangeAddress() : Promise.resolve(null));
        // prefer bech32 addresses, otherwise decode CBOR -> hex (keep as string)
        function toStr(a) {
          try { if (Array.isArray(a)) return a[0]; return a; } catch(e){ return a; }
        }
        const all = [...used, ...unused, change].filter(Boolean).map(toStr);
        this.walletAddress = all.find(x => typeof x === 'string' && x.startsWith('addr')) || (all.length ? all[0] : null);

        this.status = 'connected';
        this._emit('status', this.status);
        console.log('Wallet connected:', walletName, 'address:', this.walletAddress);
        return { success:true, wallet: walletName, address: this.walletAddress, api: this.walletApi };
      } catch (e) {
        this.status = 'error';
        this._emit('status', this.status);
        console.error('connect error', e);
        throw e;
      }
    }

    isConnected() {
      return this.walletApi !== null;
    }

    // sign data (hex payload) using signData (CIP-8)
    async signPayload(addressForSigning, hexPayload, timeoutMs = 30000) {
      if (!this.walletApi || typeof this.walletApi.signData !== 'function') {
        throw new Error('signData not supported by wallet API');
      }
      const signPromise = this.walletApi.signData(addressForSigning, hexPayload);
      const timer = new Promise((_, reject) => setTimeout(() => reject(new Error('signData timeout')), timeoutMs));
      return await Promise.race([signPromise, timer]);
    }

    // prepare Blaze-like metadata for CIP-68 (example)
    buildCIP68Metadata(transactionData) {
      // CIP-68 generally targets NFTs (label 721 for NFT metadata). We use a compact structure.
      // You can change '721' to whichever label you prefer.
      const label = '721';
      const metadata = {
        [label]: {
          'BlockNotes': {
            [String(transactionData.note_id)]: {
              name: transactionData.title ? transactionData.title.slice(0, 64) : `note-${transactionData.note_id}`,
              description: `BlockNotes ${transactionData.operation} #${transactionData.note_id}`,
              note_hash: transactionData.note_hash,
              operation: transactionData.operation,
              content_length: transactionData.content_length || 0,
              created_by_wallet: this.walletAddress || null
            }
          }
        }
      };
      return { label, metadata };
    }

    // High-level helper executed by UI code:
    // - connect if needed
    // - prepare metadata (CIP-68)
    // - send prepare request to backend
    // - sign payload (note_hash) using signData
    // - call backend confirm endpoint with signature and metadata
    async processNoteTransaction(transactionData, receiverAddress='/dev/null') {
      // ensure wallet connected
      if (!this.isConnected()) {
        await this.connect(this.selectedWallet || 'lace');
      }
      // prepare CIP-68 metadata locally
      const { label, metadata } = this.buildCIP68Metadata(transactionData);

      // send to backend to prepare tx (backend can build tx or return template)
      const prep = await fetch('/notes/api/prepare_transaction/', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
          transaction_data: transactionData,
          metadata_label: label,
          metadata: metadata,
          receiver_address: receiverAddress,
          min_lovelace: MIN_LOVELACE
        })
      }).then(r => r.json());

      if (!prep.success) {
        throw new Error(prep.error || 'prepare_transaction failed');
      }

      // The backend can either return a transaction_cbor to sign+submit,
      // or we will just sign the note hash (CIP-8) and let backend record placeholder.
      const payloadHex = (transactionData.note_hash || '').replace(/^0x/, '');
      // find address for signing: prefer bech32 if available
      let signingAddr = null;
      try {
        const used = (await this.walletApi.getUsedAddresses()) || [];
        signingAddr = used.find(a => typeof a === 'string' && a.startsWith('addr')) || (await this.walletApi.getChangeAddress()) || (used[0] || null);
        if (typeof signingAddr !== 'string') {
          // If address is bytes CBOR, convert to hex string representation - many wallets return strings though
          signingAddr = String(signingAddr);
        }
      } catch (e) {
        console.warn('Could not get specific signing address, will attempt with change address', e);
        signingAddr = this.walletAddress || null;
      }
      if (!signingAddr) throw new Error('No address available for signing');

      // Do signData (CIP-8)
      const signResp = await this.signPayload(signingAddr, payloadHex);
      // signResp usually: { signature: CBOR/Uint8Array or hex, key: CBOR/Uint8Array or hex }
      // convert to hex-friendly strings
      function toHexString(data) {
        if (!data) return null;
        if (typeof data === 'string') return data;
        if (data instanceof Uint8Array) {
          return Array.from(data).map(b => b.toString(16).padStart(2,'0')).join('');
        }
        if (data instanceof ArrayBuffer) {
          const u = new Uint8Array(data);
          return Array.from(u).map(b => b.toString(16).padStart(2,'0')).join('');
        }
        try { return JSON.stringify(data); } catch(e){ return String(data); }
      }
      const signature = {
        signature: toHexString(signResp.signature || signResp.sig || signResp),
        key: toHexString(signResp.key || signResp.publicKey || null),
        address: signingAddr,
        payload: payloadHex
      };

      // Confirm with backend (send signature + metadata)
      const confirmResp = await fetch('/notes/api/confirm_transaction/', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
          tx_hash: prep.tx_hash || `pending_${Date.now()}_${payloadHex.slice(0,16)}`,
          note_id: transactionData.note_id,
          operation: transactionData.operation,
          signature_data: signature,
          metadata_label: label,
          metadata: metadata,
          network: prep.network || 'testnet'
        })
      }).then(r => r.json());

      if (!confirmResp.success) {
        throw new Error(confirmResp.error || 'confirm_transaction failed');
      }
      return confirmResp;
    }
  }

  // expose
  global.cardanoWalletManager = new CardanoWalletManager();

  // small helper for CSRF
  function getCsrfToken() {
    const cookies = document.cookie ? document.cookie.split(';') : [];
    for (let cookie of cookies) {
      const [n,v] = cookie.trim().split('=');
      if (n === 'csrftoken') return v;
    }
    const meta = document.querySelector('meta[name="csrf-token"]') || document.querySelector('meta[name="csrfmiddlewaretoken"]');
    if (meta) return meta.getAttribute('content');
    return '';
  }
})(window);
