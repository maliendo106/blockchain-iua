//SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract CFP {
    // Evento que se emite cuando alguien registra una propuesta
    event ProposalRegistered(
        bytes32 proposal,
        address sender,
        uint256 blockNumber
    );

    // Estructura que representa una propuesta
    struct ProposalData {
        address sender;
        uint256 blockNumber;
        uint256 timestamp;
    }

    // Mapeo que asocia cada propuesta con sus datos correspondientes
    mapping (bytes32 => ProposalData) public proposalData;

    // Lista de hashes de propuestas registradas
    bytes32[] public proposals;//proposals y eliminar la del index

    // Timestamp del cierre de la recepción de propuestas
    uint256 public closingTime;

    // Identificador de este llamado
    bytes32 public callId;

    // Creador de este llamado
    address public creator;



    // Devuelve los datos asociados con una propuesta
    //function proposalData(// eliminar esta funcion
    //    bytes32 proposal
    //) public view returns (ProposalData memory) {
        // Busca la propuesta en el mapeo y devuelve sus datos
    //    return propuestas[proposal];
    //}

    // Devuelve la propuesta que está en la posición `index` de la lista de propuestas registradas
    //function proposals(uint index) public view returns (bytes32) {
    //    require(index < proposalList.length, "Indice fuera de rango");
    //    return proposalList[index];
    //}


    /** Construye un llamado con un identificador y un tiempo de cierre.
     *  Si el `timestamp` del bloque actual es mayor o igual al tiempo de cierre especificado,
     *  revierte con el mensaje "El cierre de la convocatoria no puede estar en el pasado".
     */
    constructor(bytes32 _callId, uint256 _closingTime) {
        
        require(_closingTime > block.timestamp, "El cierre de la convocatoria no puede estar en el pasado");
        
        creator = msg.sender;
        callId = _callId;
        closingTime = _closingTime;
    }

    // Devuelve la cantidad de propuestas presentadas
    function proposalCount() public view returns (uint256) {
        return proposals.length;
    }


    /** Permite registrar una propuesta espec.
     *  Registra al emisor del mensaje como emisor de la propuesta.
     *  Si el timestamp del bloque actual es mayor que el del cierre del llamado,
     *  revierte con el error "Convocatoria cerrada"
     *  Si ya se ha registrado una propuesta igual, revierte con el mensaje
     *  "La propuesta ya ha sido registrada"
     *  Emite el evento `ProposalRegistered`
     */
    function registerProposal(bytes32 proposal) public {

        require(block.timestamp <= closingTime, "Convocatoria cerrada");
        require(proposalTimestamp(proposal) == 0, "La propuesta ya ha sido registrada");

        proposalData[proposal] = ProposalData(msg.sender, block.number, block.timestamp);
        proposals.push(proposal);

        emit ProposalRegistered(proposal, msg.sender, block.number);
    }

    /** Permite registrar una propuesta especificando un emisor.
     *  Sólo puede ser ejecutada por el creador del llamado. Si no es así, revierte
     *  con el mensaje "Solo el creador puede hacer esta llamada"
     *  Si el timestamp del bloque actual es mayor que el del cierre del llamado,
     *  revierte con el error "Convocatoria cerrada"
     *  Si ya se ha registrado una propuesta igual, revierte con el mensaje
     *  "La propuesta ya ha sido registrada"
     *  Emite el evento `ProposalRegistered`
     */
    function registerProposalFor(bytes32 proposal, address sender) public {

        require(msg.sender == creator, "Solo el creador puede hacer esta llamada");
        require(block.timestamp <= closingTime, "Convocatoria cerrada");
        require(proposalTimestamp(proposal) == 0, "La propuesta ya ha sido registrada");

        proposalData[proposal] = ProposalData(sender, block.number, block.timestamp);
        proposals.push(proposal);

        emit ProposalRegistered(proposal, sender, block.number);
    }

    /** Devuelve el timestamp en el que se ha registrado una propuesta.
     *  Si la propuesta no está registrada, devuelve cero.
     */
    function proposalTimestamp( bytes32 proposal) 
    public view returns (uint256) {
        
        ProposalData memory data = proposalData[proposal];
        if (data.sender == address(0)) {
            return 0;
        }
        return data.timestamp;
    }
}
