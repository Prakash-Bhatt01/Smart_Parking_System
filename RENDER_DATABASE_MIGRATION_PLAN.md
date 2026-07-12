# Render PostgreSQL Database Migration Plan
## Safe Migration from Expiring Free Database to New Free Database

---

## 🎯 Overview

**Situation:** Your free Render PostgreSQL database is expiring with a 14-day grace period.

**Objective:** Migrate all production data to a new free Render PostgreSQL database with:
- ✅ Zero data loss
- ✅ Minimal downtime (~5-10 minutes)
- ✅ Complete rollback capability
- ✅ 100% free solution

**Migration Strategy:** Export → New Database → Import → Verify → Switch

---

## 📊 Current Database Configuration

### Database Settings (from smart_parking/settings.py)

```python
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

**Environment Variable:** `DATABASE_URL`
- Format: `postgresql://user:password@host:port/database`
- Configured in: Render Dashboard → Environment Variables


### Production Data to Preserve

Based on your Django models, the following data will be migrated:

| Table | Description | Foreign Keys | Critical Data |
|-------|-------------|--------------|---------------|
| **auth_user** | Users & admins | None | ✅ YES - All user accounts |
| **parking_parkinglot** | Parking locations | None | ✅ YES - 8 lots with configuration |
| **parking_parkingslot** | Parking slots | lot_id | ✅ YES - 171 slots |
| **parking_vehicle** | User vehicles | user_id | ✅ YES - All registered vehicles |
| **parking_booking** | Bookings | user_id, slot_id, vehicle_id | ✅ YES - All booking history |
| **parking_slotconflictnotification** | Notifications | user_id, slot_id | ⚠️ OPTIONAL - Can be cleared |
| **django_session** | Sessions | None | ⚠️ OPTIONAL - Will expire naturally |
| **django_admin_log** | Admin actions | user_id | ⚠️ OPTIONAL - Audit trail |

**Total Critical Tables:** 5 core tables + Django auth tables

---

## ⚠️ Critical Considerations

### 1. Automatic Parking Slot Seeding


**File:** `parking/migrations/0011_seed_initial_parking_data.py`

**Behavior:** This migration automatically seeds 8 parking lots with 171 slots **ONLY IF** the database is empty.

```python
# From migration file:
if ParkingLot.objects.exists():
    print("Parking lots already exist. Skipping data seeding.")
    return
```

✅ **SAFE:** Will NOT create duplicates after migration because:
1. Migration checks if `ParkingLot.objects.exists()`
2. After import, parking lots will already exist
3. Seeding will be skipped automatically

### 2. Default Admin User Creation

**File:** `parking/management/commands/create_default_admin.py`  
**Called by:** `build.sh` during deployment

**Behavior:** Creates admin user (username=admin, password=smartpark2026) if no superuser exists.

✅ **SAFE:** Will NOT create duplicate admin after migration if:
- You import the existing admin user from old database
- OR you keep the current admin credentials

---

## 📋 Complete Migration Plan


### Phase 1: Pre-Migration Preparation (No Downtime)

**Duration:** 30 minutes

#### Step 1.1: Create New PostgreSQL Database on Render

1. **Go to Render Dashboard:** https://dashboard.render.com
2. **Click "New +" button** → Select "PostgreSQL"
3. **Configure new database:**
   ```
   Name: smart-parking-db-new
   Database: smart_parking_new
   User: smart_parking_user (auto-generated)
   Region: Same as your web service (Singapore/Oregon/Frankfurt)
   PostgreSQL Version: 16 (latest)
   Plan: FREE
   ```
4. **Click "Create Database"**
5. **Wait for Status:** "Available" (takes ~2-3 minutes)

#### Step 1.2: Save New Database Connection String

1. **In new database page**, find "Connections" section
2. **Copy "Internal Database URL"** (starts with `postgresql://`)
3. **Save to notepad** - format:
   ```
   postgresql://user:password@host:5432/database
   ```
4. **DO NOT update environment variable yet**



#### Step 1.3: Export Data from Old Database

**Option A: Using Django Management Command (Recommended)**

1. **Connect to old database via Render Shell:**
   ```bash
   # In Render Dashboard → Your Web Service → Shell tab
   python manage.py dumpdata --natural-foreign --natural-primary --indent=2 > production_backup.json
   ```

2. **Download backup file:**
   ```bash
   # Copy content of production_backup.json
   cat production_backup.json
   ```
   - Copy all content to local file: `production_backup.json`

