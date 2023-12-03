//SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.19;

/// @title Votación
contract Ballot {
    // Esta estructura representa a un votante
    struct Voter {
        bool canVote; // si es verdadero, la persona puede votar
        bool voted; // si es verdadero, la persona ya votó
        uint vote; // índice de la propuesta elegida.
    }

    // Este tipo representa a una propuesta
    struct Proposal {
        bytes32 name; // nombre (hasta 32 bytes)
        uint voteCount; // votos recibidos por la propuesta
    }

    address public chairperson;

    // Variable de estado con los votantes
    mapping(address => Voter) public voters;
    // Cantidad de votantes
    uint public numVoters;

    // Arreglo dinámico de propuestas.
    Proposal[] public proposals;

    bool isStarted = false;
    bool isEnded = false;
    uint totalVotes = 0;

    /// Crea una nueva votación para elegir entre `proposalNames`.
    constructor(bytes32[] memory proposalNames) {
        chairperson = msg.sender;
        require(
            proposalNames.length > 1,
            "There should be at least 2 proposals"
        );
        for (uint i = 0; i < proposalNames.length; i++) {
            // `Proposal({...})` crea un objeto temporal
            // de tipo Proposal y  `proposals.push(...)`
            // lo agrega al final de `proposals`.
            proposals.push(Proposal({name: proposalNames[i], voteCount: 0}));
        }
    }

    // Le da a `voter` el derecho a votar.
    // Solamente puede ser ejecutado por `chairperson`.
    // No se puede hacer si
    //  * El votante ya puede votar
    //  * La votación ya comenzó
    // Actualiza numVoters
    function giveRightToVote(address voter) public {
        require(
            msg.sender == chairperson,
            "Only chairperson can give right to vote."
        );
        require(!voters[voter].voted, "The voter already voted.");
        require(!voters[voter].canVote);
        require(!isStarted, "The voting has already started");
        voters[voter].canVote = true;
        numVoters += 1;
    }

    // Quita a `voter` el derecho a votar.
    // Solamente puede ser ejecutado por `chairperson`.
    // No se puede hacer si
    //  * El votante no puede votar
    //  * La votación ya comenzó
    // Actualiza numVoters
    function withdrawRightToVote(address voter) public {
                require(
            msg.sender == chairperson,
            "Only chairperson can give right to vote."
        );
        require(voters[voter].canVote);
        require(!isStarted, "The voting has already started");
        voters[voter].canVote = false;
        numVoters -= 1;
    }

    // Le da a todas las direcciones contenidas en `list` el derecho a votar.
    // Solamente puede ser ejecutado por `chairperson`.
    // No se puede ejecutar si la votación ya comenzó
    // Si el votante ya puede votar, no hace nada.
    // Actualiza numVoters
    function giveAllRightToVote(address[] memory list) public {
        require(
            msg.sender == chairperson,
            "Only chairperson can give right to vote."
        );
        require(!isStarted, "The voting has already started");
        for (uint i = 0; i < list.length; i++){
            if(!voters[list[i]].canVote){
                giveRightToVote(list[i]);
            }
        }
    }

    // Devuelve la cantidad de propuestas
    function numProposals() public view returns (uint) {
        return proposals.length;
    }

    // Habilita el comienzo de la votación
    // Solo puede ser invocada por `chairperson`
    // No puede ser invocada una vez que la votación ha comenzado
    function start() public {
        require(
            msg.sender == chairperson,
            "Only chairperson can give right to vote."
        );
        require(!isStarted, "The voting has already started");
        isStarted = true;
    }

    // Indica si la votación ha comenzado
    function started() public view returns (bool) {
        return isStarted ? true : false;
    }

    // Finaliza la votación
    // Solo puede ser invocada por `chairperson`
    // Solo puede ser invocada una vez que la votación ha comenzado
    // No puede ser invocada una vez que la votación ha finalizado
    function end() public {
        require(
            msg.sender == chairperson,
            "Only chairperson can give right to vote."
        );
        require(isStarted, "Voting hasn't started yet");
        require(!isEnded);
        isEnded = true;
    }

    // Indica si la votación ha finalizado
    function ended() public view returns (bool) {
        return isEnded ? true : false;
    }

    // Vota por la propuesta `proposals[proposal].name`.
    // Requiere que la votación haya comenzado y no haya terminado
    // Si `proposal` está fuera de rango, lanza
    // una excepción y revierte los cambios.
    // El votante tiene que esta habilitado
    // No se puede votar dos veces
    // No se puede votar si la votación aún no comenzó
    // No se puede votar si la votación ya terminó
    function vote(uint proposal) public {
        Voter storage sender = voters[msg.sender];
        require(isStarted && (!isEnded), "hola");
        require(isStarted, "Voting hasn't started yet");
        require(!isEnded, "The voting is over");
        require(sender.canVote, "Has no right to vote");
        require(!sender.voted, "Already voted.");
        // Si `proposal` está fuera de rango, lanza una excepción y revierte los cambios.
       
        sender.voted = true;
        sender.vote = proposal;

        proposals[proposal].voteCount += 1;
        totalVotes += 1;
    }

    /// Calcula la propuestas ganadoras
    /// Devuelve un array con los índices de las propuestas ganadoras.
    // Solo se puede ejecutar si la votación terminó.
    // Si no hay votos, devuelve un array de longitud 0
    // Si hay un empate en el primer puesto, la longitud
    // del array es la cantidad de propuestas que empatan
    function winningProposals() public view
        returns (uint[] memory winningProposal_)
    {
        require(isEnded, "The vote did not end");

       // uint[] memory winningProposal_;
        uint votosPropWinning = 0;

        if(totalVotes == 0) { return winningProposal_; }

        for (uint i = 0; i < numProposals(); i++){
            if (proposals[i].voteCount > votosPropWinning){
                votosPropWinning = proposals[i].voteCount;
                delete winningProposal_; // Borra los índices de las propuestas ganadoras anteriores
                winningProposal_ = new uint256[](1); // Crea un nuevo array con capacidad para un único índice
                winningProposal_[0] = i; // Almacena el índice de la propuesta ganadora en el nuevo array
            } else if (proposals[i].voteCount == votosPropWinning){
                uint256[] memory newWinningProposal_ = new uint256[](winningProposal_.length + 1);
                for (uint256 j = 0; j < winningProposal_.length; j++){
                    newWinningProposal_[j] = winningProposal_[j];
                }
                newWinningProposal_[winningProposal_.length] = i; // Almacena el índice de la propuesta empatada en el nuevo array
                winningProposal_ = newWinningProposal_; 
            }
        }

        return winningProposal_;
    }

    // Devuelve un array con los nombres de las
    // propuestas ganadoras.
    // Solo se puede ejecutar si la votación terminó.
    // Si no hay votos, devuelve un array de longitud 0
    // Si hay un empate en el primer puesto, la longitud
    // del array es la cantidad de propuestas que empatan
    function winners() public view returns (bytes32[] memory winners_) {
        require(isEnded, "The vote did not end");

        if (totalVotes == 0) { return winners_;}

        uint[] memory winningProposals_ = winningProposals();
        uint numWinningProposals = winningProposals_.length;

        // Calcular la cantidad de propuestas que empatan en el primer puesto
        for (uint i = 1; i < numProposals(); i++) {
            if (proposals[i].voteCount == proposals[winningProposals_[0]].voteCount) {
                numWinningProposals++;
            } else {
                break;
            }
        }

        winners_ = new bytes32[](numWinningProposals); // Inicializar el array con un tamaño fijo
        for (uint i = 0; i < numWinningProposals; i++) {
            winners_[i] = proposals[winningProposals_[i]].name; // Asignar los nombres de las propuestas ganadoras
        }

        return winners_;
    }
}
