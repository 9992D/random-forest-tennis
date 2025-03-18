**Tennis Matches Dataset (matchs_tennis.csv)**

This CSV dataset contains structured information about professional tennis matches, scraped and processed from [Tennis Abstract's Match Charting Project](https://www.tennisabstract.com/charting/).

---

## 📁 **Dataset Structure**

The dataset includes the following columns:

| Column               | Description                                   | Example                           |
|----------------------|-----------------------------------------------|-----------------------------------|
| `date`               | Date of the match (`YYYY-MM-DD`)               | `2025-03-16`                      |
| `tournament`         | Tournament name                                | `Indian Wells Masters`            |
| `round`              | Round of the tournament                        | `F` (Final), `SF` (Semi-final)    |
| `player1_firstname`  | First name(s) of Player 1                      | `Holger`                          |
| `player1_lastname`   | Last name of Player 1                          | `Rune`                            |
| `player2_firstname`  | First name(s) of Player 2                      | `Jack`                            |
| `player2_lastname`   | Last name of Player 2                          | `Draper`                          |
| `category`           | Competition category (`ATP` or `WTA`)          | `ATP`                             |
| `URL`                | Relative URL link to the detailed match report | `2025xxxxxx.html`                 |

---

## 🧑‍💻 **Technical Information**

- **Source:** [Tennis Abstract Match Charting Project](https://www.tennisabstract.com/charting/)
- **Scraped using:** Python (`requests`, `BeautifulSoup`, `pandas`, `regex`)
- **Frequency:** Dataset extraction can be executed manually or automated as required.
- **Purpose:** Suitable for match analysis, player statistics, or historical data tracking.

---

## 📌 **Example of Usage**

This dataset can be used for:

- Historical match analysis
- Statistical modeling and player comparisons
- Training machine learning models for predictive analytics
- Visualization of player or tournament performances

---

## ✅ **CSV File**

The resulting CSV is saved as:
```
data/Scrapping/matchs_tennis.csv
```

---

**Written by GenAi**