3. **Verify backup file size:**
   ```bash
   ls -lh production_backup.json
   # Should be several KB to MB depending on data
   ```

**Option B: Using pg_dump (Advanced)**

1. **Get old database connection string from Render Dashboard:**
   - Go to old PostgreSQL database page
   - Copy "External Database URL"

2. **Run pg_dump locally:**
   ```bash
   pg_dump "postgresql://old-connection-string" > old_database.sql
   ```



---

### Phase 2: Setup New Database (No Downtime)

**Duration:** 10 minutes

#### Step 2.1: Apply Migrations to New Database

1. **Temporarily connect to new database locally:**
   ```bash
   # In your local project directory
   export DATABASE_URL="postgresql://new-connection-string"  # Linux/Mac
   # OR
   set DATABASE_URL=postgresql://new-connection-string  # Windows CMD
   # OR
   $env:DATABASE_URL="postgresql://new-connection-string"  # Windows PowerShell
   ```

2. **Run migrations:**
   ```bash
   python manage.py migrate
   ```
   
   **Expected output:**
   ```
   Operations to perform:
     Apply all migrations: admin, auth, contenttypes, parking, sessions
   Applying contenttypes.0001_initial... OK
   ...
   Applying parking.0011_seed_initial_parking_data... 
   Parking lots already exist. Skipping data seeding.  # This will show after import
   ```



#### Step 2.2: Import Data into New Database

1. **Load data from backup:**
   ```bash
   python manage.py loaddata production_backup.json
   ```

   **Expected output:**
   ```
   Installed 500 object(s) from 1 fixture(s)  # Number varies
   ```

2. **If using SQL dump (Option B):**
   ```bash
   psql "postgresql://new-connection-string" < old_database.sql
   ```

#### Step 2.3: Verify Data Integrity

**Run verification commands:**

```bash
# Check users
python manage.py shell -c "from django.contrib.auth.models import User; print(f'Users: {User.objects.count()}')"

# Check parking lots
python manage.py shell -c "from parking.models import ParkingLot; print(f'Parking Lots: {ParkingLot.objects.count()}')"

# Check parking slots
python manage.py shell -c "from parking.models import ParkingSlot; print(f'Parking Slots: {ParkingSlot.objects.count()}')"

# Check bookings
python manage.py shell -c "from parking.models import Booking; print(f'Bookings: {Booking.objects.count()}')"

# Check vehicles
python manage.py shell -c "from parking.models import Vehicle; print(f'Vehicles: {Vehicle.objects.count()}')"
```



**Expected Results:**
```
Users: 5-10 (or your actual count)
Parking Lots: 8
Parking Slots: 171
Bookings: 20-50 (or your actual count)
Vehicles: 5-10 (or your actual count)
```

**⚠️ CRITICAL:** If counts are 0 or don't match old database, **STOP** and investigate before proceeding.

---

### Phase 3: Switch to New Database (5-10 minutes downtime)

**Duration:** 5-10 minutes  
**Downtime:** Yes - users will see connection errors during this phase

#### Step 3.1: Update Environment Variable on Render

1. **Go to Render Dashboard** → Your Web Service
2. **Click "Environment" tab**
3. **Find `DATABASE_URL` variable**
4. **Click "Edit" (pencil icon)**
5. **Replace old connection string with new one:**
   ```
   Old: postgresql://old-user:old-pass@old-host:5432/old-db
   New: postgresql://new-user:new-pass@new-host:5432/new-db
   ```
6. **Click "Save Changes"**

**⚠️ IMPORTANT:** This triggers automatic redeployment!



#### Step 3.2: Monitor Deployment

1. **Watch deployment logs:**
   - Render Dashboard → Your Web Service → "Events" tab
   - Look for "Deploy started"

2. **Wait for build completion:**
   ```
   Expected log output:
   ==> Running build command 'bash build.sh'...
   ==> Installing dependencies...
   ==> Running migrations...
   Applying parking.0011_seed_initial_parking_data...
   Parking lots already exist. Skipping data seeding. ✅
   ==> Creating default admin...
   Admin user already exists. ✅
   ==> Build completed successfully!
   ```

3. **Deployment status changes:**
   - "Building" → "Deploying" → "Live" ✅

**Expected Time:** 5-7 minutes

---

### Phase 4: Post-Migration Verification (No Downtime)

**Duration:** 10 minutes

#### Step 4.1: Test Production Website

