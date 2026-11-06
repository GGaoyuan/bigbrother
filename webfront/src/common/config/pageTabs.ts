import { PAGE_ID, type PageId } from './ids'

export interface PageTabConfig {
  id: PageId;
  name: string;
  path: string;
}

export const PAGE_TABS: PageTabConfig[] = [
  { id: PAGE_ID.MARKET_QUOTES, name: '行情', path: '/' },
  { id: PAGE_ID.MARKET_SENTIMENT, name: '市场情绪', path: '/market_sentiment' },
  { id: PAGE_ID.TODAY_MARKET, name: '今日大盘', path: '/today' },
  { id: PAGE_ID.MARKET_ANOMALY, name: '大盘异动', path: '/market_anomaly' },
  { id: PAGE_ID.RECAP_MARKET, name: '市场面', path: '/recap' },
  { id: PAGE_ID.RECAP_INDICATORS, name: '指标面', path: '/recap/indicators' },
  { id: PAGE_ID.RECAP_MACRO, name: '宏观经济', path: '/recap/macro' },
  { id: PAGE_ID.RECAP_DIVIDEND_YIELD, name: '股息率测算', path: '/recap/dividend_yield' },
  { id: PAGE_ID.RECAP_HEATMAP, name: '热力图（复盘）', path: '/recap/heatmap' },
  { id: PAGE_ID.RECAP_SECTOR, name: '板块分析', path: '/recap/sector' },
  { id: PAGE_ID.HEATMAP_THEME, name: '题材热力图', path: '/heatmap/theme' },
  { id: PAGE_ID.HEATMAP_INDUSTRY, name: '行业热力图', path: '/heatmap/industry' },
  { id: PAGE_ID.HEATMAP_CHANGE, name: '涨跌热力图', path: '/heatmap/change' },
  { id: PAGE_ID.TIMELINE, name: '时间轴', path: '/timeline' },
  { id: PAGE_ID.THEME_LIBRARY, name: '题材库', path: '/theme_lib' },
  { id: PAGE_ID.ORDER_FLOW, name: '订单流', path: '/order_flow' },
  { id: PAGE_ID.INTRADAY_FLOW, name: '分时资金流', path: '/intraday_flow' },
  { id: PAGE_ID.TOP_LIST, name: '龙虎榜统计', path: '/popularity/top-list' },
  { id: PAGE_ID.HOT_RANK, name: '热榜', path: '/popularity/hot-rank' },
]
