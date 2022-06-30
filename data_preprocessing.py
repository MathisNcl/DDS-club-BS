from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import time
from datetime import datetime
import numpy as np
def extract_team(equipe):
    if isinstance(equipe, str):
        equipe = equipe[1:-1].split(",")
    res = [equipe[0], np.nan, np.nan]

    if len(equipe)==2:
        res[1] = equipe[1]
    elif len(equipe)==3:
        res[1] = equipe[1]
        res[2] = equipe[2]
    return(res)

while True:
    def get_current_db(PROJECT_ID, DATASET_ID, TABLE_ID):

        key_path = "bs-club-dash-b306583304a7.json"

        credentials = service_account.Credentials.from_service_account_file(
            key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        bqclient = bigquery.Client(credentials=credentials, project=credentials.project_id)
        # Download query results.
        query_string = f"""
        SELECT *
        FROM {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}
        """
        dataframe = bqclient.query(query_string).result().to_dataframe(create_bqstorage_client=True)
        return dataframe


    PROJECT_ID = "bs-club-dash"
    DATASET_ID = "club_logs"
    TABLE_ID = "battle_logs"

    df = get_current_db(PROJECT_ID, DATASET_ID,TABLE_ID)
    #Récupération des équipes
    equipes = {i : list(df[df["datetime"]==i]["name"]) for i in df["datetime"].unique()}
    equipes = pd.DataFrame({"datetime": list(equipes.keys()), "equipes": list(equipes.values())})
    df2 = df.merge(equipes, on="datetime", how="left")


    extract = df2["equipes"].apply(extract_team)
    test = pd.DataFrame({"Joueur1": [i[0] for i in extract], "Joueur2": [i[1] for i in extract], "Joueur3": [i[2] for i in extract]})

    df2["Joueur1"] = test["Joueur1"]
    df2["Joueur2"] = test["Joueur2"]
    df2["Joueur3"] = test["Joueur3"]

    df2.to_csv("database.csv", index=False)
    print("Aspiration :{}".format(datetime.now()))

    time.sleep(21600)
