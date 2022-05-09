<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import Chat from './components/SubMenu/ChatBot/Chat.vue'
import ASR from './components/SubMenu/ASR/ASR.vue'
import TTS from './components/SubMenu/TTS/TTS.vue'
import VPR from './components/SubMenu/Speaker/VPR.vue'
import IE from './components/SubMenu/IE/IE.vue'
</script>

<template>
  <Chat></Chat>
  <ASR></ASR>
  <TTS></TTS>
  <VPR></VPR>
  <IE></IE>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
