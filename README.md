# Smart Attendance Management System

A production-ready attendance management system built with Django backend and modern Bootstrap frontend, featuring OTP-based attendance verification.

## Features

### Faculty Portal
- ✅ Faculty registration and authentication
- ✅ Student registration with photo upload
- ✅ Session creation and management
- ✅ 6-digit OTP generation (30-second expiry)
- ✅ View attendance for each session
- ✅ Dashboard with statistics

### Student Portal
- ✅ Student login
- ✅ Mark attendance using OTP
- ✅ View attendance history
- ✅ Dashboard with attendance stats

## Technology Stack

### Backend
- **Django 5.0** - Web framework
- **Django REST Framework** - API development
- **Simple JWT** - JWT authentication
- **SQLite** - Database (easily switchable to PostgreSQL)
- **Pillow** - Image processing

### Frontend
- **Bootstrap 5** - UI framework
- **Vanilla JavaScript** - Dynamic interactions
- **HTML5/CSS3** - Modern web standards

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Steps

1. **Navigate to project directory**
   ```bash
   cd "e:\otp attendance"
   ```

2. **Activate virtual environment**
   ```bash
   .\venv\Scripts\activate
   ```

3. **Run the development server**
   ```bash
   python manage.py runserver
   ```

4. **Access the application**
   - Open your browser and go to: `http://127.0.0.1:8000`
   - Or open `index.html` directly in your browser

## Usage Guide

### For Faculty

1. **Register**: Go to Faculty Registration page
2. **Login**: Use your credentials to login
3. **Register Students**: Add students with their details and photos
4. **Create Sessions**: Create attendance sessions for your courses
5. **Generate OTP**: Generate 6-digit OTP for students to mark attendance
6. **View Attendance**: Check which students marked attendance

### For Students

1. **Login**: Use credentials provided by faculty
2. **Mark Attendance**: 
   - Select the session
   - Enter the 6-digit OTP provided by faculty
   - Submit within 30 seconds
3. **View History**: Check your attendance records

## API Endpoints

### Authentication
- `POST /api/auth/register/faculty/` - Faculty registration
- `POST /api/auth/register/student/` - Student registration (faculty only)
- `POST /api/auth/login/` - User login
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Sessions
- `GET /api/sessions/` - List sessions
- `POST /api/sessions/` - Create session (faculty only)

### OTP
- `POST /api/otp/generate/` - Generate OTP (faculty only)
- `GET /api/otp/<session_id>/` - Get OTP for session (faculty only)

### Attendance
- `POST /api/attendance/mark/` - Mark attendance (student only)
- `GET /api/attendance/history/` - Get attendance history (student only)
- `GET /api/attendance/session/<session_id>/` - View session attendance (faculty only)

## Project Structure

```
attendance_system/
├── accounts/              # User management app
│   ├── models.py         # User, Faculty, Student models
│   ├── serializers.py    # DRF serializers
│   ├── views.py          # API views
│   └── urls.py           # URL routing
├── attendance/           # Attendance management app
│   ├── models.py         # Session, OTP, Attendance models
│   ├── serializers.py    # DRF serializers
│   ├── views.py          # API views
│   └── urls.py           # URL routing
├── static/               # Static files
│   ├── css/
│   │   └── styles.css    # Custom styles
│   └── js/
│       └── auth.js       # Authentication logic
├── templates/            # HTML templates
├── media/                # Uploaded files
├── *.html                # Frontend pages
├── manage.py             # Django management script
└── requirements.txt      # Python dependencies
```

## Security Features

- JWT-based authentication
- Password hashing
- CORS protection
- OTP expiration (30 seconds)
- Single-use OTP validation
- Role-based access control

## Admin Panel

Access the Django admin panel at `http://127.0.0.1:8000/admin/`

Create a superuser:
```bash
python manage.py createsuperuser
```

## Troubleshooting

### Server not starting
- Make sure virtual environment is activated
- Check if port 8000 is available
- Verify all dependencies are installed

### OTP not working
- Ensure OTP is entered within 30 seconds
- Check that session has OTP enabled
- Verify student is logged in

### Photo upload issues
- Check file size (max 5MB)
- Ensure file format is JPEG or PNG
- Verify media folder permissions

## Future Enhancements

- QR code generation for sessions
- Email notifications
- GPS-based attendance verification
- Face recognition integration
- Export attendance reports (PDF/Excel)
- Mobile app

## License

This project is created for educational purposes.

## Support

For issues or questions, please check the documentation or contact the development team.
