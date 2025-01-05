from enum import Enum, auto

class Orientation(Enum):
    '''Ships can be placed in one of two orientations.'''
    DOWN = auto()
    ACROSS = auto()
    def other_orientation(self) -> 'Orientation':
        return Orientation.DOWN if self == Orientation.ACROSS else Orientation.ACROSS

class GridSpace(Enum):
    '''Represents the state of a Battleship grid space.'''
    EMPTY = auto()
    OCCUPIED = auto()
    MISS = auto()
    HIT = auto()
    DESTROYED = auto()

    def __str__(self) -> str:
        if self == GridSpace.EMPTY:
            return '\033[0;37mO\033[0m'
        elif self == GridSpace.OCCUPIED:
            return '\033[1;30mU\033[0m'
        elif self == GridSpace.MISS:
            return '\033[1;37m0\033[0m'
        elif self == GridSpace.HIT:
            return '\033[0;31mU\033[0m'
        else:
            return '\033[0;31mX\033[0m'

class Player(Enum):
    ONE = auto()
    TWO = auto()
    def other_player(self) -> 'Player':
        '''Returns the other player for self.'''
        return Player.ONE if self == Player.TWO else Player.TWO

class Ship:
    '''A classic Battleship ship with a given size.'''
    def __init__(self, size: int):
        self.size = size
        self.is_destroyed = False
        self.placed = False
        self.spaces_occupied = []
        self.hits = 0
    
    def set_destroyed(self, is_destroyed: bool) -> None:
        '''Updates the is_destroyed attribute.'''
        self.is_destroyed = is_destroyed

    def place(self, location: tuple[int, int, Orientation]):
        '''Updates instance variables to reflect the placement of the Ship at the given row and column with the given orientation.'''
        row, column, orientation = location

        if orientation == Orientation.ACROSS:
            self.spaces_occupied = [(row, column+pos) for pos in range(self.size)]
            self.placed = True
        elif orientation == Orientation.DOWN:
            self.spaces_occupied = [(row+pos, column) for pos in range(self.size)]
            self.placed = True

    def hit(self):
        '''Is called when the Ship is hit.'''
        self.hits += 1
        if self.hits >= self.size:
            self.set_destroyed(True)

    def __str__(self) -> str:
        if self.is_destroyed:
            return ' '.join([str(GridSpace.DESTROYED) for _ in range(self.size)])
        else:
            return ' '.join([str(GridSpace.OCCUPIED) for _ in range(self.size)])
        
    def __repr__(self) -> str:
        return f'Ship({self.size})'

class BattleshipGame:
    '''Implements the game logic for a game of Battleship.'''
    def __init__(self):
        self.player_one_board = [[GridSpace.EMPTY for __ in range(10)] for _ in range(10)]
        self.player_two_board = [[GridSpace.EMPTY for __ in range(10)] for _ in range(10)]
        self.player_one_ships = [Ship(5), Ship(4), Ship(3), Ship(3), Ship(2)]
        self.player_two_ships = [Ship(5), Ship(4), Ship(3), Ship(3), Ship(2)]
        self.turn = Player.ONE

    def get_player_boards(self) -> tuple[list[list[GridSpace]], list[list[GridSpace]]]:
        return (self.player_one_board, self.player_two_board)
        
    def place_ship(self, player: Player, ship_index: int, location: tuple[int, int, Orientation]):
        '''Places the ship_index-th Ship on the given player's board at the given row and column with the given orientation.'''
        row, column, orientation = location
        
        board = self.player_one_board if player == Player.ONE else self.player_two_board
        ship = self.player_one_ships[ship_index] if player == Player.ONE else self.player_two_ships[ship_index]

        # check if you can place ship there before placing it
        if orientation == Orientation.ACROSS:
            if not all([board[row][column+pos] == GridSpace.EMPTY for pos in range(ship.size)]):
                return
        elif orientation == Orientation.DOWN:
            if not all([board[row+pos][column] == GridSpace.EMPTY for pos in range(ship.size)]):
                return

        ship.place((row, column, orientation))
        #print(f'Placed ship at ({row}, {column}) with orientation {orientation}. Spaces occupied: {ship.spaces_occupied}')
        for coord in ship.spaces_occupied:
            board[coord[0]][coord[1]] = GridSpace.OCCUPIED

    def ship_at_position(self, player: Player, coordinates: tuple[int, int]) -> Ship:
        '''Returns the Ship object that is at the given row and column on the given player's board.'''
        row, column = coordinates
        
        ships = self.player_one_ships if player == Player.ONE else self.player_two_ships
        for ship in ships:
            if (row, column) in ship.spaces_occupied:
                return ship

    def attempt_strike(self, coordinates: tuple[int, int]) -> bool|None:
        '''Attempts a strike at the given row and column. Returns True if it was a hit. 
        Returns None if the coordinates have already been struck at.'''
        row, column = coordinates

        targeted_board = self.player_two_board if self.turn == Player.ONE else self.player_one_board
        if targeted_board[row][column] in (GridSpace.DESTROYED, GridSpace.HIT, GridSpace.MISS):
            raise ValueError(f'Given coordinates {coordinates} have already been struck.')
        elif targeted_board[row][column] == GridSpace.OCCUPIED:
            hit_ship: Ship = self.ship_at_position(self.turn.other_player(), (row, column))
            hit_ship.hit()
            if hit_ship.is_destroyed:
                for coord in hit_ship.spaces_occupied:
                    targeted_board[coord[0]][coord[1]] = GridSpace.DESTROYED
            else:
                targeted_board[row][column] = GridSpace.HIT
            self.turn = self.turn.other_player()
            return True
        else:
            self.turn = self.turn.other_player()
            targeted_board[row][column] = GridSpace.MISS
            return False
        
    def winner(self) -> Player|None:
        '''Returns the winner (of type Player) if there is one. Otherwise, returns None.'''
        if all([ship.is_destroyed for ship in self.player_one_ships]):
            return Player.TWO
        elif all([ship.is_destroyed for ship in self.player_two_ships]):
            return Player.ONE
        
    def __repr__(self) -> str:
        return f'BattleshipGame()'
    
    def __str__(self) -> str:
        output = '      Player 1\n'
        for row in self.player_one_board:
            for space in row:
                output += str(space) + ' '
            output += '\n'

        output += '\n      Player 2\n'
        for row in self.player_two_board:
            for space in row:
                output += str(space) + ' '
            output += '\n'
        return output
    
    def reset(self):
        '''Reset the game.'''
        self.player_one_board = [[GridSpace.EMPTY for __ in range(10)] for _ in range(10)]
        self.player_two_board = [[GridSpace.EMPTY for __ in range(10)] for _ in range(10)]
        self.player_one_ships = [Ship(5), Ship(4), Ship(3), Ship(3), Ship(2)]
        self.player_two_ships = [Ship(5), Ship(4), Ship(3), Ship(3), Ship(2)]
        self.turn = Player.ONE