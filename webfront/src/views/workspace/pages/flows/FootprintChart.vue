<script setup lang="ts">
import { computed } from 'vue'
import { formatPrice, formatTime, type Footprint, type PriceLevel } from './footprint'

const props = defineProps<{
  code: string
  data: Footprint
  selectedStart: number | null
}>()

const emit = defineEmits<{
  select: [start: number]
}>()

const maximumPrice = computed(() => props.data.profile[0]?.priceCents ?? 0)
const maximumVolume = computed(() => Math.max(1, props.data.poc?.total ?? 0))
const maximumDelta = computed(() => Math.max(
  1,
  ...props.data.periods.map((period) => Math.abs(period.cumulativeDelta)),
))

const volumeFormat = new Intl.NumberFormat('zh-CN')
const signedFormat = new Intl.NumberFormat('zh-CN', {
  signDisplay: 'exceptZero',
})

function rowPosition(price: number) {
  return `calc(${maximumPrice.value - price} * var(--row-height))`
}

function levelTitle(level: PriceLevel) {
  return `${formatPrice(level.priceCents)} 元 · 主动卖 ${level.sell} 手 · 主动买 ${level.buy} 手 · 中性 ${level.neutral} 手`
}
</script>

<template>
  <figure class="footprint" aria-label="订单流足迹图">
    <figcaption class="figure-heading">
      <div class="instrument">
        <strong class="stock-code">{{ code }}</strong>
        <span class="period-badge">5 分钟</span>
        <span v-if="data.lastTrade" class="last-price">
          {{ formatPrice(data.lastTrade.priceCents) }} <small>元</small>
        </span>
      </div>

      <div class="legend">
        <span class="sell-key">主动卖出（左）</span>
        <span class="buy-key">主动买入（右）</span>
        <span class="neutral-key">中性</span>
      </div>
    </figcaption>

    <div
      class="chart-layout"
      :style="{
        '--period-count': data.periods.length,
        '--row-count': data.profile.length,
      }"
    >
      <div class="chart-scroll" tabindex="0" aria-label="订单流图表 · 可横向滚动">
        <div class="chart-main">
          <div class="plot-heading">足迹图 · 手</div>
          <div class="price-plot">
            <div
              v-if="data.poc"
              class="poc-line"
              :style="{ top: rowPosition(data.poc.priceCents) }"
              aria-hidden="true"
            ></div>
            <div
              v-for="period in data.periods"
              :key="period.start"
              class="period-lane"
              :class="{ 'is-selected': selectedStart === period.start }"
            >
              <button
                v-if="period.levels.length"
                type="button"
                class="footprint-cluster"
                :style="{ top: rowPosition(period.levels[0]!.priceCents) }"
                :aria-label="`${formatTime(period.start)}，Delta ${signedFormat.format(period.delta)} 手，查看分笔`"
                :aria-pressed="selectedStart === period.start"
                @click="emit('select', period.start)"
              >
                <span
                  v-for="level in period.levels"
                  :key="level.priceCents"
                  class="footprint-row"
                  :title="levelTitle(level)"
                >
                  <span :class="{ 'sell-dominant': level.sell > Math.max(level.buy * 2, 40) }">
                    {{ level.sell }}
                  </span>
                  <span :class="{ 'buy-dominant': level.buy > Math.max(level.sell * 2, 40) }">
                    {{ level.buy }}
                  </span>
                </span>
                <span
                  class="period-delta"
                  :class="period.delta >= 0 ? 'positive' : 'negative'"
                >
                  {{ signedFormat.format(period.delta) }}
                </span>
              </button>
            </div>
          </div>

          <div class="delta-section">
            <div class="delta-heading">
              累计 Delta <strong>{{ signedFormat.format(data.cumulativeDelta) }} 手</strong>
            </div>
            <div class="delta-plot">
              <div
                v-for="period in data.periods"
                :key="period.start"
                class="delta-cell"
                :class="{ 'is-selected': selectedStart === period.start }"
                :title="`${formatTime(period.start)} · 累计 Delta ${signedFormat.format(period.cumulativeDelta)} 手`"
              >
                <span
                  class="delta-bar"
                  :class="period.cumulativeDelta >= 0 ? 'positive' : 'negative'"
                  :style="{ height: `${Math.abs(period.cumulativeDelta) / maximumDelta * 48}%` }"
                ></span>
              </div>
            </div>
          </div>

          <div class="time-axis">
            <span v-for="period in data.periods" :key="period.start">
              {{ formatTime(period.start) }}
            </span>
          </div>
        </div>

      </div>

      <div class="profile">
        <div class="plot-heading">价位成交量</div>
        <div class="profile-plot">
          <div
            v-for="level in data.profile"
            :key="level.priceCents"
            class="profile-row"
            :class="{ 'is-poc': level.priceCents === data.poc?.priceCents }"
            :title="`${levelTitle(level)} · 合计 ${volumeFormat.format(level.total)} 手`"
          >
            <span class="profile-track">
              <span
                class="profile-bar"
                :style="{ width: `${level.total / maximumVolume * 100}%` }"
              >
                <span class="profile-sell" :style="{ flexGrow: level.sell }"></span>
                <span class="profile-neutral" :style="{ flexGrow: level.neutral }"></span>
                <span class="profile-buy" :style="{ flexGrow: level.buy }"></span>
              </span>
            </span>
            <span
              v-if="level.priceCents === data.poc?.priceCents"
              class="axis-price poc-price"
              title="成交量最大的价位（POC）"
            >{{ formatPrice(level.priceCents) }}</span>
            <span v-else-if="level.priceCents % 5 === 0" class="axis-price">
              {{ formatPrice(level.priceCents) }}
            </span>
          </div>
        </div>
        <div v-if="data.poc" class="profile-foot">
          <span>POC {{ formatPrice(data.poc.priceCents) }}</span>
          <span>{{ volumeFormat.format(data.poc.total) }} 手</span>
        </div>
      </div>
    </div>
  </figure>
