from mpi4py import MPI # type: ignore
import numpy as np # type: ignore

# Define game class
class TicTacToeMPI:
    def __init__(self):
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()  # Rank of the current process
        self.size = self.comm.Get_size()  # Total number of processes
        
        # Board setup
        self.board = np.full(9, ' ', dtype=str)  # 3x3 board
        self.last_move = None
        self.turn = True  # First player starts
        
        if self.size != 2:
            if self.rank == 0:
                print("This game requires exactly 2 players.")
            MPI.Finalize()
        
    def print_board(self):
        board_str = f'''
        {self.board[0]} | {self.board[1]} | {self.board[2]}
        ---------
        {self.board[3]} | {self.board[4]} | {self.board[5]}
        ---------
        {self.board[6]} | {self.board[7]} | {self.board[8]}
        '''
        print(board_str)
        
    def make_move(self, position, symbol):
        if self.board[position] == ' ':
            self.board[position] = symbol
            self.last_move = position
            return True
        return False
        
    def check_win(self, symbol):
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]               # Diagonals
        ]
        for condition in win_conditions:
            if all(self.board[i] == symbol for i in condition):
                return True
        return False

    def play_game(self):
        if self.rank == 0:
            print("Player 1 (X) connected.")
        elif self.rank == 1:
            print("Player 2 (O) connected.")
        
        while True:
            if self.turn and self.rank == 0:  # Player 1's turn
                self.print_board()
                position = int(input("Player 1, enter your move (0-8): "))
                if not self.make_move(position, 'X'):
                    print("Invalid move! Try again.")
                    continue
                self.turn = False
                self.comm.send(position, dest=1, tag=0)
            elif not self.turn and self.rank == 1:  # Player 2's turn
                position = self.comm.recv(source=0, tag=0)
                if not self.make_move(position, 'O'):
                    print("Invalid move! Try again.")
                    continue
                self.turn = True
            
            # Check for winner
            if self.check_win('X'):
                self.print_board()
                print("Player 1 (X) wins!")
                break
            elif self.check_win('O'):
                self.print_board()
                print("Player 2 (O) wins!")
                break
            elif ' ' not in self.board:
                self.print_board()
                print("It's a tie!")
                break
        
        print("Game over!")
        MPI.Finalize()

if __name__ == "__main__":
    game = TicTacToeMPI()
    game.play_game()
