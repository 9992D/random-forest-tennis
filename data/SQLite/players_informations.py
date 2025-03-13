import sqlite3
import pandas as pd
from datetime import datetime

def create_players_table(csv_file, db_file):
    """
    Create an SQLite database table named 'players_informations' from a CSV file.

    Parameters:
    csv_file (str): Path to the input CSV file containing tennis players data.
    db_file (str): Path to the output SQLite database file.

    The CSV file must have columns: player_id, name_first, name_last, hand, dob, ioc, height.

    Constraints:
    - player_id: INTEGER, primary key, unique.
    - name_first: TEXT, not null.
    - name_last: TEXT, not null.
    - hand: TEXT, 1 character ('L', 'R', 'U'), not null.
    - dob: DATE, converted from YYYYMMDD format.
    - ioc: TEXT, 3 characters, not null.
    - height: INTEGER, nullable.

    Returns:
    None
    """
    df = pd.read_csv(csv_file, header=0, low_memory=False)

    df = df.dropna(subset=['player_id', 'name_first', 'name_last'])
    
    def convert_dob(date_str):
        try:
            date_int = int(float(date_str))
            date_clean = str(date_int)
            return datetime.strptime(date_clean, '%Y%m%d').date()
        except Exception as e:
            return None

    df['dob'] = df['dob'].apply(convert_dob)
    df['height'] = pd.to_numeric(df['height'], errors='coerce').astype('Int64')
    
    valid_hands = ['L', 'R', 'U']
    df['hand'] = df['hand'].where(df['hand'].isin(valid_hands), 'U')
    df['hand'] = df['hand'].fillna('U')
    
    df = df[['player_id', 'name_first', 'name_last', 'hand', 'dob', 'ioc', 'height']]

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players_informations (
        player_id INTEGER PRIMARY KEY,
        name_first TEXT NOT NULL,
        name_last TEXT NOT NULL,
        hand TEXT CHECK(hand IN ('L', 'R', 'U')) NOT NULL,
        dob DATE,
        ioc TEXT(3),
        height INTEGER
    )
    ''')

    df.to_sql('players_informations', conn, if_exists='append', index=False)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_players_table('data/CSV/atp_players.csv', 'data/SQLite/tennis.db')