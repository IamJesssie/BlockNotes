# Quick Start Guide - Cardano Integration

## 🚀 Setup (Run Once)

### 1. Create All Branches

From `feature/web3-ui-redesign` branch, run:

```powershell
.\setup_branches.ps1
```

This will:
- ✅ Create `feature/final` from `feature/web3-ui-redesign`
- ✅ Create 5 feature branches from `feature/final`
- ✅ Keep `feature/web3-ui-redesign` untouched

## 👥 Team Workflow

### Developer Setup

1. **Install Lace Wallet**
   - Chrome: https://www.lace.io/
   - Set network to **Cardano Preview** (Settings → Network → Preview)
   - Get test ADA: https://docs.cardano.org/cardano-testnet/tools/faucet/

2. **Checkout Your Branch**
   ```bash
   git checkout <your-assigned-branch>
   ```

3. **Start Coding**
   - See `TEAM_GUIDE.md` for your branch's deliverables
   - See `implementation_plan.md` for detailed specs

### Pull Request Workflow

When your work is ready:

```bash
# 1. Commit your changes
git add .
git commit -m "feat: your feature description"

# 2. Pull latest feature/final (in case someone merged before you)
git checkout feature/final
git pull origin feature/final

# 3. Merge feature/final into your branch
git checkout <your-branch>
git merge feature/final
# Resolve any conflicts if needed

# 4. Push your branch
git push origin <your-branch>

# 5. Create Pull Request on GitHub/GitLab
# Source: <your-branch>
# Target: feature/final
```

## 🔄 After Someone Else's PR Gets Merged

Stay in sync with `feature/final`:

```bash
git checkout feature/final
git pull origin feature/final
git checkout <your-branch>
git merge feature/final  # or: git rebase feature/final
```

## 📋 Branch Assignments

| Branch | Developer | Focus |
|--------|-----------|-------|
| `feature/Lapure-Cardano-Wallet-Auth` | **Lapure (You)** | Lace wallet connection UI |
| `feature/PepitoJL-Cardano-Metadata-Chunking` | **PepitoJL** | Transaction metadata & chunking |
| `feature/PepitoJP-Dual-Storage-System` | **PepitoJP** | Database schema for wallet ownership |
| `feature/Labuca-Blockfrost-Worker` | **Labuca** | Background transaction confirmation |
| `feature/Barrientos-Blockchain-Recovery` | **Barrientos** | Restore notes from blockchain |

## 🎯 Merge Order

Merge PRs in this sequence (dependencies):

1. ✅ `feature/Lapure-Cardano-Wallet-Auth` → `feature/final` (Lapure)
2. ✅ `feature/PepitoJL-Cardano-Metadata-Chunking` → `feature/final` (PepitoJL - needs wallet)
3. ✅ `feature/PepitoJP-Dual-Storage-System` → `feature/final` (PepitoJP - needs tx_hash)
4. ✅ `feature/Labuca-Blockfrost-Worker` → `feature/final` (Labuca - needs status field)
5. ✅ `feature/Barrientos-Blockchain-Recovery` → `feature/final` (Barrientos - needs Blockfrost)

## ⚠️ Important Notes

- **DO NOT modify `feature/web3-ui-redesign`** - It stays as-is
- **DO NOT remove Google OAuth** in Branch 1 - Keep it intact
- **Use Lace wallet** for testing (not Nami/Eternl)
- **Preview network only** - Not Preprod or Mainnet
- Test with **Chrome browser** + Lace extension

## 🧪 Quick Test

After each branch merge, test:

```bash
# Branch 1: Wallet connection
- Click "Connect Wallet" → Lace opens → Approve → See address in header

# Branch 2: Create note
- Create note → Approve transaction in Lace → See tx_hash

# Branch 3: Dual storage
- Note shows "Pending" status immediately
- Note has tx_hash stored

# Branch 4: Worker
- Run: python manage.py sync_transactions
- Wait 40 sec → Status changes to "Confirmed"

# Branch 5: Recovery
- Click "Sync from Blockchain" → All notes restore from chain
```

## 📞 Need Help?

- **Technical specs**: See `implementation_plan.md`
- **Team workflow**: See `TEAM_GUIDE.md`
- **Task checklist**: See artifacts in `.gemini/antigravity/brain/.../task.md`
- **Lace docs**: https://www.lace.io/faq
- **Blockfrost API**: https://docs.blockfrost.io/
