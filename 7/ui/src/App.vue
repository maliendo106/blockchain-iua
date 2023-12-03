<template>
  <v-app>
    <HeaderBar></HeaderBar>

    <v-main>
      <router-view />
    </v-main>

  </v-app>
</template>

<script>
import HeaderBar from '@/components/HeaderBar.vue';

export default {
  components: {
    HeaderBar,
  },
  data: () => ({
  }),

};
</script>