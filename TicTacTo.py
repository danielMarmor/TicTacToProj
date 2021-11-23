import random
from enum import Enum

# consts (global settings)
# in fact -- possible more than 2 players! (all you need is change this constant)
MAX_NUM_OF_PLAYERS = 2
EMPTY_CELL = '_'
HUMAN = 'H',
COMPUTER = 'C'
# player_id = player serial number in one round of game
# player_type = computer/human
# player_sign = game sign on the tic tac to board (o, x ,....)


class Player:
    def __init__(self, player_id, player_name, player_type, player_sign):
        self.player_id = player_id
        self.player_name = player_name
        self.player_type = player_type
        self.player_sign = player_sign


# **************************************************
class Game:
    def __init__(self, size, is_forecast_victory):
        self.num_of_players = MAX_NUM_OF_PLAYERS
        self.size = size
        self.max_range = self.size**2
        self.empty_cell_sign = EMPTY_CELL
        self.board = self.get_initial_board()
        self.players = []
        self.current_player_id = None
        self.is_forecast_victory = is_forecast_victory

    def __str__(self):
        board_str = ''
        for row in range(0, self.size):
            for col in range(0, self.size):
                board_str += f'{self.board[row][col]}  '
            board_str += '\n'
        return board_str

    def get_initial_board(self):
        board = []
        for i in range(0, self.size):
            row = []
            for j in range(0, self.size):
                row.append(self.empty_cell_sign)
            board.append(row)
        return board

    # init players in game
    def register_players(self):
        print('Registering Players')
        for i in range(0, self.num_of_players):
            player_id = i + 1
            print(f'Player Number {player_id} ***')
            # player name
            while True:
                player_name = input('Enter Player Name: ').strip()
                is_valid_name = self.is_valid_name(player_name)
                if is_valid_name:
                    break
            # player type
            while True:
                player_type = input('Enter Player Type (computer-C, Human-H) :').strip()
                is_valid_player_type = self.is_valid_player_type(player_type)
                if is_valid_player_type:
                    break
            # sign = (x, o)
            while True:
                player_sign = input('Enter Player Game Sign: (o, x) ').strip()
                is_game_valid_sign = self.is_game_valid_sign(player_sign)
                if is_game_valid_sign:
                    break
            new_player = Player(player_id, player_name, player_type, player_sign)
            self.players.append(new_player)

    #  game engine
    def start(self):
        active_game = True
        while active_game:
            # iterate all registered players in game
            for i in range(0, self.num_of_players):
                self.print_board()
                player = self.players[i]
                self.current_player_id = i + 1
                #  victory forecast  if COMPUTER ==> select forcast position (if winning)
                # if HUMAN ==> notify only. selection done by player
                forc_vic_pos = self.get_victory_position(self.current_player_id)
                if forc_vic_pos is not None:
                    self.notify_victory_position(forc_vic_pos, player)
                position = None
                if player.player_type == 'H':  # HUMAN
                    position = self.get_human_position(player)
                else:   # COMPUTER
                    position = self.get_comp_position(player, forc_vic_pos)
                self.update_board(player.player_sign, position)
                is_victory = self.check_victory(self.current_player_id)
                if is_victory:
                    active_game = False
                    self.print_board()
                    print(f'{player.player_name}, You are the Winner!')
                    break
                is_draw = self.check_draw()
                if is_draw:
                    active_game = False
                    self.print_board()
                    print('Draw!')
                    break

    # for player type == HUMAN
    def get_human_position(self, player: Player):
        position = None
        while True:
            pos_str = input(f'{player.player_name} ({player.player_sign}), '
                            f' Select Position(1- {self.max_range}): ').strip()
            is_valid_position = self.is_valid_position(pos_str)
            if is_valid_position:
                position = int(pos_str)
                break
        return position

    # for player type == COMPUTER
    def get_comp_position(self, player: Player, victory_for_pos):
        position = None
        if victory_for_pos is not None:
            position = victory_for_pos
            print(f'{player.player_name}({player.player_sign}) selected position number {position}')
            return position
        while True:
            position = random.randint(1, self.max_range)
            is_exists_pos = self.is_exists_position(position)
            if not is_exists_pos:
                break
        print(f'{player.player_name}({player.player_sign}) selected position number {position}')
        return position

    def get_victory_position(self, player_id):
        if not self.is_forecast_victory:
            return None
        player_index = player_id - 1
        player = self.players[player_index]
        player_sign = player.player_sign
        # check rows
        for i in range(0, self.size):
            row_cells = [cell for cell in self.board[i] if cell in (player_sign, EMPTY_CELL)]
            empty_cells = [(i, row_cells.index(cell)) for cell in row_cells if cell == EMPTY_CELL]
            is_victory_row = len(row_cells) == self.size and len(empty_cells) == 1
            if is_victory_row:
                row_index = empty_cells[0][0]
                col_index = empty_cells[0][1]
                victory_position = self.get_matrix_position_by_indexes(row_index, col_index)
                return victory_position
        # check columns
        for j in range(0, self.size):
            col_cells = [row[j] for row in self.board if row[j] in (player_sign, EMPTY_CELL)]
            empty_cells = [(col_cells.index(cell), j) for cell in col_cells if cell == EMPTY_CELL]
            is_victory_column = len(col_cells) == self.size and len(empty_cells) == 1
            if is_victory_column:
                row_index = empty_cells[0][0]
                col_index = empty_cells[0][1]
                victory_position = self.get_matrix_position_by_indexes(row_index, col_index)
                return victory_position
        # check diagonals
        # INDEXES IN DIAGONAL LTR
        ltr_diag = [index for index in range(0, self.size) if self.board[index][index] == player.player_sign]
        ltr_diag_empty = [index for index in range(0, self.size) if self.board[index][index] == EMPTY_CELL]
        is_victory_ltr_diag = len(ltr_diag) == (self.size - 1) and len(ltr_diag_empty) == 1
        if is_victory_ltr_diag:
            empty_index = ltr_diag_empty[0]
            victory_position = self.get_matrix_position_by_indexes(empty_index, empty_index)
            return victory_position
        # INDEXES IN DIAGONAL RTL
        rtl_diag = [(index, self.size - 1 - index) for index in range(0, self.size)
                        if self.board[index][self.size - 1 - index] == player_sign]
        rtl_diag_empty = [(index, self.size - 1 - index) for index in range(0, self.size)
                        if self.board[index][self.size - 1 - index] == EMPTY_CELL]
        is_victory_rtl_diag = len(rtl_diag) == (self.size - 1) and len(rtl_diag_empty) == 1
        if is_victory_rtl_diag:
            row_index = rtl_diag_empty[0][0]
            col_index = rtl_diag_empty[0][1]
            victory_position = self.get_matrix_position_by_indexes(row_index, col_index)
            return victory_position
        return None

    # set player selection on board
    def update_board(self, player_sign, position):
        row = (position - 1) // self.size
        column = (position - 1) % self.size
        self.board[row][column] = player_sign

    def check_victory(self, player_id):
        player_index = player_id - 1
        player = self.players[player_index]
        player_sign = player.player_sign
        # check rows
        for row in self.board:
            player_cells = [cell for cell in row if cell == player_sign]
            if len(player_cells) == self.size:
                return True
        # check columns
        for j in range(0, self.size):
            player_cells = [row[j] for row in self.board if row[j] == player_sign]
            if len(player_cells) == self.size:
                return True
        # check diagonals
        ltr_diagonal = [index for index in range(0, self.size) if self.board[index][index] == player_sign]
        if len(ltr_diagonal) == self.size:
            return True
        rtl_diagonal = [index for index in range(0, self.size)
                        if self.board[index][self.size - 1 - index] == player_sign]
        if len(rtl_diagonal) == self.size:
            return True
        return False

    def check_draw(self):
        cells = [cell for row in self.board for cell in row]
        if all(cell != EMPTY_CELL for cell in cells):
            return True
        return False

    def get_matrix_position_by_indexes(self, row_index, col_index):
        matrix_index = ((self.size * row_index) + col_index)
        matrix_position = matrix_index + 1
        return matrix_position

    def is_exists_position(self, position):
        row = (position - 1) // self.size
        column = (position - 1) % self.size
        if self.board[row][column] != EMPTY_CELL:
            return True
        return False

    def notify_victory_position(self, position, player):
        print(f'{player.player_name} ({player.player_sign}) - You are abount to win - Victory Position: {position}!')

    def print_board(self):
        print(self)

    # validations
    def is_valid_name(self, name: str):
        if len(name) == 0:
            print('Empty Name!')
            return False
        if any(p.player_name == name for p in self.players):
            print('The Name allready exists for other player!')
            return False
        return True

    def is_valid_player_type(self, player_type: str):
        if player_type not in ('C', 'H'):
            print('Please Enter Valid Player Type!')
            return False
        return True

    def is_game_valid_sign(self, player_sign: str):
        if player_sign not in ('o', 'x'):
            print('Please Enter Valid Game Sign!')
            return False
        if any(p.player_sign == player_sign for p in self.players):
            print('Sign allready exists for other player!')
            return False
        return True

    def is_valid_position(self, pos_str: str):
        if len(pos_str) == 0:
            return False
        if not pos_str.isnumeric():
            print('Position Must be a Number')
            return False
        position = int(pos_str)
        if position < 1 or position > self.max_range:
            print('Out of Range!')
            return False
        is_exists_pos = self.is_exists_position(position)
        if is_exists_pos:
            print('Position allready selected!')
            return False
        return True


