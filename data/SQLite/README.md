# Tennis Database (tennis.db)

This README provides an overview of the SQLite database `tennis.db`. Currently, the database contains three tables:

- **`players_informations`**: Stores information about tennis players.
- **`atp_matches`**: Contains detailed match statistics extracted from ATP match CSV files.
- **`player_stats`**: Aggregates player statistics calculated from match data, including recent win rates, performance metrics, and Elo ratings.

---

## Table `players_informations`

The `players_informations` table records the following details for each player:

| **Column Name** | **Data Type** | **Constraints**                           | **Description**                                                           |
|-----------------|---------------|-------------------------------------------|---------------------------------------------------------------------------|
| `player_id`     | INTEGER       | PRIMARY KEY, UNIQUE                       | A unique identifier for each player.                                      |
| `name_first`    | TEXT          | NOT NULL                                  | The player's first name.                                                  |
| `name_last`     | TEXT          | NOT NULL                                  | The player's last name.                                                   |
| `hand`          | TEXT          | NOT NULL, CHECK(hand IN ('L', 'R', 'U'))    | The dominant hand of the player: 'L' for left, 'R' for right, 'U' for unknown. |
| `dob`           | DATE          | -                                         | The player's date of birth, stored in `YYYY-MM-DD` (converted from `YYYYMMDD`). |
| `ioc`           | TEXT(3)       | NOT NULL                                  | The IOC (International Olympic Committee) country code representing the player's country. |
| `height`        | INTEGER       | Nullable                                  | The player's height in centimeters.                                       |

### Additional Details for `players_informations`

- **Date Conversion:**  
  The `dob` column is generated from a date string in the `YYYYMMDD` format found in the CSV file and is converted into a proper date format.

- **Data Cleaning:**  
  The `hand` column accepts only 'L', 'R', or 'U'. If an invalid or missing value is encountered, the default value 'U' (unknown) is used.

- **Integrity Constraints:**  
  A `CHECK` constraint on the `hand` column ensures that only the specified values can be inserted.

---

## Table `atp_matches`

The `atp_matches` table stores detailed match statistics extracted and enriched from ATP match CSV files (named `atp_matches_YYYY.csv` for years 1991 to 2024). The table is created by aggregating data from multiple sources and applying extensive feature engineering.

| **Column Name**            | **Data Type** | **Description**                                                                         |
|----------------------------|---------------|-----------------------------------------------------------------------------------------|
| `WINNER_ID`                | INTEGER       | Unique identifier of the match winner.                                                 |
| `LOSER_ID`                 | INTEGER       | Unique identifier of the match loser.                                                  |
| `ATP_POINT_DIFF`           | INTEGER       | Difference in ATP ranking points between the winner and the loser.                       |
| `ATP_RANK_DIFF`            | INTEGER       | Difference in ATP ranking positions between the winner and the loser.                    |
| `AGE_DIFF`                 | REAL          | Difference in age (in years) between the winner and the loser.                           |
| `HEIGHT_DIFF`              | INTEGER       | Difference in height (in centimeters) between the winner and the loser.                  |
| `BEST_OF`                  | INTEGER       | Indicates the match format (best-of series).                                             |
| `DRAW_SIZE`                | INTEGER       | The size of the tournament draw.                                                        |
| `H2H_DIFF`                 | INTEGER       | Cumulative head-to-head difference (overall) prior to each match.                        |
| `H2H_SURFACE_DIFF`         | INTEGER       | Head-to-head difference on the specific surface before each match.                       |
| `DIFF_N_GAMES`             | INTEGER       | Difference in the number of matches played by the winner vs. the loser before each match.  |
| `WIN_LAST_X_DIFF`          | REAL          | Difference in win rate over the last X matches (calculated for various window sizes: 3, 5, 10, 25, 50, 100). |
| `P_ACE_LAST_X_DIFF`        | REAL          | Difference in percentage of aces over the last X matches (for various window sizes).       |
| `P_DF_LAST_X_DIFF`         | REAL          | Difference in percentage of double faults over the last X matches (for various window sizes).|
| `P_1ST_IN_LAST_X_DIFF`     | REAL          | Difference in percentage of first serves in over the last X matches (for various window sizes).|
| `P_1ST_WON_LAST_X_DIFF`    | REAL          | Difference in percentage of first serve wins over the last X matches (for various window sizes).|
| `P_2ND_WON_LAST_X_DIFF`    | REAL          | Difference in percentage of second serve wins over the last X matches (for various window sizes).|
| `P_BP_SAVED_LAST_X_DIFF`   | REAL          | Difference in percentage of break points saved over the last X matches (for various window sizes).|
| `ELO_DIFF`                 | REAL          | Difference in overall Elo ratings between winner and loser after each match update.       |
| `ELO_SURFACE_DIFF`         | REAL          | Difference in surface-specific Elo ratings between winner and loser for the match's surface.|
| `ELO_GRAD_X_DIFF`          | REAL          | Difference in the Elo gradient (slope) over the last X matches (for various window sizes: 5, 10, 20, 35, 50, 100, 250). |

