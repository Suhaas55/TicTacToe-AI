from typing import Optional
from enum import Enum

Square = int


class Symbol(Enum):
    CIRCLE = "O"
    CROSS = "X"
    EMPTY = "#"


class Board:
    """Responsible for storing current state, making and validating moves, and updating the game

    Attributes:
        first_move (Symbol): Symbol to make the first move, alternate after every match
        p1_score (int): First player's score
        p2_score (int): Second player's score
        size (int): Board dimension     
        squares (dict[[int,int],Square]): Container to convert row,col into Square
        table (list[Symbol]): Container to store the current board state, use Square as index 
        turn (Symbol): Current turn to make a move
        win_conditions (list[list[Square]]): All possible connections to win the game
    """

    def __init__(self, size: int = 3):
        """Creating a board with given size

        Args:
            size (int, optional): Board dimension
        """
        self.size: int = size
        self.p1_score: int = 0
        self.p2_score: int = 0

        self.squares: dict[[int, int], Square] = self.get_squares()
        self.table: list[Symbol] = self.get_table()
        self.win_conditions: list[list[Square]] = self.get_win_conditions()

        self.first_move: Symbol = Symbol.CIRCLE
        self.turn: Symbol = self.first_move

    def get_win_conditions(self) -> list[list[Square]]:
        """Get all winning connections, for all board sizes

        Returns:
            list[list[Square]]: list of rows, cols, diagonals 
        """
        rows, cols = self.get_rows_cols()
        diagonals = self.get_diagonals()
        return rows + cols + diagonals

    def get_squares(self) -> dict[[int, int], Square]:
        """Create a dictionary containing all squares

        Returns:
            dict[[int, int], Square]: (row,col) as key, square name as value
        """
        return {(r, c): r * self.size + c
                for r in range(self.size) for c in range(self.size)}

    def get_table(self) -> list[Symbol]:
        """Table to store the current board state

        Returns:
            list[Symbol]: List of tiles filled with empty Symbol
        """
        return [Symbol.EMPTY for _ in range(self.size**2)]

    def get_rows_cols(self) -> tuple[list[Square], list[Square]]:
        """Group squares into corresponding rows and columns

        Returns:
            tuple[list[Square], list[Square]]: lists of rows and cols
        """
        rows: list[list[Square]] = [[] for _ in range(self.size)]
        columns: list[list[Square]] = [[] for _ in range(self.size)]
        for index, square in self.squares.items():
            r, c = index
            rows[r].append(square)
            columns[c].append(square)
        return rows, columns

    def get_diagonals(self) -> list[list[Square]]:
        """Calculate diagonal squares for all board sizes

        Returns:
            list[list[Square]]: list of diagonals
        """
        diagonals: list[list] = [[], []]
        i = 0
        j = self.size - 1
        for _ in range(self.size):
            diagonals[0].append(i)
            diagonals[1].append(j)
            i += self.size + 1
            j += self.size - 1
        return diagonals

    @property
    def empty_squares(self) -> list[Square]:
        """Get all empty squares

        Returns:
            list[Square]: list of empty squres
        """
        return [
            square for square in self.squares.values() if self.is_empty(square)
        ]

    def reset(self):
        """Reset the board and change the turn
        """
        self.table = self.get_table()
        self.first_move = Symbol.CROSS if self.first_move == Symbol.CIRCLE else Symbol.CIRCLE
        self.turn = self.first_move

    def square_pos(self, square: Square) -> Optional[tuple[int, int]]:
        """Get row, col of the square

        Args:
            square (Square): Square number

        Returns:
            Optional[tuple[int, int]]: (row, col) if square exists
        """
        for pos, sq in self.squares.items():
            if sq == square:
                return pos
        return None

    def square_name(self, row: int, col: int) -> Square:
        """Convert row, col into square

        Returns:
            Square: corresponding number
        """
        return self.squares[(row, col)]

    def square_value(self, square: Square) -> Symbol:
        """Get the symbol of the square

        Args:
            square (Square): Square name

        Returns:
            Symbol: Symbol of the square
        """
        return self.table[square]

    def is_empty(self, square: Square) -> bool:
        """Check if square is empty

        Args:
            square (Square): square name

        Returns:
            bool: True if empty symbol
        """
        return self.table[square] == Symbol.EMPTY

    def get_connection(self, winner: bool=False, gui: bool=True) -> list[Square]:
        """Check for connected tiles,returns the list of connected squares
        So just collecting all winning lines instead of returning the first one. 
        This is just for us to choose the appropriate win based on the current turn and flags.
        """
        connections=[]
        for row in self.win_conditions:
            checklist = []
            for square in row:
                if self.is_empty(square):
                    continue
                checklist.append(self.square_value(square))
            if len(checklist) == self.size and len(set(checklist)) == 1:
                connections.append(row)
        if not connections:
            return []
        elif len(connections) == 1:
            return connections[0]
        else:
            # When multiple connections are existing then to decide based on current turn and flags.
            if winner or gui:
                if self.turn == self.square_value(connections[0][0]):
                    return connections[1]
                else:
                    return connections[0]
            else:
                if self.turn == self.square_value(connections[0][0]):
                    return connections[0]
                else:
                    return connections[1]

    def is_draw(self) -> bool:
        """Check for draw

        Returns:
            bool: True if board is filled and no connection
        """
        if len(self.empty_squares) == 0 and len(self.get_connection()) == 0:
            return True
        return False
    
    def final_move(self, gui: bool = False) -> bool:
        """Checking if the current player/opponent are able too get a win with an extra move
           after a three in a row has been formed by the pther palyer/bot.
            returns bool: True if an extra winning move is possible, false otherwise.
        """
        connection = self.get_connection(gui=gui)
        # If the connection belongs to the current turn, then an extra move isn't really applicable.
        if connection and self.turn == self.square_value(connection[0]):
            return False 
        # Testing every empty square to see if placing the symbol results in a win.
        for square in self.empty_squares:
            self.push(square, self.turn)
            if self.winnerHelper() == self.turn:
                self.undo(square)
                return True
            self.undo(square)
        return False
    
    def winnerHelper(self, winner: bool = False) -> Optional[Symbol]:
        """For determinging a temporary winner based on the current board state,
           ignoring the extra move possibility.
        retuerns the winning symbol if a connection exists and if not nothing
        """
        connection = self.get_connection(winner=winner, gui=False)
        if not connection:
            return None
        return self.square_value(connection[0])

    def winner(self) -> Optional[Symbol]:
        """Get the winner of the match

        Returns:
            Optional[Symbol]: Symbol of connected tiles if exists
        
        connection = self.get_connection()
        if len(connection) == 0:
            return None
        elif self.square_value(connection[0]) == Symbol.CIRCLE:
            return Symbol.CIRCLE
        else:
            return Symbol.CROSS"""
        #this is for detrming the final winner. the wining connections only valid if 
        # opponent cant counter with extra move in this wild tictactoe game.
        temp_winner = self.winnerHelper(winner=True)
        if temp_winner and not self.final_move():
            return temp_winner
        return None



    def is_gameover(self) -> bool:
        """Check for gameover

        Returns:
            bool: True if there's winner or draw
        """
        return self.winner() is not None or self.is_draw()

    def _update(self):
        """Update the turn and score if there's winner
        """
        self.turn = Symbol.CROSS if self.turn == Symbol.CIRCLE else Symbol.CIRCLE
        if self.winner() == Symbol.CIRCLE:
            self.p1_score += 1
        elif self.winner() == Symbol.CROSS:
            self.p2_score += 1

    def push(self, square: Square, value: Symbol):
        """Store the symbol into the square

        Args:
            square (Square): square name
            value (Symbol): symbol
        """
        self.table[square] = value

    def undo(self, square: Square):
        """Change the square's value to empty

        Args:
            square (Square): square name
        """
        self.table[square] = Symbol.EMPTY

    def move(self, square: Square):
        """Mark the square with symbol of current turn if valid and update the board

        Args:
            square (Square): square name
        """
        if square >= self.size**2 or square < 0 or not self.is_empty(square):
            print("Invalid move!")
            return
        self.push(square, self.turn)
        self._update()

    def print(self):
        """Represent the board in string
        """
        turn = "Player 1" if self.turn == Symbol.CIRCLE else "Player 2"
        if self.winner():
            print("Match Over!")
            print("*" * 13)
        else:
            print("*" * 15)
            print("Turn->> ", turn)
            print('-' * (self.size * 5))
        for index, square in self.squares.items():
            r, c = index
            sign = square if self.is_empty(
                square) else "O" if self.square_value(
                    square) == Symbol.CIRCLE else "X"
            print(' |', end=' ')
            print(sign, end='')
            if c == self.size - 1:
                print(' |')
                print('-' * (self.size * 5))
        print('-' * (self.size * 5))
        print()


if __name__ == "__main__":
    # CLI game for two player mode
    board = Board()
    print("Tic Tac Toe - Duel")
    print("##################")
    board.print()
    running = True
    while running:
        turn = "Player 1" if board.turn == Symbol.CIRCLE else "Player 2"
        move = int(input(f"Enter {turn} 's move: "))
        board.move(move)
        board.print()
        if board.is_gameover():
            running = False
    if board.is_draw():
        print("Draw! What a great match!")
    else:
        print("Player 1" if board.winner() == Symbol.CIRCLE else "Player 2",
              " Wins....!")
