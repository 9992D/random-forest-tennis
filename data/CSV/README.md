# Tennis Match Data Dictionary

This repository contains detailed tennis match data. Below is a clear explanation of each column available in the data files.

## General Columns

- **tourney_id**: Unique identifier for each tournament (format: `YYYY-XXX`).
- **tourney_name**: Name of the tournament.
- **surface**: Court surface type (e.g., Clay, Hard, Grass).
- **draw_size**: Number of players in the draw (rounded up to nearest power of two).
- **tourney_level**:
  - Men:
    - `G` = Grand Slams
    - `M` = Masters 1000
    - `A` = Tour-level events
    - `C` = Challengers
    - `S` = Satellites/ITFs
    - `F` = Tour finals/season-ending events
    - `D` = Davis Cup
  - Women:
    - `P` = Premier
    - `PM` = Premier Mandatory
    - `I` = International
    - Numeric values (e.g., `15`) represent ITF tournaments by prize money (in thousands, e.g., ITF $15,000)
    - Older WTA codes such as `T1` (Tier I)
    - `D` = Fed Cup/Billie Jean King Cup, Wightman Cup, Bonne Bell Cup
  - Both Genders:
    - `E` = Exhibition
    - `J` = Juniors
    - `T` = Team Tennis (future inclusion)
- **tourney_date**: Tournament start date (`YYYYMMDD`). Usually Monday.
- **match_num**: Match-specific identifier (varies by source).

## Player Information

- **winner_id** / **loser_id**: Unique player identifiers.
- **winner_seed** / **loser_seed**: Tournament seed number, if applicable.
- **winner_entry** / **loser_entry**: Entry type (`WC`=Wild Card, `Q`=Qualifier, `LL`=Lucky Loser, `PR`=Protected Ranking, `ITF`=ITF entry, etc.).
- **winner_name** / **loser_name**: Player full name.
- **winner_hand** / **loser_hand**: Player's dominant serving hand (`R`=Right, `L`=Left, `U`=Unknown).
- **winner_ht** / **loser_ht**: Player height in centimeters (when available).
- **winner_ioc** / **loser_ioc**: Three-character IOC country code.
- **winner_age** / **loser_age**: Player age (years) at the tournament date.

## Match Information

- **score**: Final score of the match.
- **best_of**: Number of sets in the match (`3` or `5`).
- **round**: Tournament round (e.g., Final, Semi-final, etc.).
- **minutes**: Match duration in minutes (when available).

## Match Statistics

- **w_ace** / **l_ace**: Number of aces.
- **w_df** / **l_df**: Number of double faults.
- **w_svpt** / **l_svpt**: Total serve points played.
- **w_1stIn** / **l_1stIn**: First serves successfully made.
- **w_1stWon** / **l_1stWon**: Points won on first serve.
- **w_2ndWon** / **l_2ndWon**: Points won on second serve.
- **w_SvGms** / **l_SvGms**: Serve games played.
- **w_bpSaved** / **l_bpSaved**: Break points saved.
- **w_bpFaced** / **l_bpFaced**: Break points faced.

## Rankings

- **winner_rank** / **loser_rank**: ATP/WTA rank at the tournament date.
- **winner_rank_points** / **loser_rank_points**: ATP/WTA ranking points (if available).

---

**Written by GenAI**