1. **Visit production URL:** `https://your-app.onrender.com`
2. **Verify homepage loads** ✅
3. **Test login with existing user credentials** ✅
4. **Navigate to "My Bookings"** - verify historical bookings display ✅
5. **Check parking lot listings** - verify all 8 lots visible ✅



#### Step 4.2: Verify Admin Access

1. **Login to Django admin:** `https://your-app.onrender.com/admin`
2. **Use existing superuser credentials**
3. **Check admin dashboard loads** ✅
4. **Verify data in admin:**
   - Users → Check user list
   - Parking Lots → Verify 8 lots
   - Parking Slots → Verify 171 slots
   - Bookings → Check booking history

#### Step 4.3: Test New Booking Flow

1. **Create a new test booking:**
   - Select parking lot
   - Choose slot
   - Complete payment
   - Verify booking confirmation ✅
   - Check QR code displays ✅

2. **Verify booking persists:**
   - Navigate to "My Bookings"
   - Verify new booking appears in list ✅

#### Step 4.4: Check Foreign Key Relationships

**Run integrity checks via Render Shell:**

```bash
# In Render Dashboard → Web Service → Shell

# Check booking-slot relationships
python manage.py shell -c "
from parking.models import Booking
bookings = Booking.objects.select_related('slot', 'user', 'vehicle').all()
print(f'Total bookings: {bookings.count()}')
for b in bookings[:5]:
    print(f'Booking {b.id}: User={b.user.username}, Slot={b.slot.slot_number}, Status={b.status}')
"
```



**Expected Output:**
```
Total bookings: 25
Booking 1: User=testuser, Slot=C01, Status=completed
Booking 2: User=admin, Slot=B03, Status=confirmed
...
```

**✅ SUCCESS CRITERIA:** All bookings show valid user, slot, and status data.

---

### Phase 5: Cleanup Old Database (After 7 days)

**⚠️ WAIT 7 DAYS** before deleting old database to ensure everything works perfectly.

#### Step 5.1: Verify New Database Stability (1 week later)

1. **Check production website daily** for any issues
2. **Monitor error logs** in Render Dashboard
3. **Verify new bookings save correctly**
4. **Test all critical features:**
   - User registration ✅
   - Login/logout ✅
   - Create booking ✅
   - View bookings ✅
   - Cancel booking ✅
   - Admin access ✅

#### Step 5.2: Delete Old Database

**ONLY AFTER 7 DAYS OF SUCCESSFUL OPERATION:**

1. **Go to Render Dashboard**
2. **Find OLD PostgreSQL database**
3. **Click database name**
4. **Scroll to "Danger Zone"**
5. **Click "Delete Database"**
6. **Type database name to confirm**
7. **Click "Delete"**

**⚠️ This action is irreversible!**



---

## 🔄 Rollback Plan (If Issues Arise)

### Scenario A: Issues During Phase 2 (Before Switching)

**No rollback needed** - old database still active, website still working.

1. **Stop migration attempts**
2. **Investigate data export/import errors**
3. **Fix issues and retry from Phase 1.3**

### Scenario B: Issues After Phase 3 (After Switching)

**Immediate rollback required** - website using new database with issues.

#### Rollback Steps (5 minutes):

1. **Go to Render Dashboard** → Your Web Service → Environment
2. **Edit `DATABASE_URL` variable**
3. **Change back to OLD database connection string:**
   ```
   New (problematic): postgresql://new-host:5432/new-db
   Old (rollback):     postgresql://old-host:5432/old-db
   ```
4. **Save changes** - triggers automatic redeploy
5. **Wait 5-7 minutes** for deployment
6. **Verify website works** with old database

**Result:** Website back to original state, zero data loss.



### Scenario C: Partial Data Loss Detected

**If you discover missing data after migration:**

1. **Immediately rollback to old database** (see Scenario B)
2. **Re-export data from old database:**
   ```bash
   # Be more selective with export
   python manage.py dumpdata auth.user > users.json
   python manage.py dumpdata parking > parking_data.json
   ```
3. **Merge with new database:**
   ```bash
   python manage.py loaddata users.json
   python manage.py loaddata parking_data.json
   ```
4. **Re-verify and switch again**

---

## 📊 Data Integrity Checks

### Before Migration (Old Database)

Run these commands to record baseline counts:

```bash
# Via Render Shell (connect to old database)
python manage.py shell -c "
from django.contrib.auth.models import User
from parking.models import *
print('=== OLD DATABASE COUNTS ===')
print(f'Users: {User.objects.count()}')
print(f'Superusers: {User.objects.filter(is_superuser=True).count()}')
print(f'Parking Lots: {ParkingLot.objects.count()}')
print(f'Parking Slots: {ParkingSlot.objects.count()}')
print(f'Vehicles: {Vehicle.objects.count()}')
print(f'Bookings: {Booking.objects.count()}')
print(f'Confirmed Bookings: {Booking.objects.filter(status=\"confirmed\").count()}')
print(f'Notifications: {SlotConflictNotification.objects.count()}')
"
```

**Save this output to compare after migration!**



### After Migration (New Database)

Run the same commands after switching to new database:

```bash
# Via Render Shell (connect to new database)
python manage.py shell -c "
from django.contrib.auth.models import User
from parking.models import *
print('=== NEW DATABASE COUNTS ===')
print(f'Users: {User.objects.count()}')
print(f'Superusers: {User.objects.filter(is_superuser=True).count()}')
print(f'Parking Lots: {ParkingLot.objects.count()}')
print(f'Parking Slots: {ParkingSlot.objects.count()}')
print(f'Vehicles: {Vehicle.objects.count()}')
print(f'Bookings: {Booking.objects.count()}')
print(f'Confirmed Bookings: {Booking.objects.filter(status=\"confirmed\").count()}')
print(f'Notifications: {SlotConflictNotification.objects.count()}')
"
```

**Compare with old database counts - MUST MATCH!**

### Foreign Key Integrity Check

```bash
python manage.py shell -c "
from parking.models import Booking

# Check all bookings have valid relationships
total = Booking.objects.count()
valid = Booking.objects.select_related('slot', 'user').count()
orphaned = total - valid

print(f'Total bookings: {total}')
print(f'Valid bookings: {valid}')
print(f'Orphaned bookings: {orphaned}')

if orphaned > 0:
    print('⚠️ WARNING: Some bookings have broken foreign keys!')
else:
    print('✅ All foreign key relationships intact')
"
```



---

## ⚠️ Common Issues and Solutions

### Issue 1: "relation does not exist" Error

**Cause:** Migrations not applied to new database.

**Solution:**
```bash
python manage.py migrate --run-syncdb
```

### Issue 2: Duplicate Key Violations During Import

**Cause:** Trying to import data with conflicting primary keys.

**Solution:**
```bash
# Clear new database and re-import
python manage.py flush --no-input
python manage.py migrate
python manage.py loaddata production_backup.json
```

### Issue 3: "No Such Table" During Verification

**Cause:** Connected to wrong database.

**Solution:**
```bash
# Verify DATABASE_URL
echo $DATABASE_URL  # Linux/Mac
echo %DATABASE_URL%  # Windows CMD
$env:DATABASE_URL  # Windows PowerShell

# Should point to new database
```

### Issue 4: Admin Login Fails After Migration

**Cause:** Password hashing mismatch or missing superuser.

**Solution:**
```bash
# Create new superuser
python manage.py createsuperuser

# OR reset password for existing user
python manage.py changepassword admin
```



### Issue 5: Parking Slots Duplicated

**Cause:** Migration 0011 ran before data import.

**Solution:**
```bash
# Delete duplicate lots (keep only imported ones)
python manage.py shell -c "
from parking.models import ParkingLot
# Check for duplicates by name
lots = ParkingLot.objects.values('name').annotate(count=Count('id')).filter(count__gt=1)
print('Duplicate lots:', lots)
"

# If duplicates exist, identify and delete manually via admin
```

### Issue 6: QR Codes Not Displaying

**Cause:** QR codes are generated dynamically - this is expected behavior.

**Solution:** No action needed - QR codes generate on-demand from booking data.

---

## 📝 Migration Checklist

### Pre-Migration (Print and Check Off)

- [ ] New PostgreSQL database created on Render
- [ ] New database status is "Available"
- [ ] New `DATABASE_URL` saved to notepad
- [ ] Old database backup exported (`production_backup.json`)
- [ ] Backup file downloaded and saved locally
- [ ] Old database counts recorded
- [ ] Team notified about upcoming maintenance window



### During Migration

- [ ] Migrations applied to new database
- [ ] Data imported successfully (`loaddata` succeeded)
- [ ] New database counts verified and match old database
- [ ] Foreign key integrity check passed
- [ ] `DATABASE_URL` updated on Render
- [ ] Deployment triggered and completed
- [ ] Deployment logs show no errors

