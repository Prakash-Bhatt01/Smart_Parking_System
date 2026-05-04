# SmartPark - Intelligent Parking Management System

A comprehensive Django-based parking management system with modern features including payment processing, QR code generation, and user profile management.

## 🚀 Features

### Core Functionality
- **Parking Lot Management**: Browse and search available parking lots
- **Real-time Slot Booking**: Book parking slots with live availability
- **User Authentication**: Secure registration and login system
- **Vehicle Management**: Track multiple vehicles per user

### Payment System
- **Demo Payment Flow**: Simulated payment processing
- **Three-stage Workflow**: Booking → Payment → Confirmation
- **Payment Form**: Credit card form with HTML5 validation
- **Success Confirmation**: Detailed booking confirmation page

### QR Code Integration
- **Automatic Generation**: QR codes created after payment
- **Booking Details**: Contains booking ID, slot number, and location
- **Easy Access**: View QR codes in My Bookings section
- **Hardware Demo Ready**: Scan QR codes at physical parking locations

### User Profile
- **Personal Information**: Display name, email, and join date
- **Booking Statistics**: Total, active, completed, and cancelled bookings
- **Recent Activity**: View last 5 bookings with details
- **Quick Actions**: Navigate to bookings or search parking

### Time Management
- **Smart Defaults**: Pre-filled booking times (next hour + 2 hours)
- **Local Timezone**: Asia/Kolkata (IST) timezone support
- **User-friendly Format**: 12-hour time display with AM/PM
- **Duration Calculator**: Real-time cost estimation

### Additional Features
- **Booking Management**: Cancel and extend bookings
- **Overstay Detection**: Automatic fine calculation
- **Countdown Timers**: Real-time parking time tracking
- **Responsive Design**: Mobile-friendly interface
- **PWA Support**: Progressive Web App capabilities

## 🛠️ Technology Stack

- **Backend**: Django 6.0.3
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript
- **Icons**: Font Awesome 6.4.0
- **QR Codes**: qrcode library with Pillow
- **Maps**: Leaflet.js for location display

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/Prakash-Bhatt01/Smart_Parking_System.git
cd Smart_Parking_System
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install django pillow qrcode[pil]
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create superuser (optional)**
```bash
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

7. **Access the application**
- Open browser and navigate to: `http://127.0.0.1:8000/`
- Admin panel: `http://127.0.0.1:8000/admin/`

## 📱 Usage

### For Users

1. **Register/Login**
   - Create an account or login with existing credentials
   - Access personalized dashboard

2. **Find Parking**
   - Search for parking lots by city or vehicle type
   - View available slots and pricing

3. **Book a Slot**
   - Select desired time slot (default: 2 hours)
   - Enter vehicle details (optional)
   - Review booking summary

4. **Complete Payment**
   - Fill in demo payment form
   - Receive booking confirmation
   - Get QR code for parking access

5. **Manage Bookings**
   - View active, completed, and cancelled bookings
   - Extend or cancel bookings as needed
   - Download QR codes for parking entry

### For Administrators

1. **Access Admin Panel**
   - Login at `/admin/` with superuser credentials

2. **Manage Parking Lots**
   - Add new parking locations
   - Set pricing and capacity
   - Upload location images

3. **Monitor Bookings**
   - View all bookings and their status
   - Handle overstay fines
   - Generate reports

## 🗂️ Project Structure

```
Smart_Parking_System/
├── parking/                    # Main application
│   ├── migrations/            # Database migrations
│   ├── models.py              # Data models
│   ├── views.py               # View functions
│   ├── forms.py               # Form definitions
│   ├── urls.py                # URL routing
│   └── tests.py               # Test cases
├── smart_parking/             # Project settings
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL configuration
│   └── wsgi.py                # WSGI configuration
├── templates/                 # HTML templates
│   ├── base.html              # Base template
│   ├── home.html              # Homepage
│   ├── payment.html           # Payment form
│   ├── booking_success.html   # Success page
│   ├── profile.html           # User profile
│   └── ...                    # Other templates
├── static/                    # Static files
│   ├── css/                   # Stylesheets
│   ├── js/                    # JavaScript files
│   └── icons/                 # App icons
├── media/                     # User uploads
│   ├── parking_lots/          # Parking lot images
│   └── qrcodes/               # Generated QR codes
├── manage.py                  # Django management script
└── README.md                  # This file
```

## 🔧 Configuration

### Timezone Settings
The application uses Asia/Kolkata (IST) timezone by default. To change:

```python
# smart_parking/settings.py
TIME_ZONE = 'Your/Timezone'  # e.g., 'UTC', 'America/New_York'
```

### Payment Configuration
Currently uses demo payment (no real transactions). To integrate real payment:

1. Choose payment gateway (Stripe, Razorpay, etc.)
2. Update `process_payment` view in `parking/views.py`
3. Add payment gateway credentials to settings
4. Implement webhook handlers

### QR Code Customization
Modify QR code generation in `parking/views.py`:

```python
qr = qrcode.QRCode(
    version=1,                              # Size (1-40)
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction
    box_size=10,                            # Pixel size
    border=4,                               # Border size
)
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test parking.tests

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📊 Database Schema

### Main Models

- **ParkingLot**: Parking location details
- **ParkingSlot**: Individual parking spaces
- **Booking**: Reservation records
- **Vehicle**: User vehicle information
- **User**: Django's built-in user model

### Booking Status Flow
```
pending → confirmed → active → completed
                  ↓
              cancelled
                  ↓
              overstay
```

## 🔐 Security Features

- CSRF protection on all forms
- User authentication required for bookings
- Ownership verification for booking access
- POST-based logout with CSRF token
- Secure password hashing
- SQL injection prevention (Django ORM)

## 🎨 UI/UX Features

- **Responsive Design**: Works on all device sizes
- **Modern Interface**: Clean, card-based layout
- **Interactive Elements**: Hover effects and animations
- **Real-time Updates**: Countdown timers for bookings
- **Status Badges**: Color-coded booking statuses
- **Empty States**: Helpful messages for new users

## 📈 Future Enhancements

- [ ] Real payment gateway integration
- [ ] Email notifications for bookings
- [ ] SMS alerts for parking expiry
- [ ] Mobile app (React Native/Flutter)
- [ ] Admin analytics dashboard
- [ ] Booking history export (PDF/CSV)
- [ ] Multi-language support
- [ ] Dark mode theme
- [ ] Social media login
- [ ] Parking spot reviews and ratings

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Author

**Prakash Bhatt**
- GitHub: [@Prakash-Bhatt01](https://github.com/Prakash-Bhatt01)

## 🙏 Acknowledgments

- Django framework for robust backend
- Font Awesome for beautiful icons
- Leaflet.js for interactive maps
- QR code library for seamless integration

## 📞 Support

For support, email prakash@example.com or open an issue in the GitHub repository.

## 🔄 Version History

### v1.0.0 (Current)
- ✅ Complete parking management system
- ✅ Demo payment flow with 3-stage workflow
- ✅ QR code generation for bookings
- ✅ User profile with statistics
- ✅ Logout functionality with security
- ✅ Time display fixes (12-hour format, IST timezone)
- ✅ Responsive design for all devices
- ✅ PWA support

---

**Made with ❤️ for efficient parking management**
