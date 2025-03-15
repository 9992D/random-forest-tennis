import numpy as np
from collections import defaultdict
import pandas as pd
from tqdm import tqdm
import sqlite3

def load_and_clean_atp_matches(start_year=1991, end_year=2024, csv_folder="./data/CSV/"):
    all_data = pd.read_csv(f"{csv_folder}atp_matches_{start_year}.csv")
    for year in range(start_year + 1, end_year + 1):
        file_path = f"{csv_folder}atp_matches_{year}.csv"
        year_data = pd.read_csv(file_path)
        all_data = pd.concat([all_data, year_data], axis=0)
    critical_columns = [
        'winner_id', 'loser_id', 'winner_ht', 'loser_ht', 'winner_age', 'loser_age',
        "w_ace", "w_df", "w_svpt", "w_1stIn", "w_1stWon", "w_2ndWon", "w_SvGms", "w_bpSaved", "w_bpFaced",
        "l_ace", "l_df", "l_svpt", "l_1stIn", "l_1stWon", "l_2ndWon", "l_SvGms", "l_bpSaved", "l_bpFaced",
        'winner_rank_points', 'loser_rank_points', 'winner_rank', 'loser_rank', "surface",
        'tourney_date'
    ]
    all_data_filtered = all_data.dropna(subset=critical_columns).reset_index(drop=True)
    return all_data_filtered

