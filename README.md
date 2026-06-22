# ccprompt-and-hooks

Claude Code 提示词(skills)与 hooks 的可移植配置集,用于在多台机器间快速复用同一套
工作流约束与自动化。

## 目录

| 路径 | 内容 |
|------|------|
| `building-claude-code-hooks/` | **skill**:如何创建/注册/调试 Claude Code hook(stdin/退出码/settings.json/模板)。装到 `~/.claude/skills/` 后自动可用。 |
| `general-agent-operating-guidelines/` | **skill**:每次对话的基线操作规则(安全、拒答、语气、检索引用、工具与文件处理、子代理、记忆、环境感知)。 |
| `planning-with-files/` | **skill**:文件化持久规划(`task_plan.md`/`findings.md`/`progress.md` 落盘),`/clear` 或上下文丢失后可恢复。来源 [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files)。 |
| `planning-with-files-zh/` | **skill**:`planning-with-files` 的中文版。 |
| `caveman/` | **skill**:极简输出模式,砍 ~75% token 同时保留技术准确性。支持 `lite/full/ultra` 及文言文档。来源 [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)。 |
| `hooks/` | 一套 8 项 hook 脚本 + `README.md`(逐项说明 + 脱敏的 settings.json 注册片段)。 |
| `CLAUDE-FABLE-5.md` | 参考用的大段系统提示词文档。 |

## 快速使用

- **装 skill**:把 `building-claude-code-hooks/`、`general-agent-operating-guidelines/`
  整个拷到 `~/.claude/skills/` 下;在 Claude Code 里用 `Skill` 工具按名调用。
- **装 hooks**:见 `hooks/README.md`,把脚本拷到 `~/.claude/hooks/`,并把脱敏注册片段
  合并进你的 `~/.claude/settings.json`。
- **每次对话自动加载基线 skill**:在 `~/.claude/CLAUDE.md` 写一条规则要求开场调用
  `using-superpowers` + `general-agent-operating-guidelines`;并用 `SessionStart` hook
  (`hooks/inject-bootstrap-skills.py`)做代码级强制注入。再加 `UserPromptSubmit` hook
  (`hooks/remind-bootstrap-skills.py`)每轮注入精简指针兜底,扛过 `/compact` 压缩与
  `--resume` 续接。

## 安全须知

本仓库**不含任何真实密钥**。`settings.json` 注册示例中的 token 一律为占位符 `<YOU>` /
省略。在自己的机器上套用时,真实 token 只放在本地 `~/.claude/settings.json`,**切勿提交**。
