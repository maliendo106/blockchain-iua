<template>
  <v-container>
   <v-row>
      <v-col cols="12">
        <div justify="space-around">Listado de llamados</div>
      </v-col>
    </v-row>
  <v-row>
    <v-col cols="12">
      <v-data-table :headers="headers" :items="callList" :items-per-page="10" hide-default-footer class="elevation-1">
        <template v-slot:item="{ item }">
          <tr>
            <td>{{ item.address }}</td>
            <router-link :to="{ name: 'upload-file', params: { address: item.address } }">
              <td class="text-right">
                <v-btn depressed color="primary">
                  Seleccionar
                </v-btn>
              </td>
            </router-link>
          </tr>
        </template>
      </v-data-table>
    </v-col>
  </v-row>
</v-container>
</template>


<style>
.text-right {
  text-align: right;
}
.text-center {
  text-align: center;
}
</style>

  
  
<script>
import axios from 'axios';
export default {
  data() {
    return {
      callList: [],
      headers: [
        { text: 'Call ID', value: 'address', align: 'center', sortable: false }
      ],
    };
  },
  methods: {
    // Tu método para obtener la lista de calls
    fetchCallList() {
      const endpoint = `http://localhost:5000/calls`;

      axios.get(endpoint)
        .then(response => {
          this.callList = response.data.calls.map(call => {
            const aux = {
              'address': call
            }
            return aux;
          })
          console.log(this.callList)
        })
        .catch(error => {
          // Manejar el error de la solicitud
          console.error(error);
        });
    },
  },
  created() {
    this.fetchCallList();
  },
};
</script>
  