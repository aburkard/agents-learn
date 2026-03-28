# Tic Tac Toe

Write a version of the game Tic Tac Toe with a simple AI. Your program should run in the terminal and let the user play Tic Tac Toe against the computer. The human player will always make the first move (X). The program should prompt the user for a move via stdin and then compute the AI’s response.

Please implement the program in the following steps (testing each step before moving on):

1.  **Create a Tic Tac Toe board class** with methods to add a token to the board and print the board to the terminal.  
    Print the board in the following format:
    
    ```
    X|–|–
    –|O|X
    –|–|–
    ```
    
2.  **Add a method to check whether the board is full.**  
    Then create an AI function (or class) that takes a board and makes a move.  
    At this stage, do _not_ implement the full AI logic—have the AI make **any** legal move.  
    Return or throw an error if no legal move exists.
    
3.  **Create the game loop**—a loop that alternates moves between the human and the AI, displays the board after each move, and ends when the board is full.  
    If the user enters an invalid move, allow them to retry.
    
4.  **Add win-detection methods** to the board class to check when a player has completed three in a row (row, column, or diagonal).  
    Modify the game loop so that it stops immediately when either player wins.
    
5.  **Implement the full AI logic.** The AI should follow these rules, in order:  
    a. If it can win (complete 3 in a row), do so.  
    b. If the opponent can win on their next move, block them.  
    c. If neither of the above applies, choose any valid move.
