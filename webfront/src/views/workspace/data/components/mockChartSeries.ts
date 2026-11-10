export interface ChartPoint {
  date: string
  value: number
}

export interface ChartSeries {
  id: string
  name: string
  color: string
  side: 'left' | 'right'
  digits: number
  points: ChartPoint[]
}

interface Keyframe {
  date: string
  value: number
}

interface SeriesSeed {
  id: string
  name: string
  color: string
  side: 'left' | 'right'
  noise: number
  digits: number
  keyframes: Keyframe[]
}

const SERIES_SEEDS: SeriesSeed[] = [
  {
    id: 'hs300',
    name: '沪深300-收盘价',
    color: '#3d7ef0',
    side: 'left',
    noise: 12,
    digits: 0,
    keyframes: [
      { date: '2025-12-01', value: 4680 },
      { date: '2025-12-18', value: 4510 },
      { date: '2026-01-08', value: 4690 },
      { date: '2026-01-22', value: 4760 },
      { date: '2026-02-06', value: 4610 },
      { date: '2026-02-20', value: 4700 },
      { date: '2026-03-06', value: 4650 },
      { date: '2026-03-20', value: 4560 },
      { date: '2026-04-03', value: 4740 },
      { date: '2026-04-17', value: 4670 },
      { date: '2026-04-30', value: 4740 },
      { date: '2026-05-15', value: 4775 },
      { date: '2026-05-28', value: 4680 },
      { date: '2026-06-10', value: 4740 },
      { date: '2026-06-18', value: 4620 },
      { date: '2026-06-30', value: 4760 },
      { date: '2026-07-15', value: 4500 },
      { date: '2026-07-31', value: 4440 },
      { date: '2026-08-14', value: 4660 },
      { date: '2026-08-28', value: 4710 },
      { date: '2026-09-11', value: 4520 },
      { date: '2026-09-25', value: 4460 },
      { date: '2026-10-09', value: 4340 },
      { date: '2026-10-23', value: 4260 },
    ],
  },
  {
    id: 'wti',
    name: 'WTI原油现货',
    color: '#f0a024',
    side: 'right',
    noise: 1.6,
    digits: 2,
    keyframes: [
      { date: '2025-12-01', value: 74 },
      { date: '2025-12-19', value: 79 },
      { date: '2026-01-16', value: 83 },
      { date: '2026-02-13', value: 76 },
      { date: '2026-03-06', value: 81 },
      { date: '2026-03-27', value: 88 },
      { date: '2026-04-17', value: 84 },
      { date: '2026-05-15', value: 91 },
      { date: '2026-06-12', value: 86 },
      { date: '2026-07-10', value: 79 },
      { date: '2026-08-07', value: 83 },
      { date: '2026-09-04', value: 77 },
      { date: '2026-09-25', value: 82 },
      { date: '2026-10-23', value: 80 },
    ],
  },
  {
    id: 'shanghai',
    name: '上证指数-收盘价',
    color: '#2ea36a',
    side: 'left',
    noise: 10,
    digits: 0,
    keyframes: [
      { date: '2025-12-01', value: 4010 },
      { date: '2025-12-12', value: 3820 },
      { date: '2025-12-26', value: 3910 },
      { date: '2026-01-09', value: 3970 },
      { date: '2026-01-23', value: 4060 },
      { date: '2026-02-06', value: 3990 },
      { date: '2026-02-27', value: 4040 },
      { date: '2026-03-13', value: 4110 },
      { date: '2026-03-27', value: 3810 },
      { date: '2026-04-10', value: 4030 },
      { date: '2026-04-24', value: 4090 },
      { date: '2026-05-08', value: 4170 },
      { date: '2026-05-20', value: 4250 },
      { date: '2026-06-03', value: 4020 },
      { date: '2026-06-17', value: 3900 },
      { date: '2026-06-30', value: 4090 },
      { date: '2026-07-15', value: 3840 },
      { date: '2026-07-31', value: 3710 },
      { date: '2026-08-14', value: 3890 },
      { date: '2026-08-28', value: 3950 },
      { date: '2026-09-11', value: 3800 },
      { date: '2026-09-25', value: 3680 },
      { date: '2026-10-09', value: 3680 },
      { date: '2026-10-23', value: 3640 },
    ],
  },
  {
    id: 'us-cpi',
    name: '美国CPI',
    color: '#8d939c',
    side: 'right',
    noise: 0.06,
    digits: 1,
    keyframes: [
      { date: '2025-12-01', value: 325.2 },
      { date: '2026-01-15', value: 326.2 },
      { date: '2026-03-02', value: 328.1 },
      { date: '2026-04-15', value: 330.3 },
      { date: '2026-05-20', value: 331.5 },
      { date: '2026-06-18', value: 330.7 },
      { date: '2026-08-03', value: 332.3 },
      { date: '2026-09-15', value: 333.7 },
      { date: '2026-10-23', value: 334.4 },
    ],
  },
  {
    id: 'wti-2',
    name: 'WTI原油现货',
    color: '#a44bd4',
    side: 'right',
    noise: 1.8,
    digits: 2,
    keyframes: [
      { date: '2025-12-01', value: 62 },
      { date: '2026-01-09', value: 59 },
      { date: '2026-02-06', value: 63 },
      { date: '2026-02-27', value: 66 },
      { date: '2026-03-13', value: 94 },
      { date: '2026-03-27', value: 99 },
      { date: '2026-04-10', value: 110 },
      { date: '2026-04-24', value: 95 },
      { date: '2026-05-08', value: 113 },
      { date: '2026-05-22', value: 101 },
      { date: '2026-06-05', value: 106 },
      { date: '2026-06-19', value: 84 },
      { date: '2026-07-03', value: 77 },
      { date: '2026-07-17', value: 81 },
      { date: '2026-07-31', value: 72 },
      { date: '2026-08-14', value: 68 },
      { date: '2026-08-28', value: 88 },
      { date: '2026-09-11', value: 96 },
      { date: '2026-09-25', value: 84 },
      { date: '2026-10-09', value: 101 },
      { date: '2026-10-23', value: 106 },
    ],
  },
]

