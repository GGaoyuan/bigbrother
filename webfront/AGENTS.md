# Webfront 代码格式约定

- TypeScript 的对象类型与接口字段逐行书写。
- 对象字面量使用多行格式，每个属性独占一行。
- 数组中的对象或值逐项书写，每项独占一行；不要把短对象或短数组压成一行。
- Vue 单文件组件保留清晰的多行 `script`、`template`、`style` 结构。
- CSS 选择器、花括号和每条声明分别占行，不压缩成单行规则。
- 修改已有文件时，遵循以上格式整理所触及的代码；不要顺手重排无关实现。
- UI 配置数据以 YAML 或 JSON 为源文件，不在 TypeScript 模块里拼装配置对象。
- `src/common/config/config.yaml` 保存 `workspace` 与 `pages`；`config.ts` 按 interface 解析这两组数组，并导出全局共享的 `config` 对象。
- 数据 Tab 的内容单独保存在 `src/views/sidebar/data/data.json`，由数据工作区组件直接读取。
