# Webfront 固定区间成交量分布实施方案

Webfront 延续 Vue、TypeScript、Vue Router 和现有 Axios 请求层。Desktop 已使用 Lightweight Charts 5.2，Webfront 在成交量分布页复用该版本。FastAPI 当前的指数和两融接口不足以提供个股历史逐笔，演示数据由独立适配器提供并显式标注来源。

## 坐标和数据契约

- 主图视窗由 Lightweight Charts 管理。选区更新只重绘时间标记，保留主图的平移、时间缩放和价格缩放。
- 缩略图使用完整的日级历史，起点包含、结束时间为排他边界。K 线周期切换期间按时间戳保留日级选区。
- 统计结果绑定确认时的代码与区间。价格以整数分统计，数量以股统计，绘图使用同一根 K 线系列的价格坐标。
- 配置 `VITE_API_BASE_URL` 时，用 `GET /api/v1/market/profile/history` 读取 K 线及完整缩略历史，用 `GET /api/v1/market/profile/trades` 按区间读取逐笔。未配置时使用浏览器模拟适配器。两个适配器分别保证自身的 K 线与逐笔一致。

## 实施步骤

1. **主图**。在 Webfront 加入 Lightweight Charts 5.2，重写 `VolumeProfileChart.vue`，验证五种周期、拖动、缩放与十字光标。
2. **选择器**。新增 `HistoricalRangeSelector.vue`、`historicalRange.ts` 与边界测试，支持触屏、鼠标和键盘调整两个手柄及整体选区。
3. **统计与绘制**。改写 `volumeProfile.ts` 和单元测试，新增 `VolumeProfilePrimitive.ts`。逐笔按价位聚合数量和方向，计算 POC、覆盖至少 70% 的连续价值区及局部成交量节点。价格缩放后继续调用主图价格转换。
4. **确认流程**。新增 `profileMarketData.ts`、`profileMarketMock.ts`、`useHistoricalProfile.ts`。改写 `VolumeProfileView.vue`，接入确认、取消和加载失败处理。后端在 `profile_market.py` 与模拟数据模块中提供同契约接口。
5. **验收**。运行 Webfront 单元测试、生产构建、Cypress 和 Backend 单元测试。使用浏览器实际拖动选区和主图、缩放价格轴及切换周期，核对统计结果与视窗独立。同步 `prd/v1.md` 和 Webfront 启动说明。