*Note:* Columns with the suffix `_X` represent multiple columns corresponding to different window sizes used in the calculations.

### Additional Details for `atp_matches`

- **Data Integration:**  
  The table is generated by processing and concatenating CSV files from 1991 to 2024. It incorporates numerous performance metrics, head-to-head statistics, and Elo ratings (both overall and surface-specific).

- **Feature Engineering:**  
  Multiple features are derived, including win rate differences over recent matches, performance metrics differences (e.g., percentages of aces, double faults, etc.), and the evolution of Elo ratings.

- **Elo Calculations:**  
  Overall Elo ratings are updated after each match using a standard formula (with a K-factor of 24). Additionally, surface-specific Elo ratings are computed for each court type (e.g., Clay, Grass, Hard).

---

## Table `player_stats`

The new `player_stats` table aggregates player statistics derived from match data, enabling in-depth analysis of individual performance.

| **Column Name**          | **Data Type** | **Description**                                                                                          |
|--------------------------|---------------|----------------------------------------------------------------------------------------------------------|
| `player_id`              | INTEGER       | Unique identifier for the player (foreign key referencing `players_informations`).                      |
| `n_games`                | INTEGER       | Total number of matches played by the player.                                                          |
| **Win Rate Metrics**     |               |                                                                                                          |
| `win_last_3`             | REAL          | Win rate over the last 3 matches.                                                                        |
| `win_last_5`             | REAL          | Win rate over the last 5 matches.                                                                        |
| `win_last_10`            | REAL          | Win rate over the last 10 matches.                                                                       |
| `win_last_25`            | REAL          | Win rate over the last 25 matches.                                                                       |
| `win_last_50`            | REAL          | Win rate over the last 50 matches.                                                                       |
| `win_last_100`           | REAL          | Win rate over the last 100 matches.                                                                      |
| **Performance Metrics**  |               | Average percentages calculated over the last X matches (for X = 3, 5, 10, 25, 50, 100):                |
| `p_ace_last_X`           | REAL          | Percentage of aces.                                                                                      |
| `p_df_last_X`            | REAL          | Percentage of double faults.                                                                             |
| `p_1stIn_last_X`         | REAL          | Percentage of first serves in.                                                                           |
| `p_1stWon_last_X`        | REAL          | Percentage of first serves won.                                                                          |
| `p_2ndWon_last_X`        | REAL          | Percentage of second serves won.                                                                         |
| `p_bpSaved_last_X`       | REAL          | Percentage of break points saved.                                                                        |
| **Elo Ratings**          |               |                                                                                                          |
| `final_elo`              | REAL          | Final overall Elo rating of the player.                                                                  |
| `elo_hard`               | REAL          | Final Elo rating on Hard courts.                                                                         |
| `elo_clay`               | REAL          | Final Elo rating on Clay courts.                                                                         |
| `elo_grass`              | REAL          | Final Elo rating on Grass courts.                                                                        |
| **Elo Gradient**         |               | Slope (gradient) of the Elo evolution over the last X matches (for X = 5, 10, 20, 35, 50, 100, 250):       |
| `elo_grad_last_5`        | REAL          | Elo gradient over the last 5 matches.                                                                    |
| `elo_grad_last_10`       | REAL          | Elo gradient over the last 10 matches.                                                                   |
| `elo_grad_last_20`       | REAL          | Elo gradient over the last 20 matches.                                                                   |
| `elo_grad_last_35`       | REAL          | Elo gradient over the last 35 matches.                                                                   |
| `elo_grad_last_50`       | REAL          | Elo gradient over the last 50 matches.                                                                   |
| `elo_grad_last_100`      | REAL          | Elo gradient over the last 100 matches.                                                                  |
| `elo_grad_last_250`      | REAL          | Elo gradient over the last 250 matches.                                                                  |

### Additional Details for `player_stats`

- **Win Rate Calculations:**  
  Win rates are computed over various recent match windows (3, 5, 10, 25, 50, 100) to gauge current form.

- **Performance Metrics:**  
  Key performance indicators such as aces, double faults, first serves in, and more are averaged over the same windows.

- **Elo Ratings and Evolution:**  
  Elo ratings are updated match by match (using a K-factor of 24) and are computed both overall and by surface. Elo gradient values capture the trend of a player's Elo rating over different periods.

---

## Usage

Three main Python scripts are provided in the project:

1. **Player Data Import and Cleaning:**  
   A script to import and clean player data from a CSV file, which populates the `players_informations` table.

2. **Match Data Processing:**  
   A script that processes ATP match data from CSV files (`atp_matches_YYYY.csv` for years 1991 to 2024) and populates the `atp_matches` table with enriched match statistics.

3. **Aggregated Player Statistics Calculation:**  
   A script that computes aggregated statistics for each player (including the number of matches played, recent win rates, performance metrics, and Elo ratings) based on match data. The results are stored in the `player_stats` table for comprehensive individual performance analysis.

---

**Written by GenAI**