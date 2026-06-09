# SmartPark Login Credentials

## ✅ FRESH ADMIN ACCOUNT CREATED

**Status**: All login/logout functionality working perfectly!

---

## 🔐 Current Working Credentials

### Admin Account (Superuser)
- **Username**: `admin`
- **Password**: `admin@123`
- **Email**: admin@smartpark.com
- **Access**: Full admin panel access at `/admin/`
- **Permissions**: Can manage all parking lots, slots, bookings, and users

### Regular User Account 1
- **Username**: `User1`
- **Password**: `user@123`
- **Name**: Prakash Bhatt
- **Email**: prakashbhattofficial01@gmail.com
- **Access**: Can book parking slots, view bookings, manage profile

### Regular User Account 2
- **Username**: `Prakz`
- **Password**: `prakz@123`
- **Name**: Prakash Bhatt
- **Email**: prakashbhatt@gmail.com
- **Access**: Can book parking slots, view bookings, manage profile

---

## Quick Start

### 1. Start the Development Server
```bash
python manage.py runserver
```

### 2. Access the Application
- **Homepage**: http://127.0.0.1:8000/
- **Login**: http://127.0.0.1:8000/login/
- **Admin Panel**: http://127.0.0.1:8000/admin/

### 3. Login as Admin
1. Go to http://127.0.0.1:8000/admin/
2. Username: `admin`
3. Password: `admin123`
4. Click "Log in"

### 4. Login as Regular User
1. Go to http://127.0.0.1:8000/login/
2. Username: `User1`
3. Password: `user123`
4. Click "Login"

---

## Features Working

✅ **Login** - Users can login with username and password  
✅ **Logout** - Users can logout (both GET and POST methods)  
✅ **Admin Panel** - Admins can access Django admin at `/admin/`  
✅ **Registration** - New users can register at `/register/`  
✅ **Protected Pages** - Login required for booking, profile, etc.  
✅ **Session Management** - User sessions properly maintained  
✅ **Password Reset** - Can reset passwords via `python manage.py changepassword <username>`

---

## Password Management

### Reset Password for Existing User
```bash
python manage.py changepassword User1
```

### Create New Superuser
```bash
python manage.py createsuperuser
```

### Set Password Programmatically
```python
python reset_passwords.py  # Use the provided script
```

---

## Testing Authentication

### Run Diagnostic Tests
```bash
# Test all authentication features
python test_auth_final.py

# Check user credentials
python check_users.py

# Reset passwords to known values
python reset_passwords.py
```

### Manual Testing Checklist

- [ ] Can access login page
- [ ] Can login with admin credentials
- [ ] Can access admin panel
- [ ] Can logout from admin panel
- [ ] Can login with regular user credentials
- [ ] Can access protected pages (search, bookings)
- [ ] Can logout from user account
- [ ] Wrong password shows error
- [ ] Can register new account

---

## Troubleshooting

### Issue: "Invalid HTTP_HOST header"
**Solution**: Check that `ALLOWED_HOSTS` in `smart_parking/settings.py` includes your domain:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
```

### Issue: "Forgot password"
**Solution**: Run password reset script:
```bash
python reset_passwords.py
```

### Issue: "Admin panel not accessible"
**Solution**: Make sure the user is a superuser:
```python
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
user.is_superuser = True
user.is_staff = True
user.save()
```

### Issue: "CSRF verification failed"
**Solution**: 
1. Clear browser cookies
2. Make sure CSRF middleware is enabled in settings
3. Use POST form with `{% csrf_token %}` in templates

---

## Hardware Demo Notes

For the Arduino hardware demo, you may want to:

1. **Create demo users** with easy-to-remember credentials
2. **Pre-populate parking lots** with hardware slots (H1, H2, H3)
3. **Test booking flow** before the demo
4. **Keep credentials visible** for judges/audience

### Demo Credentials
```
Admin Login:
  URL: http://127.0.0.1:8000/admin/
  User: admin
  Pass: admin@123

User Login:
  URL: http://127.0.0.1:8000/login/
  User: User1
  Pass: user@123
```

---

## Security Notes

⚠️ **Development Only**: These are development credentials. For production:
- Use strong, unique passwords
- Enable HTTPS
- Set `DEBUG = False`
- Use environment variables for secrets
- Enable additional security settings

---

**Last Updated**: June 9, 2026  
**Status**: ✅ All authentication features working  
**Git Commit**: `433ed62`
