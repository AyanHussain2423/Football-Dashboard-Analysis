# ⚽ Football Dashboard Analysis

A **Football Data Analytics Project** built using Python and SQL to analyze player and team performances across different leagues.  
The goal of this project is to explore how data such as expected goals (xG), assists, passes, and shots can describe team strengths and player efficiency.

---

## 🧩 Project Description

This project uses real football datasets containing match, player, and team statistics.  
It leverages **SQLite**, **Pandas**, and **Matplotlib** for querying and visualization.  
The final outputs are exported to Excel for **Power BI dashboard integration**.

Each dataset provides deep insights into different parts of the game:

- **Teams & Leagues:** Identifies the number of teams participating in different leagues and their seasonal stats.  
- **Team Stats:** Summarizes goals, xGoals, wins, losses, and draws.  
- **Player Stats:** Analyzes top scorers, assists, xGoals, and on-target shots.  
- **Heatmaps:** Visualizes shot locations for players like Messi or Mbappé using Matplotlib and Seaborn.  
- **Best XI:** Selects the best playing 11 of each season using xGoals, xAssists, and xBuildUp contributions.  

The output file `FootballDashboard.xlsx` consolidates all SQL query results, ready to be used for visualization and reporting in Power BI.

---

## 📊 Key Features

- Data cleaning and transformation using **Pandas**
- SQL-style joins and aggregations with **SQLite**
- Analytical queries for:
  - Top scorers and assist leaders
  - Team home and away performances
  - Fouls and card analysis
  - Predictive goal modeling using xGoals
- Shot **heatmaps** to visually represent player shooting patterns
- Export of all results into a single Excel workbook for Power BI

---

## 📁 Output File

**FootballDashboard.xlsx**  
Contains 8 sheets representing:
- Team and league summaries  
- Player statistics  
- xGoal predictions  
- Best XI lineup of each season  

---

## 🧠 Tools & Libraries Used

- **Python**
- **Pandas**
- **SQLite**
- **Matplotlib**
- **Seaborn**
- **Power BI**
- **OpenPyXL**

---

## ⚽ Summary

This project showcases how football performance data can be transformed into powerful visual and statistical insights.  
From identifying top-performing players to comparing xGoals with actual goals, the analysis helps uncover the deeper story behind every match.

---

*Created by Ayan Hussain — Football Data Analysis Project 2025*
