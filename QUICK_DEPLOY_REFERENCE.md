# 🚀 BlockNotes - Quick Deployment Reference Card

**For: Team Members Deploying to Render**  
**Branch:** `feature/web3-ui-redesign`  
**Repository:** `IamJesssie/BlockNotes`

---

## ⚡ Quick Start (5 Steps)

### 1️⃣ Sign Up to Render
- Go to [render.com](https://render.com)
- Sign in with GitHub

### 2️⃣ Deploy Blueprint
- Click **"New +"** → **"Blueprint"**
- Connect: `IamJesssie/BlockNotes`
- Branch: `feature/web3-ui-redesign`
- Click **"Apply"**

### 3️⃣ Set Environment Variables
Go to **Environment** tab, add these:

```
ALLOWED_HOSTS=your-app-name.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com
GOOGLE_CLIENT_ID=943365069887-h47i0qu9u77pucn0p4kpuafh5j156nda.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET_HERE
```

Replace `your-app-name` with your actual Render URL!

### 4️⃣ Create Superuser
In **Shell** tab:
```bash
cd note_app
python manage.py createsuperuser
```

### 5️⃣ Configure Google OAuth
**Google Cloud Console:** https://console.cloud.google.com/apis/credentials

Add these URIs:

**Authorized redirect URIs:**
```
https://your-app-name.onrender.com/accounts/google/login/callback/
```

**Authorized JavaScript origins:**
```
https://your-app-name.onrender.com
```

**Django Admin:** `https://your-app-name.onrender.com/admin/`
- Add Social Application
- Provider: Google
- Client ID: `943365069887-h47i0qu9u77pucn0p4kpuafh5j156nda.apps.googleusercontent.com`
- Secret: `YOUR_GOOGLE_CLIENT_SECRET_HERE`

---

## 🔍 What Gets Deployed

✅ Django app with Google OAuth  
✅ PostgreSQL database (auto-created)  
✅ Static files (CSS, JS)  
✅ Blockchain note-taking features  
✅ Auto-migrations on deploy  

---

## ⏱️ Timeline

| Step | Time |
|------|------|
| Database creation | 1-2 min |
| First build (will fail) | 3-5 min |
| Set env vars | 2 min |
| Second build (success) | 3-5 min |
| Create superuser | 1 min |
| Configure Google OAuth | 5 min |
| **Total** | **~15-20 min** |

---

## 🆘 Quick Troubleshooting

| Error | Fix |
|-------|-----|
| DisallowedHost | Check `ALLOWED_HOSTS` matches your URL |
| CSRF Failed | Check `CSRF_TRUSTED_ORIGINS` has `https://` |
| redirect_uri_mismatch | Add redirect URI to Google Console |
| SocialApp not found | Configure Social App in Django admin |
| 500 Error | Check Logs tab for details |

---

## 📋 Checklist

- [ ] Render account created
- [ ] Blueprint deployed
- [ ] Environment variables set
- [ ] App shows "Live" status
- [ ] Superuser created
- [ ] Google OAuth URIs added
- [ ] Social App configured
- [ ] Google Sign-In tested
- [ ] Note creation tested

---

## 📚 Full Documentation

For detailed instructions, see:
- **`RENDER_DEPLOYMENT_COMPLETE_GUIDE.md`** ← Start here!
- `OAUTH_SETUP_GUIDE.md`
- `GOOGLE_CONSOLE_SETUP.md`

---

## 🔗 Important Links

- **Render Dashboard:** https://dashboard.render.com
- **Google Cloud Console:** https://console.cloud.google.com/apis/credentials
- **Repository:** https://github.com/IamJesssie/BlockNotes
- **Branch:** feature/web3-ui-redesign

---

## 💡 Pro Tips

1. ⚡ **First build will fail** - this is normal! Set env vars and it will auto-redeploy
2. 🔄 **Free tier spins down** after 15 min of inactivity (first request takes 30-60s)
3. 📝 **Save your Render URL** - you'll need it for Google OAuth setup
4. 🔒 **Never share credentials** in public channels
5. 📊 **Check Logs tab** if anything goes wrong

---

**Need Help?** Read the complete guide: `RENDER_DEPLOYMENT_COMPLETE_GUIDE.md`
