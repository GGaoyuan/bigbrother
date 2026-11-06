export const WORKSPACE_TYPE = {
  DATA: 'data',
  AI: 'ai',
  PAGES: 'pages',
} as const

export const WORKSPACE_ID = {
  DATA: 'workspace-data',
  AI: 'workspace-ai',
  PAGES: 'workspace-pages',
} as const

export const CONTAINER_TYPE = {
  DATA: 'data',
  AI: 'ai',
  ROUTE: 'route',
} as const

export const DATA_CATEGORY_ID = {
  A_SHARE: 'a-share-equities',
  A_INDEX: 'a-share-indices',
  A_VALUATION: 'a-share-index-valuations',
  MARGIN: 'margin-trading',
} as const

export const METRIC_ID = {
  CLOSE: 'close',
  OPEN: 'open',
  HIGH: 'high',
  LOW: 'low',
  VOLUME: 'volume',
  AMOUNT: 'amount',
  CHANGE_PERCENT: 'change-percent',
} as const

export const PAGE_ID = {
  MARKET_QUOTES: 'market-quotes',
  MARKET_SENTIMENT: 'market-sentiment',
  TODAY_MARKET: 'today-market',
  MARKET_ANOMALY: 'market-anomaly',
  RECAP_MARKET: 'recap-market',
  RECAP_INDICATORS: 'recap-indicators',
  RECAP_MACRO: 'recap-macro',
  RECAP_DIVIDEND_YIELD: 'recap-dividend-yield',
  RECAP_HEATMAP: 'recap-heatmap',
  RECAP_SECTOR: 'recap-sector',
  HEATMAP_THEME: 'heatmap-theme',
  HEATMAP_INDUSTRY: 'heatmap-industry',
  HEATMAP_CHANGE: 'heatmap-change',
  TIMELINE: 'timeline',
  THEME_LIBRARY: 'theme-library',
  ORDER_FLOW: 'order-flow',
  INTRADAY_FLOW: 'intraday-flow',
  TOP_LIST: 'top-list',
  HOT_RANK: 'hot-rank',
} as const

export type WorkspaceType = (typeof WORKSPACE_TYPE)[keyof typeof WORKSPACE_TYPE]
export type WorkspaceId = (typeof WORKSPACE_ID)[keyof typeof WORKSPACE_ID]
export type DataCategoryId = (typeof DATA_CATEGORY_ID)[keyof typeof DATA_CATEGORY_ID]
export type MetricId = (typeof METRIC_ID)[keyof typeof METRIC_ID]
export type PageId = (typeof PAGE_ID)[keyof typeof PAGE_ID]

export interface WorkspaceTabConfig {
  id: WorkspaceId;
  type: WorkspaceType;
  label: string;
  containerTitle: string;
}

export interface PageConfig {
  id: PageId;
  type: typeof CONTAINER_TYPE.ROUTE;
  label: string;
  path: string;
  routeNames: string[];
}

export interface DataSeriesConfig {
  id: string;
  label: string;
  code: string;
  categoryLabel: string;
}

export interface DataCategoryConfig {
  id: DataCategoryId;
  type: string;
  label: string;
  icon: string;
  series: DataSeriesConfig[];
}

export interface MetricConfig {
  id: MetricId;
  label: string;
}

export interface AppConfig {
  workspaces: WorkspaceTabConfig[];
  sidebar: {
    homeLabel: string;
    workspacesLabel: string;
    dataCategoriesLabel: string;
    marketDataLabel: string;
    marketDataHint: string;
    selectSeriesHint: string;
    searchPlaceholder: string;
    noResultsLabel: string;
    seriesNameLabel: string;
    seriesCodeLabel: string;
    metricsLabel: string;
    metricHint: string;
    addToChartLabel: string;
    pageNavigationLabel: string;
    pageCountSuffix: string;
    aiPlaceholderTitle: string;
    aiPlaceholderDescription: string;
    dataPageDescription: string;
    dataPagePlaceholder: string;
    footerLabel: string;
    footerVersion: string;
  };
  dataCategories: DataCategoryConfig[];
  metrics: MetricConfig[];
  pages: PageConfig[];
}

