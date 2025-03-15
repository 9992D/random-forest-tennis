import pandas as pd
import numpy as np
from collections import defaultdict, deque
from tqdm import tqdm
import sqlite3

def import_atp_data_to_sqlite(db_path="data/SQLite/tennis.db", table_name="atp_matches"):
    """
    This function reads ATP match CSV files (named 'atp_matches_YYYY.csv' for years 1991 to 2024),
    processes and enriches the data through several steps, and then inserts the final dataset into a SQLite database.
    
    The processing steps are as follows:
      1. Concatenate all CSV files (from 1991 to 2024) into a single DataFrame.
      2. Clean the data by dropping rows with missing critical values.
      3. Create additional features such as winner/loser IDs, differences in ATP points, rankings, ages, heights,
         match format (BEST_OF) and draw size.
      4. Calculate head-to-head (H2H) differences overall and per surface.
      5. Compute the number of matches played by each player and the difference in counts.
      6. Calculate the difference in win rates over the last N matches for various window sizes.
      7. Compute recent performance statistics differences (e.g., percentage of aces, first serve in, etc.) over various windows.
      8. Calculate overall ELO differences and surface-specific ELO differences, recording the individual overall ELO 
         for each player as well as the ELO on the match's surface.
      9. Compute the gradient (slope) difference of ELO evolution over different window sizes.
      
    Finally, the resulting dataset is stored in the specified SQLite database.
    """

    # 1) Concatenate CSV files for years 1991 to 2024
    all_data = pd.read_csv("./data/CSV/atp_matches_1991.csv")
    for year in range(1992, 2025):
        file = "./data/CSV/atp_matches_" + str(year) + ".csv"
        year_data = pd.read_csv(file)
        all_data = pd.concat([all_data, year_data], axis=0)

    # 2) Clean the data by dropping rows with missing critical values
    all_data_filtered = all_data.dropna(subset=[
        'winner_id', 'loser_id', 'winner_ht', 'loser_ht', 'winner_age', 'loser_age',
        "w_ace", "w_df", "w_svpt", "w_1stIn", "w_1stWon", "w_2ndWon", "w_SvGms", "w_bpSaved", "w_bpFaced",
        "l_ace", "l_df", "l_svpt", "l_1stIn", "l_1stWon", "l_2ndWon", "l_SvGms", "l_bpSaved", "l_bpFaced",
        'winner_rank_points', 'loser_rank_points', 'winner_rank', 'loser_rank', "surface"
        ]
    )
    all_data_filtered = all_data_filtered.reset_index(drop=True)

    # 3) Create additional features and initialize final_data DataFrame
    final_data = pd.DataFrame()
    final_data["WINNER_ID"] = all_data_filtered["winner_id"]
    final_data["LOSER_ID"] = all_data_filtered["loser_id"]
    final_data["ATP_POINT_DIFF"] = all_data_filtered["winner_rank_points"] - all_data_filtered["loser_rank_points"]
    final_data["ATP_RANK_DIFF"] = all_data_filtered["winner_rank"] - all_data_filtered["loser_rank"]
    final_data["AGE_DIFF"] = all_data_filtered["winner_age"] - all_data_filtered["loser_age"]
    final_data["HEIGHT_DIFF"] = all_data_filtered["winner_ht"] - all_data_filtered["loser_ht"]
    final_data["BEST_OF"] = all_data_filtered["best_of"]
    final_data["DRAW_SIZE"] = all_data_filtered["draw_size"]

    # 4) Calculate H2H and H2H per surface differences
    h2h_surface_dict = defaultdict(lambda: defaultdict(int))
    h2h_dict = defaultdict(int)
    total_h2h_surface = []
    total_h2h = []

    for idx, (w_id, l_id, surface) in enumerate(tqdm(zip(all_data_filtered['winner_id'], 
                                                        all_data_filtered['loser_id'], 
                                                        all_data_filtered['surface']),
                                                    total=len(all_data_filtered))):
        wins = h2h_dict[(w_id, l_id)]
        loses = h2h_dict[(l_id, w_id)]

        wins_surface = h2h_surface_dict[surface][(w_id, l_id)]
        loses_surface = h2h_surface_dict[surface][(l_id, w_id)]

        total_h2h.append(wins - loses)
        total_h2h_surface.append(wins_surface - loses_surface)

        h2h_dict[(w_id, l_id)] += 1
        h2h_surface_dict[surface][(w_id, l_id)] += 1
        

    final_data["H2H_DIFF"] = total_h2h
    final_data["H2H_SURFACE_DIFF"] = total_h2h_surface

    # 5) Calculate the number of matches played and the difference in counts
    matches_played = defaultdict(int)
    player_w_matches = []
    player_l_matches = []
    player_diff_matches = []

    for idx, (w_id, l_id) in enumerate(tqdm(zip(all_data_filtered['winner_id'], 
                                                        all_data_filtered['loser_id']),
                                                    total=len(all_data_filtered))):
        n_player_w_matches = matches_played[w_id]
        n_player_l_matches = matches_played[l_id]

        player_w_matches.append(n_player_w_matches)
        player_l_matches.append(n_player_l_matches)
        player_diff_matches.append(n_player_w_matches-n_player_l_matches)

        matches_played

        matches_played[w_id] += 1
        matches_played[l_id] += 1

    # final_data["W_N_GAMES"] = player_w_matches
    # final_data["L_N_GAMES"] = player_l_matches
    final_data["DIFF_N_GAMES"] = player_diff_matches

    # 6) Calculate win rate differences over the last N matches for various window sizes
    for k in [3, 5, 10, 25, 50, 100]:
        last_k_matches = defaultdict(lambda: deque(maxlen=k))
        wins_last_k = []

        for w_id, l_id in tqdm(zip(all_data_filtered['winner_id'], all_data_filtered['loser_id']), total=len(all_data_filtered)):
            
            if len(last_k_matches[w_id]) != 0 and len(last_k_matches[l_id]) != 0:
                wins_count_w = sum(last_k_matches[w_id])/len(last_k_matches[w_id])
                wins_count_l = sum(last_k_matches[l_id])/len(last_k_matches[l_id])
            else:
                wins_count_w = 0
                wins_count_l = 0
            
            wins_last_k.append(wins_count_w-wins_count_l)

            # Update
            last_k_matches[w_id].append(1)
            last_k_matches[l_id].append(0)

        name = "WIN_LAST_"+str(k)+"_DIFF"
        final_data[name] = wins_last_k

    # 7) Calculate recent performance statistics differences over the last N matches
    def mean(arr):
        if len(arr) == 0:
            return 0.5
        else:
            total = 0
            for val in arr:
                total += val
            return total/(len(arr))

    # Calculate the statistics in the last N matches
    for k in [3, 5, 10, 20, 50, 100, 200, 300, 2000]:
        last_k_matches = defaultdict(lambda: defaultdict(lambda: deque(maxlen=k)))
        p_ace_k = []
        p_df_k = []
        p_1stIn_k = []
        p_1stWon_k = []
        p_2ndWon_k = []
        p_bpSaved_k = []

        for row in tqdm(all_data_filtered.itertuples(index=False), total=len(all_data_filtered)):
            w_id, l_id = row.winner_id, row.loser_id
            w_ace, l_ace = row.w_ace, row.l_ace
            w_df, l_df = row.w_df, row.l_df
            w_svpt, l_svpt = row.w_svpt, row.l_svpt
            w_1stIn, l_1stIn = row.w_1stIn, row.l_1stIn
            w_1stWon, l_1stWon = row.w_1stWon, row.l_1stWon
            w_2ndWon, l_2ndWon = row.w_2ndWon, row.l_2ndWon
            w_SvGms, l_SvGms = row.w_SvGms, row.l_SvGms
            w_bpSaved, l_bpSaved = row.w_bpSaved, row.l_bpSaved
            w_bpFaced, l_bpFaced = row.w_bpFaced, row.l_bpFaced

            p_ace_k.append(mean(last_k_matches[w_id]["p_ace"])-mean(last_k_matches[l_id]["p_ace"]))
            p_df_k.append(mean(last_k_matches[w_id]["p_df"])-mean(last_k_matches[l_id]["p_df"]))
            p_1stIn_k.append(mean(last_k_matches[w_id]["p_1stIn"])-mean(last_k_matches[l_id]["p_1stIn"]))
            p_1stWon_k.append(mean(last_k_matches[w_id]["p_1stWon"])-mean(last_k_matches[l_id]["p_1stWon"]))
            p_2ndWon_k.append(mean(last_k_matches[w_id]["p_2ndWon"])-mean(last_k_matches[l_id]["p_2ndWon"]))
            p_bpSaved_k.append(mean(last_k_matches[w_id]["p_bpSaved"])-mean(last_k_matches[l_id]["p_bpSaved"]))


            # Update
            if (w_svpt != 0) and (w_svpt != w_1stIn):
                # Percentatge of aces
                last_k_matches[w_id]["p_ace"].append(100*(w_ace/w_svpt))
                # Percentatge of double faults
                last_k_matches[w_id]["p_df"].append(100*(w_df/w_svpt))
                # Percentatge of first serve in
                last_k_matches[w_id]["p_1stIn"].append(100*(w_1stIn/w_svpt))
                # Percentatge of second serve won
                last_k_matches[w_id]["p_2ndWon"].append(100*(w_2ndWon/(w_svpt-w_1stIn)))
            if l_svpt != 0 and (l_svpt != l_1stIn):
                last_k_matches[l_id]["p_ace"].append(100*(l_ace/l_svpt))
                last_k_matches[l_id]["p_df"].append(100*(l_df/l_svpt))
                last_k_matches[l_id]["p_1stIn"].append(100*(l_1stIn/l_svpt))
                last_k_matches[l_id]["p_2ndWon"].append(100*(l_2ndWon/(l_svpt-l_1stIn)))

            # Percentatge of first serve won
            if w_1stIn != 0:
                last_k_matches[w_id]["p_1stWon"].append(100*(w_1stWon/w_1stIn))
            if l_1stIn != 0:
                last_k_matches[l_id]["p_1stWon"].append(100*(l_1stWon/l_1stIn))
            
            # Percentatge of second serve won
            if w_bpFaced != 0:
                last_k_matches[w_id]["p_bpSaved"].append(100*(w_bpSaved/w_bpFaced))
            if l_bpFaced != 0:
                last_k_matches[l_id]["p_bpSaved"].append(100*(l_bpSaved/l_bpFaced))
            
        final_data["P_ACE_LAST_"+str(k)+"_DIFF"] = p_ace_k
        final_data["P_DF_LAST_"+str(k)+"_DIFF"] = p_df_k
        final_data["P_1ST_IN_LAST_"+str(k)+"_DIFF"] = p_1stIn_k
        final_data["P_1ST_WON_LAST_"+str(k)+"_DIFF"] = p_1stWon_k
        final_data["P_2ND_WON_LAST_"+str(k)+"_DIFF"] = p_2ndWon_k
        final_data["P_BP_SAVED_LAST_"+str(k)+"_DIFF"] = p_bpSaved_k

    # 8) Calculate overall ELO differences and surface-specific ELO differences
    # Calculate ELO Tennis
    elo_players = defaultdict(int)
    all_elo = defaultdict(lambda: deque())
    df_elo = []

    for w_id, l_id in tqdm(zip(all_data_filtered['winner_id'], all_data_filtered['loser_id']), total=len(all_data_filtered)):
        k = 24

        elo_w = elo_players.get(w_id, 1500)
        elo_l = elo_players.get(l_id, 1500)

        exp_w = 1/(1+10**((elo_l-elo_w)/400))
        exp_l = 1/(1+10**((elo_w-elo_l)/400))

        elo_w += k*(1-exp_w)
        elo_l += k*(0-exp_l)

        df_elo.append(elo_w-elo_l)

        # Update
        elo_players[w_id] = elo_w
        elo_players[l_id] = elo_l

        all_elo[w_id].append(elo_w)
        all_elo[l_id].append(elo_l)

    final_data["ELO_DIFF"] = df_elo

    # Calculate ELO Tennis per surface
    elo_surfaces = defaultdict(lambda: defaultdict(int))
    all_elo_surfaces = defaultdict(lambda: defaultdict(lambda: deque()))
    df_elo = []

    for w_id, l_id, surface in tqdm(zip(all_data_filtered['winner_id'], all_data_filtered['loser_id'], all_data_filtered['surface']), total=len(all_data_filtered)):
        k = 24
        
        elo_w = elo_surfaces[surface].get(w_id, 1500)
        elo_l = elo_surfaces[surface].get(l_id, 1500)

        exp_w = 1/(1+10**((elo_l-elo_w)/400))
        exp_l = 1/(1+10**((elo_w-elo_l)/400))

        elo_w += k*(1-exp_w)
        elo_l += k*(0-exp_l)

        df_elo.append(elo_w-elo_l)

        # Update
        elo_surfaces[surface][w_id] = elo_w
        elo_surfaces[surface][l_id] = elo_l

        all_elo_surfaces[surface][w_id].append(elo_w)
        all_elo_surfaces[surface][l_id].append(elo_l)

        for s in ["Clay", "Grass", "Hard", "Carpet"]:
            if surface != s:
                all_elo_surfaces[s][w_id].append(elo_surfaces[s].get(w_id, 1500))
                all_elo_surfaces[s][l_id].append(elo_surfaces[s].get(l_id, 1500))

    final_data["ELO_SURFACE_DIFF"] = df_elo        

    # Calculate the gradient difference on total ELO
    for n in [5, 10, 20, 35, 50, 100, 250]:
        elo_calc = defaultdict(lambda: deque(maxlen=n))
        grad_df_elo = []

        for w_id, l_id in tqdm(zip(all_data_filtered['winner_id'], all_data_filtered['loser_id']), total=len(all_data_filtered)):
            k = 24

            elo_w_list = elo_calc.get(w_id, deque([1500]))
            elo_l_list = elo_calc.get(l_id, deque([1500]))

            elo_w = elo_w_list[-1]
            elo_l = elo_l_list[-1]

            exp_w = 1/(1+10**((elo_l-elo_w)/400))
            exp_l = 1/(1+10**((elo_w-elo_l)/400))

            elo_w += k*(1-exp_w)
            elo_l += k*(0-exp_l)

            # Calculate gradient
            # df_elo.append(elo_w-elo_l)
            if len(elo_w_list) >= n and len(elo_l_list) >= n:
                slope_w = np.polyfit(np.arange(len(elo_w_list)), np.array(elo_w_list), 1)[0]
                slope_l = np.polyfit(np.arange(len(elo_l_list)), np.array(elo_l_list), 1)[0]
                grad_df_elo.append(slope_w-slope_l)
            else:
                grad_df_elo.append(0)

            # Update
            elo_calc[w_id].append(elo_w)
            elo_calc[l_id].append(elo_l)

        final_data["ELO_GRAD_"+str(n)+"_DIFF"] = grad_df_elo

    # Insert the final_data DataFrame into the SQLite database
    conn = sqlite3.connect(db_path)
    final_data.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    import_atp_data_to_sqlite()