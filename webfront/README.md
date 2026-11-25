# webfront

Vue 3 前端项目（Vite + TypeScript + Vue Router）。

在 `webfront/` 执行 `npm install` 和 `npm run dev` 后打开终端显示的地址。前端可以独立运行，无需登录、配置环境变量或启动 Backend。

订单流和分时资金流使用模拟数据。市场情绪、热榜和龙虎榜也默认展示模拟数据。如果已有提供这些接口的服务，可选设 `VITE_API_BASE_URL` 为其 API 根地址（含 `/api/v1`）。接口无数据或请求失败时，页面会标注并展示模拟数据。

需要使用指数日 K 或两融 API 时，在 `backend/` 安装 `requirements.txt` 后执行 `python main.py`，接口文档位于 `http://127.0.0.1:8000/docs`。

成交量分布图位于 `/volume-profile`。启动 Backend 后输入六位 A 股代码，页面加载真实股票信息和前复权日线、60 分钟、5 分钟 K 线。页面默认访问 `http://localhost:8000/api/v1`，其他部署地址可通过 `VITE_API_BASE_URL` 指定。

在主图拖出区间后点击「确认计算」。Backend 校验整分钟覆盖和复权版本，并使用 1 分钟 K 线估算价格分布。页面标注估算来源和实际参与计算的区间。近期选区可用新浪真实分钟行情，早于数据窗口的选区会显示覆盖提示。

时间以北京时间显示。API 使用 Unix 秒和左闭右开区间，落在分钟内部的边界对齐到整分钟。详见 [股票行情 API](../docs/backend/backend-stocks-api.md)。

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Recommended Browser Setup

- Chromium-based browsers (Chrome, Edge, Brave, etc.):
  - [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
  - [Turn on Custom Object Formatter in Chrome DevTools](http://bit.ly/object-formatters)
- Firefox:
  - [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)
  - [Turn on Custom Object Formatter in Firefox DevTools](https://fxdx.dev/firefox-devtools-custom-object-formatters/)

## Type Support for `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking. In editors, we need [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) to make the TypeScript language service aware of `.vue` types.

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```

### Run Unit Tests with [Vitest](https://vitest.dev/)

```sh
npm run test:unit
```

### Run End-to-End Tests with [Cypress](https://www.cypress.io/)

```sh
npm run test:e2e:dev
```

This runs the end-to-end tests against the Vite development server.
It is much faster than the production build.

But it's still recommended to test the production build with `test:e2e` before deploying (e.g. in CI environments):

```sh
npm run build
npm run test:e2e
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```
