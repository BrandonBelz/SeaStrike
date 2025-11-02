SeaStrike is a player vs computer Battleship game made with the help of Parker Russo.
To play the game, Python and PySide6 must be installed on the machine.

Move to the appropriate directory and run
```
python main.py
```

Playing the game is pretty simple. Simply left click where you want to fire when it is your turn. 
When the game first starts, you will be in ship-placement mode. In this game, ships are just contiguous collections of gray squares. When placing a ship, it will show as green when it can be placed there, and red when it cannot be. Right click to rotate a ship and left click to place it. You can also scroll through your ship inventory, but once a ship is placed it cannot be picked up again.

Note: the game was made as a Python object-oriented programming project, so formatting was not something we spent much time perfecting. For this reason, the window was not made to be dynamically resized. It can be resized, but elements of the game may not change sizes with it. Also, we are aware that sometimes the window may widen slightly when the status box's text gets long.