def compute_final_player_stats(df, player_ids):
    """
    Calculates global statistics (win rate, performance metrics and Elo)
    for the provided list of player_ids.
    
    :param df: DataFrame containing ATP matches.
    :param player_ids: List of player identifiers to be processed.
    :return: DataFrame merging match stats and Elo statistics.
    """
    
    def compute_player_stats_for_player(pid, df):
        cols = ['player_id', 'n_games', 
                'win_last_3', 'win_last_5', 'win_last_10', 
                'win_last_25', 'win_last_50', 'win_last_100']
        player_matches = df[(df['winner_id'] == pid) | (df['loser_id'] == pid)].copy()
        if player_matches.empty:
            return pd.DataFrame(columns=cols)
        player_matches['tourney_date'] = player_matches['tourney_date'].astype('int64')
        player_matches = player_matches.sort_values(by='tourney_date', ascending=False).reset_index(drop=True)
        n_games = len(player_matches)
        player_matches['result'] = player_matches.apply(lambda row: 1 if row['winner_id'] == pid else 0, axis=1)
        windows = [3, 5, 10, 25, 50, 100]
        stats = {'player_id': pid, 'n_games': n_games}
        for k in windows:
            last_k = player_matches.head(k)
            stats[f'win_last_{k}'] = last_k['result'].mean() if not last_k.empty else 0.0
        return pd.DataFrame([stats], columns=cols)
    
    def compute_player_performance_for_player(pid, df):
        def safe_mean(values):
            valid = [v for v in values if v is not None]
            return sum(valid) / len(valid) if valid else 50.0

        metrics_list = []
        player_matches = df[(df['winner_id'] == pid) | (df['loser_id'] == pid)].copy()
        if player_matches.empty:
            cols = ['player_id', 'n_games'] + [f"{m}_last_{k}" for k in [3,5,10,25,50,100] 
                        for m in ['p_ace', 'p_df', 'p_1stIn', 'p_1stWon', 'p_2ndWon', 'p_bpSaved']]
            return pd.DataFrame(columns=cols)
        player_matches['tourney_date'] = player_matches['tourney_date'].astype('int64')
        player_matches = player_matches.sort_values(by='tourney_date', ascending=False).reset_index(drop=True)
        n_games = len(player_matches)
        for _, row in player_matches.iterrows():
            if row['winner_id'] == pid:
                p_ace = 100 * (row['w_ace'] / row['w_svpt']) if row['w_svpt'] != 0 else None
                p_df = 100 * (row['w_df'] / row['w_svpt']) if row['w_svpt'] != 0 else None
                p_1stIn = 100 * (row['w_1stIn'] / row['w_svpt']) if row['w_svpt'] != 0 else None
                p_1stWon = 100 * (row['w_1stWon'] / row['w_1stIn']) if row['w_1stIn'] != 0 else None
                denom = row['w_svpt'] - row['w_1stIn']
                p_2ndWon = 100 * (row['w_2ndWon'] / denom) if denom != 0 else None
                p_bpSaved = 100 * (row['w_bpSaved'] / row['w_bpFaced']) if row['w_bpFaced'] != 0 else None
            else:
                p_ace = 100 * (row['l_ace'] / row['l_svpt']) if row['l_svpt'] != 0 else None
                p_df = 100 * (row['l_df'] / row['l_svpt']) if row['l_svpt'] != 0 else None
                p_1stIn = 100 * (row['l_1stIn'] / row['l_svpt']) if row['l_svpt'] != 0 else None
                p_1stWon = 100 * (row['l_1stWon'] / row['l_1stIn']) if row['l_1stIn'] != 0 else None
                denom = row['l_svpt'] - row['l_1stIn']
                p_2ndWon = 100 * (row['l_2ndWon'] / denom) if denom != 0 else None
                p_bpSaved = 100 * (row['l_bpSaved'] / row['l_bpFaced']) if row['l_bpFaced'] != 0 else None
            metrics_list.append({
                'p_ace': p_ace,
                'p_df': p_df,
                'p_1stIn': p_1stIn,
                'p_1stWon': p_1stWon,
                'p_2ndWon': p_2ndWon,
                'p_bpSaved': p_bpSaved
            })
        windows = [3, 5, 10, 25, 50, 100]
        stats = {'player_id': pid, 'n_games': n_games}
        for k in windows:
            window_metrics = metrics_list[:k]
            stats[f'p_ace_last_{k}'] = safe_mean([m['p_ace'] for m in window_metrics])
            stats[f'p_df_last_{k}'] = safe_mean([m['p_df'] for m in window_metrics])
            stats[f'p_1stIn_last_{k}'] = safe_mean([m['p_1stIn'] for m in window_metrics])
            stats[f'p_1stWon_last_{k}'] = safe_mean([m['p_1stWon'] for m in window_metrics])
            stats[f'p_2ndWon_last_{k}'] = safe_mean([m['p_2ndWon'] for m in window_metrics])
            stats[f'p_bpSaved_last_{k}'] = safe_mean([m['p_bpSaved'] for m in window_metrics])
        cols = ['player_id', 'n_games'] + [f"{m}_last_{k}" for k in windows for m in 
                ['p_ace', 'p_df', 'p_1stIn', 'p_1stWon', 'p_2ndWon', 'p_bpSaved']]
        return pd.DataFrame([stats], columns=cols)
    
    stats_list = []
    for pid in tqdm(player_ids):
        s_df = compute_player_stats_for_player(pid, df)
        p_df = compute_player_performance_for_player(pid, df)
        if s_df.empty and p_df.empty:
            continue
        merged = pd.merge(s_df, p_df, on=['player_id', 'n_games'], how='outer')
        stats_list.append(merged)
    if stats_list:
        stats_df = pd.concat(stats_list, ignore_index=True)
    else:
        stats_df = pd.DataFrame()
    

    df_sorted = df.sort_values(by='tourney_date').reset_index(drop=True)
    k_constant = 24
    surfaces = ["Hard", "Clay", "Grass"]
    elo_overall = defaultdict(lambda: 1500)
    elo_history = defaultdict(list)
    elo_surface = {s: defaultdict(lambda: 1500) for s in surfaces}
    elo_surface_history = {s: defaultdict(list) for s in surfaces}
    
    for _, row in tqdm(df_sorted.iterrows(), total=len(df_sorted)):
        w_id = row['winner_id']
        l_id = row['loser_id']
        surface = row['surface']

        elo_w = elo_overall[w_id]
        elo_l = elo_overall[l_id]
        exp_w = 1 / (1 + 10 ** ((elo_l - elo_w) / 400))
        exp_l = 1 / (1 + 10 ** ((elo_w - elo_l) / 400))
        new_elo_w = elo_w + k_constant * (1 - exp_w)
        new_elo_l = elo_l + k_constant * (0 - exp_l)
        elo_overall[w_id] = new_elo_w
        elo_overall[l_id] = new_elo_l
        elo_history[w_id].append(new_elo_w)
        elo_history[l_id].append(new_elo_l)

        if surface in surfaces:
            elo_w_s = elo_surface[surface][w_id]
            elo_l_s = elo_surface[surface][l_id]
            exp_w_s = 1 / (1 + 10 ** ((elo_l_s - elo_w_s) / 400))
            exp_l_s = 1 / (1 + 10 ** ((elo_w_s - elo_l_s) / 400))
            new_elo_w_s = elo_w_s + k_constant * (1 - exp_w_s)
            new_elo_l_s = elo_l_s + k_constant * (0 - exp_l_s)
            elo_surface[surface][w_id] = new_elo_w_s
            elo_surface[surface][l_id] = new_elo_l_s
            elo_surface_history[surface][w_id].append(new_elo_w_s)
            elo_surface_history[surface][l_id].append(new_elo_l_s)
    
    windows = [5, 10, 20, 35, 50, 100, 250]
    elo_data = []
    for pid in player_ids:
        final_elo = elo_overall[pid]
        final_elo_hard = elo_surface["Hard"][pid]
        final_elo_clay = elo_surface["Clay"][pid]
        final_elo_grass = elo_surface["Grass"][pid]
        history = elo_history[pid]
        grad_stats = {}
        for w in windows:
            if len(history) >= w:
                x = np.arange(len(history))
                slope = np.polyfit(x, np.array(history), 1)[0]
            else:
                slope = 0
            grad_stats[f'elo_grad_last_{w}'] = slope
        elo_entry = {
            'player_id': pid,
            'final_elo': final_elo,
            'elo_hard': final_elo_hard,
            'elo_clay': final_elo_clay,
            'elo_grass': final_elo_grass
        }
        elo_entry.update(grad_stats)
        elo_data.append(elo_entry)
    elo_df = pd.DataFrame(elo_data)
    
    final_df = pd.merge(stats_df, elo_df, on='player_id', how='outer')
    return final_df

def player_ids_from_sqlite(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT player_id FROM players_informations")
    player_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return player_ids

matches_df = load_and_clean_atp_matches()
external_player_ids = player_ids_from_sqlite("data/SQLite/tennis.db")
final_player_stats = compute_final_player_stats(matches_df, player_ids=external_player_ids)
conn = sqlite3.connect("data/SQLite/tennis.db")
final_player_stats.to_sql("players_stats", conn, if_exists="replace", index=False)
conn.close()