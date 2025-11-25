# 📊 BlockNotes Deployment Flowchart

## Visual Guide to Deployment Process

```
┌─────────────────────────────────────────────────────────────────┐
│                    START DEPLOYMENT                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Prerequisites Check                                     │
├─────────────────────────────────────────────────────────────────┤
│  ☐ GitHub account with repo access                              │
│  ☐ Render account (free tier OK)                                │
│  ☐ Google OAuth credentials from team                           │
│  ☐ Branch: feature/web3-ui-redesign                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Connect to Render                                       │
├─────────────────────────────────────────────────────────────────┤
│  1. Go to render.com                                             │
│  2. Sign in with GitHub                                          │
│  3. Authorize Render to access GitHub                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Deploy Blueprint                                        │
├─────────────────────────────────────────────────────────────────┤
│  1. Click "New +" → "Blueprint"                                  │
│  2. Connect: IamJesssie/BlockNotes                               │
│  3. Select branch: feature/web3-ui-redesign                      │
│  4. Click "Apply"                                                │
│                                                                  │
│  Render will create:                                             │
│  ✓ PostgreSQL database (blocknotes-db)                           │
│  ✓ Web service (blocknotes)                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: First Build (Expected to FAIL)                          │
├─────────────────────────────────────────────────────────────────┤
│  Status: Building... → Failed ❌                                 │
│  Reason: Missing environment variables                           │
│  Duration: ~3-5 minutes                                          │
│                                                                  │
│  This is NORMAL! Continue to next step.                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Set Environment Variables                               │
├─────────────────────────────────────────────────────────────────┤
│  Go to: Environment tab                                          │
│                                                                  │
│  Add these variables:                                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ ALLOWED_HOSTS = your-app.onrender.com                      │ │
│  │ CSRF_TRUSTED_ORIGINS = https://your-app.onrender.com       │ │
│  │ GOOGLE_CLIENT_ID = 943365069887-...                        │ │
│  │ GOOGLE_CLIENT_SECRET = YOUR_GOOGLE_CLIENT_SECRET_HERE      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Click "Save Changes"                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: Auto-Redeploy (Should SUCCEED)                          │
├─────────────────────────────────────────────────────────────────┤
│  Status: Building... → Deploying... → Live ✅                    │
│  Duration: ~3-5 minutes                                          │
│                                                                  │
│  Your app is now accessible at:                                  │
│  https://your-app-name.onrender.com                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: Create Superuser                                        │
├─────────────────────────────────────────────────────────────────┤
│  Go to: Shell tab                                                │
│  Run:                                                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ cd note_app                                                 │ │
│  │ python manage.py createsuperuser                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Enter: username, email, password                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 8: Configure Google OAuth                                  │
├─────────────────────────────────────────────────────────────────┤
│  A. Google Cloud Console                                         │
│     → https://console.cloud.google.com/apis/credentials          │
│                                                                  │
│     Add Authorized redirect URIs:                                │
│     ┌──────────────────────────────────────────────────────────┐│
│     │ https://your-app.onrender.com/accounts/google/login/     ││
│     │ callback/                                                 ││
│     └──────────────────────────────────────────────────────────┘│
│                                                                  │
│     Add Authorized JavaScript origins:                           │
│     ┌──────────────────────────────────────────────────────────┐│
│     │ https://your-app.onrender.com                            ││
│     └──────────────────────────────────────────────────────────┘│
│                                                                  │
│  B. Django Admin                                                 │
│     → https://your-app.onrender.com/admin/                       │
│                                                                  │
│     Add Social Application:                                      │
│     - Provider: Google                                           │
│     - Client ID: 943365069887-...                                │
│     - Secret: GOCSPX-...                                         │
│     - Sites: example.com                                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 9: Test Deployment                                         │
├─────────────────────────────────────────────────────────────────┤
│  ☐ Visit: https://your-app.onrender.com                         │
│  ☐ Landing page loads correctly                                 │
│  ☐ Click "Sign in with Google"                                  │
│  ☐ Google login works                                            │
│  ☐ Create a test note                                            │
│  ☐ Note saves successfully                                       │
│  ☐ Blockchain receipt generated                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  DEPLOYMENT COMPLETE! 🎉                         │
├─────────────────────────────────────────────────────────────────┤
│  Your BlockNotes app is live and ready to use!                   │
│                                                                  │
│  Share the URL with your team:                                   │
│  https://your-app-name.onrender.com                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Deployment Timeline

```
Time    │ Activity                          │ Status
────────┼───────────────────────────────────┼─────────────────
0:00    │ Start deployment                  │ 
0:02    │ Database created                  │ ✅ Available
0:05    │ First build (fails)               │ ❌ Expected
0:07    │ Set environment variables         │ 
0:10    │ Auto-redeploy triggered           │ 
0:15    │ Second build (succeeds)           │ ✅ Live
0:17    │ Create superuser                  │ ✅ Done
0:22    │ Configure Google OAuth            │ ✅ Done
0:25    │ Test application                  │ ✅ Working
────────┴───────────────────────────────────┴─────────────────
Total: ~25 minutes
```

---

## 🎯 Decision Tree: Troubleshooting

```
                    ┌─────────────────┐
                    │  Deployment     │
                    │  Failed?        │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
        ┌───────────────┐         ┌──────────────┐
        │ Build Failed? │         │ App Running  │
        │               │         │ but Errors?  │
        └───────┬───────┘         └──────┬───────┘
                │                        │
        ┌───────┴────────┐      ┌────────┴────────┐
        │                │      │                 │
        ▼                ▼      ▼                 ▼
