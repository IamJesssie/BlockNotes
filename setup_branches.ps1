# BlockNotes Cardano Integration - Branch Setup Script
# This script creates feature/final integration branch and 5 feature branches for team collaboration

Write-Host "🚀 Setting up Cardano Integration Feature Branches for BlockNotes" -ForegroundColor Cyan
Write-Host ""

# Get current branch
$currentBranch = git rev-parse --abbrev-ref HEAD
Write-Host "📍 Current branch: $currentBranch" -ForegroundColor Yellow

# Check if we're on feature/web3-ui-redesign
if ($currentBranch -ne "feature/web3-ui-redesign") {
    Write-Host "⚠️  WARNING: You should run this from 'feature/web3-ui-redesign' branch" -ForegroundColor Yellow
    Write-Host "   Current branch: $currentBranch" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne 'y') {
        Write-Host "❌ Aborted" -ForegroundColor Red
        exit
    }
}

Write-Host ""
Write-Host "This will:" -ForegroundColor Cyan
Write-Host "  1. Create 'feature/final' branch (integration branch) from current branch" -ForegroundColor White
Write-Host "  2. Create 5 feature branches from 'feature/final'" -ForegroundColor White
Write-Host "  3. Keep 'feature/web3-ui-redesign' untouched" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Continue? (y/n)"
if ($confirm -ne 'y') {
    Write-Host "❌ Aborted" -ForegroundColor Red
    exit
}

# Step 1: Create feature/final from current branch
Write-Host ""
Write-Host "📦 Step 1: Creating integration branch 'feature/final'" -ForegroundColor Cyan

$finalExists = git rev-parse --verify feature/final 2>$null
if ($finalExists) {
    Write-Host "   ⚠️  Branch 'feature/final' already exists" -ForegroundColor Yellow
    $recreate = Read-Host "   Recreate it from current branch? This will DELETE existing feature/final (y/n)"
    if ($recreate -eq 'y') {
        git branch -D feature/final 2>$null
        git branch feature/final
        Write-Host "   ✅ Recreated 'feature/final' from $currentBranch" -ForegroundColor Green
    } else {
        Write-Host "   ⏭️  Keeping existing 'feature/final'" -ForegroundColor Yellow
    }
} else {
    git branch feature/final
    Write-Host "   ✅ Created 'feature/final' from $currentBranch" -ForegroundColor Green
}

# Step 2: Switch to feature/final to create other branches from it
Write-Host ""
Write-Host "📦 Step 2: Creating 5 feature branches from 'feature/final'" -ForegroundColor Cyan
git checkout feature/final 2>$null

# Array of feature branches with team member names
$branches = @(
    "feature/Lapure-Cardano-Wallet-Auth",
    "feature/PepitoJL-Cardano-Metadata-Chunking",
    "feature/PepitoJP-Dual-Storage-System",
    "feature/Labuca-Blockfrost-Worker",
    "feature/Barrientos-Blockchain-Recovery"
)

# Create each branch from feature/final
foreach ($branch in $branches) {
    Write-Host "   🌿 Creating: $branch" -ForegroundColor Green
    
    $exists = git rev-parse --verify $branch 2>$null
    if ($exists) {
        Write-Host "      ⚠️  Already exists, skipping..." -ForegroundColor Yellow
    } else {
        git branch $branch
        Write-Host "      ✅ Created successfully" -ForegroundColor Green
    }
}

# Switch back to original branch
git checkout $currentBranch 2>$null

Write-Host ""
Write-Host "✨ Branch setup complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Branch Structure:" -ForegroundColor Cyan
Write-Host "   feature/web3-ui-redesign (PROTECTED - Do not modify)" -ForegroundColor Yellow
Write-Host "   └── feature/final (Integration branch)" -ForegroundColor Green
Write-Host "       ├── feature/Lapure-Cardano-Wallet-Auth (Lapure)" -ForegroundColor White
Write-Host "       ├── feature/PepitoJL-Cardano-Metadata-Chunking (PepitoJL)" -ForegroundColor White
Write-Host "       ├── feature/PepitoJP-Dual-Storage-System (PepitoJP)" -ForegroundColor White
Write-Host "       ├── feature/Labuca-Blockfrost-Worker (Labuca)" -ForegroundColor White
Write-Host "       └── feature/Barrientos-Blockchain-Recovery (Barrientos)" -ForegroundColor White
Write-Host ""
Write-Host "👥 Team Assignment Recommendations:" -ForegroundColor Cyan
Write-Host "   1️⃣  feature/Lapure-Cardano-Wallet-Auth        → Lapure (Frontend - Lace Wallet)" -ForegroundColor White
Write-Host "   2️⃣  feature/PepitoJL-Cardano-Metadata-Chunking → PepitoJL (Blockchain - TX Metadata)" -ForegroundColor White
Write-Host "   3️⃣  feature/PepitoJP-Dual-Storage-System      → PepitoJP (Backend - Database)" -ForegroundColor White
Write-Host "   4️⃣  feature/Labuca-Blockfrost-Worker          → Labuca (DevOps - Worker)" -ForegroundColor White
Write-Host "   5️⃣  feature/Barrientos-Blockchain-Recovery    → Barrientos (Full-Stack - Recovery)" -ForegroundColor White
Write-Host ""
Write-Host "🔀 Pull Request Workflow:" -ForegroundColor Cyan
Write-Host "   Each feature branch → Pull Request → feature/final" -ForegroundColor Yellow
Write-Host "   Merge order: 1 → 2 → 3 → 4 → 5 (into feature/final)" -ForegroundColor Yellow
Write-Host ""
Write-Host "📖 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Review TEAM_GUIDE.md for detailed workflow" -ForegroundColor White
Write-Host "   2. Assign branches to team members" -ForegroundColor White
Write-Host "   3. Each member: git checkout <branch-name>" -ForegroundColor White
Write-Host "   4. Start implementing, then create PR to feature/final" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Current branch: $currentBranch" -ForegroundColor Green
