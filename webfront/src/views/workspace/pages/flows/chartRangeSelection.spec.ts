import { describe, expect, it } from 'vitest'
import {
  candleIndicesForRange,
  formatSelectionEdge,
  projectSelection,
  rangeForDrag,
} from './chartRangeSelection'

const candles = [
  {
    start: 100,
    end: 200,
  },
  {
    start: 230,
    end: 330,
  },
  {
    start: 330,
    end: 430,
  },
  {
    start: 450,
    end: 550,
  },
]

describe('主图选区', () => {
  it('按半开时间范围查找相交的蜡烛，跳过交易间隔', () => {
    expect(candleIndicesForRange(candles, {
      start: 230,
      end: 330,
    })).toEqual({
      first: 1,
      last: 1,
    })
    expect(candleIndicesForRange(candles, {
      start: 200,
      end: 230,
    })).toBeNull()
  })

  it('以半根 K 线为视觉边界，只在实际边界可见时显示手柄', () => {
    const range = {
      start: 100,
      end: 430,
    }
    const result = projectSelection(candles, range, 50, (index) =>
      Number.isInteger(index) ? index * 20 - 5 : 0,
    )
    expect(result).toEqual({
      left: 0,
      right: 45,
      startVisible: false,
      endVisible: true,
    })
    expect(projectSelection(candles, range, 50, (index) => index * 20 - 90)).toBeNull()
  })

  it('点击选中单根 K 线，反向拖动按照时间顺序建立选区', () => {
    expect(rangeForDrag(candles, 'create', 2, 2, null)).toEqual({
      start: 330,
      end: 430,
    })
    expect(rangeForDrag(candles, 'create', 2, 0, null)).toEqual({
      start: 100,
      end: 430,
    })
  })

  it('拖动单端时保留另一端的实际细周期时间，端点不会相互越过', () => {
    const original = {
      start: 125,
      end: 370,
    }
    expect(rangeForDrag(candles, 'start', 0, 0, original)).toBe(original)
    expect(rangeForDrag(candles, 'start', 0, 3, original)).toEqual({
      start: 330,
      end: 370,
    })
    expect(rangeForDrag(candles, 'end', 2, 0, original)).toEqual({
      start: 125,
      end: 200,
    })
  })

  it('整体拖动保留蜡烛根数并夹紧完整历史边界', () => {
    const original = {
      start: 240,
      end: 370,
    }
    expect(rangeForDrag(candles, 'selection', 1, 8, original)).toEqual({
      start: 330,
      end: 550,
    })
    expect(rangeForDrag(candles, 'selection', 1, -4, original)).toEqual({
      start: 100,
      end: 330,
    })
  })

  it('独立显示上海时间和日线的最后一个包含日期', () => {
    const timestamp = (value: string) => Date.parse(value) / 1000
    expect(formatSelectionEdge(timestamp('2026-11-20T09:35:00+08:00'), 'start'))
      .toBe('2026-11-20 09:35')
    expect(formatSelectionEdge(timestamp('2026-11-20T14:00:00+08:00'), 'end'))
      .toBe('2026-11-20 14:00')
    expect(formatSelectionEdge(timestamp('2026-11-21T00:00:00+08:00'), 'end'))
      .toBe('2026-11-20')
  })
})
