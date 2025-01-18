import csv
import json
import argparse
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass(frozen=True)
class PasswordEntry:
    """Represents a password entry from Bitwarden."""

    name: str
    login_uri: str
    login_username: str
    login_password: str
    notes: str = field(default="")

    def format_uri(self) -> str:
        """Formats the URI to match Google's expected format."""
        if not self.login_uri:
            # Special URL for entries that only contain notes
            return "https://mybitwardensecurenotesdonotdelete.com"

        # If both androidapp:// and base domain exist, use only the base domain
        uris = self.login_uri.split(',')
        for uri in uris:
            if uri.startswith(("http://", "https://")):
                parsed_uri = urlparse(uri)
                return f"https://{parsed_uri.netloc}"
            elif '.' in uri and not uri.startswith("androidapp://"):
                return f"https://{uri.strip()}"

        # If no http:// or https:// is found, return the updated URI
        return self.login_uri.replace("androidapp://", "android://@")

    def to_google_format(self, secure_note_counter: Optional[int] = None) -> Dict[str, str]:
        """Converts the entry to Google CSV format."""
        url = self.format_uri()
        password = self.login_password if self.login_password else "secure_note_password"
        username = self.login_username if self.login_username else f"{self.name} - row:{secure_note_counter}"
        return {
            "name": self.name,
            "url": url,
            "username": username,
            "password": password,
            "note": self.notes
        }


class PasswordManager:
    """Manages Bitwarden passwords and converts them to Google CSV format."""

    def __init__(self, entries: List[PasswordEntry]):
        self.entries = entries

    @classmethod
    def from_csv(cls, file_path: Path) -> "PasswordManager":
        """Loads passwords from a Bitwarden CSV file."""
        entries = []
        with file_path.open(mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                entry = PasswordEntry(
                    name=row.get('name', ''),
                    login_uri=row.get('login_uri', ''),
                    login_username=row.get('login_username', ''),
                    login_password=row.get('login_password', ''),
                    notes=row.get('notes', '')
                )
                entries.append(entry)
        return cls(entries)

    @classmethod
    def from_json(cls, file_path: Path) -> "PasswordManager":
        """Loads passwords from a Bitwarden JSON file."""
        with file_path.open(mode='r', encoding='utf-8') as file:
            data = json.load(file)
            entries = []
            items = data['items']

            for item in items:
                if item.get('type') == 1:  # Login type
                    login = item.get('login', {})
                    uris = login.get('uris', [])
                    uri = uris[0]['uri'] if uris else ""
                    entry = PasswordEntry(
                        name=item.get('name', ''),
                        login_uri=uri,
                        login_username=login.get('username', ''),
                        login_password=login.get('password', ''),
                        notes=item.get('notes', '')
                    )
                elif item.get('type') == 4:  # Identity type
                    identity = item.get('identity', {})
                    notes = (
                        f"Name: {identity.get('firstName', '')} {identity.get('lastName', '')}\n"
                        f"Phone: {identity.get('phone', '')}\n"
                        f"Email: {identity.get('email', '')}\n"
                        f"Address: {identity.get('address1', '')}\n"
                        f"Company: {identity.get('company', '')}\n"
                        f"Notes: {item.get('notes', '')}"
                    )
                    entry = PasswordEntry(
                        name=item.get('name', ''),
                        login_uri="",
                        login_username="",
                        login_password="",
                        notes=notes
                    )
                else:
                    # Default behavior for other types
                    entry = PasswordEntry(
                        name=item.get('name', ''),
                        login_uri="",
                        login_username="",
                        login_password="",
                        notes=item.get('notes', '')
                    )
                entries.append(entry)
        return cls(entries)

    def to_google_csv(self, file_path: Path) -> None:
        """Exports passwords to a Google CSV file."""
        fieldnames = ["name", "url", "username", "password", "note"]
        secure_note_counter = 1
        with file_path.open(mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for entry in self.entries:
                if not entry.login_uri and not entry.login_username:
                    # Create a unique username for secure notes
                    writer.writerow(entry.to_google_format(secure_note_counter))
                    secure_note_counter += 1
                else:
                    writer.writerow(entry.to_google_format())


def main():
    """Command-line interface for the script."""
    parser = argparse.ArgumentParser(
        description="Convert Bitwarden passwords to Google CSV format.",
        epilog="""
        Examples:
          # Convert a CSV file (default output: google_passwords.csv)
          python bitwarden_to_google.py -i bitwarden_export.csv

          # Convert a JSON file with custom output name
          python bitwarden_to_google.py -i bitwarden_export.json -o custom_output.csv
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('-i', '--input', type=str, required=True, help='Path to the Bitwarden export file (CSV or JSON)')
    parser.add_argument('-o', '--output', type=str, default='google_passwords.csv',
                        help='Path to save the Google CSV file (default: google_passwords.csv)')

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    file_extension = input_path.suffix.lower()
    if file_extension == '.csv':
        manager = PasswordManager.from_csv(input_path)
    elif file_extension == '.json':
        manager = PasswordManager.from_json(input_path)
    else:
        raise ValueError("Unsupported file format. Please provide a CSV or JSON file.")

    manager.to_google_csv(output_path)
    print(f"Google CSV file saved as {output_path}.")


if __name__ == "__main__":
    main()