function weekdayDates(start: string, end: string): string[] {
  const dates: string[] = []
  const cursor = new Date(`${start}T00:00:00`)
  const last = new Date(`${end}T00:00:00`)

  while (cursor.getTime() <= last.getTime()) {
    const day = cursor.getDay()
    if (day !== 0 && day !== 6) {
      const year = cursor.getFullYear()
      const month = String(cursor.getMonth() + 1).padStart(2, '0')
      const date = String(cursor.getDate()).padStart(2, '0')
      dates.push(`${year}-${month}-${date}`)
    }
    cursor.setDate(cursor.getDate() + 1)
  }

  return dates
}

function parseDate(value: string): number {
  return new Date(`${value}T00:00:00`).getTime()
}

function interpolate(keyframes: Keyframe[], date: string): number {
  const time = parseDate(date)
  const first = keyframes[0]
  const last = keyframes[keyframes.length - 1]

  if (!first || !last) {
    return 0
  }

  if (time <= parseDate(first.date)) {
    return first.value
  }

  if (time >= parseDate(last.date)) {
    return last.value
  }

  for (let index = 1; index < keyframes.length; index += 1) {
    const current = keyframes[index]
    const previous = keyframes[index - 1]
    if (!current || !previous) {
      continue
    }

    if (time <= parseDate(current.date)) {
      const span = parseDate(current.date) - parseDate(previous.date)
      const ratio = span === 0 ? 0 : (time - parseDate(previous.date)) / span
      return previous.value + (current.value - previous.value) * ratio
    }
  }

  return last.value
}

function wave(index: number, amplitude: number, seed: number): number {
  return (
    Math.sin(index / 2.7 + seed) * amplitude * 0.55 +
    Math.sin(index / 1.35 + seed * 1.6) * amplitude * 0.3 +
    Math.sin(index / 6.4 + seed * 0.45) * amplitude * 0.15
  )
}

function buildMockSeries(seeds: SeriesSeed[]): ChartSeries[] {
  const dates = weekdayDates('2025-12-01', '2026-10-23')

  return seeds.map((seed, seriesIndex) => ({
    id: seed.id,
    name: seed.name,
    color: seed.color,
    side: seed.side,
    digits: seed.digits,
    points: dates.map((date, index) => ({
      date,
      value: Number(
        (
          interpolate(seed.keyframes, date) +
          wave(index, seed.noise, seriesIndex + seed.name.length)
        ).toFixed(seed.digits),
      ),
    })),
  }))
}

export const mockChartSeries: ChartSeries[] = buildMockSeries(SERIES_SEEDS)
