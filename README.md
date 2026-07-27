# certbot-dns-lws

[![PyPI version](https://img.shields.io/pypi/v/certbot-dns-lws.svg)](https://pypi.org/project/certbot-dns-lws/)
[![Python Versions](https://img.shields.io/pypi/pyversions/certbot-dns-lws.svg)](https://pypi.org/project/certbot-dns-lws/)
[![License](https://img.shields.io/github/license/zergflag/certbot-dns-lws.svg)](https://github.com/zergflag/certbot-dns-lws/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/certbot-dns-lws.svg)](https://pypi.org/project/certbot-dns-lws/)

A Certbot DNS plugin for **LWS (Ligne Web Services)**.

This plugin allows Certbot to complete **DNS-01** ACME challenges using the official LWS DNS API, enabling automatic issuance and renewal of Let's Encrypt certificates, including wildcard certificates.

## Features

* ✅ Automatic DNS-01 challenge
* ✅ Automatic certificate renewal
* ✅ Wildcard certificate support (`*.example.com`)
* ✅ Uses the official LWS DNS API
* ✅ Compatible with Certbot 2.x+
* ✅ Compatible with Nginx Proxy Manager (custom image or future native integration)

## Requirements

* Python 3.10+
* Certbot 2.x or newer
* An LWS account
* An API key generated from the LWS customer area
* The public IP address of the server must be authorized in the LWS API settings

## Installation

### From source

```bash
git clone https://github.com/zergflag/certbot-dns-lws.git
cd certbot-dns-lws

python3 -m venv .venv
source .venv/bin/activate

pip install .
```

## Credentials

Create a credentials file:

```ini
dns_lws_login = 123456
dns_lws_api_key = YOUR_API_KEY
```

Protect it:

```bash
chmod 600 lws.ini
```

## Usage

### Single domain

```bash
certbot certonly \
    --authenticator dns-lws \
    --dns-lws-credentials lws.ini \
    -d example.com
```

### Wildcard certificate

```bash
certbot certonly \
    --authenticator dns-lws \
    --dns-lws-credentials lws.ini \
    -d example.com \
    -d '*.example.com'
```

### Custom propagation time

```bash
certbot certonly \
    --authenticator dns-lws \
    --dns-lws-credentials lws.ini \
    --dns-lws-propagation-seconds 60 \
    -d example.com
```

## Configuration options

| Option                          | Description                    |
| ------------------------------- | ------------------------------ |
| `--dns-lws-credentials`         | Credentials file               |
| `--dns-lws-propagation-seconds` | Time to wait before validation |

Credentials file format:

```ini
dns_lws_login = 123456
dns_lws_api_key = YOUR_API_KEY
```

## Renewal

Dry run:

```bash
certbot renew --dry-run
```

Automatic renewal is fully supported.

## Nginx Proxy Manager

The plugin has been successfully tested with:

* Nginx Proxy Manager 2.15.x
* DNS Challenge
* Wildcard certificates
* Automatic renewals

Support for native integration into NPM is planned.

## Tested

The plugin has been successfully tested with:

* Standard certificates
* Wildcard certificates
* DNS-01 validation
* Automatic TXT record cleanup
* Certbot renew (`--dry-run`)
* Nginx Proxy Manager

## Development

Clone the repository:

```bash
git clone https://github.com/zergflag/certbot-dns-lws.git
```

Install in editable mode:

```bash
pip install -e .
```

Verify that the plugin is detected:

```bash
certbot plugins
```

## Contributing

Pull requests, bug reports and feature requests are welcome.

## License

MIT License.
