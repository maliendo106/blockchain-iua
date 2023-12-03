<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <div justify="space-around">Seleccion de propuestas</div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-file-input v-model="selected_files" @change="handleFiles" id="input" multiple chips counter show-size>
        </v-file-input>
      </v-col> </v-row>
    <v-row>
      <v-col cols="12">

        <div>Call ID: {{ this.account }}</div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">

        <v-data-table :items="files" :headers="headers" :items-per-page="5" hide-default-footer class="elevation-1">
          <template v-slot:item="{ item }">

            <tr>
              <td>{{ item.name }}</td>
              <td>{{ item.hash }}</td>
              <td>
                <v-icon v-if="item.block > 0" :color="signerColor(item.sender)">
                  mdi-thumb-up</v-icon>
                <v-icon v-else-if="item.block == 0" color="red">mdi-thumb-down</v-icon>
              </td>
              <td v-show="item.block > 0">{{ item.block }}</td>
            </tr>
          </template>
        </v-data-table>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">

        <v-container>
          <v-row align="center" justify="space-around">
            <v-btn depressed color="primary" @click="register">Registrar</v-btn>
            <v-btn depressed color="primary" @click="verify">Verificar</v-btn>
          </v-row>
        </v-container>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import sha256 from "js-sha256";
import axios from "axios";
export default {
  name: "RegisterHola",
  // props: ["web3", "apiUrl", "stamper", "account"],
  props: ["account"],
  data: () => ({
    selected_files: [],  // archivos -> proposal
    files: [],  // archivos adjuntos
    //accounts: [], // call_id
    headers: [
      { text: 'Nombre', value: 'name', align: 'center', sortable: false },
      { text: 'Propuesta', value: 'hash', align: 'center', sortable: false },
      { text: 'Sellado', value: 'sealed', align: 'center', sortable: false },
      { text: 'Bloque', value: 'block', align: 'center', sortable: false },
    ],
  }),
  // watch: {
  //   account: {
  //     immediate: true,
  //     handler(newValue) {
  //       this.files = [newValue, ...this.files];
  //     },
  //   },
  // },
  methods: {
    reset() {
      this.files = [];
      this.$emit("warning", false);
      this.$emit("error", false);
    },
    unhandledError(err, errorMessage) {
      this.$emit("error", errorMessage);
      console.log(err);
    },
    signerColor(signer) { // revisar esto cuando haga lo de metamask
      return signer == this.account ? "blue" : "green";
    },
    handleFiles(files) {
      for (let file of files) {
        this.files.push({
          file: file,
          name: file.name,
          hash: "",
          block: -1,
          sender: "",
          timestamp: ""
        });
      }
    },
    async hashFile(file) {
      let buffer = await file.file.arrayBuffer();
      let hash = sha256.create();
      hash.update(buffer);
      file.hash = `0x${hash.hex()}`;
    },
    async verifyFile(file) {
      try {
        if (!file.hash) {
          await this.hashFile(file);
        }
        let res = await axios.get(`http://localhost:5000/proposal-data/0x${this.account}/${file.hash}`);
        file.block = res.data.blockNumber;
        file.sender = res.data.sender;
        file.timestamp = res.data.timestamp;
        if (file.block > 0) {
          return true;
        }
      } catch (err) {
        if (err.response?.status == 404) { // TODO: revisar esto!
          file.block = 0;
          return false;
        }
        throw err;
      }
    },
    async verify() {
      this.selected_files = [];
      for (let file of this.files) {
        if (file.block > 0) continue;
        this.verifyFile(file).catch((err) =>
          this.unhandledError(
            err,
            `Se ha producido un error al verificar el archivo ${file.name}: ${err.message}`
          )
        );
      }
    },


    async registerFile(file) {
      let stamped = await this.verifyFile(file);
      if (stamped) return;
      await axios.post(`http://localhost:5000/register-proposal`, { callId: `0x${this.account}`, proposal: file.hash });
      await this.verifyFile(file);
    },
    async register() {
      this.selected_files = [];
      for (let file of this.files) {
        if (file.block > 0) continue;
        this.registerFile(file).catch((err) => {
          let errorMessage = err.response?.data?.message;
          if (errorMessage) {
            this.$emit("error", errorMessage);
          } else {
            this.unhandledError(
              err,
              `Se ha producido un error al sellar el archivo ${file.name}: ${err.message}`
            );
          }
        });
      }
    },
  }
};
</script>
  