</template>

<style scoped>
.footprint {
  --surface: #161d30;
  --surface-raised: #1b2540;
  --rule: #2d3952;
  --muted-ink: #a5b4cb;
  --buy: #ef7773;
  --sell: #66c7a1;
  --poc: #e5b662;
  min-width: 0;
  margin: 0;
  border: 1px solid var(--rule);
  border-radius: 9px;
  background: var(--surface);
  color: #edf2fa;
  font-variant-numeric: tabular-nums;
}

.figure-heading,
.instrument,
.legend {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px 14px;
}

.figure-heading {
  justify-content: space-between;
  min-height: 54px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--rule);
  border-radius: 9px 9px 0 0;
  background: var(--surface-raised);
}

.stock-code,
.last-price {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', monospace;
}

.stock-code {
  font-size: 18px;
  letter-spacing: 0.03em;
}

.period-badge,
.last-price small,
.legend {
  font-size: 11px;
  color: var(--muted-ink);
}

.last-price {
  color: #f6d496;
  font-size: 15px;
}

.legend span::before {
  display: inline-block;
  width: 6px;
  height: 6px;
  margin-right: 5px;
  border-radius: 1px;
  background: currentColor;
  content: '';
  vertical-align: 1px;
}

.sell-key {
  color: var(--sell);
}

.buy-key {
  color: var(--buy);
}

.chart-scroll {
  overflow-x: auto;
  scrollbar-color: #526687 var(--surface);
}

.chart-scroll:focus-visible {
  outline: 2px solid #8fb0fc;
  outline-offset: -2px;
}

.chart-layout {
  --row-height: clamp(11px, calc((100dvh - 270px) / var(--row-count)), 17px);
  --columns: repeat(var(--period-count), minmax(0, 1fr));
  --profile-width: clamp(102px, 13vw, 164px);
  display: grid;
  grid-template-columns: minmax(0, 1fr) var(--profile-width);
}

.chart-main {
  min-width: calc(var(--period-count) * 3.55rem);
}

.plot-heading {
  height: 30px;
  padding: 6px 10px;
  border-bottom: 1px solid var(--rule);
  color: var(--muted-ink);
  font-size: 11px;
}

.price-plot {
  position: relative;
  display: grid;
  grid-template-columns: var(--columns);
  height: calc(var(--row-height) * var(--row-count));
  background-image: repeating-linear-gradient(
    to bottom,
    transparent 0 calc(var(--row-height) * 5 - 1px),
    var(--rule) calc(var(--row-height) * 5 - 1px) calc(var(--row-height) * 5)
  );
}

