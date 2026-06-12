# 🚀 RENDER.COM MANUAL DEPLOYMENT GUIDE

## SmartPark Django Application - Production Deployment

**Repository**: https://github.com/Prakash-Bhatt01/Smart_Parking_System.git  
**Branch**: main  
**Commit**: adf0d90

---

## ✅ PRE-DEPLOYMENT CHECKLIST (COMPLETED)

- [x] Production dependencies installed (gunicorn, whitenoise, psycopg2, etc.)
- [x] requirements.txt created with all packages
- [x] settings.py updated for environment variables
- [x] PostgreSQL database configuration added
- [x] render.yaml configuration file created
- [x] build.sh script created
- [x] Procfile created for Gunicorn
- [x] runtime.txt specifies Python 3.11.0
- [x] Static files configured with WhiteNoise
- [x] Production security settings added
- [x] Local testing completed successfully
- [x] All changes pushed to GitHub

---

## 📋 MANUAL DEPLOYMENT STEPS ON RENDER.COM

### Step 1: Sign Up / Log In to Render

1. Go to **https://render.com**
2. Click **"Sign Up"** or **"Log In"**
3. Choose **"Sign in with GitHub"**
4. Authorize Render to access your GitHub account

---

### Step 2: Create PostgreSQL Database FIRST

**IMPORTANT**: Create the database BEFORE the web service so it's ready to link.

1. In Render Dashboard, click **"New +"** button (top right)
2. Select **"PostgreSQL"**
3. Configure database settings:
   - **Name**: `smartpark-db`
   - **Database**: `smartpark`
   - **User**: `smartpark_user`
   - **Region**: **Singapore** (closest to India/Bengaluru)
   - **PostgreSQL Version**: Leave default (latest)
   - **Plan**: **Free**

4. Click **"Create Database"**

5. Wait for database to be created (takes 1-2 minutes)

6. Once created, go to database **Info** tab

7. **COPY** the **"Internal Database URL"** (starts with `postgres://`)
   - Format: `postgres://smartpark_user:password@dpg-xxxxx/smartpark`
   - You'll need this in Step 6

---

### Step 3: Create Web Service

1. In Render Dashboard, click **"New +"** button
2. Select **"Web Service"**
3. Click **"Connect a repository"**
4. If this is your first time, click **"Configure account"** to grant access
5. Find and select: **Prakash-Bhatt01/Smart_Parking_System**
6. Click **"Connect"**

---

### Step 4: Configure Web Service Settings

Fill in these exact values:

| Setting | Value |
|---------|-------|
| **Name** | `smartpark` |
| **Region** | **Singapore (Southeast Asia)** |
| **Branch** | `main` |
| **Root Directory** | *(leave empty)* |
| **Runtime** | **Python 3** |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn smart_parking.wsgi:application` |
| **Plan** | **Free** |

---

### Step 5: Add Environment Variables

Scroll down to **"Environment Variables"** section.

Click **"Add Environment Variable"** and add these **ONE BY ONE**:

#### Variable 1: DEBUG
- **Key**: `DEBUG`
- **Value**: `False`

#### Variable 2: ALLOWED_HOSTS
- **Key**: `ALLOWED_HOSTS`
- **Value**: `.onrender.com`

#### Variable 3: SECRET_KEY (GENERATE NEW)
- **Key**: `SECRET_KEY`
- **Value**: Click **"Generate"** button (Render will create a random 50-character key)
  
  **OR** manually paste a secure key:
  - Go to: https://djecrety.ir/
  - Click "Generate"
  - Copy the generated key
  - Paste it here

#### Variable 4: DATABASE_URL
- **Key**: `DATABASE_URL`
- **Value**: Paste the **Internal Database URL** you copied from Step 2
  - Example: `postgres://smartpark_user:xxxxxxxxxxx@dpg-xxxxx-singapore-postgres.render.com/smartpark`

#### Variable 5: PYTHON_VERSION
- **Key**: `PYTHON_VERSION`
- **Value**: `3.11.0`

---

### Step 6: Deploy the Service

1. Scroll to bottom
2. Click **"Create Web Service"** (blue button)
3. Render will start building your application
4. Watch the **Deploy Logs** in real-time

---

### Step 7: Monitor Deployment Logs

You'll see logs like this:

```
==> Cloning from https://github.com/Prakash-Bhatt01/Smart_Parking_System...
==> Using Python version: 3.11.0
==> Running build command: ./build.sh
==> Installing dependencies from requirements.txt
==> Collecting static files...
138 static files copied to 'staticfiles'
==> Running migrations...
Operations to perform: Apply all migrations
Running migrations: OK
==> Build successful 🎉
==> Deploying...
==> Starting service with gunicorn...
==> Your service is live at https://smartpark-xxxx.onrender.com
```

**Expected Build Time**: 3-5 minutes

---

### Step 8: Verify Successful Deployment

#### Success Indicators:

✅ Logs show: **"Build successful"**  
✅ Logs show: **"Your service is live at https://..."**  
✅ Service status shows green **"Live"** badge

#### If Build Fails:

- Check the error message in logs
- Most common issues:
  1. **Missing DATABASE_URL** - Go back to Environment tab and add it
  2. **SECRET_KEY not set** - Add SECRET_KEY environment variable
  3. **Build command failed** - Ensure build.sh has correct syntax

---

### Step 9: Test Your Live Application

1. Click on your service URL: `https://smartpark-xxxx.onrender.com`

