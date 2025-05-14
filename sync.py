import os
import time
import sqlite3
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

# === הגדרות והתחברות === #
load_dotenv()
DB_PATH = os.getenv("DB_PATH")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
WORKSHEET_NAME = os.getenv("WORKSHEET_NAME")

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)


# === פונקציות עזר === #

def init_db():
    """יוצר את טבלת contacts במסד הנתונים אם לא קיימת"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS contacts")
    cursor.execute("""
        CREATE TABLE contacts (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            middle_name TEXT,
            last_name TEXT,
            organization TEXT,
            mobile TEXT,
            clean_phone TEXT,
            home TEXT,
            updated_at TEXT
        );
    """)
    conn.commit()
    conn.close()


def fetch_sheet_data():
    """מחזיר נתונים מגוגל שיטס כ-DataFrame עם parsing ל-updated_at"""
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    df["updated_at"] = pd.to_datetime(df["updated_at"], errors='coerce')
    return df


def fetch_sqlite_data():
    """מחזיר נתונים ממסד הנתונים כ-DataFrame עם parsing ל-updated_at"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM contacts", conn)
    df["updated_at"] = pd.to_datetime(df["updated_at"], errors='coerce')
    conn.close()
    return df


def update_google_sheet_timestamp(row_id, sheet_df, all_records):
    """מעדכן את עמודת updated_at עבור שורה לפי ID"""
    updated_at_str = datetime.now().replace(second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M')
    updates = []

    for i, record in enumerate(all_records, start=2):
        if str(record["id"]) == str(row_id):
            col_index = sheet_df.columns.get_loc("updated_at") + 1
            cell_range = gspread.utils.rowcol_to_a1(i, col_index)
            updates.append({'range': cell_range, 'values': [[updated_at_str]]})
            break

    if updates:
        try:
            sheet.batch_update(updates)
            time.sleep(0.7)
            print(f"🕒 updated_at עודכן בגוגל שיטס עבור id: {row_id}")
        except Exception as e:
            print(f"⚠️ שגיאה בעת עדכון Google Sheets עבור id {row_id}: {e}")
    else:
        print(f"⚠️ לא נמצא id מתאים בגוגל שיטס: {row_id}")


# === סנכרון Sheets -> SQLite === #

def sync_to_sqlite(sheet_df, sqlite_df, all_records):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for _, row in sheet_df.iterrows():
        if not str(row["id"]).isdigit():
            continue

        row_id = int(row["id"])
        updated_at = pd.to_datetime(row["updated_at"]) if pd.notna(row["updated_at"]) else datetime.now()
        match = sqlite_df[sqlite_df["id"] == row_id]

        if match.empty:
            cursor.execute("""
                INSERT INTO contacts (id, first_name, middle_name, last_name, organization, mobile, clean_phone, home, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row_id,
                row.get("First Name", ""),
                row.get("Middle Name", ""),
                row.get("Last Name", ""),
                row.get("Organization", ""),
                row.get("Mobile", ""),
                row.get("clean phone", ""),
                row.get("Home", ""),
                updated_at.isoformat()
            ))
            print("🆕 שורה חדשה הוספה עבור id:", row_id)
            update_google_sheet_timestamp(row_id, sheet_df, all_records)

        else:
            db_updated_at = pd.to_datetime(match.iloc[0]["updated_at"])
            if updated_at > db_updated_at:
                cursor.execute("""
                    UPDATE contacts SET 
                        first_name = ?, 
                        middle_name = ?, 
                        last_name = ?, 
                        organization = ?, 
                        mobile = ?, 
                        clean_phone = ?, 
                        home = ?, 
                        updated_at = ?
                    WHERE id = ?
                """, (
                    row.get("First Name", ""),
                    row.get("Middle Name", ""),
                    row.get("Last Name", ""),
                    row.get("Organization", ""),
                    row.get("Mobile", ""),
                    row.get("clean phone", ""),
                    row.get("Home", ""),
                    updated_at.isoformat(),
                    row_id
                ))
                print("🔄 שורה קיימת עודכנה עבור id:", row_id)
                update_google_sheet_timestamp(row_id, sheet_df, all_records)
            else:
                print("⏭ אין צורך בעדכון עבור id:", row_id)
    # מחיקת רשומות שלא קיימות בגיליון
    ids_in_sheet = set(sheet_df['id'].dropna().astype(int))
    ids_in_db = set(sqlite_df['id'].dropna().astype(int))
    ids_to_delete = ids_in_db - ids_in_sheet

    for delete_id in ids_to_delete:
        cursor.execute("DELETE FROM contacts WHERE id = ?", (delete_id,))
        print(f"🗑️ נמחק id שלא קיים עוד בגיליון: {delete_id}")

    conn.commit()
    conn.close()


# === סנכרון SQLite -> Sheets === #

def sync_to_sheet(sheet_df, sqlite_df):
    sheet_dict = sheet_df.set_index("id").to_dict("index")

    for _, row in sqlite_df.iterrows():
        sid = row["id"]
        updated_at = pd.to_datetime(row["updated_at"]) if pd.notna(row["updated_at"]) else None

        if sid not in sheet_dict:
            sheet.append_row([
                row["id"], row["first_name"], row["middle_name"], row["last_name"],
                row["organization"], row["mobile"], row["clean_phone"], row["home"],
                updated_at.isoformat() if updated_at else ""
            ])
        elif updated_at > pd.to_datetime(sheet_dict[sid]["updated_at"]):
            cell_row = sheet_df[sheet_df["id"] == sid].index[0] + 2
            sheet.update(f"B{cell_row}", row["first_name"])
            sheet.update(f"C{cell_row}", row["middle_name"])
            sheet.update(f"D{cell_row}", row["last_name"])
            sheet.update(f"E{cell_row}", row["organization"])
            sheet.update(f"F{cell_row}", row["mobile"])
            sheet.update(f"G{cell_row}", row["clean_phone"])
            sheet.update(f"H{cell_row}", row["home"])
            sheet.update(f"I{cell_row}", updated_at.isoformat() if updated_at else "")


# === Main === #

def main():
    init_db()
    sheet_df = fetch_sheet_data()
    sqlite_df = fetch_sqlite_data()
    all_records = sheet.get_all_records()

    sync_to_sqlite(sheet_df, sqlite_df, all_records)
    updated_sqlite_df = fetch_sqlite_data()
    sync_to_sheet(sheet_df, updated_sqlite_df)

    # הדפסת תוכן הטבלה (לצורכי בדיקה)
    for row in updated_sqlite_df.itertuples(index=False):
        print(row)


if __name__ == "__main__":
    main()
