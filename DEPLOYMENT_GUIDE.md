# 🚀 BlockNotes Deployment Guide for Render.com

## ✅ What We've Done

1. **Updated `settings.py`** to support both environments:
   - **Local**: Uses MySQL database (your existing setup)
   - **Production**: Uses PostgreSQL (Render's free tier)
   
2. **Created deployment files**:
   - `requirements.txt` - Python dependencies
   - `build.sh` - Build script for Render
   - `render.yaml` - Infrastructure as Code blueprint
   
3. **Committed and pushed** changes to `feature/web3-ui-redesign` branch

## 📋 Deployment Steps on Render.com

### Step 1: Sign Up / Log In to Render
1. Go to [https://render.com](https://render.com)
2. Sign up or log in (you can use GitHub to sign in)

### Step 2: Deploy Using Blueprint
1. Click **"New +"** button in the top right
2. Select **"Blueprint"**
3. Connect your GitHub repository: `IamJesssie/BlockNotes`
4. Select the branch: `feature/web3-ui-redesign`
5. Render will detect the `render.yaml` file automatically
6. Click **"Apply"**

### Step 3: Configure Environment Variables
After the blueprint is applied, you need to set these environment variables in the Render dashboard:

1. Go to your web service → **Environment** tab
2. Add/Update these variables:

```
ALLOWED_HOSTS=your-app-name.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com
```

**Note**: Replace `your-app-name` with your actual Render app name.

### Step 4: Wait for Deployment
- Render will automatically:
  - Create a PostgreSQL database
  - Install dependencies
  - Collect static files
  - Run migrations
  - Start the application

This takes about 5-10 minutes for the first deployment.

### Step 5: Create Superuser (Optional)
Once deployed, you can create a superuser via Render's shell:

1. Go to your web service → **Shell** tab
2. Run:
```bash
cd note_app
python manage.py createsuperuser
```

## 🏠 Local Development (MySQL Retained)

Your local setup remains **unchanged**! The code automatically detects the environment:

### To run locally:
```bash
cd note_app
py manage.py runserver
```

It will use your MySQL database (`Blocknotes`) because there's no `DATABASE_URL` environment variable set locally.

### Your local MySQL configuration:
- Database: `Blocknotes`
- User: `root`
- Password: `dblapuredemo123`
- Host: `127.0.0.1`
- Port: `3306`

## 🔄 How Environment Detection Works

The `settings.py` now checks:
```python
if os.environ.get('DATABASE_URL'):
    # Use PostgreSQL (Render)
else:
    # Use MySQL (Local)
```

## 📝 Important Notes

1. **Database Separation**: 
   - Local: MySQL database with your test data
   - Production: Fresh PostgreSQL database (you'll need to create test data there)

2. **Static Files**: 
   - Handled by WhiteNoise in production
   - No additional configuration needed

3. **Google OAuth** (if you're using it):
   - You'll need to add your Render URL to Google Cloud Console
   - Update authorized redirect URIs

4. **Blockchain/Ganache**:
   - You may need to configure Web3 provider for production
   - Consider using a testnet like Sepolia or Goerli for production

## 🐛 Troubleshooting

### If deployment fails:
1. Check the **Logs** tab in Render dashboard
2. Common issues:
   - Missing environment variables
   - Database connection errors
   - Static files not collecting

### If local development breaks:
- Make sure you don't have `DATABASE_URL` in your local environment
- Your MySQL server should be running
- Run: `py manage.py runserver` from the `note_app` directory

## 🎯 Next Steps After Deployment

1. **Test the deployed app** at `https://your-app-name.onrender.com`
2. **Create a superuser** on production
3. **Test note creation** with blockchain integration
4. **Configure Google OAuth** for production (if needed)
5. **Set up Web3 provider** for production blockchain features

## 📞 Need Help?

If you encounter any issues during deployment, check:
- Render deployment logs
- Database connection status
- Environment variables are set correctly

---

**Your local MySQL database is safe and unchanged!** 🎉