2. Test these features:

   **🏠 Homepage**:
   - ✅ Page loads without errors
   - ✅ Map displays (Leaflet.js with OpenStreetMap)
   - ✅ Parking lots are visible

   **👤 User Registration**:
   - ✅ Register new account
   - ✅ Login works

   **🅿️ Parking Features**:
   - ✅ Search parking by city
   - ✅ View lot details
   - ✅ Book a parking slot
   - ✅ Demo payment flow works
   - ✅ QR code generates after payment

   **📱 My Bookings**:
   - ✅ Active bookings display
   - ✅ Countdown timer works
   - ✅ Extend booking works
   - ✅ Cancel booking works

   **👨‍💼 Admin Panel**:
   - ✅ Access `/admin/` URL
   - ✅ Create superuser (see below)

---

### Step 10: Create Admin Superuser

To access the admin panel, you need to create a superuser.

#### Method 1: Via Render Shell (Recommended)

1. Go to your Web Service dashboard
2. Click **"Shell"** tab (top right)
3. A terminal will open
4. Run this command:
   ```bash
   python manage.py createsuperuser
   ```
5. Enter:
   - Username: `admin`
   - Email: `your-email@example.com`
   - Password: (enter twice)
6. Go to `https://your-app.onrender.com/admin/`
7. Login with the credentials you just created

#### Method 2: Via One-Off Job

1. In your service, click **"Shell"** → **"Run command"**
2. Enter:
   ```bash
   python manage.py createsuperuser --username admin --email admin@example.com --noinput
   ```
3. Then reset password:
   ```bash
   python manage.py changepassword admin
   ```

---

### Step 11: Configure Custom Domain (Optional)

If you have a custom domain:

1. Go to **Settings** tab
2. Scroll to **"Custom Domain"**
3. Click **"Add Custom Domain"**
4. Enter your domain (e.g., `smartpark.yourdomain.com`)
5. Follow DNS configuration instructions
6. Update `ALLOWED_HOSTS` environment variable:
   - Add: `.onrender.com,smartpark.yourdomain.com`

---

## 🔧 POST-DEPLOYMENT CONFIGURATION

### Update ALLOWED_HOSTS with Your Actual Domain

1. Go to **Environment** tab
2. Find `ALLOWED_HOSTS` variable
3. Click **"Edit"**
4. Update value to include your actual Render domain:
   ```
   .onrender.com,smartpark-xxxx.onrender.com
   ```
5. Click **"Save Changes"**
6. Service will redeploy automatically

---

## 📊 MONITORING & MAINTENANCE

### View Logs

- Go to **"Logs"** tab to see real-time application logs
- Useful for debugging errors

### View Metrics

- Go to **"Metrics"** tab to see:
  - Response times
  - Memory usage
  - HTTP requests

### Database Backups

- Free PostgreSQL plan does NOT include automatic backups
- To backup manually:
  1. Go to database **"Connect"** tab
  2. Use `pg_dump` command provided
  3. Run locally to download backup

---

## 🚨 TROUBLESHOOTING COMMON ISSUES

### Issue 1: "Application Error" or 500 Error

**Cause**: Database not connected or SECRET_KEY missing

**Fix**:
1. Check Environment Variables
2. Ensure `DATABASE_URL` is set correctly
3. Ensure `SECRET_KEY` is set
4. Check logs for specific error

### Issue 2: Static Files Not Loading (CSS/JS missing)

**Cause**: Collectstatic didn't run or WhiteNoise not configured

**Fix**:
1. Check build logs - should show "138 static files copied"
2. Verify `STATICFILES_STORAGE` is set in settings.py
3. Ensure WhiteNoise middleware is in MIDDLEWARE list

### Issue 3: Database Connection Refused

**Cause**: Wrong DATABASE_URL or database not created

**Fix**:
1. Verify database was created in Step 2
2. Use **Internal Database URL**, not External
3. URL format: `postgres://user:password@host/database`

### Issue 4: "This site can't provide a secure connection"

**Cause**: HTTPS redirect causing loop

**Fix**:
1. Check `SECURE_SSL_REDIRECT` is in `if not DEBUG:` block
2. Verify `SECURE_PROXY_SSL_HEADER` is set correctly

### Issue 5: Media Files (QR Codes) Not Persisting

**Cause**: Render's free tier has ephemeral filesystem

**Fix** (for production):
1. Use cloud storage like AWS S3 or Cloudinary
2. Install `django-storages` and `boto3`
3. Configure S3 for MEDIA_ROOT

---

## 📱 PWA INSTALLATION ON MOBILE

After deployment, users can install SmartPark as a Progressive Web App:

**Android (Chrome)**:
1. Visit your Render URL on mobile
2. Tap 3-dot menu
3. Tap "Add to Home Screen"
4. Tap "Install"

**iOS (Safari)**:
1. Visit your Render URL
2. Tap Share button
3. Tap "Add to Home Screen"

---

## 🎉 DEPLOYMENT COMPLETE!

Your SmartPark application is now live on Render.com!

**Live URL**: `https://smartpark-xxxx.onrender.com`

### Free Plan Limitations

- ⚠️ **Spins down after 15 minutes of inactivity**
- ⚠️ **Cold start takes 30-60 seconds on first request**
- ⚠️ **750 hours/month free** (enough for 24/7 operation)
- ⚠️ **Ephemeral filesystem** (uploaded files don't persist across deploys)

### Upgrade to Paid Plan ($7/month) for:

- ✅ No spin down (always online)
- ✅ Instant response times
- ✅ More compute resources
- ✅ Persistent disk storage

---

## 📞 SUPPORT & RESOURCES

- **Render Documentation**: https://render.com/docs
- **Render Status**: https://status.render.com
- **GitHub Repository**: https://github.com/Prakash-Bhatt01/Smart_Parking_System

---

**Deployment Date**: June 12, 2026  
**Django Version**: 6.0.3  
**Python Version**: 3.11.0  
**Database**: PostgreSQL 16 (free tier)

**Deployed by**: Kiro AI Assistant