┌──────────────┐ ┌──────────┐ ┌─────────┐ ┌──────────────┐
│ Check Logs   │ │ Check    │ │ CSRF    │ │ Google OAuth │
│ for missing  │ │ build.sh │ │ Error?  │ │ Error?       │
│ dependencies │ │ syntax   │ └────┬────┘ └──────┬───────┘
└──────┬───────┘ └────┬─────┘      │             │
       │              │             │             │
       ▼              ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌─────────┐ ┌──────────────┐
│ Add to       │ │ Fix and  │ │ Check   │ │ Add redirect │
│ requirements │ │ redeploy │ │ CSRF_   │ │ URI to       │
│ .txt         │ │          │ │ TRUSTED │ │ Google       │
│              │ │          │ │ ORIGINS │ │ Console      │
└──────────────┘ └──────────┘ └─────────┘ └──────────────┘
```

---

## 📊 Environment Variables Matrix

| Variable | Source | When Set | Example |
|----------|--------|----------|---------|
| `SECRET_KEY` | Auto-generated | During blueprint apply | `django-insecure-abc123...` |
| `DATABASE_URL` | Auto-set by Render | When database created | `postgres://user:pass@...` |
| `PYTHON_VERSION` | render.yaml | During blueprint apply | `3.11.0` |
| `DEBUG` | render.yaml | During blueprint apply | `False` |
| `ALLOWED_HOSTS` | **Manual** | After first build | `app.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | **Manual** | After first build | `https://app.onrender.com` |
| `GOOGLE_CLIENT_ID` | **Manual** | After first build | `943365069887-...` |
| `GOOGLE_CLIENT_SECRET` | **Manual** | After first build | `GOCSPX-...` |

---

## 🔍 What Happens During Build

```
build.sh execution:
│
├─ 1. Install dependencies
│   ├─ pip install --upgrade pip
│   └─ pip install -r requirements.txt
│       ├─ Django
│       ├─ mysqlclient (not used in production)
│       ├─ psycopg2-binary (PostgreSQL driver)
│       ├─ dj-database-url
│       ├─ whitenoise (static files)
│       ├─ django-allauth (Google OAuth)
│       ├─ gunicorn (web server)
│       ├─ web3 (blockchain)
│       └─ python-dotenv
│
├─ 2. Collect static files
│   └─ python manage.py collectstatic --no-input
│       ├─ Copies CSS from note_app/static/
│       ├─ Copies JS from note_app/static/
│       └─ Saves to note_app/staticfiles/
│
└─ 3. Run database migrations
    └─ python manage.py migrate
        ├─ Creates database tables
        ├─ Sets up Django auth
        ├─ Sets up allauth tables
        └─ Sets up notes app tables
```

---

## 🎯 Success Indicators

After deployment, you should see:

```
✅ Render Dashboard
   ├─ Database: blocknotes-db [Available]
   └─ Web Service: blocknotes [Live]

✅ Logs Tab
   ├─ "Starting server with gunicorn"
   ├─ "Booting worker with pid: 123"
   └─ No error messages

✅ Application
   ├─ https://your-app.onrender.com loads
   ├─ Landing page displays correctly
   ├─ Google Sign-In button visible
   └─ Static files (CSS/JS) loading

✅ Google OAuth
   ├─ Sign-in redirects to Google
   ├─ After login, redirects back to app
   └─ User is logged in

✅ Functionality
   ├─ Can create notes
   ├─ Notes save to database
   └─ Blockchain receipts generated
```

---

For detailed step-by-step instructions, see:
**`RENDER_DEPLOYMENT_COMPLETE_GUIDE.md`**
