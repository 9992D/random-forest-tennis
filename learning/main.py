import numpy as np
import pandas as pd
import sqlite3
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

conn = sqlite3.connect("data/SQLite/tennis.db")
final_data = pd.read_sql_query("SELECT * from atp_matches", conn)
conn.close()
final_data = final_data.reset_index(drop=True)

final_data["RESULT"] = 1
column_to_randomize = []

for val in list(final_data.columns):
    if "DIFF" in val:
        column_to_randomize.append(val)

column_to_randomize.append("RESULT")
column_to_randomize.append("WINNER_ID")
column_to_randomize.append("LOSER_ID")

final_data[column_to_randomize] = final_data[column_to_randomize].apply(
    lambda row: row * (-1) if np.random.rand() < 0.5 else row, axis=1
)

def fix_ids(row):
    winner, loser = row['WINNER_ID'], row['LOSER_ID']
    if winner < 0 and loser < 0:
        winner, loser = abs(loser), abs(winner) 
    return pd.Series([winner, loser])

final_data[['WINNER_ID', 'LOSER_ID']] = final_data.apply(fix_ids, axis=1)
final_data.rename(columns={'WINNER_ID': 'PLAYER_1', 'LOSER_ID': 'PLAYER_2'}, inplace=True)

data_np = final_data.to_numpy(dtype=object)[:95375, 2:]
np.random.shuffle(data_np)

split = 0.85
total_rows = final_data.shape[0]
value = round(split * total_rows)

data_np_train = data_np[:value, :]
data_np_test = data_np[value:, :]

mapper = np.vectorize(lambda x: "Player 2 Wins" if x == -1 else "Player 1 Wins")
reverse_mapper = np.vectorize(lambda x: 0 if x == "Player 2 Wins" else 1)

x_train = data_np_train[:, :-1]
x_test = data_np_test[:, :-1]
y_pred_train = mapper(data_np_train[:, -1:])
y_pred_test = mapper(data_np_test[:, -1:])

xgb_model = XGBClassifier(n_estimators=200, max_depth=10, learning_rate=0.1, 
                          subsample=0.8, colsample_bytree=0.7)

xgb_model.fit(data_np_train[:, :-1], reverse_mapper(y_pred_train))

predictions_train = xgb_model.predict(data_np_train[:, :-1])
predictions_test = xgb_model.predict(data_np_test[:, :-1])

next_data = pd.read_csv("learning/next.csv")

X_next = next_data.iloc[:, 2:].to_numpy(dtype=object)

predictions_next = xgb_model.predict(X_next)

prediction_labels = np.where(predictions_next == 0, "Player 2 Wins", "Player 1 Wins")

print(prediction_labels)
