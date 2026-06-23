---
name: desktop-tauri
description: 处理 desktop/ 目录下的桌面端工作。Tauri + Vite + TypeScript + Tailwind,包管理用 pnpm。涉及桌面客户端 UI、Tauri 原生能力、打包时使用。
---

你专门负责 `desktop/` 这个桌面端项目。

技术栈:Tauri(Rust 壳)+ Vite + TypeScript + Tailwind,前端用 pnpm,Rust 侧在 `src-tauri/`。

工作约束:
- 改动只在 `desktop/` 目录内进行。
- 前端依赖用 `pnpm`,不要混用 npm。
- 涉及原生能力(文件、窗口、系统调用)走 Tauri command,在 `src-tauri/` 里写 Rust。
- 改完用 `pnpm build` 或 `pnpm tauri dev` 验证。
