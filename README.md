# Google Sheets to SQLite Sync

## Overview
This project provides a script that syncs contact data from a Google Sheets document to an SQLite database. It ensures that any new or updated records in the Google Sheets are added to the database, and old records that no longer exist in the sheet are deleted from the database.

### Key Features:
- **Syncs contact information**: Transfers data such as first name, last name, phone numbers, etc., from Google Sheets to an SQLite database.
- **Handles updates**: Updates records in the SQLite database if the data in the Google Sheets is newer.
- **Deletes non-existent records**: Deletes records from the SQLite database that no longer appear in the Google Sheets.

## Installation

To use this project, you need to have the following installed:

- Python 3.x
- Required Python packages:
    - `pandas`
    - `sqlite3`
    - `gspread` (for accessing Google Sheets)
    - `oauth2client` (for Google Sheets API authentication)

You can install the necessary Python packages using the following command:
```bash
pip install pandas sqlite3 gspread oauth2client
Setup
Google Sheets API:

Enable Google Sheets API in the Google Cloud Console.

Create credentials (OAuth2) and download the credentials.json file.

Share the Google Sheet with the email address from the credentials.json.

Configure the SQLite Database:

Define the path to your SQLite database by modifying the DB_PATH variable in the script.

Google Sheets:

Make sure your Google Sheets document contains the columns: id, First Name, Middle Name, Last Name, Organization, Mobile, clean phone, Home, and updated_at.

How It Works
Sync Contacts:

The script fetches data from the Google Sheets, compares it with the records in the SQLite database, and performs the following:

Inserts new contacts into the database.

Updates existing records if the updated_at field in the sheet is newer.

Deletes records from the database that no longer exist in the Google Sheets.

Run the Script:

Call the sync_to_sqlite(sheet_df) function to sync the data from Google Sheets to the SQLite database.

Scheduling:

You can automate the syncing process using a task scheduler (e.g., cron on Linux or Task Scheduler on Windows).

Usage
Clone the repository to your local machine.

Set up the Google Sheets API and SQLite database as described above.

Run the script to sync your contacts.

bash
Always show details

Copy
python sync_contacts.py
Example
Below is an example of how the script processes the data:

If a contact with ID 1 is new, it will be inserted into the database.

If the contact already exists, and the updated_at field in the sheet is newer, the contact will be updated.

If a contact with ID 5 no longer exists in the Google Sheets, it will be deleted from the database.

Contributions
Contributions are welcome! Feel free to fork the repository, make changes, and submit pull requests.

License
This project is licensed under the MIT License - see the LICENSE file for details.
