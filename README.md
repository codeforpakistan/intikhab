# Intikhab - Electronic Voting System

![Intikhab Banner](https://img.shields.io/badge/Intikhab-Electronic%20Voting%20System-success?style=for-the-badge)

A secure electronic voting platform built with Django that ensures transparency and privacy in democratic elections using advanced cryptographic methods.

## 🗳️ Features

- **🔒 Secure & Private**: Advanced cryptographic methods ensure vote privacy using homomorphic encryption
- **👁️ Transparent & Verifiable**: Election results are publicly verifiable while maintaining voter anonymity
- **📱 Easy & Accessible**: User-friendly interface accessible to everyone, anywhere, anytime
- **⏰ Real-time Election Management**: Live election status updates and vote counting
- **👥 Multi-candidate Support**: Support for multiple candidates with party affiliations
- **🛡️ CSRF Protection**: Built-in security features to prevent malicious attacks
- **📊 Results Dashboard**: Comprehensive election results with vote percentages and visual charts

## 🚀 Technology Stack

- **Backend**: Django 5.2.6
- **Frontend**: Bootstrap 5.3.3 + Bootstrap Icons 1.11.0
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Encryption**: LightPHE (Homomorphic Encryption Library)
- **Security**: CSRF protection, Django authentication system
- **Testing**: pytest framework

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/codeforpakistan/intikhab.git
cd intikhab
```

### 2. Create Virtual Environment

**Windows:**
```cmd
python -m venv env
env\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv env
source env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Seed Database (Optional)

```bash
python manage.py seed
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the application.

## 📁 Project Structure

```
intikhab/
├── app/                          # Main Django application
│   ├── models.py                 # Data models (Election, Candidate, Vote, Party)
│   ├── views.py                  # View logic and business logic
│   ├── admin.py                  # Django admin customization
│   ├── encryption.py             # Homomorphic encryption utilities
│   ├── templates/                # HTML templates
│   │   ├── app/
│   │   │   ├── layouts/          # Base templates
│   │   │   ├── elections/        # Election-specific templates
│   │   │   └── partials/         # Reusable components
│   │   └── registration/         # Authentication templates
│   ├── static/app/               # Static files (CSS, JS, images)
│   └── management/commands/      # Custom Django commands
├── project/                      # Django project settings
│   ├── settings.py               # Application settings
│   ├── urls.py                   # URL configuration
│   └── wsgi.py                   # WSGI configuration
├── env/                          # Virtual environment
├── uploads/                      # Media files (candidate photos, party symbols)
├── requirements.txt              # Python dependencies
└── manage.py                     # Django management script
```

## 🎯 Usage

### For Voters

1. **Register/Login**: Create an account or login to existing account
2. **View Elections**: Browse active elections from the home page
3. **Cast Vote**: Select a candidate and submit your vote securely
4. **View Profile**: Check your voting history in your profile

### For Election Administrators

1. **Admin Access**: Login to `/admin/` with superuser credentials
2. **Create Elections**: Set up new elections with start/end dates
3. **Add Candidates**: Register candidates with their party affiliations
4. **Manage Elections**: Open/close elections and monitor voting progress
5. **View Results**: Access detailed election results after voting closes

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration

For production, update `project/settings.py` to use PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'intikhab_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🔐 Security Features

- **CSRF Protection**: All forms include CSRF tokens
- **Authentication Required**: Voting requires user authentication
- **Permission-Based Access**: Admin functions restricted to superusers
- **Secure Vote Storage**: Votes encrypted and stored securely
- **One Vote Per User**: Database constraints prevent duplicate voting
- **Timezone-Aware Elections**: Proper handling of election timing

## 🧪 Testing

Run the test suite:

```bash
python -m pytest
```

Run Django tests:

```bash
python manage.py test
```

## 📊 API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/` | GET | Home page with active elections | No |
| `/elections` | GET | List all elections | Yes |
| `/elections/<id>` | GET | Election details and voting | Yes |
| `/elections/<id>/vote/<candidate_id>` | POST | Cast vote | Yes |
| `/elections/<id>/close` | POST | Close election | Superuser |
| `/profile` | GET | User voting history | Yes |
| `/admin/` | GET | Admin interface | Superuser |

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG = False` in settings
- [ ] Configure proper database (PostgreSQL recommended)
- [ ] Set up static file serving
- [ ] Configure HTTPS
- [ ] Set up proper logging
- [ ] Configure email backend
- [ ] Set secure session cookies
- [ ] Update `ALLOWED_HOSTS`

### Docker Deployment

```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation for API changes
- Use Bootstrap components for consistent UI
- Ensure CSRF protection on all forms

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Code for Pakistan** - *Initial work* - [@codeforpakistan](https://github.com/codeforpakistan)

## 🙏 Acknowledgments

- Django framework for robust web development
- Bootstrap for responsive UI components
- LightPHE for homomorphic encryption capabilities
- Bootstrap Icons for comprehensive icon set

## 📞 Support

For support and questions:

- Create an issue on GitHub
- Email: info@codeforpakistan.org
- Website: [Code for Pakistan](https://codeforpakistan.org)

## 🗺️ Roadmap

- [ ] **Mobile App**: Flutter mobile application
- [ ] **API Integration**: RESTful API for third-party integrations
- [ ] **Real-time Updates**: WebSocket integration for live results
- [ ] **Multi-language Support**: Internationalization (i18n)
- [ ] **Advanced Analytics**: Detailed voting pattern analysis
- [ ] **Blockchain Integration**: Additional security layer
- [ ] **SMS Notifications**: Vote confirmation via SMS
- [ ] **Audit Trail**: Comprehensive logging system

---

**Made with ❤️ by Code for Pakistan**