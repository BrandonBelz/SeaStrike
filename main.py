from PySide6.QtGui import QHoverEvent, QFont
from PySide6.QtWidgets import (QApplication, QMainWindow,
                               QLabel, QPushButton, QWidget,
                               QGridLayout, QMessageBox)
from game_logic import *
from bot_logic import *
from PySide6.QtCore import Qt, QTimer

# StyleSheets for the QPushButtons of the Battleship grid
empty_stylesheet = 'background-color: rgb(50, 132, 245); height: 30px; width: 30px; border: 2px solid black;'
hit_stylesheet = 'background-color: rgb(50, 132, 245); color: red; height: 30px; width: 30px; border: 2px solid black;'
miss_stylesheet = 'background-color: rgb(50, 132, 245); color: white; height: 30px; width: 30px; border: 2px solid black;'
occupied_stylesheet = 'background-color: gray; height: 30px; width: 30px; border: 2px solid black'
opp_hit_stylesheet = 'background-color: gray; color: red; height: 30px; width: 30px; border: 2px solid black;'
aim_stylesheet = 'background-color: rgb(50, 132, 245); color: orange; height: 30px; width: 30px; border: 2px solid black;'
hover_ship_stylesheet = 'background-color: rgb(123, 244, 78); height: 30px; width: 30px; border: 2px solid black;'
invalid_hover_stylesheet = 'background-color: red; height: 30px; width: 30px; border: 2px solid black;'
hover_occupied_stylesheet = 'background-color: rgb(191, 128, 128); height: 30px; width: 30px; border: 2px solid black;'

class buttonWithID(QPushButton):
    def __init__(self, position: str, gui: 'BattleshipGUI'):
        super().__init__()
        self.position = position
        self.setText(' ')
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.installEventFilter(self)
        self.gui = gui
        self.setFixedSize(30, 30)
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)
        self.setFont(font)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            player = Player.ONE if self.position[4] == '1' else Player.TWO
            self.gui.change_orientation()
            self.gui.button_hover((int(self.position[0]), int(self.position[2]), player))
        else:
            super().mousePressEvent(event)

    def wheelEvent(self, event):
        player = Player.ONE if self.position[4] == '1' else Player.TWO
        self.gui.mouse_scroll(event)
        self.gui.button_hover((int(self.position[0]), int(self.position[2]), player))

    def eventFilter(self, obj, event):
        player = Player.ONE if self.position[4] == '1' else Player.TWO
        if isinstance(event, QHoverEvent):
            self.gui.button_hover((int(self.position[0]), int(self.position[2]), player), event)
            return True
        return False

