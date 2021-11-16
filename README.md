# comp472-mp2
Repo-URL: `https://github.com/theWoogle/comp472-mp2/`
* Run the required games from the assignment with `pypy3 skeleton-tictactoe.py`
* To play manually change add another game to the list of games to play in line 576: 
  
```python
# ensure that n,b in get_random_blocs matches the game parameters
games.append(Game(askInputs = False, n=8, b=6, s=5, d1=6, d2=6, t=5, a1=True, a2=True, get_random_blocs(n=8,b=6)))
games.append(Game(askInputs = True)) # To make the settings manually and play with 1 or more human players
 ```
* This will play 1 + 2x10 with the given board parameters where the last 2x10 games are playey by 2 AIs 
