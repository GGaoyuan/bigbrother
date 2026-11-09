<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

interface Panel {
  id: number
  name: string
}

const panels = ref<Panel[]>([
  {
    id: 1,
    name: '面板1',
  },
])
const activePanelId = ref(1)
const nextPanelId = ref(2)
const editingPanelId = ref<number | null>(null)
const panelNameDraft = ref('')
const editingPanel = computed(() => panels.value.find((panel) => panel.id === editingPanelId.value))

function addPanel() {
  const panel: Panel = {
    id: nextPanelId.value,
    name: `面板${nextPanelId.value}`,
  }

  panels.value.push(panel)
  activePanelId.value = panel.id
  nextPanelId.value += 1
}

function openPanelSettings(panel: Panel) {
  editingPanelId.value = panel.id
  panelNameDraft.value = panel.name
}

function selectPanel(panel: Panel) {
  if (panel.id === activePanelId.value) {
    openPanelSettings(panel)
    return
  }

  activePanelId.value = panel.id
}

function closePanelSettings() {
  editingPanelId.value = null
  panelNameDraft.value = ''
}

function savePanelSettings() {
  const panel = editingPanel.value

  if (!panel) {
    closePanelSettings()
    return
  }

  const name = panelNameDraft.value.trim()
  if (name) {
    panel.name = name
  }

  closePanelSettings()
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && editingPanelId.value !== null) {
    closePanelSettings()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <nav class="panel-bar" aria-label="工作面板">
    <div class="panel-tabs">
      <div class="panel-list" role="tablist" aria-label="面板列表">
        <button
          v-for="panel in panels"
          :key="panel.id"
          class="panel-tab"
          :class="{ 'is-active': panel.id === activePanelId }"
          type="button"
          role="tab"
          :aria-selected="panel.id === activePanelId"
          @click="selectPanel(panel)"
        >
          {{ panel.name }}
        </button>
      </div>
      <button
        class="add-panel-button"
        type="button"
        aria-label="添加面板"
        title="添加面板"
        @click="addPanel"
      >
        <span aria-hidden="true">+</span>
      </button>
    </div>

    <Teleport to="body">
      <div
        v-if="editingPanel"
        class="dialog-backdrop"
        role="presentation"
        @click.self="closePanelSettings"
      >
        <section
          class="panel-settings-dialog"
          role="dialog"
          aria-modal="true"
          aria-labelledby="panel-settings-title"
        >
          <header class="dialog-header">
            <div>
              <p class="dialog-eyebrow">工作区</p>
              <h2 id="panel-settings-title">面板设置</h2>
            </div>
            <button
              class="dialog-close-button"
              type="button"
              aria-label="关闭设置"
              @click="closePanelSettings"
            >
              ×
            </button>
          </header>

          <form class="panel-settings-form" @submit.prevent="savePanelSettings">
            <label for="panel-name">面板名称</label>
            <input
              id="panel-name"
              v-model="panelNameDraft"
              type="text"
              maxlength="24"
              autocomplete="off"
              autofocus
            />
            <p class="field-hint">名称最多 24 个字符。</p>
            <footer class="dialog-actions">
              <button class="cancel-button" type="button" @click="closePanelSettings">
                取消
              </button>
              <button class="save-button" type="submit">
                保存
              </button>
            </footer>
          </form>
        </section>
      </div>
    </Teleport>
  </nav>
</template>

<style scoped>
.panel-bar {
  position: sticky;
  top: 0;
  z-index: 30;
  margin: -16px -20px 0;
  padding: 10px 20px 0;
  border-bottom: 1px solid #dce4ef;
  background: rgb(248 250 252 / 94%);
  backdrop-filter: blur(14px);
}

.panel-tabs {
  display: flex;
  min-height: 48px;
  align-items: flex-start;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: thin;
}

.panel-list {
  display: flex;
  flex: 0 0 auto;
  gap: 8px;
}

.panel-tab,
.add-panel-button {
  display: inline-flex;
  min-height: 38px;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  border: 1px solid #dce4ee;
  border-radius: 9px;
  background: #fff;
  color: #6d7888;
  font: inherit;
  cursor: pointer;
  transition: border-color 140ms ease, color 140ms ease, background-color 140ms ease;
}

.panel-tab {
  min-width: 78px;
  padding: 0 16px;
  font-size: 14px;
  font-weight: 600;
}

.panel-tab:hover,
.add-panel-button:hover {
  border-color: #8fb2ff;
  color: #2458cb;
}

.panel-tab.is-active {
  border: 1.5px solid #2f65f5;
  background: #f3f7ff;
  color: #2458cb;
  box-shadow: 0 0 0 1px rgb(47 101 245 / 8%);
}

.add-panel-button {
  width: 38px;
  padding: 0;
  color: #8792a2;
  font-size: 22px;
  font-weight: 400;
  line-height: 1;
}

.dialog-backdrop {
  position: fixed;
  z-index: 100;
  inset: 0;
  display: grid;
  align-items: center;
  justify-items: center;
  padding: 20px;
  background: rgb(22 34 54 / 34%);
  backdrop-filter: blur(3px);
}

.panel-settings-dialog {
  width: min(100%, 440px);
  overflow: hidden;
  border: 1px solid #dce4ef;
  border-radius: 13px;
  background: #fff;
  box-shadow: 0 24px 70px rgb(24 43 76 / 22%);
}

.dialog-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 20px 22px 17px;
  border-bottom: 1px solid #e8edf4;
}

.dialog-eyebrow {
  margin: 0 0 5px;
  color: #8995a6;
  font-size: 11px;
  font-weight: 600;
}

.dialog-header h2 {
  margin: 0;
  color: #273449;
  font-size: 18px;
  font-weight: 650;
}

.dialog-close-button {
  width: 30px;
  height: 30px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  color: #7b8798;
  font: inherit;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
}

.dialog-close-button:hover {
  background: #f1f5fa;
  color: #2f4058;
}

.panel-settings-form {
  padding: 20px 22px 22px;
}

.panel-settings-form label {
  display: block;
  margin-bottom: 8px;
  color: #445269;
  font-size: 13px;
  font-weight: 600;
}

.panel-settings-form input {
  width: 100%;
  min-height: 42px;
  padding: 0 12px;
  border: 1px solid #d5deea;
  border-radius: 8px;
  outline: none;
  color: #273449;
  font: inherit;
  font-size: 14px;
  transition: border-color 140ms ease, box-shadow 140ms ease;
}

.panel-settings-form input:focus {
  border-color: #4a7df0;
  box-shadow: 0 0 0 3px rgb(74 125 240 / 15%);
}

.field-hint {
  margin: 7px 0 0;
  color: #8995a6;
  font-size: 11px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 9px;
  margin-top: 22px;
}

.dialog-actions button {
  min-width: 76px;
  min-height: 36px;
  padding: 0 13px;
  border: 1px solid #d7e0ec;
  border-radius: 8px;
  background: #fff;
  color: #57657a;
  font: inherit;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.dialog-actions .cancel-button:hover {
  background: #f7f9fc;
}

.dialog-actions .save-button {
  border-color: #2f65f5;
  background: #2f65f5;
  color: #fff;
}

.dialog-actions .save-button:hover {
  border-color: #2455dc;
  background: #2455dc;
}

@media (max-width: 760px) {
  .panel-bar {
    margin-right: -12px;
    margin-left: -12px;
    padding-right: 12px;
    padding-left: 12px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .panel-tab,
  .add-panel-button,
  .panel-settings-form input {
    transition: none;
  }
}
</style>