class BattleshipGUI(QMainWindow):
    def __init__(self, size_num: int):
        super().__init__()
        self.setWindowTitle("SeaStrike")
        self.resize(600, 500)
        self.Player_1_Field: list[list[buttonWithID]] = []
        self.Player_2_Field: list[list[buttonWithID]] = []
        self.size_num = size_num
        self.game = BattleshipGame()
        self.orientation = Orientation.ACROSS
        self.virtual_player_2 = ComputerPlayer(self.game.player_two_board, self.game.player_one_board, self.game.player_one_ships)
        self.placed_ships = 0
        self.ships_indices_in_hand = [0, 1, 2, 3, 4]
        self.ship_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.computer_strike)
        self.timer.setSingleShot(True)
        self.computer_place()
        
        
        # point of no return
        self.grid = QGridLayout()
        # sets up the foramting of the tic tac toe table interface
        
        self.title = QLabel("SeaStrike")
        font = QFont()
        font.setBold(True)
        font.setPointSize(30)
        self.title.setFont(font)
        font.setPointSize(15)
        self.last_strike = QLabel("Waiting for someone to make a move!")
        self.player_label_1 = QLabel("You")
        self.player_label_2 = QLabel("Player 2")
        self.player_label_1.setFont(font)
        self.player_label_2.setFont(font)
        font.setBold(False)
        font.setPointSize(11)
        self.turn_display = QLabel("Place your ships!")
        self.restart_button = QPushButton("Restart")
        self.last_strike.setFont(font)
        font.setBold(True)
        font.setPointSize(12)
        self.turn_display.setFont(font)
        self.restart_button.setFont(font)
        self.player_label_1.setAlignment(Qt.AlignCenter)
        self.player_label_2.setAlignment(Qt.AlignCenter)
        self.title.setAlignment(Qt.AlignCenter)
        self.last_strike.setAlignment(Qt.AlignCenter)
        self.turn_display.setAlignment(Qt.AlignCenter)
        
        info_box = QWidget()
        info_box.setStyleSheet('QWidget {border: 2px solid white;} QPushButton {border: 2px outset gray;} QLabel {border: none;}')
        info_layout = QGridLayout()
        info_layout.addWidget(self.restart_button, 0, 2, 1, 2)
        info_layout.addWidget(self.last_strike, 3, 0, 1, 6)
        info_layout.addWidget(self.turn_display, 1, 0, 1, 6)
        info_box.setLayout(info_layout)
        self.grid.addWidget(info_box, 2, 12, 4, 6)

        self.restart_button.clicked.connect(self.restart)
        
        self.grid.addWidget(self.title, 0, 12, 1, 6)
        self.grid.addWidget(self.player_label_1, 1, 3, 1, 4)
        self.grid.addWidget(self.player_label_2, 1, 22, 1, 4)

        # make the table of buttons for player 1's board
        self.game.turn = Player.ONE
        for row_1 in range(self.size_num):
            self.Player_1_Field.append([])
            for column_1 in range(self.size_num):
                
                button = buttonWithID(str(row_1) + ' ' + str(column_1) + ' 1', self)
                button.clicked.connect(self.player_strikeORplace)
                button.setEnabled(True)
                self.Player_1_Field[row_1].append(button)
                self.grid.addWidget(button, row_1 + 2, column_1, 1, 1)

        # make the table of buttons for player 2's board
       
        for row_2 in range(self.size_num):
            self.Player_2_Field.append([])
            for column_2 in range(self.size_num):
                button = buttonWithID(str(row_2) + ' ' + str(column_2) + ' 2', self)
                button.clicked.connect(self.player_strikeORplace)
                button.setEnabled(False)
                self.Player_2_Field[row_2].append(button)
                self.grid.addWidget(button, row_2 + 2, column_2 + 19, 1, 1)  
        

        self.update_screen()


        panel = QWidget()
        panel.setLayout(self.grid)
        self.setCentralWidget(panel)
        
    def player_strikeORplace(self):
        #tell the console what board and where it is getting striked
        coordinate_tuple = (int(self.sender().position[0]), int(self.sender().position[2]))
        if self.placed_ships < 5:
            if self.can_place_ship_at_coordinates(coordinate_tuple):
                self.game.place_ship(self.game.turn, self.ships_indices_in_hand.pop(self.ship_index), (int(self.sender().position[0]), int(self.sender().position[2]), self.orientation) )
                self.placed_ships += 1
                self.ship_index = 0
                if self.placed_ships == 5:
                    self.turn_display.setText('It is your turn!')
                    for row_num, row in enumerate(self.Player_1_Field):
                        for col_num, button in enumerate(row):
                            button.setEnabled(False)
                            self.Player_2_Field[row_num][col_num].setEnabled(True)
                self.update_screen()
        elif self.turn_display.text() == 'It is your turn!':
            result = 'hit' if self.game.attempt_strike(coordinate_tuple) else 'miss'
            self.sender().setEnabled(False)
            self.update_screen()
            if self.win_check():
                return
            self.last_strike.setText(f'You shot at {coordinate_tuple} and it was a {result}')
            self.turn_display.setText('It is Player 2\'s Turn')
            self.timer.start(random()*1500 + 1500)
        
    def win_check(self) -> bool:
        if self.game.winner() == Player.ONE:
            alert = QMessageBox()
            alert.setText('You won!')
            alert.setInformativeText('Would you like to play again?')
            alert.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            if alert.exec() == QMessageBox.Yes:
                self.restart()
            else:
                for row in self.Player_2_Field:
                    for button in row:
                        button.setDisabled(True)
            return True
        elif self.game.winner() == Player.TWO:
            alert = QMessageBox()
            alert.setText('You lost!')
            alert.setInformativeText('Would you like to play again?')
            alert.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            if alert.exec() == QMessageBox.Yes:
                self.restart()
            else:
                for row in self.Player_2_Field:
                    for button in row:
                        button.setDisabled(True)
            return True
        return False
            
    def can_place_ship_at_coordinates(self, coordinates: tuple[int, int]) -> bool:
        ship_size = self.game.player_one_ships[self.ships_indices_in_hand[self.ship_index]].size
        if self.orientation == Orientation.ACROSS:
            if coordinates[1] + ship_size <= 10 and\
                all([self.game.player_one_board[coordinates[0]][coordinates[1] + pos] == GridSpace.EMPTY for pos in range(ship_size)]):
                return True
            else:
                return False
        else:
            if coordinates[0] + ship_size <= 10 and\
                all([self.game.player_one_board[coordinates[0] + pos][coordinates[1]] == GridSpace.EMPTY for pos in range(ship_size)]):
                return True
            else:
                return False

    def update_screen(self):
        for row_num, row in enumerate(self.game.get_player_boards()[1]):
            for col_num, space in enumerate(row):
                if space == GridSpace.DESTROYED:
                    self.Player_2_Field[row_num][col_num].setText('X')
                    self.Player_2_Field[row_num][col_num].setStyleSheet(hit_stylesheet)
                if space == GridSpace.MISS:
                    self.Player_2_Field[row_num][col_num].setText('O')
                    self.Player_2_Field[row_num][col_num].setStyleSheet(miss_stylesheet)
                if space == GridSpace.HIT:
                    self.Player_2_Field[row_num][col_num].setText('O')
                    self.Player_2_Field[row_num][col_num].setStyleSheet(hit_stylesheet)
                if space == GridSpace.EMPTY or space == GridSpace.OCCUPIED:
                    self.Player_2_Field[row_num][col_num].setStyleSheet(empty_stylesheet)
                    self.Player_2_Field[row_num][col_num].setText(' ')
        for row_num, row in enumerate(self.game.get_player_boards()[0]):
            for col_num, space in enumerate(row):
                if space == GridSpace.DESTROYED:
                    self.Player_1_Field[row_num][col_num].setText('X')
                    self.Player_1_Field[row_num][col_num].setStyleSheet(opp_hit_stylesheet)
                if space == GridSpace.MISS:
                    self.Player_1_Field[row_num][col_num].setText('O')
                    self.Player_1_Field[row_num][col_num].setStyleSheet(miss_stylesheet)
                if space == GridSpace.HIT:
                    self.Player_1_Field[row_num][col_num].setText('O')
                    self.Player_1_Field[row_num][col_num].setStyleSheet(opp_hit_stylesheet)
                if space == GridSpace.OCCUPIED:
                    self.Player_1_Field[row_num][col_num].setText(' ')
                    self.Player_1_Field[row_num][col_num].setStyleSheet(occupied_stylesheet)
                if space == GridSpace.EMPTY:
                    self.Player_1_Field[row_num][col_num].setText(' ')
                    self.Player_1_Field[row_num][col_num].setStyleSheet(empty_stylesheet)

    def computer_place(self):
        for pos, ship in enumerate(self.game.player_two_ships):
            self.game.place_ship(Player.TWO, pos, self.virtual_player_2.place_ship(ship))

    def computer_strike(self):
        coordinate_tuple = self.virtual_player_2.strike_coordinates()
        result = 'hit' if self.game.attempt_strike(coordinate_tuple) else 'miss'
        self.virtual_player_2.update_weights()
        print(self.virtual_player_2._targets)
        self.update_screen()
        if self.win_check():
            return
        self.last_strike.setText(f'Player 2 shot at {coordinate_tuple} and it was a {result}')
        self.turn_display.setText('It is your turn!')

    def restart(self):
        #resets the game to ground zero, as if you never just ran the file for the first time
        #lets you know the game was actually restarted
        if QMessageBox.question(self, 'Restart game', 'Are you sure you want to restart? You will lose this game.') == QMessageBox.Yes:
            self.turn_display.setText("Place your ships!")
            self.last_strike.setText('Waiting for someone to make a move!')

            for row_num, row in enumerate(self.game.get_player_boards()[1]):
                for col_num, space in enumerate(row):
                    self.Player_2_Field[row_num][col_num].setEnabled(False)
            for row_num, row in enumerate(self.game.get_player_boards()[0]):
                for col_num, space in enumerate(row):
                    self.Player_1_Field[row_num][col_num].setEnabled(True)
            self.game.reset()
            self.virtual_player_2 = ComputerPlayer(self.game.player_two_board, self.game.player_one_board, self.game.player_two_ships)
            self.computer_place()
            self.update_screen()
            self.placed_ships = 0
            self.ships_indices_in_hand = [0, 1, 2, 3, 4]

    def mouse_scroll(self, event) -> bool:
        if event.angleDelta().y() < 0:
            if self.ship_index >= len(self.ships_indices_in_hand) - 1:
                self.ship_index = 0
            else:
                self.ship_index += 1
        elif event.angleDelta().y() > 0:
            if self.ship_index == 0:
                self.ship_index = len(self.ships_indices_in_hand) - 1
            else:
                self.ship_index -= 1
              
    def button_hover(self, position: tuple[int, int, Player], event: QHoverEvent=None):
        # mouse hover enter event
        if event == None or event.type() == 129:
            if self.placed_ships < 5:
                ship_size = self.game.player_one_ships[self.ships_indices_in_hand[self.ship_index]].size
                if position[2] == Player.ONE and self.can_place_ship_at_coordinates(position[:2]):
                    for row_num, row in enumerate(self.Player_1_Field):
                        for col_num, button in enumerate(row):
                            if self.game.player_one_board[row_num][col_num] == GridSpace.EMPTY:
                                button.setStyleSheet(empty_stylesheet)
                    for pos in range(ship_size):
                        if self.orientation == Orientation.ACROSS:
                            self.Player_1_Field[position[0]][position[1] + pos].setStyleSheet(hover_ship_stylesheet)
                        elif self.orientation == Orientation.DOWN:
                            self.Player_1_Field[position[0] + pos][position[1]].setStyleSheet(hover_ship_stylesheet)
                elif position[2] == Player.ONE:
                    for row_num, row in enumerate(self.Player_1_Field):
                        for col_num, button in enumerate(row):
                            if self.game.player_one_board[row_num][col_num] == GridSpace.EMPTY:
                                button.setStyleSheet(empty_stylesheet)
                    for pos in range(ship_size):
                        if self.orientation == Orientation.ACROSS:
                            if position[1] + pos <= 9:
                                if self.game.player_one_board[position[0]][position[1] + pos] == GridSpace.EMPTY:
                                    self.Player_1_Field[position[0]][position[1] + pos].setStyleSheet(invalid_hover_stylesheet)
                                elif self.game.player_one_board[position[0]][position[1] + pos] == GridSpace.OCCUPIED:
                                    self.Player_1_Field[position[0]][position[1] + pos].setStyleSheet(hover_occupied_stylesheet)
                            else:
                                break
                        elif self.orientation == Orientation.DOWN:
                            if position[0] + pos <= 9:
                                if self.game.player_one_board[position[0] + pos][position[1]] == GridSpace.EMPTY:
                                    self.Player_1_Field[position[0] + pos][position[1]].setStyleSheet(invalid_hover_stylesheet)
                                elif self.game.player_one_board[position[0] + pos][position[1]] == GridSpace.OCCUPIED:
                                    self.Player_1_Field[position[0] + pos][position[1]].setStyleSheet(hover_occupied_stylesheet)
                            else:
                                break
            else:
                if self.game.player_two_board[position[0]][position[1]] in (GridSpace.EMPTY, GridSpace.OCCUPIED) and position[2] == Player.TWO and self.game.turn == Player.ONE:
                    self.Player_2_Field[position[0]][position[1]].setText('+')
                    self.Player_2_Field[position[0]][position[1]].setStyleSheet(aim_stylesheet)
        # mouse hover leave event
        elif event.type() == 128:
            if self.placed_ships < 5:
                if position[2] == Player.ONE:
                    ship_size = self.game.player_one_ships[self.ships_indices_in_hand[self.ship_index]].size
                    for row_num, row in enumerate(self.Player_1_Field):
                        for col_num, button in enumerate(row):
                            if self.game.player_one_board[row_num][col_num] == GridSpace.EMPTY:
                                button.setStyleSheet(empty_stylesheet)
                            elif self.game.player_one_board[row_num][col_num] == GridSpace.OCCUPIED:
                                button.setStyleSheet(occupied_stylesheet)
            else:
                if self.game.player_two_board[position[0]][position[1]] in (GridSpace.EMPTY, GridSpace.OCCUPIED) and position[2] == Player.TWO:
                    self.Player_2_Field[position[0]][position[1]].setText(' ')
                    self.Player_2_Field[position[0]][position[1]].setStyleSheet(empty_stylesheet)

    def change_orientation(self):
        self.orientation = self.orientation.other_orientation()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.change_orientation()

if __name__ == "__main__":
    app = QApplication()
    ttt_list = BattleshipGUI(10)
    ttt_list.show()
    app.exec()