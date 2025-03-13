# Tennis Database (tennis.db)

This README provides an overview of the SQLite database `tennis.db`. At present, the database contains a single table, `players_informations`, which stores information about tennis players.

## Table `players_informations`

The `players_informations` table is designed to record the following details for each player:

| **Column Name** | **Data Type** | **Constraints**                                             | **Description**                                                          |
|-----------------|---------------|-------------------------------------------------------------|--------------------------------------------------------------------------|
| `player_id`     | INTEGER       | PRIMARY KEY, UNIQUE                                         | A unique identifier for each player.                                     |
| `name_first`    | TEXT          | NOT NULL                                                    | The player's first name.                                                 |
| `name_last`     | TEXT          | NOT NULL                                                    | The player's last name.                                                  |
| `hand`          | TEXT          | NOT NULL, CHECK(hand IN ('L', 'R', 'U'))                      | The dominant hand of the player: 'L' for left, 'R' for right, 'U' for unknown. |
| `dob`           | DATE          | -                                                           | The player's date of birth, stored in the format `YYYY-MM-DD` (converted from `YYYYMMDD`). |
| `ioc`           | TEXT(3)       | NOT NULL                                                    | The IOC (International Olympic Committee) country code representing the player's country. |
| `height`        | INTEGER       | Nullable                                                    | The player's height in centimeters.                                      |

### Additional Details

- **Date Conversion:**  
  The `dob` column is generated from a date string in the `YYYYMMDD` format found in the CSV file. A dedicated conversion function cleans and transforms this string into a date object.

- **Data Cleaning:**  
  The `hand` column is filtered to accept only the values 'L', 'R', or 'U'. If an invalid or missing value is encountered, the default value 'U' (unknown) is used.

- **Integrity Constraints:**  
  The `CHECK` constraint on the `hand` column ensures that only one of the specified values can be inserted.

## Usage

The `players_informations` table is created from a CSV file containing the following columns:  
`player_id, name_first, name_last, hand, dob, ioc, height`.

A Python script included in the project reads the CSV file, cleans and converts the data (including proper date conversion), and then inserts the cleaned data into the SQLite database `tennis.db`.

---

**Written by GenAI**