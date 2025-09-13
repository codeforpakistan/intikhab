# Intikhab - DigitalOcean App Platform Deployment Guide

## 🚀 Quick Deployment Steps

### 1. Prerequisites
- GitHub repository with the Intikhab code
- DigitalOcean account
- SendGrid account for email services
- Google OAuth2 credentials

### 2. Deploy to DigitalOcean App Platform

1. **Connect Repository**
   - Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
   - Click "Create App"
   - Select "GitHub" and authorize DigitalOcean
   - Choose your `intikhab` repository
   - Select the `main` branch

2. **Configuration**
   - DigitalOcean will automatically detect the `.do/app.yaml` file
   - Review the configuration and click "Next"

3. **Set Environment Variables**
   Add these environment variables in the DigitalOcean App Platform dashboard:

## 🔐 Required Environment Variables

### Core Django Settings
```bash
SECRET_KEY=your-secret-key-here  # Generate a new one for production
DEBUG=False
ALLOWED_HOSTS=.ondigitalocean.app,yourdomain.com
```

### Database (Automatically configured by DigitalOcean)
```bash
DATABASE_URL=postgresql://user:pass@host:port/db  # Auto-populated by DO
```

### Email Settings (SendGrid)
```bash
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
SENDGRID_API_KEY=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Google OAuth2
```bash
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret
```

### Security Settings (Production)
```bash
SECURE_HSTS_SECONDS=31536000
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Optional: Admin User Creation
```bash
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
DJANGO_SUPERUSER_PASSWORD=secure-admin-password
```

## 🌍 Domain Configuration

### Custom Domain Setup
1. In your app settings, go to "Settings" > "Domains"
2. Add your custom domain (e.g., `intikhab.codeforpakistan.org`)
3. Update your DNS records:
   ```
   Type: CNAME
   Name: intikhab (or @)
   Value: your-app-name.ondigitalocean.app
   ```

### Update Google OAuth Settings
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" > "Credentials"
3. Edit your OAuth 2.0 Client ID
4. Add authorized redirect URIs:
   ```
   https://your-app-name.ondigitalocean.app/accounts/google/login/callback/
   https://yourdomain.com/accounts/google/login/callback/
   ```

## 📧 SendGrid Configuration

### Setup SendGrid
1. Create a SendGrid account
2. Generate an API key with "Mail Send" permissions
3. Add the API key to your environment variables
4. Verify your domain in SendGrid for better deliverability

### Email Templates
The app includes custom email templates for:
- User registration verification
- Welcome emails
- Password reset
- Vote confirmations

## 🗃️ Database

### Automatic Setup
- PostgreSQL database is automatically created and configured
- Migrations run automatically during deployment
- Initial data is seeded via the `deploy.sh` script

### Manual Operations (if needed)
Connect to your app via console and run:
```bash
# Create superuser
python manage.py createsuperuser

# Seed database
python manage.py seed

# Create Citizens group
python manage.py create_citizens_group
```

## 🔒 Security Features Enabled

### HTTPS & Security Headers
- ✅ Force HTTPS redirect
- ✅ HSTS headers with 1-year max-age
- ✅ Secure cookies
- ✅ XSS protection
- ✅ Content type sniffing protection

### Authentication Security
- ✅ Mandatory email verification
- ✅ Secure session handling
- ✅ CSRF protection
- ✅ OAuth2 integration

## 📊 Monitoring & Logs

### View Logs
```bash
# In DigitalOcean dashboard
Apps > Your App > Runtime Logs
```

### Health Checks
- Health check endpoint: `/`
- Automatic restart on failure
- Email notifications on deployment issues

## 🚨 Troubleshooting

### Common Issues

1. **Static Files Not Loading**
   - Ensure WhiteNoise is in MIDDLEWARE
   - Check STATIC_ROOT configuration
   - Verify collectstatic runs in build process

2. **Email Not Sending**
   - Verify SendGrid API key
   - Check email configuration in settings
   - Test with management command: `python manage.py test_email`

3. **Google OAuth Not Working**
   - Verify client ID and secret
   - Check authorized redirect URIs
   - Ensure domain is properly configured

4. **Database Connection Issues**
   - Verify DATABASE_URL is set
   - Check database is running
   - Review migration logs

### Getting Help
- Check DigitalOcean App Platform logs
- Review Django error logs
- Use `python manage.py check --deploy` for deployment checks

## 🎯 Post-Deployment Checklist

- [ ] App is accessible via URL
- [ ] Google OAuth login works
- [ ] Email verification works
- [ ] Database contains seeded data
- [ ] Static files load correctly
- [ ] Admin panel is accessible
- [ ] SSL certificate is active
- [ ] Custom domain (if applicable) resolves

## 🔄 Updates & Maintenance

### Automatic Deployments
- Push to `main` branch triggers automatic deployment
- Migrations run automatically
- Static files are collected automatically

### Manual Updates
```bash
# Update dependencies
uv add package-name

# Update requirements.txt
uv pip compile pyproject.toml -o requirements.txt

# Commit and push to trigger deployment
git add .
git commit -m "Update dependencies"
git push origin main
```

---

## 📞 Support

For deployment issues or questions:
- Create an issue in the GitHub repository
- Contact: Code for Pakistan team
- Documentation: https://github.com/codeforpakistan/intikhab

**Happy Voting! 🗳️ 🇵🇰**