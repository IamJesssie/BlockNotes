# 🚀 BlockNotes - Complete Render Deployment Guide

**For Team Members Deploying to Production**

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Understanding the Project Structure](#understanding-the-project-structure)
3. [Step-by-Step Deployment](#step-by-step-deployment)
4. [Environment Variables Configuration](#environment-variables-configuration)
5. [Post-Deployment Setup](#post-deployment-setup)
6. [Testing the Deployment](#testing-the-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Important Notes](#important-notes)

---

## ✅ Prerequisites

Before you start, make sure you have:

- [ ] **GitHub Account** with access to `IamJesssie/BlockNotes` repository
- [ ] **Render Account** (free tier is fine) - Sign up at [render.com](https://render.com)
- [ ] **Google OAuth Credentials** (get these from the project owner):
  - Google Client ID
  - Google Client Secret
- [ ] Access to this branch: `feature/web3-ui-redesign`

---

## 📁 Understanding the Project Structure

The `feature/web3-ui-redesign` branch contains:

```
BlockNotes/
├── note_app/                    # Main Django application
│   ├── manage.py               # Django management script
│   ├── note_app/               # Project settings
│   ├── notes/                  # Notes app (main functionality)
│   ├── static/                 # Static files (CSS, JS, images)
│   └── templates/              # HTML templates
├── UIUX protype/               # UI/UX design files
├── ganache-data/               # Blockchain data (local only)
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── build.sh                    # ⭐ Render build script
├── render.yaml                 # ⭐ Render deployment blueprint
├── requirements.txt            # ⭐ Python dependencies
├── DEPLOYMENT_GUIDE.md         # General deployment info
├── OAUTH_SETUP_GUIDE.md        # OAuth setup details
├── GOOGLE_CONSOLE_SETUP.md     # Google Console configuration
└── README.md                   # Project description

⭐ = Critical files for Render deployment
```

### Key Files Explained:

| File | Purpose |
|------|---------|
| `render.yaml` | Tells Render how to deploy (blueprint) |
| `build.sh` | Automated build script (installs deps, runs migrations) |
| `requirements.txt` | Lists all Python packages needed |
| `.env.example` | Template showing what environment variables are needed |

---

## 🚀 Step-by-Step Deployment

### **Step 1: Sign Up / Log In to Render**

1. Go to [https://render.com](https://render.com)
2. Click **"Get Started for Free"** or **"Sign In"**
3. **Recommended:** Sign in with your GitHub account (makes connection easier)
4. Authorize Render to access your GitHub repositories

---

### **Step 2: Connect GitHub Repository**

1. In Render Dashboard, click **"New +"** button (top right)
2. Select **"Blueprint"**
3. You'll see "Connect a repository" screen
4. Click **"Connect GitHub"** if not already connected
5. Search for: `IamJesssie/BlockNotes`
6. Click **"Connect"** next to the repository

> **Note:** If you don't see the repository, you may need to configure GitHub App permissions to grant Render access.

---

### **Step 3: Deploy Using Blueprint**

1. After connecting the repository, you'll see "Create resources from Blueprint"
2. **Select Branch:** `feature/web3-ui-redesign` (very important!)
3. Render will automatically detect the `render.yaml` file
4. You'll see a preview showing:
   - ✅ **Web Service:** `blocknotes`
   - ✅ **Database:** `blocknotes-db` (PostgreSQL)
5. **Blueprint Name:** Leave as default or name it `blocknotes-production`
6. Click **"Apply"**

**What happens next:**
- Render creates a PostgreSQL database
- Render creates a web service
- Starts the build process automatically

---

### **Step 4: Wait for Initial Build**

You'll be redirected to the service dashboard. You'll see:

1. **Database:** `blocknotes-db` - Status: "Creating..." → "Available" (1-2 min)
2. **Web Service:** `blocknotes` - Status: "Building..." → "Deploying..." → "Live"

**Build Process (5-10 minutes):**
```
Building...
├── Cloning repository
├── Running build.sh
│   ├── Installing Python dependencies
│   ├── Collecting static files
│   └── Running database migrations
└── Starting application
```

⚠️ **IMPORTANT:** The first build will **FAIL** because environment variables are not set yet. This is expected!

You'll see an error like:
```
Error: ALLOWED_HOSTS is not set
```

This is normal - we'll fix it in the next step.

---

## ⚙️ Environment Variables Configuration

### **Step 5: Set Required Environment Variables**

1. In Render Dashboard, click on your **`blocknotes`** web service
2. Go to **"Environment"** tab (left sidebar)
3. You'll see some variables already set:
   - `PYTHON_VERSION` = 3.11.0 ✅
   - `DEBUG` = False ✅
   - `SECRET_KEY` = (auto-generated) ✅
   - `DATABASE_URL` = (auto-set from database) ✅

4. **Add the following variables manually:**

Click **"Add Environment Variable"** for each:

#### **Required Variables:**

| Key | Value | Example |
|-----|-------|---------|
| `ALLOWED_HOSTS` | Your Render app URL | `blocknotes-abc123.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | Your Render app URL with https:// | `https://blocknotes-abc123.onrender.com` |
| `GOOGLE_CLIENT_ID` | From project owner | `943365069887-h47i0qu9u77pucn0p4kpuafh5j156nda.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | From project owner | `YOUR_GOOGLE_CLIENT_SECRET_HERE` |

#### **How to find your Render app URL:**
- Look at the top of your service page
- It will be something like: `https://blocknotes-abc123.onrender.com`
- Copy this URL (without https:// for ALLOWED_HOSTS, with https:// for CSRF_TRUSTED_ORIGINS)

#### **Example Configuration:**

```
ALLOWED_HOSTS=blocknotes-abc123.onrender.com
CSRF_TRUSTED_ORIGINS=https://blocknotes-abc123.onrender.com
GOOGLE_CLIENT_ID=943365069887-h47i0qu9u77pucn0p4kpuafh5j156nda.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET_HERE
```

5. Click **"Save Changes"**

**What happens:**
- Render will automatically trigger a new deployment
- This time it should succeed!

---

### **Step 6: Monitor the Deployment**

1. Go to **"Logs"** tab to watch the deployment
2. You should see:
   ```
   ==> Building...
   ==> Installing dependencies from requirements.txt
   ==> Collecting static files
   ==> Running migrations
   ==> Starting server with gunicorn
   ==> Your service is live 🎉
   ```

3. Wait for status to change to **"Live"** (green dot)

---

## 🔧 Post-Deployment Setup

### **Step 7: Create Superuser (Admin Account)**

You need an admin account to manage the application.

1. In Render Dashboard, go to your `blocknotes` service
2. Click **"Shell"** tab (left sidebar)
3. Click **"Launch Shell"** button
4. Wait for the shell to connect (may take 30 seconds)
5. Run these commands:

```bash
cd note_app
python manage.py createsuperuser
```

6. Follow the prompts:
   - Username: (choose a username)
   - Email: (your email)
   - Password: (choose a strong password)
   - Password (again): (confirm)

7. You should see: `Superuser created successfully.`

---

### **Step 8: Configure Google OAuth for Production**

⚠️ **CRITICAL STEP** - Without this, Google Sign-In won't work!

1. **Get your Render URL** (e.g., `https://blocknotes-abc123.onrender.com`)

2. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/apis/credentials
   - Sign in with the Google account that owns the OAuth credentials

3. **Find the OAuth 2.0 Client ID:**
   - Look for client ID: `943365069887-h47i0qu9u77pucn0p4kpuafh5j156nda`
   - Click the **edit icon** (pencil)

4. **Add Production Redirect URI:**
   - Scroll to "Authorized redirect URIs"
   - Click **"+ ADD URI"**
   - Add: `https://your-render-url.onrender.com/accounts/google/login/callback/`
   - Example: `https://blocknotes-abc123.onrender.com/accounts/google/login/callback/`
   - ⚠️ **Include the trailing slash!**

5. **Add Production JavaScript Origin:**
   - Scroll to "Authorized JavaScript origins"
   - Click **"+ ADD URI"**
   - Add: `https://your-render-url.onrender.com`
   - Example: `https://blocknotes-abc123.onrender.com`

6. Click **"SAVE"**

---

### **Step 9: Configure Social Application in Django Admin**

1. **Visit your admin panel:**
   - Go to: `https://your-render-url.onrender.com/admin/`
   - Login with the superuser credentials you created

2. **Add Google Social Application:**
   - Click on **"Social applications"** → **"Add social application"**
   - Fill in:
     - **Provider:** Google
     - **Name:** Google
     - **Client id:** `943365069887-h47i0qu9u77pucn0p4kpuafh5j156nda.apps.googleusercontent.com`
     - **Secret key:** `YOUR_GOOGLE_CLIENT_SECRET_HERE`
     - **Sites:** Select `example.com` and move it to "Chosen sites"
   - Click **"SAVE"**

---

## ✅ Testing the Deployment

### **Step 10: Test the Application**

1. **Visit your app:**
   - Go to: `https://your-render-url.onrender.com`
   - You should see the BlockNotes landing page

2. **Test Google Sign-In:**
   - Click **"Sign in with Google"**
   - You should be redirected to Google's login page
   - Sign in with your Google account
   - You should be redirected back to the app and logged in

3. **Test Note Creation:**
   - Try creating a new note
   - Add some content
   - Save the note
   - Verify it appears in your notes list

4. **Test Blockchain Integration:**
   - Check if blockchain receipts are being generated
   - (Note: Ganache is for local development only - production may need a different blockchain setup)

---

## 🐛 Troubleshooting

### Common Issues and Solutions:

#### **Issue 1: "Application Error" or 500 Error**

**Cause:** Missing or incorrect environment variables

**Solution:**
1. Check **Environment** tab in Render
2. Verify all required variables are set:
   - `ALLOWED_HOSTS`
   - `CSRF_TRUSTED_ORIGINS`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
3. Check **Logs** tab for specific error messages

---

#### **Issue 2: "DisallowedHost" Error**

**Cause:** `ALLOWED_HOSTS` doesn't match your Render URL

**Solution:**
1. Go to **Environment** tab
2. Update `ALLOWED_HOSTS` to your exact Render URL (without https://)
3. Example: `blocknotes-abc123.onrender.com`
4. Save and wait for redeployment

---

#### **Issue 3: "CSRF Verification Failed"**

**Cause:** `CSRF_TRUSTED_ORIGINS` not set correctly

**Solution:**
1. Go to **Environment** tab
2. Set `CSRF_TRUSTED_ORIGINS` to your Render URL (with https://)
3. Example: `https://blocknotes-abc123.onrender.com`
4. Save and wait for redeployment

---

#### **Issue 4: Google Sign-In Shows "Error 400: redirect_uri_mismatch"**

**Cause:** Production redirect URI not added to Google Cloud Console

**Solution:**
1. Go to Google Cloud Console
2. Add the exact redirect URI:
   - `https://your-render-url.onrender.com/accounts/google/login/callback/`
3. Make sure the trailing slash is included!
4. Save in Google Console
5. Wait a few minutes for changes to propagate

---

#### **Issue 5: "SocialApp matching query does not exist"**

**Cause:** Google Social Application not configured in Django admin

**Solution:**
1. Go to `/admin/` on your deployed app
2. Add Social Application (see Step 9 above)

---

#### **Issue 6: Static Files Not Loading (No CSS/JS)**

**Cause:** Static files not collected properly

**Solution:**
1. Check **Logs** tab for errors during `collectstatic`
2. Manually trigger a rebuild:
   - Go to **Manual Deploy** tab
   - Click **"Clear build cache & deploy"**

---

#### **Issue 7: Database Connection Errors**

**Cause:** Database not properly linked

**Solution:**
1. Check that `DATABASE_URL` is set in **Environment** tab
2. It should be automatically set by Render
3. If missing, go to **Environment** tab and link the database:
   - Key: `DATABASE_URL`
   - Value: Select `blocknotes-db` from dropdown

---

## 📝 Important Notes

### **About the Database:**

- ✅ **Production:** Uses PostgreSQL (provided by Render)
- ✅ **Local Development:** Uses MySQL (on developer's machine)
- ⚠️ **Data is separate:** Production and local databases are completely independent
- ⚠️ **Fresh start:** Production database starts empty - you'll need to create test data

### **About Blockchain (Ganache):**

- ⚠️ **Ganache is local only:** The `ganache-data` folder is for local development
- ⚠️ **Production blockchain:** You may need to configure a testnet (Sepolia, Goerli) or mainnet for production
- 💡 **Ask the team:** Check with the project owner about blockchain configuration for production

### **About Free Tier Limitations:**

Render's free tier has some limitations:
- ⏰ **Spins down after 15 minutes of inactivity**
- ⏰ **First request after spin-down takes 30-60 seconds**
- 💾 **750 hours/month** (enough for one app running 24/7)
- 💾 **PostgreSQL:** 90 days retention, then deleted if inactive

### **About Environment Variables:**

- 🔒 **Never commit `.env` to Git** - it contains secrets!
- 🔒 **Each team member** should have their own local `.env` file
- 🔒 **Production credentials** are set in Render dashboard only
- ✅ **Use `.env.example`** as a template for local development

---

## 🎯 Deployment Checklist

Use this checklist to ensure everything is set up correctly:

### **Pre-Deployment:**
- [ ] Have GitHub access to `IamJesssie/BlockNotes`
- [ ] Have Render account (signed up with GitHub)
- [ ] Have Google OAuth credentials from project owner
- [ ] Confirmed branch: `feature/web3-ui-redesign`

### **During Deployment:**
- [ ] Connected GitHub repository to Render
- [ ] Selected correct branch: `feature/web3-ui-redesign`
- [ ] Applied Blueprint (render.yaml detected)
- [ ] Database created: `blocknotes-db`
- [ ] Web service created: `blocknotes`

### **Environment Variables:**
- [ ] `ALLOWED_HOSTS` set to Render URL
- [ ] `CSRF_TRUSTED_ORIGINS` set to Render URL with https://
- [ ] `GOOGLE_CLIENT_ID` set
- [ ] `GOOGLE_CLIENT_SECRET` set
- [ ] `DATABASE_URL` auto-set by Render
- [ ] `SECRET_KEY` auto-generated by Render

### **Post-Deployment:**
- [ ] Superuser created via Shell
- [ ] Google OAuth redirect URI added to Google Cloud Console
- [ ] Google OAuth JavaScript origin added to Google Cloud Console
- [ ] Social Application configured in Django admin
- [ ] Tested: App loads successfully
- [ ] Tested: Google Sign-In works
- [ ] Tested: Can create and save notes

---

## 📞 Getting Help

If you encounter issues not covered in this guide:

1. **Check the Logs:**
   - Render Dashboard → Your Service → **Logs** tab
   - Look for error messages

2. **Review Other Guides:**
   - `OAUTH_SETUP_GUIDE.md` - Detailed OAuth setup
   - `GOOGLE_CONSOLE_SETUP.md` - Google Console configuration
   - `DEPLOYMENT_GUIDE.md` - General deployment info

3. **Contact the Team:**
   - Reach out to the project owner
   - Share screenshots of error messages
   - Share relevant logs from Render

---

## 🎉 Success!

If you've completed all steps and tests pass, congratulations! 🎊

Your BlockNotes application is now live at:
**`https://your-render-url.onrender.com`**

Share this URL with your team and stakeholders!

---

**Last Updated:** November 25, 2025  
**Branch:** feature/web3-ui-redesign  
**Deployment Platform:** Render.com (Free Tier)
