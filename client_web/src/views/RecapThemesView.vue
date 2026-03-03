<script setup lang="ts">
import { ref, computed } from 'vue'

interface TimelineItem {
  time: string
  title: string
  content: string
  /** 匹配的月份 1–12，当前月份在此范围内则高亮 */
  months?: number[]
}

const timelineItems = ref<TimelineItem[]>([
  { time: '11月底～12月初', title: '春节题材布局', content: '消费+农业+电影。消费、农业可能是小坑，电影是大坑。布局要在11月底12月初就开始。', months: [11, 12] },
  { time: '春节前后', title: '消费 + 农业 + 电影', content: '消费农业可能是小坑，电影是大坑。', months: [1, 2] },
  { time: '1月', title: '三月开会埋伏', content: '三月开会题材有点敏感，不说了，反正别碰；想参与的1月份就要埋伏了。', months: [1] },
  { time: '3月', title: '开会期间', content: '别碰，想参与需提前埋伏。', months: [3] },
  { time: '春节～4月', title: '年报季 · 绩优股', content: '4月要出年报了，一般经验是远离概念题材股，拥抱绩优股，春节就要埋伏了。', months: [1, 2, 3, 4] },
  { time: '3月～4月中旬', title: '五一假期题材', content: '5月要放假了，旅游+电影+消费三大坑。老样子，三月埋伏，四月就要跑了，现在跑的越来越快，最晚最晚四月中旬一定要跑。放假回来黄花菜都凉了。', months: [3, 4] },
  { time: '5月', title: '旅游 + 电影 + 消费', content: '五一假期相关，需提前在3月埋伏、4月中旬前跑。', months: [5] },
  { time: '五一放假回来', title: '夏季伏笔', content: '6月天气热了，空调、电、煤。五一放假回来就能埋伏了。', months: [5] },
  { time: '6月', title: '空调、电、煤', content: '天气热了，空调、电、煤。五一回来就能埋伏。', months: [6] },
  { time: '6月', title: '暑假旅游埋伏', content: '7月8月暑假来了，旅游旺季。六月就要埋伏了，最晚八月中就要跑。', months: [6] },
  { time: '7月～8月', title: '暑假旅游旺季', content: '旅游旺季，六月埋伏，最晚八月中跑。', months: [7, 8] },
  { time: '7月', title: '国庆题材埋伏', content: '9月10月国庆要来了，军工、电影。七月提前埋伏，国庆前半个月跑。为啥提前这么多？老6太多了，你得跑前面。', months: [7] },
  { time: '9月～10月', title: '国庆 · 军工 + 电影', content: '国庆前半个月跑，跑在前面。', months: [9, 10] },
  { time: '十一', title: '双11埋伏', content: '11月双11，电商物流什么的。十一埋伏，双11跑。', months: [10] },
  { time: '11月', title: '双11 · 电商物流', content: '十一埋伏，双11跑。', months: [11] },
  { time: '双11', title: '年末题材埋伏', content: '12月天冷了，燃气煤炭、绩优股，还有基金业绩排名的传说。双11埋伏，兑现就跑。', months: [11] },
  { time: '12月', title: '燃气、煤炭、绩优股', content: '天冷了，燃气煤炭，绩优股，基金业绩排名。双11埋伏，兑现就跑。', months: [12] },
  { time: '备注', title: '世界杯', content: '世界杯可能会利好啤酒（大家喝酒撸串）。' },
  { time: '', title: '说明', content: '以上不是教你投机，而是告诉你，投机也要有方法。这些个烂大街的套路不一定赚得上钱，总比你傻傻的追热点强。' },
])

const currentMonth = computed(() => new Date().getMonth() + 1)

function isCurrentNode(item: TimelineItem): boolean {
  if (!item.months || item.months.length === 0) return false
  return item.months.includes(currentMonth.value)
}

// 常规时间轴：按具体日期展示的事件
interface RegularTimelineEntry {
  date: string
  title: string
  content: string
}

const regularTimelineEntries = ref<RegularTimelineEntry[]>([
  { date: '2025-01-02', title: '元旦后首个交易日', content: '可关注节后资金回流与开门红预期。' },
  { date: '2025-02-10', title: '春节前', content: '节前效应，交投或趋淡。' },
  { date: '2025-03-05', title: '重要会议窗口', content: '政策与行业表述受关注。' },
  { date: '2025-04-30', title: '年报披露收官', content: '业绩落地，注意业绩雷与高送转。' },
  { date: '2025-05-01', title: '五一假期', content: '休市。' },
  { date: '2025-06-01', title: '六月开局', content: '可关注夏季相关题材布局。' },
  { date: '2025-09-01', title: '开学季', content: '教育、消费等板块或有机会。' },
  { date: '2025-10-01', title: '国庆', content: '休市。' },
  { date: '2025-11-11', title: '双十一', content: '电商、物流等题材兑现窗口。' },
  { date: '2025-12-31', title: '年末收官', content: '基金排名、机构调仓等影响盘面。' },
])
</script>

