<script setup lang="ts">const open=()=>console.log('ok')</script>
<template>
 <img src="/hero.png">
 <a href="#">Continuar</a>
 <div @click="open">Abrir</div>
 <input type="text" placeholder="E-mail">
</template>
<style>.low {color:#bdbdbd;background-color:#fff}</style>