### Post-Migration

- [ ] Production website loads successfully
- [ ] User login works with existing credentials
- [ ] Admin panel accessible
- [ ] All parking lots visible (8 total)
- [ ] Historical bookings display correctly
- [ ] New booking flow works end-to-end
- [ ] QR codes generate dynamically
- [ ] No "Parking lots already exist" in deployment logs ✅
- [ ] No duplicate parking slots created ✅
- [ ] All foreign key relationships intact ✅

### Cleanup (After 7 Days)

- [ ] 7 days passed since migration
- [ ] No errors or issues reported
- [ ] All features working correctly
- [ ] Old database deleted on Render

---

## 🎯 Expected Timeline

| Phase | Duration | Downtime | Actions |
|-------|----------|----------|---------|
| **Phase 1:** Preparation | 30 min | No | Create new DB, export data |
| **Phase 2:** Setup New DB | 10 min | No | Migrate, import, verify |
| **Phase 3:** Switch | 5-10 min | **Yes** | Update env var, redeploy |
| **Phase 4:** Verification | 10 min | No | Test website, verify data |
| **Phase 5:** Cleanup | - | No | Delete old DB (after 7 days) |
| **TOTAL** | ~1 hour | **5-10 min** | Complete migration |



---

## 💰 Cost Analysis

### Current Setup (Expiring)
- **Old PostgreSQL Database:** FREE (expiring in 14 days)
- **Web Service:** FREE
- **Total:** $0/month

### After Migration
- **New PostgreSQL Database:** FREE (256 MB storage, sufficient for your data)
- **Web Service:** FREE
- **Total:** $0/month ✅

**Migration Cost:** $0
**Ongoing Cost:** $0/month forever

---

## 🔐 Security Considerations

### Database Connection Strings

**Format:**
```
postgresql://username:password@hostname:5432/database
```

**Security Tips:**
1. ✅ Never commit `DATABASE_URL` to git
2. ✅ Use Render's internal database URL (not external)
3. ✅ Keep connection strings in Render environment variables only
4. ✅ Change database password if connection string is ever exposed

### Admin Credentials

**Current default admin:**
- Username: `admin`
- Password: `smartpark2026`

**⚠️ RECOMMENDATION:** Change admin password after migration:
```bash
python manage.py changepassword admin
```



---

## 📞 When to Redeploy

### Automatic Redeployment

**Render automatically redeploys when:**
- ✅ You update any environment variable (including `DATABASE_URL`)
- ✅ You push code to GitHub main branch
- ✅ You click "Manual Deploy" in Render dashboard

### Manual Redeployment Required

**You need to manually redeploy if:**
- ❌ Never needed for this migration - updating `DATABASE_URL` triggers auto-deploy

### Redeployment Process

1. **Update `DATABASE_URL`** → Auto-redeploy triggers
2. **Wait 5-7 minutes** for build and deploy
3. **Check "Events" tab** for deployment status
4. **Verify "Live" status** appears

**No manual redeploy button click needed!**

---

## 🎓 Understanding the Migration

### Why This Works

1. **Separate Database Creation:** New DB created while old DB still serves traffic
2. **Data Export:** Snapshot of old DB taken without affecting live site
3. **Parallel Import:** Data loaded into new DB independently
4. **Atomic Switch:** Single environment variable change = instant switch
5. **Rollback Ready:** Old DB kept alive for 7 days as safety net



### Why No Duplicate Parking Slots

**Migration 0011 logic:**
```python
if ParkingLot.objects.exists():
    print("Parking lots already exist. Skipping data seeding.")
    return
```

**Sequence:**
1. New DB created (empty) ✅
2. Migrations run → 0011 creates 8 lots + 171 slots ✅
3. Data imported → **ERROR: Duplicate keys!** ❌

**Wait, that's wrong! Correct sequence:**

1. New DB created (empty) ✅
2. Migrations run up to 0010 ✅
3. Migration 0011 checks: `if ParkingLot.objects.exists()` → FALSE (empty DB)
4. Migration 0011 seeds: 8 lots + 171 slots ✅
5. Data import: `loaddata production_backup.json`
   - **Option A:** Succeeds → old data replaces seeded data ✅
   - **Option B:** Fails with duplicate keys → flush and retry ✅

**Safe approach to avoid conflicts:**

