import { PAGE_ID, type PageId } from './ids'

export const PAGE_ROUTE_NAMES: Record<PageId, string[]> = {
  [PAGE_ID.MARKET_QUOTES]: ['marketQuotes'],
  [PAGE_ID.MARKET_SENTIMENT]: ['marketSentiment'],
  [PAGE_ID.TODAY_MARKET]: ['todayMarket'],
  [PAGE_ID.MARKET_ANOMALY]: ['marketAnomaly'],
  [PAGE_ID.RECAP_MARKET]: ['recapMarket'],
  [PAGE_ID.RECAP_INDICATORS]: ['recapIndicators'],
  [PAGE_ID.RECAP_MACRO]: ['recapMacro'],
  [PAGE_ID.RECAP_DIVIDEND_YIELD]: ['recapDividendYield'],
  [PAGE_ID.RECAP_HEATMAP]: ['recapHeatmap'],
  [PAGE_ID.RECAP_SECTOR]: ['recapSectorTab1', 'recapSectorTab2', 'recapSectorTab3'],
  [PAGE_ID.HEATMAP_THEME]: ['heatmapTheme'],
  [PAGE_ID.HEATMAP_INDUSTRY]: ['heatmapIndustry'],
  [PAGE_ID.HEATMAP_CHANGE]: ['heatmapChange'],
  [PAGE_ID.TIMELINE]: ['timeline'],
  [PAGE_ID.THEME_LIBRARY]: ['themeLibrary'],
  [PAGE_ID.ORDER_FLOW]: ['orderFlow'],
  [PAGE_ID.INTRADAY_FLOW]: ['intradayFlow'],
  [PAGE_ID.TOP_LIST]: ['topList'],
  [PAGE_ID.HOT_RANK]: ['hotRank'],
}
