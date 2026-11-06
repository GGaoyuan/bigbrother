import { DATA_CATEGORY_ID, METRIC_ID, type DataCategoryId, type MetricId } from './ids'

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

export const DATA_CATEGORIES: DataCategoryConfig[] = [
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
  ]

export const METRICS: MetricConfig[] = [
    { id: METRIC_ID.CLOSE, label: '收盘价' },
    { id: METRIC_ID.OPEN, label: '开盘价' },
    { id: METRIC_ID.HIGH, label: '最高价' },
    { id: METRIC_ID.LOW, label: '最低价' },
    { id: METRIC_ID.VOLUME, label: '成交量' },
    { id: METRIC_ID.AMOUNT, label: '成交额' },
    { id: METRIC_ID.CHANGE_PERCENT, label: '涨跌幅' },
  ]
