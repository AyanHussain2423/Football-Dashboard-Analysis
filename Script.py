import pandas as pd
import numpy as np
import sqlite3 as sql


pd.set_option('display.max_rows', None)
df_team = pd.read_csv('teams.csv')
df_teamstats = pd.read_csv('teamstats.csv')

conn = sql.connect(":memory:")

df_team.to_sql("Teams", conn, index=False, if_exists="replace")
df_teamstats.to_sql("Teamstats", conn, index=False, if_exists="replace")

df_games = pd.read_csv('games.csv')
df_games.to_sql("Games", conn, index=False, if_exists="replace")

df_leagues = pd.read_csv('leagues.csv')
df_leagues.to_sql("Leagues", conn, index=False, if_exists="replace")

df_Apearence = pd.read_csv('appearances.csv' )
df_Apearence.to_sql("appearances", conn, index=False, if_exists="replace")

df_players = pd.read_csv('players.csv' , encoding='latin1')
df_players.to_sql("players", conn, index=False, if_exists="replace")

df_shots = pd.read_csv('shots.csv' )
df_shots.to_sql("shots", conn, index=False, if_exists="replace")

Query_1 = """
Select 
Distinct
 t.name as Team_Name,
 l.name as League_Name
From
 Teams t
   Join Teamstats ts ON t.teamID = ts.teamID
   Join Games g ON ts.gameID = g.gameID
   Join Leagues l ON g.leagueID = l.leagueID;

"""
Team_League_Season = pd.read_sql_query(Query_1, conn)
## print(Team_League_Season) ## number of teams in different leagues 

Query_2 = """
SELECT 
    ts.season AS Season,
    t.name AS Team_Name,
    l.name AS League_Name,
    COUNT(DISTINCT g.gameID) AS Total_Games,
    ROUND(Avg(ts.xGoals)) as Avg_xGoals, 
    Sum(ts.Goals) as Total_Goals,
    COUNT(DISTINCT CASE WHEN ts.result = 'W' THEN g.gameID END) AS Total_Wins,
    COUNT(DISTINCT CASE WHEN ts.result = 'L' THEN g.gameID END) AS Total_Losses,
    COUNT(DISTINCT CASE WHEN ts.result = 'D' THEN g.gameID END) AS Total_Draws
FROM 
    Teams t
    JOIN Teamstats ts ON t.teamID = ts.teamID
    JOIN Games g ON ts.gameID = g.gameID
    JOIN Leagues l ON g.leagueID = l.leagueID
GROUP BY 
    ts.season, t.name, l.name
ORDER BY 
    ts.season DESC, l.name ASC, Total_Wins DESC;


"""

Team_Stats = pd.read_sql_query(Query_2, conn)
##print(Team_Stats) ## number of teams in different leagues andf there points in season 

Query_3 = """
SELECT
  ts.season AS Season,
  l.name AS League_Name,
  T.name AS Team_Name,
  COUNT(DISTINCT G.gameID) AS Total_Games_Played,
  SUM(CASE WHEN ts.result = 'W' AND ts.location = 'h' and ts.shots >=8 THEN 1 ELSE 0 END) AS Total_Wins_Home_Shots_More_8,
  SUM(CASE WHEN ts.result = 'W' AND ts.location = 'h' THEN 1 ELSE 0 END) AS Total_Wins_in_Home,
  SUM(CASE WHEN ts.result = 'W' AND ts.location = 'a' and ts.shots >=8 THEN 1 ELSE 0 END) AS Total_Wins_Away_Shots_More_8,
  SUM(CASE WHEN ts.result = 'W' AND ts.location = 'a' THEN 1 ELSE 0 END) AS Total_Wins_in_Away,
  SUM(CASE WHEN ts.result = 'L' AND ts.location = 'h' and ts.shots <8 THEN 1 ELSE 0 END) AS Total_Loss_Home_Shots_less_8,
  SUM(CASE WHEN ts.result = 'L' AND ts.location = 'h' THEN 1 ELSE 0 END) AS Total_Loss_in_Home,
  SUM(CASE WHEN ts.result = 'L' AND ts.location = 'a' and ts.shots <8 THEN 1 ELSE 0 END) AS Total_Loss_Away_Shots_Less_8,
  SUM(CASE WHEN ts.result = 'L' AND ts.location = 'a' THEN 1 ELSE 0 END) AS Total_Loss_in_Away
FROM 
    Teams t
    JOIN Teamstats ts ON t.teamID = ts.teamID
    JOIN Games g ON ts.gameID = g.gameID
    JOIN Leagues l ON g.leagueID = l.leagueID  
GROUP BY 
    ts.season, t.name, l.name;
  """

