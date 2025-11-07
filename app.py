import streamlit as st
import pandas as pd
import requests

st.title("NHL Player Shots & Points Tracker")

# --- Helper Functions ---
def get_player_id(name):
    url = f"https://search.d3.nhle.com/api/v1/search/player?query={name}"
    data = requests.get(url).json()
    items = data.get("items", [])
    if not items:
        return None
    nhl_players = [p for p in items if p.get("leagueAbbrev") == "NHL"]
    if nhl_players:
        return nhl_players[0].get("playerId")
    return items[0].get("playerId")

def get_game_log(player_id, season):
    url = f"https://api-web.nhle.com/v1/player/{player_id}/game-log/{season}?site=en_nhl"
    data = requests.get(url).json()
    return pd.DataFrame(data.get("gameLog", []))

def career_shots_avg(player_id):
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    data = requests.get(url).json()
    seasons = data.get("seasonTotals", [])
    df = pd.DataFrame(seasons)
    total_shots = df["shots"].sum()
    total_games = df["gamesPlayed"].sum()
    return round(total_shots / total_games, 2) if total_games > 0 else 0:
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    data = requests.get(url).json()
    seasons = data.get("seasonTotals", [])
    df = pd.DataFrame(seasons)
    total_shots = df["shots"].sum()
    total_games = df["gamesPlayed"].sum()
    return round(total_shots / total_games, 2) if total_games > 0 else 0

# --- UI ---
player_name = st.text_input("Search Player Name")
season = "20242025"

if player_name:
    player_id = get_player_id(player_name)

    if not player_id:
        st.error("Player not found.")
    else:
        df = get_game_log(player_id, season)
        if df.empty:
            st.error("No game data found.")
        else:
            df = df[["gameDate", "opponentAbbrev", "shots", "points"]]
            df.rename(columns={"gameDate": "Date", "opponentAbbrev": "Opponent"}, inplace=True)
            df["Date"] = pd.to_datetime(df["Date"])

            st.subheader("Game Log (Most Recent First)")
            st.dataframe(df.sort_values("Date", ascending=False))

            # Stats
            last5 = df.tail(5)
            last10 = df.tail(10)
            season_points = df["points"].sum()
            season_shots = df["shots"].sum()

            st.subheader("Averages & Totals")
            st.write(f"**Last 5 Games - Points:** {last5['points'].mean():.2f}")
            st.write(f"**Last 5 Games - Shots:** {last5['shots'].mean():.2f}")
            st.write(f"**Last 10 Games - Points:** {last10['points'].mean():.2f}")
            st.write(f"**Last 10 Games - Shots:** {last10['shots'].mean():.2f}")
            st.write(f"**Season Total Points:** {season_points}")
            st.write(f"**Season Total Shots:** {season_shots}")

            # Career shots per game
            career_avg = career_shots_avg(player_id)
            st.subheader("Career Average Shots per Game")
            st.write(f"**{career_avg} shots/game**")
