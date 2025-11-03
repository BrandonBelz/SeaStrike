from game_logic import Ship, GridSpace, Orientation
from random import randrange, random


def weighted_choice(options: list, weights: list[float]) -> int:
    """Returns the index of a random choice using given weights.
    https://scaron.info/blog/python-weighted-choice.html"""
    total_weights = sum(weights)
    x = random() * total_weights
    for pos in range(len(weights)):
        if weights[pos] >= x:
            return options[pos]
        x -= weights[pos]


def is_type_at_coordinates(
    board: list[list[GridSpace]], coordinates: tuple[int, int], space_type: GridSpace
) -> bool:
    """Returns True if the value of board[coordinates[0]][coordinates[1]] is space_type. Returns False if it is a different space_type
    or if the coordinates are out of range.
    >>> is_type_at_coordinates([[GridSpace.EMPTY]], (0, 0), GridSpace.EMPTY)
    True
    >>> is_type_at_coordinates([[GridSpace.EMPTY]], (0, 0), GridSpace.HIT)
    False
    >>> is_type_at_coordinates([[GridSpace.EMPTY]], (0, 1), GridSpace.EMPTY)
    False"""
    try:
        return board[coordinates[0]][coordinates[1]] == space_type
    except:
        return False


class ComputerPlayer:
    def __init__(
        self,
        own_gameboard: list[list[GridSpace]],
        opponent_gameboard: list[list[GridSpace]],
        opponent_ships: list[Ship],
    ):
        self.own_gameboard = own_gameboard
        self.opponent_gameboard = opponent_gameboard
        self.opponent_ships = opponent_ships
        self._last_strike = ()
        self._targets = set()
        self.weights = [
            8.0,
            11.5,
            14.3,
            15.9,
            16.7,
            16.7,
            15.9,
            14.3,
            11.5,
            8.0,
            11.5,
            14.3,
            16.6,
            17.8,
            18.4,
            18.4,
            17.8,
            16.6,
            14.3,
            11.5,
            14.3,
            16.6,
            18.4,
            19.4,
            19.9,
            19.9,
            19.4,
            18.4,
            16.6,
            14.3,
            15.9,
            17.8,
            19.4,
            20.3,
            20.8,
            20.8,
            20.3,
            19.4,
            17.8,
            15.9,
            16.7,
            18.4,
            19.9,
            20.8,
            21.4,
            21.4,
            20.8,
            19.9,
            18.4,
            16.7,
            16.7,
            18.4,
            19.9,
            20.8,
            21.4,
            21.4,
            20.8,
            19.9,
            18.4,
            16.7,
            15.9,
            17.8,
            19.4,
            20.3,
            20.8,
            20.8,
            20.3,
            19.4,
            17.8,
            15.9,
            14.3,
            16.6,
            18.4,
            19.4,
            19.9,
            19.9,
            19.4,
            18.4,
            16.6,
            14.3,
            11.5,
            14.3,
            16.6,
            17.8,
            18.4,
            18.4,
            17.8,
            16.6,
            14.3,
            11.5,
            8.0,
            11.5,
            14.3,
            15.9,
            16.7,
            16.7,
            15.9,
            14.3,
            11.5,
            8.0,
        ]
        self.smallest_ship_size = 2

    def place_ship(self, ship: Ship) -> tuple[int, int, Orientation]:
        """Returns the position and orientation of a random valid placement of the given Ship."""
        while True:
            row = randrange(10)
            column = randrange(10)
            orientation = Orientation.ACROSS if randrange(2) == 0 else Orientation.DOWN

            if orientation == Orientation.ACROSS:
                if column + ship.size <= 10 and all(
                    [
                        self.own_gameboard[row][column + pos] == GridSpace.EMPTY
                        for pos in range(ship.size)
                    ]
                ):
                    return (row, column, orientation)
            elif orientation == Orientation.DOWN:
                if row + ship.size <= 10 and all(
                    [
                        self.own_gameboard[row + pos][column] == GridSpace.EMPTY
                        for pos in range(ship.size)
                    ]
                ):
                    return (row, column, orientation)

    def strike_coordinates(self) -> tuple[int, int]:
        """Returns coordinates of a valid strike. Uses different methods depending on the difficulty given when self was instantiated."""
        if len(self._targets) == 0:
            for ship in reversed(self.opponent_ships):
                if not ship.is_destroyed:
                    self.smallest_ship_size = ship.size
                    break
            options = []
            temp_weights = []
            for row in range(10):
                for column in range(10):
                    if (
                        column + row
                    ) % self.smallest_ship_size == 0 and self.opponent_gameboard[row][
                        column
                    ] in (
                        GridSpace.EMPTY,
                        GridSpace.OCCUPIED,
                    ):
                        options.append((row, column))
                        temp_weights.append(self.weights[row * 10 + column])
            if options == []:
                for row in range(10):
                    for column in range(10):
                        if self.opponent_gameboard[row][column] in (
                            GridSpace.EMPTY,
                            GridSpace.OCCUPIED,
                        ):
                            options.append((row, column))
                            temp_weights.append(self.weights[row * 10 + column])

            coords = weighted_choice(options, temp_weights)
            self._last_strike = coords
            if coords[0] > 9 or coords[0] < 0 or coords[1] > 9 or coords[1] < 0:
                raise IndexError(
                    "Invalid coordinates generated by ComputerPlayer using difficulty 3"
                )
            return coords
        else:
            result = self._targets.pop()
            self._last_strike = result
            if result[0] > 9 or result[0] < 0 or result[1] > 9 or result[1] < 0:
                raise IndexError(
                    f"Invalid coordinates {result} generated by ComputerPlayer using difficulty 3"
                )
            return result

    def update_weights(self):
        """Must be called after the strike coordinates have been handled by the game.
        Updates the ComputerPlayer's methods based on the results of the last strike."""
        if (
            self.opponent_gameboard[self._last_strike[0]][self._last_strike[1]]
            == GridSpace.HIT
        ):
            self._targets = set()
            if (
                is_type_at_coordinates(
                    self.opponent_gameboard,
                    (self._last_strike[0] - 1, self._last_strike[1]),
                    GridSpace.HIT,
                )
                or is_type_at_coordinates(
                    self.opponent_gameboard,
                    (self._last_strike[0] + 1, self._last_strike[1]),
                    GridSpace.HIT,
                )
                or is_type_at_coordinates(
                    self.opponent_gameboard,
                    (self._last_strike[0], self._last_strike[1] + 1),
                    GridSpace.HIT,
                )
                or is_type_at_coordinates(
                    self.opponent_gameboard,
                    (self._last_strike[0], self._last_strike[1] - 1),
                    GridSpace.HIT,
                )
            ):

                if is_type_at_coordinates(
                    self.opponent_gameboard,
                    (self._last_strike[0] - 1, self._last_strike[1]),
                    GridSpace.HIT,
                ) or is_type_at_coordinates(
                    self.opponent_gameboard,
                    (self._last_strike[0] + 1, self._last_strike[1]),
                    GridSpace.HIT,
                ):
                    for pos in range(self._last_strike[0] + 1, 10):
                        if self.opponent_gameboard[pos][self._last_strike[1]] in (
                            GridSpace.EMPTY,
                            GridSpace.OCCUPIED,
                        ):
                            self._targets.add((pos, self._last_strike[1]))
                            break
                        elif self.opponent_gameboard[pos][self._last_strike[1]] in (
                            GridSpace.MISS,
                            GridSpace.DESTROYED,
                        ):
                            break
                    for pos in range(self._last_strike[0] - 1, -1, -1):
                        if self.opponent_gameboard[pos][self._last_strike[1]] in (
                            GridSpace.EMPTY,
                            GridSpace.OCCUPIED,
                        ):
                            self._targets.add((pos, self._last_strike[1]))
                            break
                        elif self.opponent_gameboard[pos][self._last_strike[1]] in (
                            GridSpace.MISS,
                            GridSpace.DESTROYED,
                        ):
                            break

                if is_type_at_coordinates(
                    self.opponent_gameboard,
                    (self._last_strike[0], self._last_strike[1] + 1),
                    GridSpace.HIT,
                ) or is_type_at_coordinates(
                    self.opponent_gameboard,
                    (self._last_strike[0], self._last_strike[1] - 1),
                    GridSpace.HIT,
                ):
                    for pos in range(self._last_strike[1] + 1, 10):
                        if self.opponent_gameboard[self._last_strike[0]][pos] in (
                            GridSpace.EMPTY,
                            GridSpace.OCCUPIED,
                        ):
                            self._targets.add((self._last_strike[0], pos))
                            break
                        elif self.opponent_gameboard[self._last_strike[0]][pos] in (
                            GridSpace.MISS,
                            GridSpace.DESTROYED,
                        ):
                            break
                    for pos in range(self._last_strike[1] - 1, -1, -1):
                        if self.opponent_gameboard[self._last_strike[0]][pos] in (
                            GridSpace.EMPTY,
                            GridSpace.OCCUPIED,
                        ):
                            self._targets.add((self._last_strike[0], pos))
                            break
                        elif self.opponent_gameboard[self._last_strike[0]][pos] in (
                            GridSpace.MISS,
                            GridSpace.DESTROYED,
                        ):
                            break

            else:
                if self._last_strike[0] - 1 >= 0 and self.opponent_gameboard[
                    self._last_strike[0] - 1
                ][self._last_strike[1]] in (GridSpace.EMPTY, GridSpace.OCCUPIED):
                    self._targets.add((self._last_strike[0] - 1, self._last_strike[1]))
                if self._last_strike[0] + 1 <= 9 and self.opponent_gameboard[
                    self._last_strike[0] + 1
                ][self._last_strike[1]] in (GridSpace.EMPTY, GridSpace.OCCUPIED):
                    self._targets.add((self._last_strike[0] + 1, self._last_strike[1]))
                if self._last_strike[1] - 1 >= 0 and self.opponent_gameboard[
                    self._last_strike[0]
                ][self._last_strike[1] - 1] in (GridSpace.EMPTY, GridSpace.OCCUPIED):
                    self._targets.add((self._last_strike[0], self._last_strike[1] - 1))
                if self._last_strike[1] + 1 <= 9 and self.opponent_gameboard[
                    self._last_strike[0]
                ][self._last_strike[1] + 1] in (GridSpace.EMPTY, GridSpace.OCCUPIED):
                    self._targets.add((self._last_strike[0], self._last_strike[1] + 1))

        elif (
            self.opponent_gameboard[self._last_strike[0]][self._last_strike[1]]
            == GridSpace.MISS
        ):
            if self._last_strike[0] >= 1 and self.opponent_gameboard[
                self._last_strike[0] - 1
            ][self._last_strike[1]] in (GridSpace.OCCUPIED, GridSpace.EMPTY):
                self.weights[(self._last_strike[0] - 1) * 10 + self._last_strike[1]] = 0
            if self._last_strike[1] >= 1 and self.opponent_gameboard[
                self._last_strike[0]
            ][self._last_strike[1] - 1] in (GridSpace.OCCUPIED, GridSpace.EMPTY):
                self.weights[(self._last_strike[0]) * 10 + self._last_strike[1] - 1] = 0
            if self._last_strike[0] <= 8 and self.opponent_gameboard[
                self._last_strike[0] + 1
            ][self._last_strike[1]] in (GridSpace.OCCUPIED, GridSpace.EMPTY):
                self.weights[(self._last_strike[0] + 1) * 10 + self._last_strike[1]] = 0
            if self._last_strike[1] <= 8 and self.opponent_gameboard[
                self._last_strike[0]
            ][self._last_strike[1] + 1] in (GridSpace.OCCUPIED, GridSpace.EMPTY):
                self.weights[(self._last_strike[0]) * 10 + self._last_strike[1] + 1] = 0

        elif (
            self.opponent_gameboard[self._last_strike[0]][self._last_strike[1]]
            == GridSpace.DESTROYED
        ):
            self._targets = set()

    def __repr__(self) -> str:
        return f"ComputerPlayer()"


if __name__ == "__main__":
    from doctest import testmod

    testmod()