Team_Stats_per_match = pd.read_sql_query(Query_3, conn)
##print(Team_Stats_per_match)


Query_4 = """
SELECT
  ts.season AS Season,
  l.name AS League_Name,
  T.name AS Team_Name,
  SUM(Ts.fouls) as Total_Fouls,
  SUM(Ts.yellowCards) as Total_Yellow_Cards,
  SUM(Ts.redCards) as Total_Red_Cards
FROM 
    Teams t
    JOIN Teamstats ts ON t.teamID = ts.teamID
    JOIN Games g ON ts.gameID = g.gameID
    JOIN Leagues l ON g.leagueID = l.leagueID  
GROUP BY 
    ts.season, t.name, l.name
ORDER BY l.name ASC;
"""

Fouls_per_team = pd.read_sql_query(Query_4, conn)
##print(Fouls_per_team)


##player stats 

Query_5 = """
 -- Step 1: Make a summary of shots per player per game
WITH ShotSummary AS (
    SELECT 
        ShooterID,
        gameID,
        COUNT(*) AS Total_Shots,
        SUM(CASE 
                WHEN shotResult = 'SavedShot' OR shotResult = 'Goal' 
                THEN 1 ELSE 0 
            END) AS On_Target
    FROM Shots
    GROUP BY ShooterID, gameID
)

-- Step 2: Use that summary in your main query
SELECT 
    Season,
    League_Name,
    Player_Name,
    Total_Goals,
    Shots,
    On_Target
FROM (
    SELECT 
        g.season AS Season,
        l.name AS League_Name,
        p.name AS Player_Name,
        SUM(a.goals) AS Total_Goals,
        SUM(ss.Total_Shots) AS Shots,
        SUM(ss.On_Target) AS On_Target,
        ROW_NUMBER() OVER (
            PARTITION BY g.season, l.name
            ORDER BY SUM(a.goals) DESC
        ) AS rank
    FROM Appearances a
    JOIN Players p ON a.playerID = p.playerID
    JOIN Games g ON a.gameID = g.gameID
    JOIN Leagues l ON g.leagueID = l.leagueID
    LEFT JOIN ShotSummary ss 
        ON ss.ShooterID = p.playerID 
       AND ss.gameID = g.gameID
    GROUP BY g.season, l.name, p.name
) ranked
WHERE rank <= 5
ORDER BY Season DESC, League_Name ASC, Total_Goals DESC;


"""

Player_Stats = pd.read_sql_query(Query_5, conn)
##print(Player_Stats)


##heatmap data
Query_6 = """
SELECT
    P.name AS Player_Name,
    S.PositionX,
    S.PositionY
FROM 
    Players P
    JOIN Shots S ON P.playerID = S.ShooterID
    JOIN Games G ON S.gameID = G.gameID
WHERE S.shotResult = 'Goal' OR S.shotResult = 'SavedShot' 
ORDER BY P.name;
"""

Heatmap_Data = pd.read_sql_query(Query_6, conn)
##print(Heatmap_Data)
## can change the clauseof player name to get heatmap data for different players

##predition of goals based on xgoals

Query_7 = """
SELECT
    ts.season AS Season,
    t.name AS Team_Name,
    l.name AS League_Name,
    SUM(ts.xGoals) AS Total_xGoals,
    SUM(ts.Goals) AS Total_Goals
FROM 
    Teams t 
    JOIN Teamstats ts ON t.teamID = ts.teamID
    JOIN Games g ON ts.gameID = g.gameID
    JOIN Leagues l ON g.leagueID = l.leagueID  
GROUP BY
    ts.season, t.name, l.name
ORDER BY ts.season DESC, l.name ASC, t.name ASC;
  """


Prediction_Data = pd.read_sql_query(Query_7, conn)      
##print(Prediction_Data)

