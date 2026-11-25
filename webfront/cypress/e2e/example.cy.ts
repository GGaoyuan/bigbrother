describe('独立运行的 Webfront', () => {
  beforeEach(() => {
    cy.intercept('**/api/v1/**', { forceNetworkError: true })
  })

  it('后端不可用时通过侧栏直接切换页面', () => {
    cy.visit('/')
    cy.contains('h1', /^行情$/).should('be.visible')
    cy.get('aside [role="tablist"]').should('not.exist')
    cy.get('aside footer').should('not.exist')
    cy.get('aside a[aria-label="首页"] img').should('be.visible')

    cy.get('nav[aria-label="页面导航"]').within(() => {
      cy.get('a').should('have.length', 20)
      cy.get('a').first().should('contain.text', '行情').and('have.attr', 'aria-current', 'page')
      cy.contains('a', /^订单流$/).click()
    })
    cy.location('pathname').should('eq', '/order_flow')
    cy.contains('h1', /^订单流$/).should('be.visible')
    cy.go('back')
    cy.contains('h1', /^行情$/).should('be.visible')
  })

  it('侧栏单列显示，拖动右边缘时右侧内容同步调整', () => {
    cy.visit('/')

    cy.get('nav[aria-label="页面导航"] a').should((links) => {
      const first = links[0]!.getBoundingClientRect()
      const second = links[1]!.getBoundingClientRect()
      expect(second.left).to.equal(first.left)
      expect(second.top).to.be.at.least(first.bottom)
    })

    cy.get('[role="separator"][aria-label="调整侧栏宽度"]').then(($handle) => {
      const handle = $handle[0]!
      const startX = handle.getBoundingClientRect().left
      const initialWidth = handle.closest('aside')!.getBoundingClientRect().width
      cy.stub(handle, 'setPointerCapture')

      cy.wrap(handle).trigger('pointerdown', {
        eventConstructor: 'PointerEvent',
        pointerId: 1,
        isPrimary: true,
        button: 0,
        clientX: startX,
      })
      cy.wrap(handle).trigger('pointermove', {
        eventConstructor: 'PointerEvent',
        pointerId: 1,
        clientX: startX + 80,
      })
      cy.get('.sidebar').should(($sidebar) => {
        expect($sidebar[0]!.getBoundingClientRect().width).to.equal(initialWidth + 80)
      })
      cy.get('.main-content').should(($main) => {
        expect($main[0]!.getBoundingClientRect().left).to.equal(initialWidth + 80)
      })
      cy.wrap(handle).trigger('pointermove', {
        eventConstructor: 'PointerEvent',
        pointerId: 1,
        clientX: startX - 500,
      })
      cy.wrap(handle).trigger('pointerup', {
        eventConstructor: 'PointerEvent',
        pointerId: 1,
      })
      cy.wrap(handle).trigger('pointermove', {
        eventConstructor: 'PointerEvent',
        pointerId: 1,
        clientX: startX + 100,
      })
      cy.wrap(handle).should((separator) => {
        expect(separator.getAttribute('aria-valuenow')).to.equal(
          separator.getAttribute('aria-valuemin'),
        )
      })
    })
  })

  it('输入股票代码后更新足迹图，并可查看所选时段的模拟分笔', () => {
    cy.visit('/order_flow')
    cy.contains('模拟数据').should('be.visible')
    cy.contains('价位成交量').should('be.visible')
    cy.contains('累计 Delta').should('be.visible')
    cy.get('.footprint-cluster').should('have.length.greaterThan', 1)
    cy.get('input[name="stock-code"]').clear().type('000001')
    cy.contains('button', '查询').click()
    cy.get('figure[aria-label="订单流足迹图"]').should('contain.text', '000001')
    cy.get('.chart-scroll').scrollTo('right')
    cy.get('.footprint-cluster').last().click()
    cy.contains('caption', '000001 · 10:35 模拟分笔').should('be.visible')
    cy.get('.chart-scroll').scrollTo('left')
    cy.get('.footprint-cluster').first().click()
    cy.get('.footprint-cluster').first().should('have.attr', 'aria-pressed', 'true')
    cy.contains('caption', '000001 · 09:30').should('be.visible')
    cy.get('tbody tr').should('have.length.greaterThan', 0)
    cy.contains('th', '方向').should('be.visible')
    cy.get('input[name="stock-code"]').clear().type('123')
    cy.contains('button', '查询').click()
    cy.get('figure[aria-label="订单流足迹图"]').should('contain.text', '000001')
  })

  it('在 K 线主图创建并编辑选区，只在确认时更新成交量分布', () => {
    const chart = '[aria-label="K 线与成交量分布"]'
    const overlay = '[data-range-overlay]'
    const day = 86400
    const firstDay = Date.UTC(2026, 5, 1) / 1000 - 8 * 3600
    const prices = Array.from({ length: 90 }, (_, index) => {
      const timestamp = firstDay + index * day
      const close = 12.3 + index / 100
      return {
        timestamp,
        end_timestamp: timestamp + day,
        open: close - 0.02,
        high: close + 0.03,
        low: close - 0.04,
        close,
        volume: 456000,
        amount: 5824400,
      }
    })
    let coverageAvailable = true

    function requestedSymbol(url: string) {
      return new URL(url).pathname.split('/')[4]!
    }

    cy.intercept({
      method: 'GET',
      pathname: '/api/v1/stocks/*',
    }, (request) => {
      const symbol = requestedSymbol(request.url)
      request.reply({
        body: {
          code: 200,
          message: '',
          data: {
            symbol,
            name: symbol === '000001' ? '平安银行' : '贵州茅台',
            exchange: symbol === '000001' ? 'SZSE' : 'SSE',
            market: 'CN',
            currency: 'CNY',
            price_tick: 0.01,
            source: 'a-stock-data',
          },
        },
      })
    }).as('profileStock')
    cy.intercept({
      method: 'POST',
      pathname: '/api/v1/stocks/*/klines',
    }, (request) => {
      request.reply({
        body: {
          code: 200,
          message: '',
          data: {
            symbol: requestedSymbol(request.url),
            source: 'a-stock-data',
            adjust: 'qfq',
            adjustment_version: 'qfq-v1',
            bars: prices,
          },
        },
      })
    }).as('profileKlines')
    cy.intercept({
      method: 'POST',
      pathname: '/api/v1/stocks/*/volume-profile',
    }, (request) => {
      if (!coverageAvailable) {
        request.reply({
          statusCode: 409,
          body: {
            code: 409,
            message: '所选区间缺少 1 分钟 K 线',
            data: null,
          },
        })
        return
      }

      const level = {
        priceCents: 1285,
        lowPriceCents: 1283,
        highPriceCents: 1287,
        total: 45600,
        buy: 0,
        sell: 0,
        neutral: 0,
        unknown: 45600,
        delta: null,
        node: null,
      }
      request.reply({
        body: {
          code: 200,
          message: '',
          data: {
            symbol: requestedSymbol(request.url),
            source: 'mootdx',
            start: request.body.start,
            end: request.body.end,
            actual_start: request.body.start,
            actual_end: request.body.end,
            complete: true,
            calculation_method: 'estimated_1m_weighted_range',
            adjustment_version: 'qfq-v1',
            price_step: 0.05,
            profile: {
              levels: [
                level,
              ],
              poc: level,
              valueArea: {
                low: 1283,
                high: 1287,
                volume: level.total,
              },
              total: level.total,
              hasDirection: false,
            },
          },
        },
      })
    }).as('profileCalculation')

    function drag(selector: string, targetFraction: number, startFraction?: number) {
      cy.get(selector).then(($target) => {
        const target = $target[0]!
        const surface = target.closest(overlay) as HTMLElement
        const plot = surface.getBoundingClientRect()
        const marker = target.getBoundingClientRect()
        const from = startFraction === undefined ? marker.left + marker.width / 2
          : plot.left + plot.width * startFraction
        const end = plot.left + plot.width * targetFraction
        const y = plot.top + 120

        cy.wrap(target).trigger('pointerdown', {
          eventConstructor: 'PointerEvent',
          pointerId: 1,
          pointerType: 'mouse',
          isPrimary: true,
          button: 0,
          buttons: 1,
          clientX: from,
          clientY: y,
          force: true,
        })
        cy.wrap(surface).trigger('pointermove', {
          eventConstructor: 'PointerEvent',
          pointerId: 1,
          pointerType: 'mouse',
          isPrimary: true,
          clientX: end,
          clientY: y,
          force: true,
        })
        cy.wrap(surface).trigger('pointerup', {
          eventConstructor: 'PointerEvent',
          pointerId: 1,
          pointerType: 'mouse',
          isPrimary: true,
          clientX: end,
          clientY: y,
          force: true,
        })
      })
    }

    cy.visit('/')
    cy.contains('nav a', /^成交量分布图$/).click()
    cy.location('pathname').should('eq', '/volume-profile')
    cy.contains('h1', '成交量分布图').should('be.visible')
    cy.get('#profile-code').should('have.value', '')
    cy.get(chart).should('not.exist')
    cy.contains('button', '确认计算').should('not.exist')
    cy.get('@profileStock.all').should('have.length', 0)
    cy.get('@profileKlines.all').should('have.length', 0)
    cy.get('#profile-code').type('600519{enter}')
    cy.wait('@profileStock')
    cy.wait('@profileKlines').its('request.body').should('deep.equal', {
      interval: '1d',
    })
    cy.contains('贵州茅台').should('be.visible')
    cy.contains('前复权 K 线 · 腾讯行情 · a-stock-data').should('be.visible')
    cy.contains('估算型 Volume Profile · 基于 1 分钟 K 线').should('be.visible')
    cy.get('[role="group"][aria-label="K 线周期"] button').should('have.length', 3)
    cy.contains('模拟数据').should('not.exist')
    cy.get(chart).find('canvas').should('be.visible')
    cy.get('[aria-label="完整历史时间范围"]').should('not.exist')
    cy.get('[data-draft-range]').should('not.exist')
    cy.contains('button', '确认计算').should('be.disabled')

    cy.window().then((window) => {
      cy.stub(window.HTMLElement.prototype, 'setPointerCapture')
    })

    cy.get('.tool-button').should('contain.text', '固定区间成交量分布').click()
    cy.get(chart).invoke('attr', 'data-visible-from').then((visibleFrom) => {
      expect(visibleFrom).to.be.ok
      drag(overlay, 0.48, 0.22)

      cy.get('[data-range-part="start"]').should('be.visible')
      cy.get('[data-range-part="end"]').should('be.visible')
      cy.get('[data-profile-volume]').should('not.exist')
      cy.get('@profileCalculation.all').should('have.length', 0)
      cy.contains('button', '确认计算').click()
      cy.wait('@profileCalculation').its('request.body').should((body) => {
        expect(body).to.have.all.keys('start', 'end')
        expect(body.start).to.be.lessThan(body.end)
      })
      cy.get('[data-profile-volume]').should('be.visible')
      cy.get('[data-applied-range]').invoke('text').as('computedRange')
      cy.get('.tool-button').should('have.attr', 'aria-pressed', 'false').click()

      cy.get('[data-draft-range]').invoke('text').then((original) => {
        drag('[data-range-part="end"]', 0.62)
        cy.get('[data-draft-range]').should('not.have.text', original)
      })
      cy.get('[data-draft-range]').invoke('text').then((resized) => {
        drag('[data-range-part="selection"]', 0.5)
        cy.get('[data-draft-range]').should('not.have.text', resized)
      })

      cy.contains('选区已修改，尚未重新计算').should('be.visible')
      cy.get('@computedRange').then((computedRange) => {
        cy.get('[data-applied-range]').should('have.text', computedRange)
      })
      cy.get('[data-draft-range]').invoke('text').then((draft) => {
        coverageAvailable = false
        cy.contains('button', '确认计算').click()
        cy.wait('@profileCalculation')
        cy.contains('[role="status"]', '该区间的 1 分钟 K 线覆盖不足').should('be.visible')
        cy.get('.coverage-notice details').should('not.have.attr', 'open')
        cy.contains('summary', '查看数据源详情').click()
        cy.get('.coverage-notice details').should('have.attr', 'open')
        cy.contains('所选区间缺少 1 分钟 K 线').should('be.visible')
        cy.get('@computedRange').then((computedRange) => {
          cy.get('[data-applied-range]').should('have.text', computedRange)
        })
        cy.get('[data-draft-range]').should('have.text', draft)
        cy.then(() => {
          coverageAvailable = true
        })
        cy.contains('button', '确认计算').click()
        cy.wait('@profileCalculation')
        cy.get('[data-applied-range]').should('have.text', draft)
      })
      cy.get(chart).should('have.attr', 'data-visible-from', visibleFrom)
    })

    cy.get('[data-draft-range]').invoke('text').then((range) => {
      cy.contains('button', /^5 分钟$/).click()
      cy.wait('@profileKlines').its('request.body').should('deep.equal', {
        interval: '5m',
      })
      cy.contains('button', /^5 分钟$/).should('have.attr', 'aria-pressed', 'true')
      cy.get('[data-draft-range]').should('have.text', range)
      cy.get('[data-applied-range]').should('have.text', range)
      cy.get(overlay).should('be.visible')
      cy.contains('button', '取消选区').click()
      cy.get('[data-draft-range]').should('not.exist')
      cy.get('[data-applied-range]').should('have.text', range)
      cy.contains('button', '清除分布').click()
      cy.get('[data-profile-volume]').should('not.exist')
    })
    cy.get('.tool-button').click()
    cy.get(overlay).focus()
    cy.press(Cypress.Keyboard.Keys.ENTER)
    cy.get('[data-draft-range]').should('be.visible')
    cy.get('#profile-code').clear().type('000001')
    cy.contains('button', '查询').click()
    cy.wait('@profileStock')
    cy.wait('@profileKlines')
    cy.contains('.profile-chart-symbol', '000001').should('be.visible')
    cy.contains('平安银行').should('be.visible')
  })

  it('缺少接口的页面可以查看演示数据', () => {
    cy.visit('/market_sentiment')
    cy.contains('模拟数据').should('be.visible')
    cy.get('.grid-item').should('have.length.greaterThan', 0)

    cy.visit('/popularity/hot-rank')
    cy.contains('模拟数据').should('be.visible')
    cy.get('tbody tr').should('have.length.greaterThan', 0)

    cy.visit('/popularity/top-list')
    cy.contains('模拟数据').should('be.visible')
    cy.get('tbody tr').should('have.length.greaterThan', 0)

    cy.visit('/intraday_flow')
    cy.contains('模拟数据').should('be.visible')
    cy.contains('.grid-item', '人工智能').click()
    cy.contains('.legend-item', '人工智能').should('be.visible')
  })
})
