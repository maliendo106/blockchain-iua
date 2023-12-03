//SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.3;

import "./Game.sol";


contract TicTacToe is Game {

    mapping(uint => mapping(uint => address)) public board;
    uint public turn = 0;
   // uint public amount = 0;
    
    
    event Play(address player, uint256 row, uint256 col);
   // event PrintMessage(string message);
    constructor() payable {
        setInitialPlayer(); // el jugador se selecciona aleatoriamente
    }
    // Permite realizar una jugada, indicando fila y columna
    // Las filas y columnas comienzan en 0
    // Sólo puede invocarse si el juego ya comenzó
    // Sólo puede invocarla el jugador que tiene el turno
    // Si la jugada es inválida, se rechaza con error "invalid move"
    // Debe emitir el evento Play(player, row, col) con cada jugada
    // Si un jugador gana al jugar, emite el evento Winner(winner)
    // Si no se puede jugar más es un empate y emite el evento
    // Draw(creator, challenger)
    function play(uint256 row, uint256 col) public onlyRunning() inTurn() {
        require(row < 3 && col < 3, "invalid move");
        require(board[row][col] == address(0), "invalid move");
        board[row][col] = msg.sender;
        turn++;
        emit Play(msg.sender, row, col);
        checkGameOver();
        changeTurn();
        
    }

     function checkGameOver() private {
        if (turn >= 5) {
            for (uint i = 0; i < 3; i++) {
                if (board[i][0] != address(0) && board[i][0] == board[i][1] && board[i][0] == board[i][2]) {
                    winner = players[next];  
                    status = Status.ended;
                    winnings[next] = 2 * bet;
                    transferWinnings(winner);
                    emit GameTerminated(msg.sender);
                    emit Winner(winner);
                    return;
                }
                if (board[0][i] != address(0) && board[0][i] == board[1][i] && board[0][i] == board[2][i]) {
                    winner = players[next];
                    status = Status.ended;
                    winnings[next] = 2 * bet;
                    transferWinnings(winner);
                    emit GameTerminated(msg.sender);
                    emit Winner(winner);
                    return;
                }
            }
            if (board[0][0] != address(0) && board[0][0] == board[1][1] && board[0][0] == board[2][2]) {
                winner = players[next];
                status = Status.ended;
                winnings[next] = 2 * bet;
                transferWinnings(winner);
                emit GameTerminated(msg.sender);
                emit Winner(winner);
                return;
            }
            if (board[0][2] != address(0) && board[0][2] == board[1][1] && board[0][2] == board[2][0]) {
                winner = players[next];
                status = Status.ended;
                winnings[next] = 2 * bet;
                transferWinnings(winner);
                emit GameTerminated(msg.sender);
                emit Winner(winner);
                return;
            }
            if (turn == 9) { // 8 o 9?
                //emit PrintMessage("Este es un empate");
                emit Draw(players[0], players[1]);

                status = Status.ended;

                winnings[0] = bet;
                winnings[1] = bet;

                emit GameTerminated(msg.sender);
                claimWinnings();
                return;
            }
        }
    }
}

