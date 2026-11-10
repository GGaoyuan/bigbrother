import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mount, type VueWrapper } from '@vue/test-utils'
import type { ECharts } from 'echarts'
import DataChart from './DataChart.vue'
import { mockChartSeries } from './mockChartSeries'

const state = vi.hoisted(() => ({
  chart: null as ECharts | null,
}))

vi.mock('echarts', async (importOriginal) => {
  const actual = await importOriginal<typeof import('echarts')>()
  return {
    ...actual,
    init: (element: HTMLElement) => {
      state.chart = actual.init(element, undefined, {
        renderer: 'svg',
        width: 1000,
        height: 540,
      })
      return state.chart
    },
  }
})

let wrapper: VueWrapper | undefined

function axisOpacities(): number[] {
  const axes = state.chart!.getOption().yAxis as {
    axisLine: {
      lineStyle: {
        opacity?: number
      }
    }
    axisLabel: {
      opacity?: number
    }
  }[]
  return axes.map((axis) => {
    const opacity = axis.axisLabel.opacity ?? 1
    expect(axis.axisLine.lineStyle.opacity ?? 1).toBe(opacity)
    return opacity
  })
}

beforeEach(() => {
  vi.stubGlobal('ResizeObserver', class {
    observe() {}
    disconnect() {}
  })
  vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({
    measureText: (text: string) => ({
      width: text.length * 7,
    }),
  } as unknown as CanvasRenderingContext2D)
  wrapper = mount(DataChart)
})

afterEach(() => {
  wrapper?.unmount()
  state.chart = null
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
})

describe('legend axis focus', () => {
  it('dims other axes on highlight and restores them on downplay', () => {
    const focused = mockChartSeries[1]!
    state.chart!.dispatchAction({
      type: 'highlight',
      seriesName: focused.id,
    })
    expect(axisOpacities()).toEqual(mockChartSeries.map((spec) => (
      spec.id === focused.id ? 1 : 0.1
    )))

    state.chart!.dispatchAction({
      type: 'downplay',
      seriesName: focused.id,
    })
    expect(axisOpacities()).toEqual(mockChartSeries.map(() => 1))
  })

  it('keeps a deselected axis hidden and does not focus its legend item', () => {
    const hidden = mockChartSeries[0]!
    state.chart!.dispatchAction({
      type: 'legendToggleSelect',
      name: hidden.id,
    })
    state.chart!.dispatchAction({
      type: 'highlight',
      seriesName: hidden.id,
    })
    const axes = state.chart!.getOption().yAxis as {
      show: boolean
    }[]
    expect(axes[0]!.show).toBe(false)
    expect(axisOpacities()).toEqual(mockChartSeries.map(() => 1))
  })
})