```bash
# After migrations, BEFORE running 0011 seeding
python manage.py migrate parking 0010  # Stop before 0011
python manage.py loaddata production_backup.json  # Import old data
python manage.py migrate  # Run remaining migrations (0011 skipped due to existing data)
```



---

## 🚨 CRITICAL WARNINGS

### ❌ DO NOT DO THESE BEFORE APPROVAL

1. **DO NOT** delete old database before 7 days of verification
2. **DO NOT** run `python manage.py flush` on old database
3. **DO NOT** update `DATABASE_URL` until new database is verified
4. **DO NOT** skip data integrity checks
5. **DO NOT** proceed if verification counts don't match

### ✅ SAFE TO DO ANYTIME

1. ✅ Create new PostgreSQL database on Render
2. ✅ Export data from old database (`dumpdata`)
3. ✅ Apply migrations to new database
4. ✅ Import data to new database
5. ✅ Run verification queries
6. ✅ Keep both databases running simultaneously

---

## 📧 Communication Template

### Notify Users (Optional)

**Subject:** Scheduled Maintenance - Smart Parking System

**Body:**
```
Dear Users,

We will be performing a database migration to improve system reliability.

Date: [Your chosen date]
Time: [Your chosen time]
Duration: 5-10 minutes
Impact: Temporary unavailability of the website

During this time:
- Website will be inaccessible
- Active bookings are NOT affected
- All data will be preserved

We appreciate your patience.

Smart Parking Team
```



---

## 🎬 Quick Start Guide (TL;DR)

For experienced users who want the condensed version:

### Commands to Run

```bash
# 1. Create new DB on Render (via dashboard)
# 2. Export old data
python manage.py dumpdata --natural-foreign --natural-primary --indent=2 > backup.json

# 3. Setup new DB locally
export DATABASE_URL="new-connection-string"
python manage.py migrate parking 0010  # Before seeding migration
python manage.py loaddata backup.json
python manage.py migrate  # Complete remaining migrations

# 4. Verify
python manage.py shell -c "from parking.models import *; print(ParkingLot.objects.count(), ParkingSlot.objects.count())"

# 5. Switch on Render
# Update DATABASE_URL env var → auto-deploys

# 6. Verify production
# Visit website, test features

# 7. Delete old DB (after 7 days)
```

---

## ✅ Final Checklist Before You Begin

- [ ] I have read and understood this entire migration plan
- [ ] I have 14 days remaining on old database (grace period)
- [ ] I can afford 5-10 minutes of downtime
- [ ] I have access to Render Dashboard
- [ ] I have local development environment set up
- [ ] I have saved old `DATABASE_URL` connection string
- [ ] I understand rollback procedure
- [ ] I will wait 7 days before deleting old database
- [ ] I am ready to proceed with Phase 1



---

## 📞 Support and Questions

### If You Need Help

1. **Before starting:** Reply with questions about any step
2. **During migration:** I can guide you through each phase
3. **After migration:** Report any issues immediately for troubleshooting

### Common Questions

**Q: Can I do this migration during business hours?**  
A: Yes, but expect 5-10 minutes downtime. Best to do during low-traffic hours.

**Q: Will user passwords be preserved?**  
A: Yes, all password hashes are migrated intact. Users can login with existing credentials.

**Q: What if the new database runs out of space?**  
A: Render free tier provides 256 MB. Your current data is likely <50 MB. You're safe.

**Q: Can I test the migration on a staging environment first?**  
A: Yes! Create a second web service + database for testing, then repeat for production.

**Q: What if I accidentally delete the old database?**  
A: If you have `production_backup.json`, you can restore. Otherwise, data is lost. **Always keep backup!**

**Q: How often do I need to migrate databases?**  
A: Render free tier databases last 90 days. You'll need to migrate every ~80-85 days.

**Q: Can I automate this process?**  
A: Partially. The export/import can be scripted, but DATABASE_URL update requires manual action.

---

## 🏁 Ready to Proceed?

### Next Steps

1. **Read this entire document carefully** ✅
2. **Ask any questions** before proceeding
3. **Wait for my approval** to begin Phase 1
4. **Follow the checklist** step-by-step
5. **Report progress** after each phase

---

**Migration Plan Created:** 2025-01-XX  
**Document Version:** 1.0  
**Status:** ⏳ AWAITING YOUR APPROVAL TO BEGIN  

---

**🚦 STOP HERE - DO NOT PROCEED WITHOUT CONFIRMATION**

Reply with "APPROVED" when you're ready to start Phase 1, or ask any questions you have about the plan.