<template>
  <div class="themes-page">
    <h1 class="page-title">时间轴</h1>

    <div class="timeline-layout">
      <section class="timeline-panel timeline-panel--annual">
        <h2 class="panel-title">年度题材时间轴</h2>
        <p class="panel-desc">按月份梳理的常见题材与埋伏节奏。当前 <span class="current-month-tag">{{ currentMonth }} 月</span> 相关节点已高亮。</p>
        <div class="timeline">
          <div
            v-for="(item, index) in timelineItems"
            :key="index"
            class="timeline-item"
            :class="{ 'timeline-item--current': isCurrentNode(item) }"
          >
            <div class="timeline-marker" />
            <div class="timeline-content" :class="{ 'timeline-content--current': isCurrentNode(item) }">
              <div v-if="item.time" class="timeline-time">{{ item.time }}</div>
              <h3 class="timeline-title">{{ item.title }}</h3>
              <p class="timeline-text">{{ item.content }}</p>
            </div>
          </div>
        </div>
      </section>

      <section class="timeline-panel timeline-panel--regular">
        <h2 class="panel-title">常规时间轴</h2>
        <p class="panel-desc">按日期排列的重要节点与事件。</p>
        <div class="timeline-regular">
          <div
            v-for="(entry, index) in regularTimelineEntries"
            :key="index"
            class="regular-item"
          >
            <div class="regular-item-marker" />
            <div class="regular-item-body">
              <div class="regular-item-date">{{ entry.date }}</div>
              <h3 class="regular-item-title">{{ entry.title }}</h3>
              <p class="regular-item-text">{{ entry.content }}</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.themes-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 60vh;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-heading);
  margin-bottom: 1.25rem;
}

.timeline-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  align-items: stretch;
  height: calc(100vh - 140px);
  min-height: 400px;
}

.timeline-panel {
  min-width: 0;
  min-height: 0;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  background: var(--color-background-soft);
  padding: 1.25rem;
  overflow-y: auto;
}

.panel-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--color-heading);
  margin-bottom: 0.35rem;
}

.panel-desc {
  font-size: 0.85rem;
  color: var(--color-text);
  opacity: 0.85;
  margin-bottom: 1.25rem;
}

.timeline {
  position: relative;
  padding-left: 1.5rem;
  border-left: 2px solid var(--color-border);
  margin-left: 0.5rem;
}

.timeline-item {
  position: relative;
  padding-bottom: 1.75rem;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-marker {
  position: absolute;
  left: -1.5rem;
  top: 0.4rem;
  width: 10px;
  height: 10px;
  margin-left: -5px;
  border-radius: 50%;
  background: #1565c0;
  border: 2px solid var(--color-background);
  box-sizing: content-box;
}

.timeline-content {
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem 1.25rem;
}

.timeline-time {
  font-size: 0.8rem;
  font-weight: 600;
  color: #1565c0;
  margin-bottom: 0.35rem;
}

.timeline-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--color-heading);
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.timeline-text {
  font-size: 0.9rem;
  color: var(--color-text);
  line-height: 1.6;
  margin: 0;
  opacity: 0.9;
}

.current-month-tag {
  font-weight: 600;
  color: #1565c0;
}

.timeline-item--current .timeline-marker {
  background: #2e7d32;
  width: 12px;
  height: 12px;
  margin-left: -6px;
  box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.25);
}

.timeline-content--current {
  border-color: #2e7d32;
  background: rgba(46, 125, 50, 0.06);
  box-shadow: 0 0 0 1px rgba(46, 125, 50, 0.15);
}

.timeline-content--current .timeline-time {
  color: #2e7d32;
}

/* 常规时间轴 */
.timeline-regular {
  position: relative;
  padding-left: 1.5rem;
  border-left: 2px solid var(--color-border);
  margin-left: 0.5rem;
}

.regular-item {
  position: relative;
  padding-bottom: 1.25rem;
}

.regular-item:last-child {
  padding-bottom: 0;
}

.regular-item-marker {
  position: absolute;
  left: -1.5rem;
  top: 0.35rem;
  width: 10px;
  height: 10px;
  margin-left: -5px;
  border-radius: 50%;
  background: #5c6bc0;
  border: 2px solid var(--color-background);
  box-sizing: content-box;
}

.regular-item-body {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 0.9rem 1rem;
}

.regular-item-date {
  font-size: 0.8rem;
  font-weight: 600;
  color: #5c6bc0;
  margin-bottom: 0.25rem;
  font-family: ui-monospace, monospace;
}

.regular-item-title {
  font-size: 0.98rem;
  font-weight: 600;
  color: var(--color-heading);
  margin-bottom: 0.35rem;
  line-height: 1.4;
}

.regular-item-text {
  font-size: 0.85rem;
  color: var(--color-text);
  line-height: 1.5;
  margin: 0;
  opacity: 0.9;
}

@media (max-width: 900px) {
  .timeline-layout {
    grid-template-columns: 1fr;
  }
}
</style>
