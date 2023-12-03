<template>
  <v-container>
    <div style="height: 30px;"/>
    <v-container >

      <v-row>
        <v-col cols="12">
          <v-row align="end" justify="end">
            <v-btn depressed color="primary" @click="back">Volver</v-btn>
          </v-row>
        </v-col>
      </v-row>
    </v-container>

    <div class="register-call">
      <register-call :account="this.$route.params.address" />
    </div>
    
  </v-container>
  </template>
  
  <script>
import RegisterCall from '@/components/Register.vue';
  
  export default {
    components: {
      RegisterCall
    },
    data: () => ({
      
    }),
    methods: {
    back () {             
      this.$router.go(-1);         
    },
         }
  }
  </script>