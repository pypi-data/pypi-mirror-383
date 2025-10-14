# WSBA HOCKEY
![WSBA128](https://github.com/user-attachments/assets/4f349728-b99d-4e03-9d77-95cd177fefe2)

### A Python package for scraping and analyzing hockey data under the motto: ***Evaluating, analyzing, and understanding the game of hockey through the lens of different analytical methods, including incorporation of analytics.***

## INSTALLATION AND USAGE
```bash
pip install wsba_hockey
```

```python
import wsba_hockey as wsba
```

## ALL FEATURES

## SCRAPING
### NHL Play-by-Play (of any game frame up to a full season)
#### Functions:

```python
wsba.nhl_scrape_game(2024020918,split_shifts=False,remove=['game-end'])
wsba.nhl_scrape_season(20242025,split_shifts=False,remove=['game-end'],local=True)
```

### NHL Season Information

```python
wsba.nhl_scrape_schedule(20242025)
wsba.nhl_scrape_seasons_info(seasons=[20212022,20222023,20232024,20242025])
wsba.nhl_scrape_standings(arg = '2024-03-20')
```

### NHL Rosters and Player Information

```python
wsba.nhl_scrape_roster(20242025)
wsba.nhl_scrape_team_info()
```

### NHL Draft Rankings and Prospects

```python
wsba.nhl_scrape_draft_rankings()
wsba.nhl_scrape_prospects('BOS')
```


## DATA ANALYTICS
### Expected Goals
```python
pbp = wsba.nhl_scrape_game(2024020918,split_shifts=False,remove=['game-end'])
pbp = wsba.nhl_apply_xG(pbp)
```

### Goal Impacts and Shot Analysis

### Stat Aggregation
```python
pbp = wsba.nhl_scrape_season(20232024,remove=[], local = True)
wsba.nhl_calculate_stats(pbp,'skater',[2],['5v5','4v4','3v3'],shot_impact = True)
```
### Shot Plotting (Plots, Heatmaps, etc.)
```python
skater_dict = {
    'Patrice Bergeron':[20212022,'BOS']
}
pbp = wsba.nhl_scrape_season(20212022,remove=[], local = True)

wsba.nhl_plot_skaters_shots(pbp,skater_dict,['5v5'],onice='for',legend=True)
wsba.nhl_plot_games(pbp,legend=True)
```

## REPOSITORY 
### Past Season Play-by-Play
```python
wsba.repo_load_pbp(seasons=[20212022,20222023,20232024,20242025])
```
### Team Information
```python
wsba.repo_load_teaminfo()
wsba.repo_load_rosters(seasons=[20212022,20222023,20232024,20242025])
```
### Schedule
```python
wsba.repo_load_schedule(seasons=[20212022,20222023,20232024,20242025])
```

## DOCUMENTATION
View full documentation here: [WSBA Hockey Package Documentation](https://owensingh38.github.io/wsba_hockey/)

## ACKNOWLEDGEMENTS AND CREDITS 
### Huge thanks to the following:
Harry Shomer - Creator of the hockey_scraper package, which contains select utils functions within this package and otherwise inspires the creation of this package.

Dan Morse - Creator of the hockeyR package; another important inspiration and model for developing an NHL scraper.

Patrick Bacon - Creator of TopDownHockey package

Anyone in the NHL Public Analytics community who has stuck around and supported WeakSide Breakout Analysis hockey.