<template>
  <main>
    <img src="/photo.png" alt="Equipe">
    <a href="#portfolio">Ver portfólio</a>
    <button aria-label="Abrir menu" @click="open = !open"><span aria-hidden="true">+</span></button>
    <label for="search">Pesquisa</label><input id="search" type="text">
    <a href="/home" target="_blank" rel="noopener noreferrer">Nova aba</a>
    <section id="portfolio">Resultados</section>
  </main>
</template>
<script setup lang="ts">import { ref } from 'vue'; const open = ref(false);</script>
