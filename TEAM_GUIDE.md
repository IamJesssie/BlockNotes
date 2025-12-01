# BlockNotes - Cardano Integration Team Guide

## 🎯 Project Overview

We're transforming BlockNotes from a Ganache-based notes app into a **Cardano-native decentralized application** where:
- Cardano wallet (Lace) = authentication
- Blockchain = permanent source of truth
- Local database = fast cache for instant UX
- Metadata = rich note data stored on-chain

## 🌳 Branch Strategy

- **feature/web3-ui-redesign**: Protected branch (do NOT modify, keep existing login/features)
- **feature/final**: Integration branch (copied from feature/web3-ui-redesign)
- **5 feature branches**: All branched from feature/final, all PRs merge back to feature/final

## 👥 Team Structure & Branch Assignments

### Branch 1: `feature/Lapure-Cardano-Wallet-Auth`
**Developer:** Lapure (You!)  
**Focus:** User authentication via Cardano Lace wallet connection  
**Base Branch:** feature/final  
**PR Target:** feature/final

**Key Files:**
- `note_app/static/notes/wallet.js` (NEW)
- `note_app/static/notes/cardano-config.js` (NEW)
- `note_app/notes/templates/notes/base.html` (MODIFY)
- `note_app/note_app/settings.py` (MODIFY)

