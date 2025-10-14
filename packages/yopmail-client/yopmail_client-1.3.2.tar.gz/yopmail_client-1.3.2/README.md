# 📧 YOPmail Client

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](README.md)
[![Version](https://img.shields.io/badge/Version-1.3.1-orange.svg)](setup.py)
[![Release](https://img.shields.io/badge/Release-v1.3.1-brightgreen.svg)](https://github.com/DeGanLabs/yopmail_auto/releases)

> **⚠️ IMPORTANT DISCLAIMER**: This project is for **educational purposes only**. Please use responsibly and in accordance with YOPmail's terms of service. The authors are not responsible for any misuse of this software.

---

## 🎯 Overview

A clean, modular Python client for interacting with YOPmail disposable email service. Built with modern Python practices, comprehensive error handling, and a simple API for easy integration.

### ✨ Key Features

- 🔐 **License Protection** - Secure license validation using KeyAuth cloud service
- 🛡️ **Secure Authentication** - Robust cookie management and session handling
- 📬 **Message Management** - List, fetch, and process emails efficiently  
- 📤 **Send Messages** - Send emails to other YOPmail addresses
- 📡 **RSS Feeds** - Get RSS feed URLs and data for any YOPmail address
- 🛡️ **Rate Limiting** - Built-in protection against service limits
- 🌐 **Proxy Support** - Advanced proxy rotation capabilities
- 📊 **Comprehensive Logging** - Detailed operation tracking
- 🎛️ **CLI Interface** - Easy command-line access
- 📚 **Type Safety** - Full type annotations throughout
- ⚙️ **Simple Configuration** - Easy setup with `yopmail_config.py`

---

## 🚀 Quick Start

### Prerequisites

**⚠️ License Required**: This client now requires a valid license key to function. You must:

1. **Purchase a License**: Contact the developer to obtain a license key
2. **Create Configuration**: Set up `yopmail_config.py` with your license key
3. **Install Dependencies**: Install all required packages including KeyAuth

### License Setup

Create a `yopmail_config.py` file in your project directory:

```python
# yopmail_config.py
API_KEY = "YOUR_LICENSE_KEY_HERE"  # Required: Get from developer
PROXY_URL = None  # Optional: "http://proxy:8080"
PROXY_LIST = None  # Optional: ["http://proxy1:8080", "http://proxy2:8080"]
PROXY_ROTATION = False  # Optional: Enable proxy rotation
```

**⚠️ Important**: Without a valid license key, the client will raise a `LicenseError` and refuse to operate.

### Development Mode

For development and testing, you can skip license validation:

```python
from yopmail_client import YOPMailClient

# Skip license check for development
client = YOPMailClient("test@yopmail.com", skip_license_check=True)
```

### Installation

```bash
# Clone the repository
git clone https://github.com/DeGanLabs/yopmail_auto.git
cd yopmail_auto

# Install dependencies (includes KeyAuth for license verification)
pip install -r requirements.txt

# Install the package
pip install -e .
```

### License Setup

1. **Create Configuration File**:
   ```python
   # yopmail_config.py
   API_KEY = "YOUR_LICENSE_KEY_HERE"  # Get this from the developer
   PROXY_URL = None  # Optional: "http://proxy:8080"
   ```

2. **Get Your License Key**: Contact the developer to purchase a license

3. **Test Your Setup**:
   ```bash
   python test_license_integration.py
   ```

### Development Setup

For developers working on the project:

```bash
# Set up development environment
python setup_dev_env.py

# Configure environment variables
# Edit .env file with your KeyAuth credentials

# Test the setup
python keyauth_example.py
```

### CI/CD Deployment

The project includes automated CI/CD with GitHub Actions:

- **CI workflow** (`.github/workflows/ci.yml`): Tests on every push/PR
- **PyPI Release workflow** (`.github/workflows/pypi-release.yml`): Publishes to PyPI on release
- **Multi-Python version testing** (3.8-3.12)
- **Cross-platform compatibility** (Windows, Linux, macOS)
- **License integration tests** with KeyAuth credentials
- **Security scanning** with Bandit and Safety
- **Automatic PyPI publishing** on release
- **CI environment support** - Gracefully handles missing config files in CI

**Note**: CI environments automatically skip license validation when KeyAuth is not available, ensuring tests pass across all platforms.

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete setup instructions.

### Basic Usage

```python
from yopmail_client import YOPMailClient, LicenseError

try:
    # The client will automatically validate your license key
    client = YOPMailClient("your_mailbox")
    client.open_inbox()
    messages = client.list_messages()
    
    for message in messages:
        print(f"Subject: {message.subject}")
        
except LicenseError as e:
    print(f"License validation failed: {e}")
    # Handle license error appropriately

# Create client and send a message
with YOPMailClient("yourmailbox") as client:
    client.open_inbox()
    
    # Send a message to another YOPmail address
    result = client.send_message(
        "recipient@yopmail.com",
        "Test Subject",
        "This is a test message"
    )
    print(f"Message sent: {result['success']}")
    
    # List messages
    messages = client.list_messages()
    for msg in messages:
        print(f"Subject: {msg.subject}")
```

---

## 📖 Essential API

### Core Functions

| Function | Description | Parameters |
|----------|-------------|------------|
| `client.open_inbox()` | Initialize inbox access | None |
| `client.list_messages(page)` | List messages in inbox | `page: int = 1` |
| `client.fetch_message(msg_id)` | Fetch specific message content | `msg_id: str` |
| `client.send_message(to, subject, body)` | Send email to YOPmail address | `to: str, subject: str, body: str` |
| `client.get_inbox_info()` | Get inbox overview | None |

### Advanced Usage

```python
from yopmail_client import YOPMailClient

# Full client control with send functionality
with YOPMailClient("mailbox") as client:
    client.open_inbox()
    
    # Send a message
    result = client.send_message(
        "recipient@yopmail.com",
        "Important Update",
        "This is an important message with details..."
    )
    
    # Get RSS feed URL
    rss_url = client.get_rss_feed_url("mailbox")
    print(f"RSS URL: {rss_url}")
    
    # Get RSS feed data
    rss_data = client.get_rss_feed_data("mailbox")
    print(f"RSS has {rss_data['message_count']} messages")
    
    # List and process messages
    messages = client.list_messages()
    for msg in messages:
        content = client.fetch_message(msg.id)
        print(f"Subject: {msg.subject}")
        print(f"From: {msg.sender}")
        print(f"Content: {content[:100]}...")
```

---

## 🖥️ Command Line Interface

```bash
# List all messages
yopmail-client yourmailbox --list

# Show detailed message information
yopmail-client yourmailbox --list --details

# Fetch specific message content
yopmail-client yourmailbox --fetch MESSAGE_ID

# Send an email message
yopmail-client yourmailbox --send --to "recipient@yopmail.com" --subject "Test Subject" --body "Test message body"

# Get RSS feed URL
yopmail-client yourmailbox --rss

# Get RSS feed data
yopmail-client yourmailbox --rss-data
```

---

## 🏗️ Architecture

### Project Structure

```
yopmail-client/
├── 📁 modules/
│   └── 📁 yopmail_client/
│       ├── 📄 client.py          # Core client implementation
│       ├── 📄 simple_api.py      # Essential API functions
│       ├── 📄 constants.py       # Configuration constants
│       ├── 📄 cookies.py         # Cookie management
│       ├── 📄 exceptions.py      # Custom exceptions
│       ├── 📄 utils.py           # Utility functions
│       ├── 📄 cli.py             # Command-line interface
│       └── 📄 proxy_manager.py   # Proxy rotation
├── 📁 artifacts/
│   └── 📄 api_summary.json       # API documentation
├── 📄 requirements.txt           # Dependencies
├── 📄 setup.py                   # Package configuration
└── 📄 README.md                  # This file
```

### Design Principles

- **🔧 Modularity** - Clean separation of concerns
- **🛡️ Security** - Safe handling of credentials and sessions
- **📈 Scalability** - Built for high-volume operations
- **🔍 Observability** - Comprehensive logging and monitoring
- **🎯 Simplicity** - Easy-to-use API design

---

## ⚙️ Configuration

### License Configuration

**Required**: Create `yopmail_config.py` in your project directory:

```python
# yopmail_config.py
API_KEY = "YOUR_LICENSE_KEY_HERE"  # Required: Get from developer
PROXY_URL = None  # Optional: "http://proxy:8080"
PROXY_LIST = None  # Optional: ["http://proxy1:8080", "http://proxy2:8080"]
PROXY_ROTATION = False  # Optional: Enable proxy rotation
```

### Rate Limiting

```python
config = {
    "rate_limit_detection": True,
    "rate_limit_delay": 2.0,  # seconds
    "max_retries": 3
}

messages = check_inbox("mailbox", config=config)
```

### Proxy Support

```python
# Via yopmail_config.py (recommended)
PROXY_URL = "http://proxy:8080"
PROXY_LIST = ["http://proxy1:8080", "http://proxy2:8080"]
PROXY_ROTATION = True

# Or via config parameter
config = {
    "proxy_enabled": True,
    "proxy_list": [
        "http://proxy1:8080",
        "http://proxy2:8080"
    ],
    "proxy_rotation": True
}
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest --cov=modules.yopmail_client tests/

# Run specific test file
pytest tests/test_client_basic.py
```

---

## 📊 Performance

- **⚡ Fast Response** - Optimized HTTP requests
- **🔄 Connection Pooling** - Efficient resource usage
- **📈 Rate Limiting** - Automatic backoff strategies
- **🌐 Proxy Rotation** - Load distribution across proxies

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/DeGanLabs/yopmail_auto.git
cd yopmail_auto

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Legal Notice

**This software is provided for educational and research purposes only.**

- 🚫 **No Spam** - Do not use for sending unsolicited emails
- 🚫 **No Abuse** - Respect YOPmail's terms of service
- 🚫 **No Commercial Use** - Not intended for commercial applications
- ✅ **Educational Use** - Perfect for learning email automation
- ✅ **Research** - Ideal for academic and research projects

**The authors are not responsible for any misuse of this software.**

---

## 📞 Support

- 📧 **Issues**: [GitHub Issues](https://github.com/DeGanLabs/yopmail_auto/issues)
- 📚 **Documentation**: [Wiki](https://github.com/DeGanLabs/yopmail_auto/wiki)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/DeGanLabs/yopmail_auto/discussions)

---

<div align="center">

**Made with ❤️ for the Python community**

[![GitHub stars](https://img.shields.io/github/stars/firasguendouz/yopmail_auto?style=social)](https://github.com/DeGanLabs/yopmail_auto)
[![GitHub forks](https://img.shields.io/github/forks/firasguendouz/yopmail_auto?style=social)](https://github.com/DeGanLabs/yopmail_auto)

</div>