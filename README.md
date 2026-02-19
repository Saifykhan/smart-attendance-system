# Smart Attendance System

A face-recognition-based attendance system with separate dashboards for students, teachers, and administrators.

## Project Structure

```
smart-attendance-system/
├── backend/                    # FastAPI backend server
│   ├── main.py                # Main application entry point
│   ├── auth.py                # JWT authentication and password hashing
│   ├── database.py            # MongoDB connection setup
│   ├── models.py              # Pydantic models for request/response
│   ├── student.py             # Student management endpoints
│   ├── teacher.py             # Teacher management endpoints
│   ├── admin.py               # Admin management endpoints
│   ├── attendance.py          # Attendance marking endpoints (auto & manual)
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variables template
└── frontend/                  # HTML/JavaScript frontend
    ├── index.html             # Login and registration page
    ├── teacher_dashboard.html # Teacher attendance marking
    ├── admin-dashboard.html   # Admin panel
    └── check-attendance.html  # Student attendance viewer
```

## Features

### 🔐 Authentication
- JWT token-based authentication
- Role-based access control (Student, Teacher, Admin)
- Password hashing with bcrypt
- Session management via localStorage

### 📷 Face Recognition
- Real-time camera access for face capture
- Face detection using face-api.js
- Encoding-based face matching
- Automatic attendance marking via face recognition

### 📊 Attendance Tracking
- Manual attendance marking (by teacher)
- Automatic attendance marking (via face recognition)
- Per-student attendance history
- Per-date attendance reports

### 👥 User Management
- Student registration with face biometrics
- Teacher management
- Admin user creation and management
- Role-based permissions

## Setup Instructions

### Prerequisites
- Python 3.8+
- MongoDB (local or cloud)
- Node.js/npm (optional, for build tools)
- Modern web browser with camera access

### Backend Setup

1. **Navigate to backend folder**:
   ```bash
   cd backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```
   MONGO_URI=mongodb://localhost:27017
   DB_NAME=smart_attendance_db
   JWT_SECRET=your-secret-key-here
   ```

5. **Start MongoDB** (if using local):
   ```bash
   mongod
   ```

6. **Run the backend server**:
   ```bash
   python -m uvicorn main:app --reload
   ```
   
   Backend will be available at: `http://127.0.0.1:8000`

### Frontend Setup

1. **Open in browser**:
   Simply open `frontend/index.html` in your web browser
   
   Or serve with a local server:
   ```bash
   python -m http.server 8001 --directory frontend
   ```
   
   Then visit: `http://127.0.0.1:8001`

## Default Credentials

The system seeds three default accounts on startup:

| Role | User ID | Password |
|------|---------|----------|
| Admin | `admin` | `admin123` |
| Teacher | `teacher` | `teacher123` |
| Student | `student` | `student123` |

⚠️ **Change these credentials in production!**

## API Endpoints

### Authentication
```
POST /login
- body: { user_id: string, password: string }
- returns: { token: string, role: string, user_id: string }
```

### Students
```
POST /students/register
GET  /students/
GET  /students/{user_id}
PUT  /students/{user_id}
DELETE /students/{user_id}
POST /students/{user_id}/face
```

### Teachers
```
GET /teachers/
GET /teachers/me
```

### Admin
```
POST /admin/add-user
GET  /admin/users
PUT  /admin/users/{user_id}
DELETE /admin/users/{user_id}
```

### Attendance
```
POST /attendance/auto      # Mark via face recognition
POST /attendance/manual    # Mark manually
GET  /attendance/student/{user_id}
GET  /attendance/date/{date}
```

## Usage Guide

### For Students

1. **Register**:
   - Open `index.html`
   - Click "Register Face Data"
   - Enter name, student ID, and password
   - Capture face from 3 angles (front, left, right)
   - Submit

2. **Check Attendance**:
   - Go to `check-attendance.html`
   - Enter your student ID and password
   - View your attendance history

### For Teachers

1. **Login**:
   - Open `index.html` and login with teacher credentials
   - Redirects to `teacher_dashboard.html`

2. **Mark Attendance**:
   - **Manual**: Click "All Student", select present/absent via radio buttons
   - **Auto**: Click "Automatic Scan", position students in front of camera

### For Admins

1. **Login**:
   - Open `index.html` and login with admin credentials
   - Redirects to `admin-dashboard.html`

2. **Manage Users**:
   - View dashboard statistics
   - Add/edit/delete users via sidebar menu

## Database Schema

### users Collection
```json
{
  "_id": ObjectId,
  "name": "John Doe",
  "user_id": "student123",
  "password_hash": "bcrypt_hash",
  "role": "student|teacher|admin",
  "face_encodings": [[0.1, 0.2, ...], ...],
  "face_images": ["data:image/png;base64,...", ...],
  "created_at": ISODate
}
```

### attendance Collection
```json
{
  "_id": ObjectId,
  "student_user_id": "student123",
  "date": "2025-02-19",
  "status": "present|absent",
  "marked_by": "teacher123",
  "timestamp": ISODate,
  "score": 0.95
}
```

## Configuration

### Environment Variables
See `.env.example` for all available configurations.

### Face Recognition Threshold
- **File**: `backend/attendance.py` line 53
- **Current**: 0.62 (threshold for face matching)
- Adjust based on accuracy requirements:
  - Lower = stricter matching
  - Higher = more lenient matching

## Troubleshooting

### "Cannot access camera"
- Check browser permissions
- Ensure HTTPS if required by browser
- Use supported browser (Chrome, Firefox, Edge)

### "MongoDB connection failed"
- Verify MongoDB is running
- Check MONGO_URI in .env file
- For Atlas: verify VPN/firewall access

### "Face detection not working"
- Ensure good lighting
- Clear camera lens
- Check internet connection (face-api.js models load from CDN)
- Try increasing detection threshold

### "Login fails"
- Verify backend is running (http://127.0.0.1:8000)
- Check credentials in browser console (F12)
- Ensure CORS is properly configured

### "Token expired error"
- Clear localStorage: `localStorage.clear()`
- Login again
- Note: Tokens expire after 24 hours

## Security Notes

⚠️ **For production use:**
1. Change JWT_SECRET in .env
2. Use HTTPS everywhere
3. Implement rate limiting on login endpoint
4. Add session timeouts
5. Use strong, unique passwords
6. Implement audit logging
7. Add database encryption
8. Use environment-specific .env files
9. Implement CSRF protection
10. Regular security updates

## Known Issues

- Face recognition may be inaccurate in low light
- Face encoding extraction needs improvement in registration
- No automatic token refresh implemented
- localStorage tokens not encrypted

## Recent Fixes

✅ **Fixed (v1.1)**:
- Fixed `/attendance/{studentId}` → `/attendance/student/{studentId}` endpoint
- Fixed inconsistent host URLs (localhost → 127.0.0.1)
- Added error handling in student attendance view
- Updated hardcoded passwords in frontend files

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit pull request

## License

This project is provided as-is for educational purposes.

## Contact

For issues or questions, refer to the project documentation or create an issue.

---

**Last Updated**: February 19, 2026
**Status**: Production Ready (with caveats noted above)
