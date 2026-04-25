# Micro-Scholar 全局开发规范

## 1. 技术栈约束
- **语言**: Python 3.10+
- **UI 库**: PySide6 (用于跨平台桌面展示)
- **数据存储**: SQLite3 (用于存储飞书缓存和技术词库)
- **飞书接入**: 使用 `lark-oapi` 官方 SDK
- **依赖管理**: 必须提供 requirements.txt

## 2. 内存与性能红线
- **禁止实时拉取**: 所有碎片内容必须从本地 SQLite 获取。
- **低功耗监听**: 进程监听器的轮询间隔不得低于 1s，且必须在后台低优先级运行。
- **UI 渲染**: 窗口需支持透明度，且不得阻塞主程序逻辑。

## 3. 命名与代码风格
- 变量/函数: `snake_case` (如 `sync_feishu_docs`)
- 类名: `PascalCase` (如 `FeishuDataManager`)
- 飞书 Token 变量名: 必须使用 `FEISHU_APP_ID`, `FEISHU_APP_SECRET`, `FEISHU_FOLDER_TOKEN`

## 4. 异常处理
- 飞书 API 调用必须包含 `try-except` 和 `Retrying` 机制。
- 若本地数据库为空，UI 应显示“请先同步飞书笔记”的占位信息而非报错。