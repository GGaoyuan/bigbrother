<script setup lang="ts">

</script>

<template>
  <div>
    <header>
      <img alt="Vue logo" class="logo" src="../assets/logo.svg" width="125" height="125" />
      <div class="wrapper">
        <h1>Home Page</h1>
      </div>
    </header>
    <main>
      <p>这是首页内容</p>
    </main>
  </div>
</template>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }
}
</style>