**Deliverables:**
- Working "Connect Wallet" button
- Wallet address displayed in header
- **Keep existing Google OAuth intact** (don't remove it from feature/final)
- Tested with **Lace wallet** on Chrome with Cardano Preview network

---

### Branch 2: `feature/PepitoJL-Cardano-Metadata-Chunking`
**Developer:** PepitoJL  
**Focus:** Transaction building with metadata and chunking  
**Base Branch:** feature/final  
**PR Target:** feature/final

**Key Files:**
- `note_app/static/notes/cardano-transactions.js` (NEW)
- Integration with note editor/creation flow

**Deliverables:**
- `formatContent()` function for 64-byte chunking
- `sendTransaction()` function with Blaze SDK
- Metadata structure with label 42819n
- Actions: CREATE, UPDATE, DELETE

**Dependencies:** Branch 1 (needs wallet connection)

---

### Branch 3: `feature/PepitoJP-Dual-Storage-System`
**Developer:** PepitoJP  
**Focus:** Database schema redesign for wallet-based ownership  
**Base Branch:** feature/final  
**PR Target:** feature/final

**Key Files:**
- `note_app/notes/models.py` (MODIFY)
- `note_app/notes/migrations/0005_cardano_migration.py` (NEW)
- `note_app/notes/views.py` (MODIFY)
- `note_app/notes/templates/notes/list_notes.html` (MODIFY)

**Deliverables:**
- New Note model with `address`, `tx_hash`, `status` fields
- Migration from User FK to wallet address
- Views updated for wallet-based filtering
- Status badges (Pending/Confirmed/Failed) in UI

**Dependencies:** Branch 2 (needs tx_hash from transactions)

---

### Branch 4: `feature/Labuca-Blockfrost-Worker`
**Developer:** Labuca  
**Focus:** Background worker for transaction confirmation  
**Base Branch:** feature/final  
**PR Target:** feature/final

**Key Files:**
- `note_app/notes/management/commands/sync_transactions.py` (NEW)
- `note_app/notes/blockfrost.py` (NEW)
- `note_app/note_app/settings.py` (MODIFY)
- `.env` (MODIFY)

**Deliverables:**
- Blockfrost API client
- Background worker checking pending transactions every 20 seconds
- Status updates from 'pending' to 'confirmed'
- Worker runs via `python manage.py sync_transactions`

**Dependencies:** Branch 3 (needs status field in database)

**Setup Required:**
- Blockfrost account (https://blockfrost.io)
- Preview network Project ID

---

### Branch 5: `feature/Barrientos-Blockchain-Recovery`
**Developer:** Barrientos  
**Focus:** Restore notes from blockchain history  
**Base Branch:** feature/final  
**PR Target:** feature/final

**Key Files:**
- `note_app/notes/management/commands/restore_from_blockchain.py` (NEW)
- `note_app/static/notes/blockchain-recovery.js` (NEW)
- `note_app/notes/utils.py` (NEW - helper functions)
- `note_app/notes/views.py` (ADD restore endpoint)
- `note_app/notes/templates/notes/blockchain_proof.html` (MODIFY)

**Deliverables:**
- "Sync from Blockchain" button in UI
- Fetch all transactions for wallet address
- Parse metadata (handle de-chunking)
- Rebuild local database
- Updated blockchain proof page with Cardano Explorer links

**Dependencies:** Branch 4 (needs Blockfrost client)

---

## 🚀 Getting Started

### 1. Run Branch Setup Script

```powershell
cd "d:\CSIT360 BLOCKCHAIN\Blocknotes"
.\setup_branches.ps1
```

This creates all 5 feature branches.

### 2. Assign Branches to Team Members

Each team member should:
```bash
git checkout <your-branch-name>
```

### 3. Review Documentation

- **implementation_plan.md**: Detailed technical specifications for each branch
- **task.md**: Checklist of tasks for each branch

### 4. Set Up Environment

**All team members need:**
1. **Lace wallet extension** for Chrome: https://www.lace.io/
2. Switch wallet to **Cardano Preview** network (Settings → Network → Preview)
3. Get test ADA from Preview faucet: https://docs.cardano.org/cardano-testnet/tools/faucet/

**Branch 4 & 5 team members additionally need:**
1. Blockfrost account: https://blockfrost.io
2. Create Preview network project
3. Copy Project ID to `.env` file:
   ```
   BLOCKFROST_PROJECT_ID=preview...your_project_id
   BLOCKFROST_API_URL=https://cardano-preview.blockfrost.io/api/v0
   ```

### 5. Install Dependencies

**Branch 1 & 2 (Frontend/Blockchain devs):**
```bash
# Blaze SDK is loaded via CDN in HTML, no npm install needed
# But for testing chunking logic, optionally:
npm init -y
npm install @blaze-cardano/sdk
```

**Branch 3, 4, 5 (Backend devs):**
```bash
pip install requests celery redis
```

---

## 🔀 Merge Strategy

All branches merge into **feature/final** via Pull Requests:

```
feature/web3-ui-redesign (PROTECTED - Do not modify)
  ↓
feature/final (Integration branch)
  ↑
  ├── PR from feature/Lapure-Cardano-Wallet-Auth (Lapure)
  ├── PR from feature/PepitoJL-Cardano-Metadata-Chunking (PepitoJL)
  ├── PR from feature/PepitoJP-Dual-Storage-System (PepitoJP)
  ├── PR from feature/Labuca-Blockfrost-Worker (Labuca)
  └── PR from feature/Barrientos-Blockchain-Recovery (Barrientos)
```

**Process:**
1. All 5 branches are created from **feature/final**
2. Each developer works on their feature branch
3. When ready, create Pull Request: `feature/cardano-xxx → feature/final`
4. Merge order: Branch 1 → 2 → 3 → 4 → 5 (into feature/final)
5. After each merge, other developers should pull latest feature/final:
   ```bash
   git checkout feature/final
   git pull origin feature/final
   git checkout <your-branch>
   git merge feature/final  # or git rebase feature/final
   ```
---

## ✅ Testing Checklist

### Individual Branch Testing

Each developer should test their branch independently before merging:

**Branch 1:**
- [ ] Connect wallet button appears and works
- [ ] Wallet address displays in header
- [ ] Can disconnect and reconnect
- [ ] Works in Chrome, Firefox

**Branch 2:**
- [ ] `formatContent()` correctly chunks long strings
- [ ] Transaction signs and submits to blockchain
- [ ] Returns transaction hash
- [ ] Metadata visible in Cardano Explorer

**Branch 3:**
- [ ] Notes save with wallet address (not user ID)
- [ ] Status defaults to 'pending'
- [ ] Transaction hash stores correctly
- [ ] Status badge shows in UI

**Branch 4:**
- [ ] Worker starts without errors
- [ ] Detects pending notes
- [ ] Calls Blockfrost API
- [ ] Updates status to 'confirmed' after ~40 seconds

**Branch 5:**
- [ ] "Sync from Blockchain" button appears
- [ ] Fetches transactions from Blockfrost
- [ ] Reconstructs chunked content
- [ ] Rebuilds database correctly

### Integration Testing (After All Merges)

- [ ] Full flow: Connect wallet → Create note → See pending → Auto-confirm
- [ ] Delete local database → Restore from blockchain → All notes back
- [ ] Multiple wallets see only their own notes
- [ ] Long notes (>500 chars) correctly chunk and reconstruct

---

## 🛠️ Development Tips

### For Branch 1 (Wallet Auth)
- Use `window.cardano` to detect wallets
- Check `window.cardano.lace` for Lace wallet
- Enable wallet must be called on user action (button click)
- **Do NOT remove existing Google OAuth** from feature/final
- Store wallet API handle in sessionStorage, not localStorage

### For Branch 2 (Metadata)
- Import Blaze: `import { Blaze, Core } from "@blaze-cardano/sdk"`
- Remember BigInt suffix: `42819n` not `42819`
- Use `Core.Metadatum.newText()` for strings
- Use `Core.Metadatum.newList()` for arrays

### For Branch 3 (Database)
- Create migration carefully, test on fresh DB first
- Use `@wallet_required` decorator instead of `@login_required`
- Index `address` and `status` fields for performance
- Remember to filter by `is_deleted=False` in queries

### For Branch 4 (Worker)
- Use `requests.get()` with headers `{'project_id': BLOCKFROST_PROJECT_ID}`
- Handle rate limits gracefully
- Log all API calls for debugging
- Use `time.sleep(20)` for 20-second intervals

### For Branch 5 (Recovery)
- Blockfrost returns metadata as JSON with numeric keys
- Convert keys to int: `metadata.get(str(42819))`
- Reconstruct chunks in order: `"".join(chunks)`
- Handle transactions without metadata (skip them)

---

## 📚 Resources

**Cardano Wallets:**
- **Lace (Primary)**: https://www.lace.io/
- Nami: https://namiwallet.io
- Eternl: https://eternl.io

**Cardano Development:**
- Blaze SDK Docs: https://blaze.butane.dev
- Cardano Serialization Lib: https://github.com/Emurgo/cardano-serialization-lib
- Preview Testnet Faucet: https://docs.cardano.org/cardano-testnet/tools/faucet/

**Blockfrost API:**
- Docs: https://docs.blockfrost.io
- API Reference: https://docs.blockfrost.io/#tag/Cardano-Transactions
- Dashboard: https://blockfrost.io/dashboard

**Cardano Explorers:**
- Preview: https://preview.cardanoscan.io
- Mainnet: https://cardanoscan.io

---

## 🆘 Common Issues & Solutions

### Issue: Wallet not detected
**Solution:** 
1. Ensure Lace extension is installed in Chrome
2. Lace must be on localhost or HTTPS
3. Check wallet is set to Preview network (not Preprod or Mainnet)
4. Reload page after switching network

### Issue: Transaction fails with "insufficient funds"
**Solution:** Get test ADA from Preview faucet. Need ~5 tADA for testing.

### Issue: Blockfrost returns 403 Forbidden
**Solution:** Check `project_id` in headers (NOT query params). Verify Project ID is for Preview network.

### Issue: Worker doesn't update status
**Solution:** 
1. Check worker is running: `ps aux | grep sync_transactions`
2. Check Blockfrost API quota (500 req/day free)
3. Verify transaction is actually on-chain (use Cardano Explorer)

### Issue: Chunking reconstruction fails
**Solution:** Ensure you're joining chunks in correct order. Blockfrost returns them as list, join with `"".join(chunks)`.

---

## 🎯 Success Criteria

Your team is successful when:

1. ✅ User can connect wallet and see their address
2. ✅ Creating a note sends a transaction to Cardano Preview
3. ✅ Note appears immediately with "Pending" status
4. ✅ After ~40 seconds, status automatically updates to "Confirmed"
5. ✅ Blockchain proof page shows transaction on Cardano Explorer
6. ✅ Deleting local database and clicking "Sync from Blockchain" restores all notes
7. ✅ Different wallets see different notes (privacy)
8. ✅ Long notes (>500 characters) work correctly

---

**Good luck! 🚀**

If you have questions about your specific branch, refer to the detailed implementation_plan.md file.
