# DNS Checker CLI

A powerful command-line tool for DNS lookups, SSL certificate inspection, and HTTP pinging.

## Features

- 🔍 **DNS Record Lookup**: Query A, AAAA, CNAME, MX, TXT records
- 🔒 **SSL Certificate Inspection**: Detailed certificate information and expiration warnings
- 📡 **HTTP Ping**: Real-time HTTP/HTTPS request monitoring with server IP change detection
- 🎨 **Rich Output**: Visually rich terminal output
- ⚙️ **Custom Nameserver**: Specify custom DNS servers for queries

## Installation

### Requirements

- Python 3.7 or higher

### Installation Steps

```bash
# Clone the repository
git clone <repository-url>
cd dns-checker-cli

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Usage

### DNS Record Lookup

Query DNS records for a domain.

```bash
# Basic usage
dns-checker dns example.com

# Use custom nameserver
dns-checker dns example.com --nameserver 8.8.8.8
dns-checker dns example.com -n 1.1.1.1
```

### SSL Certificate Inspection

Query both DNS information and SSL certificate for a domain.

```bash
# Basic usage
dns-checker inspect example.com

# Use custom nameserver
dns-checker inspect example.com --nameserver 8.8.8.8
```

**Output Information:**
- DNS records (A, AAAA, CNAME, MX, TXT)
- SSL certificate issuer and subject
- Certificate validity period
- SAN (Subject Alternative Names)
- Signature algorithm
- Expiration warning (within 30 days)

### HTTP Ping

Periodically send HTTP/HTTPS requests to monitor server status.

```bash
# Basic usage (1 second interval, infinite loop)
dns-checker httping https://example.com

# Specify interval (2 seconds)
dns-checker httping https://example.com --interval 2
dns-checker httping https://example.com -i 2

# Specify count (10 times)
dns-checker httping https://example.com --count 10
dns-checker httping https://example.com -c 10

# Use custom nameserver
dns-checker httping https://example.com --nameserver 8.8.8.8

# Force connection to specific IP (keep domain but change IP)
dns-checker httping https://naver.com --server 223.130.200.219
dns-checker httping https://example.com -s 93.184.216.34

# Combined usage
dns-checker httping https://example.com -i 2 -c 20 -n 8.8.8.8 -s 93.184.216.34
```

**Output Information:**
- Response time (milliseconds)
- HTTP status code
- Server IP address
- Content-Length (response size)
- Content-Type (response type)
- IP change detection (migration monitoring)
- Forced IP connection indicator
- Statistics (average/min/max response time, success rate)

**Stop:** Press `Ctrl+C` to stop and display statistics.

## Usage Examples

### Domain Migration Monitoring

```bash
# Monitor domain during migration to new server
dns-checker httping https://mysite.com -i 5

# Server IP changes will be highlighted
```

### Test with Specific IP

```bash
# Request to specific IP while keeping domain as naver.com
# Host header remains naver.com, works with virtual host environments
dns-checker httping https://naver.com --server 223.130.200.219 -c 5

# Test new server before migration
dns-checker httping https://mysite.com --server 192.168.1.100 -c 10
```

### DNS Propagation Check

```bash
# Check DNS records with multiple nameservers
dns-checker dns example.com -n 8.8.8.8
dns-checker dns example.com -n 1.1.1.1
dns-checker dns example.com -n 208.67.222.222
```

### SSL Certificate Expiration Check

```bash
# Check certificate expiration date
dns-checker inspect example.com

# Warning displayed if expiring within 30 days
```

## Options

### Common Options

- `--help`: Show help message
- `--version`: Show version information

### DNS Command Options

- `--nameserver, -n`: Custom nameserver IP address

### Inspect Command Options

- `--nameserver, -n`: Custom nameserver IP address

### HTTPing Command Options

- `--interval, -i`: Request interval in seconds (default: 1)
- `--count, -c`: Number of requests (infinite if not specified)
- `--nameserver, -n`: Custom nameserver IP address
- `--server, -s`: Force connection to specific server IP (keep domain but use specific IP)

## Development

### Development Environment Setup

```bash
# Install development dependencies
make dev

# Or manually
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock flake8 black
pip install -e .
```

### Running Tests

```bash
# Using Makefile (recommended)
make test           # Run all tests
make test-cov       # Run tests with coverage

# Or run directly
pytest
pytest tests/test_dns_service.py
pytest --cov=dns_checker
```

### Code Quality

```bash
make lint           # Run code linting
make format         # Format code
make verify         # Full verification (lint + tests)
```

### Build and Deploy

```bash
make build          # Build package
make upload-test    # Upload to TestPyPI
make upload         # Upload to PyPI
make release        # Full release (test → build → upload)
```

For more details, see [PYPI_UPLOAD_GUIDE.md](PYPI_UPLOAD_GUIDE.md).

### Code Style

This project follows the PEP 8 style guide.

## Dependencies

- `click>=8.0.0`: CLI framework
- `dnspython>=2.0.0`: DNS queries
- `cryptography>=3.4.0`: SSL certificate parsing
- `requests>=2.25.0`: HTTP requests
- `rich>=10.0.0`: Terminal output formatting

## License

MIT License

## Contributing

Issues and pull requests are welcome!
