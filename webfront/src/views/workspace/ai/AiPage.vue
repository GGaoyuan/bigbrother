<template>
  <section class="ai-page">
    <div class="ai-page-card">
      <div class="ai-page-mark">✳</div>
      <h1>AI 工作区</h1>
      <p>在这里开始探索市场数据</p>
    </div>
  </section>
</template>

<style>
.ai-page {
  display: grid;
  min-height: calc(100vh - 32px);
  place-items: center;
}
.ai-page-card {
  display: grid;
  justify-items: center;
  gap: 8px;
  padding: 36px;
  color: #8b96a5;
  text-align: center;
}
.ai-page-card h1 {
  margin: 0;
  color: #526176;
  font-size: 18px;
  font-weight: 650;
}
.ai-page-card p {
  font-size: 13px;
}
.ai-page-mark {
  display: grid;
  width: 48px;
  height: 48px;
  place-items: center;
  margin-bottom: 4px;
  border-radius: 14px;
  background: #f1f5fc;
  color: #7495d5;
  font-size: 24px;
}
</style>
