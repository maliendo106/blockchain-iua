<template>
  <v-container>
    <v-row> 
      <v-col cols="12"> 
        <div class="home">
          <call-table/>
        </div>
      </v-col>
    </v-row>
  </v-container>
  </template>
  
  <script>
import CallTable from '@/components/CallTable.vue';
  
  export default {
    components: {
    CallTable
    }
  }
  </script>