##PLAYINMG 11 OF THE BEST YEAR 
Query_8 = """
WITH RankedPlayers AS (
  SELECT
    g.season AS Season,
    p.name AS Player_Name,
    a.position AS Position,
    SUM(a.xGoals) AS Total_xGoals,
    SUM(a.xAssists) AS Total_xAssists,
    SUM(a.xGoalsChain) AS Total_xGoalsChain,
    SUM(a.xGoalsBuildup) AS Total_xGoalsBuildup,
    SUM(a.assists) AS Total_Assists,
    SUM(a.keyPasses) AS Total_KeyPasses,

    ROW_NUMBER() OVER (
      PARTITION BY g.season, a.position
      ORDER BY 
        SUM(
          a.xGoals * 0.4 +
          a.xAssists * 0.3 +
          a.xGoalsChain * 0.15 +
          a.xGoalsBuildup * 0.15
        ) DESC
    ) AS Rank
  FROM Appearances a
  JOIN Players p ON a.playerID = p.playerID
  JOIN Games g ON a.gameID = g.gameID
  GROUP BY g.season, a.position, p.name
)
SELECT
  Season,
  Player_Name,
  Position,
  Total_xGoals,
  Total_xAssists,
  Total_xGoalsChain,
  Total_xGoalsBuildup,
  Total_Assists,
  Total_KeyPasses
FROM RankedPlayers
WHERE 
  (Position IN ('GK') AND Rank <= 1) OR       -- 1 Goalkeeper
  (Position IN ('DR', 'DC', 'DL', 'DMR', 'DML') AND Rank <= 4) OR  -- 4 Defenders
  (Position IN ('MR', 'MC', 'ML', 'DMC', 'AMR', 'AMC', 'AML') AND Rank <= 3) OR  -- 3 Midfielders
  (Position IN ('FW', 'FWR', 'FWL') AND Rank <= 1)  -- 1 Forward
ORDER BY 
  Season DESC, 
  CASE 
    WHEN Position IN ('GK') THEN 1
    WHEN Position IN ('DR', 'DC', 'DL', 'DMR', 'DML') THEN 2
    WHEN Position IN ('MR', 'MC', 'ML', 'DMC', 'AMR', 'AMC', 'AML') THEN 3
    WHEN Position IN ('FW', 'FWR', 'FWL') THEN 4
    ELSE 5
  END,
  Rank ASC;

"""

Playing_11 = pd.read_sql_query(Query_8, conn)
##print(Playing_11)


##Run all queries and export to one Excel file 
with pd.ExcelWriter("FootballDashboard.xlsx", engine="openpyxl") as writer:
    pd.read_sql(Query_1, conn).to_excel(writer, sheet_name="Team_League_Season", index=False)
    pd.read_sql(Query_2, conn).to_excel(writer, sheet_name="Team_Stats", index=False)
    pd.read_sql(Query_3, conn).to_excel(writer, sheet_name="Top_Scorers", index=False)
    pd.read_sql(Query_4, conn).to_excel(writer, sheet_name="Player_Stats", index=False)
    pd.read_sql(Query_5, conn).to_excel(writer, sheet_name="xGoals_Analysis", index=False)
    pd.read_sql(Query_6, conn).to_excel(writer, sheet_name="Heatmap_OfPlayer", index=False)
    pd.read_sql(Query_7, conn).to_excel(writer, sheet_name="Possession_Data", index=False)
    pd.read_sql(Query_8, conn).to_excel(writer, sheet_name="Best_XI", index=False)


import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as patches

# Pick player
player_name = "Kylian Mbappe-Lottin"  # Change to desired player name
player_data = Heatmap_Data[Heatmap_Data["Player_Name"] == player_name].copy()

# ✅ Scale normalized coordinates (0–1) to match 120x80 pitch
player_data["x"] = player_data["positionX"] * 120
player_data["y"] = player_data["positionY"] * 80

# Create the pitch
fig, ax = plt.subplots(figsize=(10, 6))
pitch = patches.Rectangle((0, 0), 120, 80, linewidth=2, edgecolor='black', facecolor='none')
ax.add_patch(pitch)

# Center line and circle
plt.plot([60, 60], [0, 80], color='black', linewidth=1.2)
center_circle = plt.Circle((60, 40), 9.15, color='black', fill=False, linewidth=1.2)
ax.add_patch(center_circle)

# Penalty boxes
penalty_box_left = patches.Rectangle((0, 18), 18, 44, linewidth=1.2, edgecolor='black', facecolor='none')
penalty_box_right = patches.Rectangle((102, 18), 18, 44, linewidth=1.2, edgecolor='black', facecolor='none')
ax.add_patch(penalty_box_left)
ax.add_patch(penalty_box_right)

# Goal areas
goal_area_left = patches.Rectangle((0, 30), 6, 20, linewidth=1.2, edgecolor='black', facecolor='none')
goal_area_right = patches.Rectangle((114, 30), 6, 20, linewidth=1.2, edgecolor='black', facecolor='none')
ax.add_patch(goal_area_left)
ax.add_patch(goal_area_right)

# ✅ Heatmap using scaled positions
sns.kdeplot(
    x=player_data["x"], 
    y=player_data["y"], 
    fill=True, 
    cmap="Reds", 
    alpha=0.6,
    bw_adjust=0.4,
    ax=ax
)

# Styling
ax.set_xlim(0, 120)
ax.set_ylim(0, 80)
ax.invert_yaxis()  # make it look like TV view
ax.axis('off')
plt.title(f"Shot Heatmap — {player_name}", fontsize=16, fontweight='bold')
plt.show()
