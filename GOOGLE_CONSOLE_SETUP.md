# 🔐 Google Cloud Console - Quick Setup Checklist

## ✅ What You Need to Add in Google Cloud Console

### 📍 Go to: https://console.cloud.google.com/apis/credentials

---

## 1️⃣ Authorized Redirect URIs

Add these **exact URLs** to your OAuth 2.0 Client ID:

### For Local Development (Add Now):
```
http://localhost:8000/accounts/google/login/callback/
http://127.0.0.1:8000/accounts/google/login/callback/
```

### For Production (Add After Deploying to Render):
```
https://your-app-name.onrender.com/accounts/google/login/callback/
```
⚠️ Replace `your-app-name` with your actual Render app URL

---

## 2️⃣ Authorized JavaScript Origins

Add these **exact URLs** to your OAuth 2.0 Client ID:

### For Local Development (Add Now):
```
http://localhost:8000
http://127.0.0.1:8000
```

### For Production (Add After Deploying to Render):
```
https://your-app-name.onrender.com
```
⚠️ Replace `your-app-name` with your actual Render app URL

---

## 📋 Step-by-Step Instructions

1. **Open Google Cloud Console:**
   - Go to: https://console.cloud.google.com/apis/credentials

2. **Find your OAuth 2.0 Client ID:**
   - Look for the client ID starting with `943365069887-...`
   - Click the **edit icon** (pencil) next to it

3. **Add Authorized Redirect URIs:**
   - Scroll to "Authorized redirect URIs"
   - Click **"+ ADD URI"**
   - Add the local development URIs (listed above)
   - Click **"+ ADD URI"** again for each URL

4. **Add Authorized JavaScript Origins:**
   - Scroll to "Authorized JavaScript origins"
   - Click **"+ ADD URI"**
   - Add the local development origins (listed above)
   - Click **"+ ADD URI"** again for each URL

5. **Save:**
   - Click **"SAVE"** at the bottom

---

## ⏰ When to Add Production URLs

**After you deploy to Render:**

1. Get your Render app URL (e.g., `blocknotes-abc123.onrender.com`)
2. Go back to Google Cloud Console
3. Edit your OAuth 2.0 Client ID
4. Add the production redirect URI and JavaScript origin
5. Save

---

## ✅ Current Status

- [x] Google Client ID: `943365069887-h47i0qu9u77pucn0p4kpuafh5j156nda.apps.googleusercontent.com`
- [x] Google Client Secret: `YOUR_GOOGLE_CLIENT_SECRET_HERE`
- [x] Credentials saved in local `.env` file
- [ ] **TODO: Add Authorized Redirect URIs in Google Cloud Console**
- [ ] **TODO: Add Authorized JavaScript Origins in Google Cloud Console**
- [ ] **TODO: Test Google Sign-In locally**
- [ ] **TODO: Add production URLs after Render deployment**

---

## 🧪 Testing Locally

After adding the redirect URIs and JavaScript origins:

1. Make sure your dev server is running:
   ```bash
   cd note_app
   py manage.py runserver
   ```

2. Visit: http://localhost:8000/notes/landing/

3. Click **"Sign in with Google"**

4. You should see Google's login page

5. After signing in, you should be redirected back to your app

---

## 🐛 Common Errors

### "Error 400: redirect_uri_mismatch"
- **Cause:** The redirect URI is not added to Google Cloud Console
- **Fix:** Make sure you added the **exact** redirect URI (including the trailing slash!)

### "Error 401: invalid_client"
- **Cause:** Client ID or Secret is incorrect
- **Fix:** Double-check your `.env` file has the correct credentials

---

## 📝 Summary

Your `.env` file is now configured with:
- ✅ SECRET_KEY (generated)
- ✅ Google Client ID
- ✅ Google Client Secret

**Next step:** Add the redirect URIs and JavaScript origins in Google Cloud Console!
