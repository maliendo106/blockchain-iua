# Trabajo Práctico 6

### Despliegue de contratos
> Los contratos se despliegan en la red local de Ganache.

> Se puede especificar la url con el argumento `--uri`.

> La url por defaul es la siguiente: http://localhost:7545

> Se asume que los contratos se encuentran en el directorio /TP/5/build/contracts

> Despliegue en la red `$truffle migrate --network ganache `

### Archivo Mnemónico
> Se puede introducir la frase mnemónica cuando se solicite por la terminal.

> Otra forma es crear un archivo con la frase mnemónica en él, e indicarlo con el argumento `--mnemonic name-file`

### Build
> `$python3 apiserver.py --mnemonic mnemonic`

### Requerimientos
> Los requerimientos de ejecución, se encuentran en el archivo `requeriments.txt`

### Endpoints Adicionales
### `/calls`

* Retorna todos los callId.
* Retorno exitoso:
  * Código HTTP: 200
  * Cuerpo: Un objeto JSON con un campo de tipo `string`:
    * "calls", lista de hashes que identifican a los llamados.

### `/register/list`

* Lista los pedidos de registro, es decir las registraciones en estado PENDIENTE.
* Sólo debería usarlo el dueño de la Factory.
* Retorno exitoso:
  * Código HTTP: 200
  * Cuerpo: Un objeto JSON con un campo de tipo `string`:
    * "registers", lista de direcciones en estado pendiente.

### `/register/auth`
* Quita una cuenta de la lista de PENDIENTES, y la AUTORIZA a crear llamados.
* Método: `POST`
* Content-type: `application/json`
* Cuerpo: Un objeto JSON con los siguientes campos:
  * `account`: Dirección de la cuenta a autorizar.
* Retorno exitoso:
  * Código HTTP: 200
  * Cuerpo: Un objeto JSON con un campo "message" con valor OK.
* Retorno fallido:
  * Código HTTP: Según la tabla siguiente.
  * Cuerpo: Un objeto JSON con un campo "message" con valor indicado en la tabla siguiente.

    | Causa                    | Código |  Mensaje             |
    |--------------------------|--------|----------------------|
    |ya estaba autorizado      | 403    | ALREADY_AUTHORIZED   |
    |desconocida               | 500    | INTERNAL_ERROR       |
