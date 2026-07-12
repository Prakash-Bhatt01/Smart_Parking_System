# Render Database Migration - Quick Reference Card

## 🎯 Goal
Migrate from expiring Render PostgreSQL to new free Render PostgreSQL with zero data loss.

---

## ⚡ Quick Steps

### 1. Create New Database (Render Dashboard)
```
New+ → PostgreSQL → FREE tier
Name: smart-parking-db-new
Wait for "Available" status
Copy "Internal Database URL"
```

### 2. Export Old Data
```bash
# Via Render Shell (old database)
python manage.py dumpdata --natural-foreign --natural-primary --indent=2 > backup.json
cat backup.json  # Copy to local file
```

### 3. Setup New Database (Local)
```bash
export DATABASE_URL="postgresql://new-connection-string"
python manage.py migrate parking 0010
python manage.py loaddata backup.json
python manage.py migrate
```

### 4. Verify Counts
```bash
python manage.py shell -c "
from django.contrib.auth.models import User
from parking.models import *
print(f'Users: {User.objects.count()}')
print(f'Lots: {ParkingLot.objects.count()}')
print(f'Slots: {ParkingSlot.objects.count()}')
print(f'Bookings: {Booking.objects.count()}')
"
```

### 5. Switch Database (Render Dashboard)
```
Web Service → Environment → DATABASE_URL
Replace old URL with new URL → Save
Auto-deploys in 5-7 minutes
```

### 6. Verify Production
- Visit website ✅
- Login ✅
- Check bookings ✅
- Create test booking ✅

### 7. Delete Old DB (After 7 Days)
```
Render Dashboard → Old PostgreSQL → Delete
```

---

## ⚠️ Expected Counts

```
Parking Lots: 8
Parking Slots: 171
Users: [Your count]
Bookings: [Your count]
```

---

## 🔄 Rollback (If Issues)

```
Render Dashboard → Web Service → Environment
DATABASE_URL → Change back to OLD connection string → Save
```

---

## ⏱️ Timeline

- **Phase 1-2:** 40 min (No downtime)
- **Phase 3:** 5-10 min (⚠️ Downtime)
- **Phase 4:** 10 min (No downtime)
- **Total:** ~1 hour, 5-10 min downtime

---

## 🚨 Critical Rules

1. ❌ Don't delete old DB before 7 days
2. ❌ Don't update DATABASE_URL until verified
3. ❌ Don't skip count verification
4. ✅ Keep backup.json file safe
5. ✅ Test rollback if unsure

---

**Status: Awaiting Approval**