export const PROJECT_CONFIG: AppConfig = {
  workspaces: [
    {
      id: WORKSPACE_ID.DATA,
      type: WORKSPACE_TYPE.DATA,
      label: '数据',
      containerTitle: '数据工作台',
    },
    {
      id: WORKSPACE_ID.AI,
      type: WORKSPACE_TYPE.AI,
      label: 'AI',
      containerTitle: 'AI 工作区',
    },
    {
      id: WORKSPACE_ID.PAGES,
      type: WORKSPACE_TYPE.PAGES,
      label: '页面',
      containerTitle: '页面导航',
    },
  ],
  sidebar: {
    homeLabel: '首页',
    workspacesLabel: '工作区',
    dataCategoriesLabel: '数据类别',
    marketDataLabel: '数据源',
    marketDataHint: 'MARKET DATA',
    selectSeriesHint: '选择数据系列并添加到图表',
    searchPlaceholder: '搜索数据名称或代码',
    noResultsLabel: '没有匹配的数据',
    seriesNameLabel: '名称',
    seriesCodeLabel: '代码',
    metricsLabel: '指标',
    metricHint: '选择一个指标',
    addToChartLabel: '添加到图表',
    pageNavigationLabel: '页面导航',
    pageCountSuffix: 'PAGES',
    aiPlaceholderTitle: 'AI 工作区',
    aiPlaceholderDescription: '在这里开始探索市场数据',
    dataPageDescription: '从左侧数据分类选择数据系列，添加后在这里进行展示。',
    dataPagePlaceholder: '数据图表容器',
    footerLabel: '数据工作台',
    footerVersion: 'v1.0',
  },
  dataCategories: [
    {
      id: DATA_CATEGORY_ID.A_SHARE,
      type: 'equity',
      label: 'A股个股',
      icon: '◉',
      series: [
        { id: '600519.SH', label: '贵州茅台', code: '600519.SH', categoryLabel: '白酒' },
        { id: '300750.SZ', label: '宁德时代', code: '300750.SZ', categoryLabel: '电池' },
        { id: '601318.SH', label: '中国平安', code: '601318.SH', categoryLabel: '保险' },
        { id: '002594.SZ', label: '比亚迪', code: '002594.SZ', categoryLabel: '汽车' },
      ],
    },
    {
      id: DATA_CATEGORY_ID.A_INDEX,
      type: 'index',
      label: 'A股指数',
      icon: '▥',
      series: [
        { id: '000001.SH', label: '上证指数', code: '000001.SH', categoryLabel: '上交所' },
        { id: '399001.SZ', label: '深证成指', code: '399001.SZ', categoryLabel: '深交所' },
        { id: '000300.SH', label: '沪深300', code: '000300.SH', categoryLabel: '宽基指数' },
        { id: '399006.SZ', label: '创业板指', code: '399006.SZ', categoryLabel: '深交所' },
      ],
    },
    {
      id: DATA_CATEGORY_ID.A_VALUATION,
      type: 'valuation',
      label: 'A股指数估值',
      icon: '◷',
      series: [
        { id: '300-pe-ttm', label: '沪深300 PE-TTM', code: '000300.SH', categoryLabel: '市盈率' },
        {
          id: '000001-pe-ttm',
          label: '上证指数 PE-TTM',
          code: '000001.SH',
          categoryLabel: '市盈率',
        },
        { id: '000905-pb', label: '中证500 PB', code: '000905.SH', categoryLabel: '市净率' },
      ],
    },
    {
      id: DATA_CATEGORY_ID.MARGIN,
      type: 'margin',
      label: '融资融券',
      icon: '↗',
      series: [
        { id: 'FIN.MARGIN', label: '两市融资余额', code: 'FIN.MARGIN', categoryLabel: '融资余额' },
        { id: 'SH.MARGIN', label: '沪市融资余额', code: 'SH.MARGIN', categoryLabel: '上交所' },
        { id: 'SZ.MARGIN', label: '深市融资余额', code: 'SZ.MARGIN', categoryLabel: '深交所' },
      ],
    },
  ],
  metrics: [
    { id: METRIC_ID.CLOSE, label: '收盘价' },
    { id: METRIC_ID.OPEN, label: '开盘价' },
    { id: METRIC_ID.HIGH, label: '最高价' },
    { id: METRIC_ID.LOW, label: '最低价' },
    { id: METRIC_ID.VOLUME, label: '成交量' },
    { id: METRIC_ID.AMOUNT, label: '成交额' },
    { id: METRIC_ID.CHANGE_PERCENT, label: '涨跌幅' },
  ],
  pages: [
    {
      id: PAGE_ID.MARKET_QUOTES,
      type: CONTAINER_TYPE.ROUTE,
      label: '行情',
      path: '/',
      routeNames: ['marketQuotes'],
    },
    {
      id: PAGE_ID.MARKET_SENTIMENT,
      type: CONTAINER_TYPE.ROUTE,
      label: '市场情绪',
      path: '/market_sentiment',
      routeNames: ['marketSentiment'],
    },
    {
      id: PAGE_ID.TODAY_MARKET,
      type: CONTAINER_TYPE.ROUTE,
      label: '今日大盘',
      path: '/today',
      routeNames: ['todayMarket'],
    },
    {
      id: PAGE_ID.MARKET_ANOMALY,
      type: CONTAINER_TYPE.ROUTE,
      label: '大盘异动',
      path: '/market_anomaly',
      routeNames: ['marketAnomaly'],
    },
    {
      id: PAGE_ID.RECAP_MARKET,
      type: CONTAINER_TYPE.ROUTE,
      label: '市场面',
      path: '/recap',
      routeNames: ['recapMarket'],
    },
    {
      id: PAGE_ID.RECAP_INDICATORS,
      type: CONTAINER_TYPE.ROUTE,
      label: '指标面',
      path: '/recap/indicators',
      routeNames: ['recapIndicators'],
    },
    {
      id: PAGE_ID.RECAP_MACRO,
      type: CONTAINER_TYPE.ROUTE,
      label: '宏观经济',
      path: '/recap/macro',
      routeNames: ['recapMacro'],
    },
    {
      id: PAGE_ID.RECAP_DIVIDEND_YIELD,
      type: CONTAINER_TYPE.ROUTE,
      label: '股息率测算',
      path: '/recap/dividend_yield',
      routeNames: ['recapDividendYield'],
    },
    {
      id: PAGE_ID.RECAP_HEATMAP,
      type: CONTAINER_TYPE.ROUTE,
      label: '热力图（复盘）',
      path: '/recap/heatmap',
      routeNames: ['recapHeatmap'],
    },
    {
      id: PAGE_ID.RECAP_SECTOR,
      type: CONTAINER_TYPE.ROUTE,
      label: '板块分析',
      path: '/recap/sector',
      routeNames: ['recapSectorTab1', 'recapSectorTab2', 'recapSectorTab3'],
    },
    {
      id: PAGE_ID.HEATMAP_THEME,
      type: CONTAINER_TYPE.ROUTE,
      label: '题材热力图',
      path: '/heatmap/theme',
      routeNames: ['heatmapTheme'],
    },
    {
      id: PAGE_ID.HEATMAP_INDUSTRY,
      type: CONTAINER_TYPE.ROUTE,
      label: '行业热力图',
      path: '/heatmap/industry',
      routeNames: ['heatmapIndustry'],
    },
    {
      id: PAGE_ID.HEATMAP_CHANGE,
      type: CONTAINER_TYPE.ROUTE,
      label: '涨跌热力图',
      path: '/heatmap/change',
      routeNames: ['heatmapChange'],
    },
    {
      id: PAGE_ID.TIMELINE,
      type: CONTAINER_TYPE.ROUTE,
      label: '时间轴',
      path: '/timeline',
      routeNames: ['timeline'],
    },
    {
      id: PAGE_ID.THEME_LIBRARY,
      type: CONTAINER_TYPE.ROUTE,
      label: '题材库',
      path: '/theme_lib',
      routeNames: ['themeLibrary'],
    },
    {
      id: PAGE_ID.ORDER_FLOW,
      type: CONTAINER_TYPE.ROUTE,
      label: '订单流',
      path: '/order_flow',
      routeNames: ['orderFlow'],
    },
    {
      id: PAGE_ID.INTRADAY_FLOW,
      type: CONTAINER_TYPE.ROUTE,
      label: '分时资金流',
      path: '/intraday_flow',
      routeNames: ['intradayFlow'],
    },
    {
      id: PAGE_ID.TOP_LIST,
      type: CONTAINER_TYPE.ROUTE,
      label: '龙虎榜统计',
      path: '/popularity/top-list',
      routeNames: ['topList'],
    },
    {
      id: PAGE_ID.HOT_RANK,
      type: CONTAINER_TYPE.ROUTE,
      label: '热榜',
      path: '/popularity/hot-rank',
      routeNames: ['hotRank'],
    },
  ],
}