.period-lane {
  position: relative;
  min-width: 0;
  border-right: 1px solid var(--rule);
}

.period-lane.is-selected,
.delta-cell.is-selected {
  background-color: #263757;
}

.poc-line {
  position: absolute;
  z-index: 1;
  inset-inline: 0;
  height: var(--row-height);
  border-block: 1px solid #e5b66252;
  background: #e5b66214;
  pointer-events: none;
}

.footprint-cluster {
  position: absolute;
  z-index: 2;
  inset-inline: 3px;
  display: block;
  width: calc(100% - 6px);
  padding: 0;
  border: 0;
  outline: 1px solid #75849d;
  background: #182238;
  color: inherit;
  cursor: pointer;
  font: 10px/1 'SFMono-Regular', Consolas, 'Liberation Mono', monospace;
  font-variant-numeric: tabular-nums;
  text-align: center;
}

.footprint-cluster:hover,
.footprint-cluster:focus-visible,
.footprint-cluster[aria-pressed='true'] {
  outline-color: #a6c2ff;
  outline-width: 2px;
}

.footprint-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  height: var(--row-height);
  background: #1b2941;
}

.footprint-row:nth-child(even) {
  background: #202e46;
}

.footprint-row:hover {
  outline: 1px solid #a6c2ff;
  outline-offset: -1px;
}

.footprint-row > span {
  display: grid;
  place-items: center;
}

.footprint-row > span + span {
  border-left: 1px solid #8393b354;
}

.footprint-row .sell-dominant {
  background: #26473f;
  color: #97f3cf;
}

.footprint-row .buy-dominant {
  background: #542e3a;
  color: #ffaaa7;
}

.period-delta {
  position: absolute;
  inset: 100% 0 auto;
  padding-top: 3px;
  font-size: 9px;
}

.period-delta.positive {
  color: var(--buy);
}

.period-delta.negative {
  color: var(--sell);
}

.delta-section {
  padding-top: 5px;
  border-top: 1px solid var(--rule);
}

.delta-heading {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 10px 0;
  color: var(--muted-ink);
  font-size: 11px;
}

.delta-heading strong {
  color: #edf2fa;
  font-weight: 600;
}

.delta-plot,
.time-axis {
  display: grid;
  grid-template-columns: var(--columns);
}

.delta-plot {
  height: 58px;
  background: linear-gradient(
    transparent calc(50% - 1px),
    var(--rule) calc(50% - 1px) 50%,
    transparent 50%
  );
}

.delta-cell {
  position: relative;
  border-right: 1px solid var(--rule);
}

.delta-bar {
  position: absolute;
  inset-inline: 19%;
  opacity: 0.78;
}

.delta-bar.positive {
  bottom: 50%;
  background: var(--buy);
}

.delta-bar.negative {
  top: 50%;
  background: var(--sell);
}

.time-axis {
  border-top: 1px solid var(--rule);
  color: var(--muted-ink);
  font: 10px/1.15 'SFMono-Regular', Consolas, 'Liberation Mono', monospace;
  text-align: center;
  white-space: nowrap;
}

.time-axis span {
  padding: 8px 0;
  border-right: 1px solid var(--rule);
}

.profile {
  min-width: 0;
  border-left: 1px solid var(--rule);
  background: var(--surface);
}

.profile-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 40px;
  align-items: center;
  height: var(--row-height);
  padding-right: 5px;
}

.profile-row:nth-child(5n + 1) {
  background: #202b41;
}

.profile-row.is-poc {
  background: #453a30;
}

.profile-track,
.profile-bar {
  display: flex;
  justify-content: flex-end;
  height: calc(var(--row-height) - 3px);
}

.profile-sell {
  background: #4a9f80;
}

.profile-buy {
  background: #cc655f;
}

.profile-neutral {
  background: #8592a8;
}

.axis-price {
  color: var(--muted-ink);
  font: 9px/1 'SFMono-Regular', Consolas, 'Liberation Mono', monospace;
  text-align: right;
  white-space: nowrap;
}

.poc-price {
  color: var(--poc);
}

.profile-foot {
  display: grid;
  gap: 2px;
  padding: 9px;
  border-top: 1px solid var(--rule);
  color: var(--poc);
  font-size: 10px;
  white-space: nowrap;
}
</style>
