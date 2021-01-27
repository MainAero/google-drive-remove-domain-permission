# Removes domain permissions from all GDrive files / folders
This cli script removes every permissions of type `domain` from every file / folder of a user specified by email in your domain.

## Install
This project uses `pipenv` to manage the environment. To install all dependencies run:

```bash
make install
```

## Configuration
This script expects a `service.json` to be in the project root. It should look like:

```json
{
    "type": "service_account",
    "project_id": "foobar",
    "private_key_id": "...",
    "private_key": "...",
    "client_email": "foo@bar.com",
    "client_id": "...",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "..."
  }
  
```

To get this you have to create a [service acount](https://developers.google.com/identity/protocols/oauth2/service-account) and enable the option to delegating authority. Afterwards a google super admin of your domain has to allow the drive scope for the client id of this service account (see [here](https://developers.google.com/identity/protocols/oauth2/service-account#delegatingauthority)).

## Usage
After installation of all dependencies you can run the script in the pipenv by:

```bash
python main.py -e foo@bar.com
```
