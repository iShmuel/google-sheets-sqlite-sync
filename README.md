
# Google Sheets to SQLite Sync

This project facilitates the synchronization of data between a Google Sheet and an SQLite database. The sync process automatically updates records in the SQLite database based on changes made in the Google Sheet. This solution is designed for situations where you need to ensure your SQLite database is always up-to-date with the latest data stored in Google Sheets.

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Notes](#notes)
- [License](#license)

---

## Overview

Google Sheets to SQLite Sync is a Python-based solution that integrates Google Sheets with an SQLite database. It enables you to synchronize data from a specified Google Sheet and store it within an SQLite database, allowing for seamless data management and interaction between the two platforms.

This project automatically:
- Fetches data from a Google Sheet.
- Inserts or updates data in the SQLite database.
- Tracks changes and maintains the integrity of the data.

---

## Prerequisites

Before running the project, make sure you have the following installed on your system:

1. **Python 3.x**: Ensure Python is installed on your machine. [Download Python](https://www.python.org/downloads/)
2. **Google Cloud Account**: You will need to create a project in Google Cloud and enable the Google Sheets API to generate credentials.
3. **SQLite**: The database engine used for storing data locally. [SQLite download link](https://www.sqlite.org/download.html)
4. **Required Python Packages**: Install the required libraries using `pip`:
    ```bash
    pip install gspread oauth2client sqlite3
    ```

---

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/USERNAME/google-sheets-sqlite-sync.git
   ```

2. Navigate to the project directory:
   ```bash
   cd google-sheets-sqlite-sync
   ```

3. Install the necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Setup Instructions

1. **Create Google Sheets API Credentials**:
   - Go to the [Google Cloud Console](https://console.developers.google.com/).
   - Create a new project or use an existing one.
   - Enable the **Google Sheets API** and the **Google Drive API**.
   - Create credentials for the OAuth 2.0 Client ID and download the `credentials.json` file.

2. **Create and Set Up the SQLite Database**:
   - If you don’t already have an SQLite database, create one using the following SQL command:
     ```sql
     sqlite3 database_name.db
     ```
   - Define the structure of your database tables to match the data in the Google Sheet.

3. **Set Up the Credentials File**:
   - Place the `credentials.json` file in the root directory of this project.

4. **Set Up Google Sheets API Access**:
   - Share the Google Sheet with the email associated with your Google API credentials (this email can be found in the `credentials.json` file).

---

## Usage

1. **Run the synchronization script**:
   - To start the synchronization, run the Python script:
     ```bash
     python sync.py
     ```

2. **Behavior of the Script**:
   - The script will:
     - Fetch data from the specified Google Sheet.
     - Check for any differences in the data compared to the SQLite database.
     - Insert or update records as necessary in the SQLite database.
   
3. **Schedule the Sync (Optional)**:
   - To run the sync process on a regular basis, you can schedule the script using a task scheduler such as `cron` on Unix-based systems or Task Scheduler on Windows.

---

## How It Works

- **Google Sheets API**: The script interacts with the Google Sheets API to fetch the data. It retrieves data from the provided sheet and stores it in a dictionary.
- **SQLite Database**: The data is compared with the existing entries in the SQLite database. If there is a discrepancy, the script inserts or updates the relevant rows in the database.
- **Error Handling**: The script includes error handling to ensure that if the database connection fails or the API is unreachable, the process is aborted gracefully.

---

## Configuration

You can configure the following parameters:

1. **Google Sheet ID**:
   - Find your sheet ID in the URL of the Google Sheet:
     ```
     https://docs.google.com/spreadsheets/d/your_sheet_id/edit
     ```
   - Set this ID in the script configuration.
   
2. **SQLite Database Path**:
   - Set the path to your SQLite database in the configuration file.

3. **Google Sheets Range**:
   - Specify the range of data to be fetched from the Google Sheet. This range can be adjusted depending on the data you need.

---

## Notes

- Ensure that the format of the data in the Google Sheet matches the format expected by the SQLite database for smooth syncing.
- The project uses OAuth 2.0 to authenticate the Google Sheets API requests. You will need to authenticate once and grant permission to the script to access your Google Sheets.
- You may encounter rate limits from Google Sheets API depending on the frequency of requests.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
