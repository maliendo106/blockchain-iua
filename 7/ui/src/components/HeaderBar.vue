<template>
      <!-- <v-app-bar app color="primary" dark>
        <div class="d-flex align-center">
          <v-img alt="Vuetify Logo" class="shrink mr-2" contain
            src="https://cdn.vuetifyjs.com/images/logos/vuetify-logo-dark.png" transition="scale-transition" width="40" />
  
          <v-img alt="Vuetify Name" class="shrink mt-1 hidden-sm-and-down" contain min-width="100"
            src="https://cdn.vuetifyjs.com/images/logos/vuetify-name-dark.png" width="100" />
        </div>
      </v-app-bar> -->

      <v-app-bar app color="primary" dark>
      <v-spacer></v-spacer>
      <div class="d-flex align-center">
        <v-btn v-if="stamper && !account" @click="enableEthereum">Habilitar Ethereum</v-btn>
        <v-img v-if="stamper" alt="Contract" class="shrink mr-2" contain :src="contract_logo"
          transition="scale-transition" width="60" />
        <v-img alt="Metamask" class="shrink mr-2" contain :style="grayed" :src="metamask_logo"
          transition="scale-transition" width="40" />
        <v-btn v-if="stamper && account" >Soy el dueño</v-btn>
      </div>
    </v-app-bar>
  </template>

<script>
import axios from "axios"
import Web3 from "web3";
import { abi, networks } from "../../../../5/build/contracts/CFPFactory.json"
let apiUrl = "http://localhost:5000"

export default {
  data: () => ({
    metamask_logo: require("../assets/metamask.png"),
    contract_logo: require("../assets/contract.png"),
    networkId: 0,
    web3: window.ethereum ? new Web3(window.ethereum) : null,
    account: null,
    error: false,
    errorMessage: "Error",
    warning: false,
    warningMessage: "Advertencia",
    apiContractAddress: "",
    abi: abi,
    networks: networks,
    apiUrl: apiUrl
  }),
 
  methods: {
    async enableEthereum() {
      window.ethereum
        .request({ method: "eth_requestAccounts" })
        .then(this.accountsChanged)
        .then(window.ethereum.on("accountsChanged", this.accountsChanged))
        .catch((err) => {
          if (err.code === 401) {
            this.errorMessage = "El usuario negó la habilitación de Ethereum";
          } else {
            this.errorMessage =
              "Se ha producido un error al habilitar Ethereum";
            console.log(err);
          }
          this.error = true;
        });
    },
    async accountsChanged(accounts) {
      this.account = this.web3.utils.toChecksumAddress(accounts[0]);
    },
    async updateNetwork() {
      this.networkId = window.ethereum.request({ method: "net_version" }).then(
        (id) => (this.networkId = id),
        () => (this.networkId = 0)
      );
    },
    showError(errorMessage) {
      if (errorMessage) {
        this.error = true;
        this.errorMessage = errorMessage;
      } else {
        this.error = false;
      }
    },
    showWarning(warningMessage) {
      if (warningMessage) {
        this.warning = true;
        this.warningMessage = warningMessage;
      } else {
        this.warning = false;
      }
    },
  },
  computed: {
    grayed() {
      if (this.web3) return {};
      else
        return {
          filter: "grayscale(100%)",
        };
    },
    stamperAddress() {
      return this.networks?.[this.networkId]?.address;
    },
    stamper() {
      if (!this.web3) {
        return null;
      }
      let address = this.stamperAddress;
      if (address == this.apiContractAddress) {
        return new this.web3.eth.Contract(this.abi, address);
      } else {
        return null;
      }
    },
  },
  created() {
    if (this.web3) {
      this.updateNetwork().then(
        window.ethereum?.on("chainChanged", () => this.updateNetwork())
      );
    }
    axios.get(`${this.apiUrl}/contract-address`)
      .then((res) => this.apiContractAddress = res.data.address)
      .catch(err => {
        this.errorMessage = `Fallo al obtener la dirección del contrato de la API: ${err.message}`
        this.error = true
      })
    //   agrgar metodo de apribacion de address
  },
};
</script>