# Electronic Voting Machine using Homomorphic Encryption

A secure electronic voting system implemented using Django and Paillier Homomorphic Encryption. This system allows for secure vote casting and counting while maintaining voter privacy through advanced cryptographic techniques.

## Features

- Secure voter registration and authentication
- End-to-end encrypted voting process
- Homomorphic vote tallying (count votes without decrypting individual ballots)
- Vote verification system
- Admin dashboard for election management

## Technology Stack

- Python 3.x
- Django 4.2
- Paillier Homomorphic Encryption (lightphe 0.0.8)
- SQLite (default Django database)

## Prerequisites

- Python 3.x installed
- Basic understanding of command line operations
- pip (Python package manager)

## Installation and Setup

1. Clone the repository
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment
### On Windows
```bash
python -m venv venv
venv\Scripts\activate
```
### On Mac/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the required dependencies
```bash
pip install -r requirements.txt
```

4. Run database migrations
```bash
python manage.py migrate
```

5. Run the development server
```bash
python manage.py runserver
```

6. Access the application at http://127.0.0.1:8000/ or http://localhost:8000/

## Project Structure
```
electronic-voting-machine/
├── app/
│ ├── management/
│ ├── migrations/
│ ├── static/
│ ├── templates/
│ ├── admin.py # Admin configuration
│ ├── apps.py # Application configuration
│ ├── encryption.py # Homomorphic encryption implementation
│ ├── models.py # Database models
│ ├── tests.py # Test cases
│ ├── views.py # View controllers
├── project/
│ ├── asgi.py # ASGI configuration
│ ├── settings.py # Project settings
│ ├── urls.py # URL configuration
│ └── wsgi.py # WSGI configuration
├── uploads/
├── manage.py
├── ReadMe.md
└── requirements.txt
```
## How It Works

This electronic voting system uses Paillier Homomorphic Encryption to ensure:

1. **Vote Privacy**: Individual votes are encrypted and cannot be traced back to voters
2. **Vote Integrity**: Votes cannot be altered once cast
3. **Verifiable Counting**: Vote tallying can be verified without compromising privacy

The Paillier cryptosystem allows for mathematical operations on encrypted values, enabling vote counting without decrypting individual votes.

## Security Features

- Homomorphic encryption for vote privacy
- Secure user authentication
- Encrypted data transmission
- Protection against double voting
- Audit trail for verification

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is open-sourced under the MIT License - see the LICENSE file for details.

## Contact

For any questions or feedback, please contact us at [info@codeforpakistan.org](mailto:info@codeforpakistan.org).


## Changelog
```
v0.0.1
- Initial release
- Basic E2EVV implementation
```