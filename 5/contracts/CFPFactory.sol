//SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./CFP.sol";

contract CFPFactory {
    // Evento que se emite cuando se crea un llamado a presentación de propuestas
    event CFPCreated(address creator, bytes32 callId, CFP cfp);

    // Estructura que representa un llamado
    struct CallForProposals {
        address creator;
        CFP cfp;
    }

    enum Status {
        None,
        pendiente,
        autorizado,
        no_autorizado
    }

    
    address public owner; // Dirección del dueño de la factoría
    mapping (bytes32 => CallForProposals) public calls; // Devuelve el llamado asociado con un callId
    address[] public creatorsList; // lista de creadores
    mapping (address => bytes32[]) public creatorsMap; //almacena los callId creados por cada creador
    mapping (bytes32 => address) public instancesList; // instancias de propuestas registradas
    address[] public pendingList; // lista de pendientes
    mapping (address => Status) public registro; //asocia la cuenta con su estado


    modifier isOwner() {
        require(owner == msg.sender, 
        unicode"Solo el creador puede hacer esta llamada");
        _;
    }
    
    modifier callExist(bytes32 callId) {
        require(calls[callId].creator == address(0), 
        unicode"El llamado ya existe");
        _;
    }

    modifier authorized(address addr) {
        require(isAuthorized(addr), 
        unicode"No autorizado");
        _;
    }


    constructor() {
        // registra al emisor como dueño de la factoria
        owner = msg.sender;
    }

    // Devuelve la dirección de un creador de la lista de creadores
    function creators(uint index) public view returns (address) {
        return creatorsList[index];
    }

    /** Crea un llamado, con un identificador y un tiempo de cierre
     *  Si ya existe un llamado con ese identificador, revierte con el mensaje de error "El llamado ya existe"
     *  Si el emisor no está autorizado a crear llamados, revierte con el mensaje "No autorizado"
     */
    function create(bytes32 callId, uint256 timestamp) public callExist(callId) authorized(msg.sender)
     returns (CFP) {

        CFP cfpInstance = new CFP(callId, timestamp);
        calls[callId] = CallForProposals(msg.sender, cfpInstance);
        
        address cfpAddress = address(cfpInstance);
        instancesList[callId] = cfpAddress;// agrego la direccion de la instancia

        addListCreators(msg.sender); // agrego el creador a la lista de creadores
        creatorsMap[msg.sender].push(callId);

        emit CFPCreated(msg.sender, callId, cfpInstance);
        return cfpInstance;
    }

    /**
     * Crea un llamado, estableciendo a `creator` como creador del mismo.
     * Sólo puede ser invocada por el dueño de la factoría.
     * Se comporta en todos los demás aspectos como `createFor(bytes32 callId, uint timestamp)`
     */
    function createFor( bytes32 callId, uint timestamp, address creator
    ) public isOwner callExist(callId) authorized(creator)
    returns (CFP) {

        CFP cfpInstance = new CFP(callId, timestamp);
        calls[callId] = CallForProposals(creator, cfpInstance);

        address cfpAddress = address(cfpInstance);
        instancesList[callId] = cfpAddress;

        addListCreators(creator); // agrego el creador a la lista de creadores
        creatorsMap[creator].push(callId);

        emit CFPCreated(creator, callId, cfpInstance);
        return cfpInstance;
    }

    /// agrega a la lista de creadores, pero solo si no está
    function addListCreators(address creator) private {
        bool flag = false;
        for (uint i = 0; i < creatorsList.length; i++) {
            if (creatorsList[i] == creator) {
                flag = true;
            }
        }
        if (!flag) {
            creatorsList.push(creator);
        }
    }

    // Devuelve la cantidad de cuentas que han creado llamados.
    function creatorsCount() public view returns (uint256) {
        return creatorsList.length;
    }

    /// Devuelve el identificador del llamado que está en la posición `index` de la lista de llamados creados por `creator`
    function createdBy( address creator, uint256 index
    ) public view returns (bytes32) {
        //require(index > 0 && index <= creatorsMap[creator].length); //q el indice no este fuera de rango
        return creatorsMap[creator][index]; //index o index-1 ???
    }

    // Devuelve la cantidad de llamados creados por `creator`
    function createdByCount(address creator) public view returns (uint256) {
        return creatorsMap[creator].length;
    }

    /** Permite a un usuario registrar una propuesta, para un llamado con identificador `callId`.
     *  Si el llamado no existe, revierte con el mensaje  "El llamado no existe".
     *  Registra la propuesta en el llamado asociado con `callId` y pasa como creador la dirección del emisor del mensaje.
     */
    function registerProposal(bytes32 callId, bytes32 proposal) public {
        require(calls[callId].creator != address(0), "El llamado no existe");
        
        // llama al metodo registerProposalFor() del contrato CFP
        CFP(instancesList[callId]).registerProposalFor(proposal, msg.sender);
    }

    /** Permite que una cuenta se registre para poder crear llamados.
     *  El registro queda en estado pendiente hasta que el dueño de la factoría lo autorice.
     *  Si ya se ha registrado, revierte con el mensaje "Ya se ha registrado"
     */
    function register() public {
        require(!isRegistered(msg.sender), "Ya se ha registrado");

        registro[msg.sender] = Status.pendiente;
        pendingList.push(msg.sender); // agrego la cuenta a la lista de pendientes
    }

    /** Autoriza a una cuenta a crear llamados.
     *  Sólo puede ser ejecutada por el dueño de la factoría.
     *  En caso contrario revierte con el mensaje "Solo el creador puede hacer esta llamada".
     *  Si la cuenta se ha registrado y está pendiente, la quita de la lista de pendientes.
     */
    function authorize(address creator) public isOwner {
        if (isRegistered(creator)) {   //esta registrado
            if (registro[creator] == Status.pendiente) {
                //quitar de la lista de pendientes
                removeAddressFromList(creator);
            } 
        }    
        registro[creator] = Status.autorizado; // se autoriza aunque no este registrado?????
    }

    /** Quita la autorización de una cuenta para crear llamados.
     *  Sólo puede ser ejecutada por el dueño de la factoría.
     *  En caso contrario revierte con el mensaje "Solo el creador puede hacer esta llamada".
     *  Si la cuenta se ha registrado y está pendiente, la quita de la lista de pendientes.
     */
    function unauthorize(address creator) public isOwner {
        if (isRegistered(creator)) {   
            if (registro[creator] == Status.pendiente) {
               //quitar de la lista de pendientes
                removeAddressFromList(creator); 
            }
        }   
        registro[creator] = Status.no_autorizado;  //aunque no este registrado, no entiendo xq. 
    }


    ///elimina de la lista de pendientes, una direccion especifica
    function removeAddressFromList(address _address) public {
        uint indexToRemove;
        for (uint i = 0; i < pendingList.length; i++) {
            if (pendingList[i] == _address) {
                indexToRemove = i;
                break;
            }
        }
        for (uint j = indexToRemove; j < pendingList.length-1; j++) {
            pendingList[j] = pendingList[j+1];
        }
        pendingList.pop();
    }


    // Devuelve la lista de todas las registraciones pendientes.
    // Sólo puede ser ejecutada por el dueño de la factoría
    // En caso contrario revierte con el mensaje "Solo el creador puede hacer esta llamada".
    function getAllPending() public isOwner view returns (address[] memory) {
        return pendingList;
    }

    // Devuelve la registración pendiente con índice `index`
    // Sólo puede ser ejecutada por el dueño de la factoría
    // En caso contrario revierte con el mensaje "Solo el creador puede hacer esta llamada".
    function getPending(uint256 index) public isOwner view returns (address) {
        return pendingList[index];
    }

    // Devuelve la cantidad de registraciones pendientes.
    // Sólo puede ser ejecutada por el dueño de la factoría
    // En caso contrario revierte con el mensaje "Solo el creador puede hacer esta llamada".
    function pendingCount() public isOwner view returns (uint256) {
        return pendingList.length;
    }

    // Devuelve verdadero si una cuenta se ha registrado, tanto si su estado es pendiente como si ya se la ha autorizado.
    function isRegistered(address account) public view returns (bool) {
        if (registro[account] == Status.pendiente) {
            return true;
        }
        if (registro[account] == Status.autorizado){
            return true;
        }
        return false;
    }

    // Devuelve verdadero si una cuenta está autorizada a crear llamados.
    function isAuthorized(address account) public view returns (bool) {
        if (registro[account] == Status.autorizado) {
            return true;
        }
        return false;
    }
}
