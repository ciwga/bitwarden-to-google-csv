# Bitwarden-to-Google-CSV
Easily migrate your Bitwarden passwords to Google Passwords! This tool converts Bitwarden exports (CSV/JSON) into Google's CSV format.
## Prerequisites
- Python 3.7 or higher.
## Installation
```bash
git clone https://github.com/ciwga/bitwarden-to-google-csv.git
cd bitwarden-to-google-csv
```
## Usage (CLI)
The script supports the following arguments:
- `-i` or `--input`: Path to the Bitwarden export file (CSV or JSON). `Required`.
- `-o` or `--output`: Path to save the Google CSV file. Defaults to google_passwords.csv
- ### Examples:
  1. Convert a Bitwarden CSV file:
     ```bash
     python bitwarden_to_google.py -i bitwarden_export.csv
     ```
  2. Convert a Bitwarden JSON file (unencrypted) with a custom output name:
     ```bash
     python bitwarden_to_google.py -i bitwarden_export.json -o custom_output.csv
     ```
## Supported Data Types from Bitwarden
- **Logins:** Converts login URIs, usernames, and passwords.
- **Secure Notes:** Converts notes into Google's format with unique usernames.
- **Identity Data:** Converts identity information (name, email, phone, email, etc.) into notes.
