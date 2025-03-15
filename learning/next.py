import sqlite3
import csv
from collections import defaultdict
from tqdm import tqdm
import pandas as pd

def add_matches(player1_id, player2_id, atp_point_diff, atp_rank_diff, best_of, draw_size, age_diff, height_diff, h2h_diff, h2h_surface_diff):
    conn = sqlite3.connect("data/SQLite/tennis.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM players_stats WHERE player_id IN (?, ?)", (player1_id, player2_id))
    rows = cursor.fetchall()
    if len(rows) != 2:
        print("Données insuffisantes pour les deux joueurs")
        conn.close()
        return
    
    player1, player2 = None, None
    for row in rows:
        if row["player_id"] == player1_id:
            player1 = row
        elif row["player_id"] == player2_id:
            player2 = row
            
    if player1 is None or player2 is None:
        print("Erreur lors de l'identification des joueurs")
        conn.close()
        return

    row_data = {}

    row_data["PLAYER_1"] = player1_id
    row_data["PLAYER_2"] = player2_id
    row_data["ATP_POINT_DIFF"] = atp_point_diff
    row_data["ATP_RANK_DIFF"] = atp_rank_diff
    row_data["BEST_OF"] = best_of
    row_data["DRAW_SIZE"] = draw_size
    row_data["H2H_DIFF"] = h2h_diff
    row_data["H2H_SURFACE_DIFF"] = h2h_surface_diff
    row_data["AGE_DIFF"] = age_diff
    row_data["HEIGHT_DIFF"] = height_diff

    row_data["DIFF_N_GAMES"] = player1["n_games"] - player2["n_games"]
    
    for p in [3, 5, 10, 25, 50, 100]:
        col = f"win_last_{p}"
        header_key = f"WIN_LAST_{p}_DIFF"
        if col in player1.keys() and col in player2.keys():
            row_data[header_key] = player1[col] - player2[col]
        else:
            row_data[header_key] = ""
    
    performance_metrics = {
        "P_ACE": "p_ace",
        "P_DF": "p_df",
        "P_1ST_IN": "p_1stIn",
        "P_1ST_WON": "p_1stWon",
        "P_2ND_WON": "p_2ndWon",
        "P_BP_SAVED": "p_bpSaved"
    }

    performance_periods = [3, 5, 10, 20, 50, 100, 200, 300, 2000]
    for period in performance_periods:
        for header_metric, db_metric in performance_metrics.items():
            db_col = f"{db_metric}_last_{period}"
            header_key = f"{header_metric}_LAST_{period}_DIFF"
            if db_col in player1.keys() and db_col in player2.keys():
                row_data[header_key] = player1[db_col] - player2[db_col]
            else:
                row_data[header_key] = ""
    

    row_data["ELO_DIFF"] = (player1["final_elo"] - player2["final_elo"]) if "final_elo" in player1.keys() and "final_elo" in player2.keys() else ""

    row_data["ELO_SURFACE_DIFF"] = (player1["elo_hard"] - player2["elo_hard"]) if "elo_hard" in player1.keys() and "elo_hard" in player2.keys() else ""
    
    for p in [5, 10, 20, 35, 50, 100, 250]:
        col_name = f"elo_grad_last_{p}"
        header_name = f"ELO_GRAD_{p}_DIFF"
        if col_name in player1.keys() and col_name in player2.keys():
            row_data[header_name] = player1[col_name] - player2[col_name]
        else:
            row_data[header_name] = ""
    
    header = [
        "PLAYER_1", "PLAYER_2", "ATP_POINT_DIFF", "ATP_RANK_DIFF", "AGE_DIFF", "HEIGHT_DIFF", "BEST_OF", "DRAW_SIZE", 
        "H2H_DIFF", "H2H_SURFACE_DIFF", "DIFF_N_GAMES",
        "WIN_LAST_3_DIFF", "WIN_LAST_5_DIFF", "WIN_LAST_10_DIFF", "WIN_LAST_25_DIFF", "WIN_LAST_50_DIFF", "WIN_LAST_100_DIFF",
        "P_ACE_LAST_3_DIFF", "P_DF_LAST_3_DIFF", "P_1ST_IN_LAST_3_DIFF", "P_1ST_WON_LAST_3_DIFF", "P_2ND_WON_LAST_3_DIFF", "P_BP_SAVED_LAST_3_DIFF",
        "P_ACE_LAST_5_DIFF", "P_DF_LAST_5_DIFF", "P_1ST_IN_LAST_5_DIFF", "P_1ST_WON_LAST_5_DIFF", "P_2ND_WON_LAST_5_DIFF", "P_BP_SAVED_LAST_5_DIFF",
        "P_ACE_LAST_10_DIFF", "P_DF_LAST_10_DIFF", "P_1ST_IN_LAST_10_DIFF", "P_1ST_WON_LAST_10_DIFF", "P_2ND_WON_LAST_10_DIFF", "P_BP_SAVED_LAST_10_DIFF",
        "P_ACE_LAST_20_DIFF", "P_DF_LAST_20_DIFF", "P_1ST_IN_LAST_20_DIFF", "P_1ST_WON_LAST_20_DIFF", "P_2ND_WON_LAST_20_DIFF", "P_BP_SAVED_LAST_20_DIFF",
        "P_ACE_LAST_50_DIFF", "P_DF_LAST_50_DIFF", "P_1ST_IN_LAST_50_DIFF", "P_1ST_WON_LAST_50_DIFF", "P_2ND_WON_LAST_50_DIFF", "P_BP_SAVED_LAST_50_DIFF",
        "P_ACE_LAST_100_DIFF", "P_DF_LAST_100_DIFF", "P_1ST_IN_LAST_100_DIFF", "P_1ST_WON_LAST_100_DIFF", "P_2ND_WON_LAST_100_DIFF", "P_BP_SAVED_LAST_100_DIFF",
        "P_ACE_LAST_200_DIFF", "P_DF_LAST_200_DIFF", "P_1ST_IN_LAST_200_DIFF", "P_1ST_WON_LAST_200_DIFF", "P_2ND_WON_LAST_200_DIFF", "P_BP_SAVED_LAST_200_DIFF",
        "P_ACE_LAST_300_DIFF", "P_DF_LAST_300_DIFF", "P_1ST_IN_LAST_300_DIFF", "P_1ST_WON_LAST_300_DIFF", "P_2ND_WON_LAST_300_DIFF", "P_BP_SAVED_LAST_300_DIFF",
        "P_ACE_LAST_2000_DIFF", "P_DF_LAST_2000_DIFF", "P_1ST_IN_LAST_2000_DIFF", "P_1ST_WON_LAST_2000_DIFF", "P_2ND_WON_LAST_2000_DIFF", "P_BP_SAVED_LAST_2000_DIFF",
        "ELO_DIFF", "ELO_SURFACE_DIFF", "ELO_GRAD_5_DIFF", "ELO_GRAD_10_DIFF", "ELO_GRAD_20_DIFF", "ELO_GRAD_35_DIFF", "ELO_GRAD_50_DIFF", "ELO_GRAD_100_DIFF", "ELO_GRAD_250_DIFF"
    ]
    
    with open("learning/next.csv", "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        csvfile.seek(0, 2)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow(row_data)
    
    conn.close()

add_matches(208029, 209950, -1080, 7, 3, 128, -8, -0.1, -1, -1)