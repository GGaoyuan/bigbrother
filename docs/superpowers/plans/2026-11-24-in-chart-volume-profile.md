# 主图内固定区间成交量分布实施方案

复用 Webfront 的 Lightweight Charts 5.2.0、成交量分布 Primitive、逐笔计算和两个行情适配器。选区迁入主图并移除底部时间选择器。

1. 核对 5.2.0 的绘图区尺寸、逻辑索引坐标和可见范围订阅。图表保持现有五种周期、轴和缩放方式。
2. 新增 `RangeSelectionOverlay.vue` 与 `chartRangeSelection.ts`。覆盖层绘制草稿区间，识别边界、内部和图表空白区域。工具开启时捕获拖动，关闭后让指针回到图表。
3. 将 `VolumeProfileChart.vue` 接入覆盖层，通过图表时间轴重投影选区。持久范围使用 Unix 秒的半开区间。切换周期保留原时间，仅显式拖动时吸附到新周期。
4. 保留 `VolumeProfilePrimitive.ts` 的价位绘制。通过 `useHistoricalProfile.ts` 保持草稿和已确认区间独立。退出工具保留草稿，取消撤销草稿，清除移除已确认结果，确认才读取逐笔。
5. 更新范围映射、状态及浏览器测试。验收创建、改边、整体拖动、确认、取消和清除，核对主图缩放、平移和价格轴变化后的坐标。更新 README 和 PRD。