#  ***********************************************
def is_game_selection_valid(new_game: str):
    if new_game not in ['0', '1']:
        print('No Valid Selection!')
        return False
    return True


def is_board_size_valid(size_str: str):
    if len(size_str) == 0:
        print('Enter Valid size!')
        return False
    if not size_str.isnumeric():
        print('Must Be Numeric. Enter Valid size!')
        return False
    return True


def is_forecast_vic_valid(for_vic_str: str):
    if for_vic_str not in ['0', '1']:
        print('Enter Valid Selection!')
        return False
    return True


def manage_game():
    while True:
        game_selection = None
        while True:
            game_selection = input('New Game?  Yes - 1, No - 0: ').strip()
            is_selection_valid = is_game_selection_valid(game_selection)
            if is_selection_valid:
                break
        if game_selection == '0':
            break
        size = None
        while True:
            size_str = input('Enter Board Size: ').strip()
            is_size_valid = is_board_size_valid(size_str)
            if is_size_valid:
                size = int(size_str)
                break
        is_forecast_victory = None
        while True:
            forecast_victory_str = input('Is Forecast Victory? (Yes - 1, No - 0): ').strip()
            is_for_vic_valid = is_forecast_vic_valid(forecast_victory_str)
            if is_for_vic_valid:
                is_forecast_victory = True if forecast_victory_str == '1' else False
                break
        # create new game
        game = Game(size, is_forecast_victory)
        game.register_players()
        game.start()
    print('Thank You!')


def main():
    manage_game()


main()

