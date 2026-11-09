<template>
  <section class="ai-empty workspace-pane">
    <div class="ai-mark">✳</div>
    <strong>AI 工作区</strong>
    <span>在这里开始探索市场数据</span>
  </section>
</template>

<style>
.ai-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  min-height: 200px;
  color: #97a2b1;
}
.ai-mark {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  margin-bottom: 10px;
  border-radius: 12px;
  background: #f2f6ff;
  color: #6494eb;
  font-size: 18px;
}
.ai-empty strong {
  color: #5b687a;
  font-size: 12px;
}
.ai-empty span {
  margin-top: 3px;
  font-size: 10px;
}
</style>
