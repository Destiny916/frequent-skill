# 在新机器上复现这套 Claude Code 配置

本指南说明如何在另一台机器上,从零复现本仓库提供的整套配置:
**2 个开场 bootstrap skill + 全局每次对话规则 + 8 个生命周期 hook**。

适用平台:Windows(主),文末附 macOS/Linux 差异。前置:已安装 Claude Code、Python 3、git。

> 本仓库结构(根目录平铺):
> - `building-claude-code-hooks/` — 构建 hooks 的 skill
> - `general-agent-operating-guidelines/` — 基线操作规则 skill
> - `superpowers-main/` — superpowers 套件(含 `using-superpowers` 等)
> - `andrej-karpathy-skills-main/`、`backup_skills/` — 其它 skill 备份
> - `hooks/` — 8 个 hook 脚本 + 说明
> - `CLAUDE-FABLE-5.md` — 参考用系统提示词文档

---

## 0. 全局目录约定

| 用途 | Windows | macOS/Linux |
|------|---------|-------------|
| skills 根 | `C:\Users\<YOU>\.claude\skills\` | `~/.claude/skills/` |
| hooks 根 | `C:\Users\<YOU>\.claude\hooks\` | `~/.claude/hooks/` |
| 全局规则 | `C:\Users\<YOU>\.claude\CLAUDE.md` | `~/.claude/CLAUDE.md` |
| 全局设置 | `C:\Users\<YOU>\.claude\settings.json` | `~/.claude/settings.json` |

下文 `<YOU>` 替换为你的用户名。

---

## 1. 拉取本仓库

```bash
git clone https://github.com/Destiny916/frequent-skill.git
cd frequent-skill
```

> 直连 GitHub 受限时:
> - clone 走镜像:URL 换成 `https://gh-proxy.com/https://github.com/Destiny916/frequent-skill.git`(镜像仅供 clone/fetch,不支持 push)。
> - 有本地代理(如 Clash 端口 7897)时,push 用:`git -c http.proxy=http://127.0.0.1:7897 push origin main`。

---

## 2. 安装 skills

把这些 skill 目录拷到 `~/.claude/skills/`:

```powershell
# Windows PowerShell
$dst = "C:\Users\<YOU>\.claude\skills"
Copy-Item "building-claude-code-hooks"          "$dst\" -Recurse -Force
Copy-Item "general-agent-operating-guidelines"  "$dst\" -Recurse -Force
# using-superpowers 等来自 superpowers 套件:
Copy-Item "superpowers-main\skills\*"           "$dst\" -Recurse -Force
```

```bash
# macOS/Linux
cp -r building-claude-code-hooks          ~/.claude/skills/
cp -r general-agent-operating-guidelines  ~/.claude/skills/
cp -r superpowers-main/skills/*           ~/.claude/skills/
```

> SessionStart 注入需要 `using-superpowers` 与 `general-agent-operating-guidelines` 两个 skill
> 都在 `~/.claude/skills/`;缺失项脚本会静默跳过。

---

## 3. 安装 hooks 脚本

```powershell
# Windows
$h = "C:\Users\<YOU>\.claude\hooks"
New-Item -ItemType Directory -Force -Path $h | Out-Null
Copy-Item "hooks\*.py"  "$h\" -Force
Copy-Item "hooks\*.ps1" "$h\" -Force
```

```bash
# macOS/Linux
mkdir -p ~/.claude/hooks
cp hooks/*.py  ~/.claude/hooks/
# notify-stop.ps1 仅 Windows;mac/Linux 见第 6 节替换
```

可选:`pip install black`(供 PostToolUse 格式化 hook 使用,缺了会静默跳过)。

---

## 4. 配置全局规则 CLAUDE.md

在 `~/.claude/CLAUDE.md` 写入(若已存在,追加 `## Baseline skills` 段):

```markdown
# Global Operating Rules

## Baseline skills — every conversation

At the start of **every** conversation, before selecting any task-specific skill,
invoke these two bootstrap skills (via the Skill tool) and let them govern the
whole session:

1. `using-superpowers` — establishes how to find and use skills; requires checking
   for any applicable skill (even a 1% chance) and invoking it before any response.
2. `general-agent-operating-guidelines` — baseline behavior for safety, refusals,
   tone, freshness/search, citations, tool/file handling, skill selection, subagent
   delegation, memory, and environment awareness.

Invoke `using-superpowers` first, then `general-agent-operating-guidelines`.

- Invoke each once per conversation; do not re-invoke if already loaded this session.
- When dispatching a task-specific subagent, pass `general-agent-operating-guidelines`;
  per its <SUBAGENT-STOP> clause such a subagent skips `using-superpowers`.
- User instructions always take precedence over skills.
```

这一层是**软指令**:把规则注入每个会话,提示 agent 调用 skill。

---

## 5. 注册 hooks 到 settings.json

把下面的 `hooks` 段**合并**进 `~/.claude/settings.json`(已有 settings 就只加/合并 `hooks`
键,**不要覆盖整文件**;路径里 `<YOU>` 换成你的用户名,反斜杠保持 `\\`)。

```jsonc
{
  // env / permissions / model 等保持你自己的;真实 token 只留本地,切勿提交
  "hooks": {
    "PreToolUse": [
      { "matcher": "Edit|Write", "hooks": [
        { "type": "command", "command": "python \"C:\\Users\\<YOU>\\.claude\\hooks\\backup-before-edit.py\"" } ] },
      { "matcher": "Bash", "hooks": [
        { "type": "command", "command": "python \"C:\\Users\\<YOU>\\.claude\\hooks\\dangerous-command-blocker.py\"" },
        { "type": "command", "command": "python \"C:\\Users\\<YOU>\\.claude\\hooks\\secret-scanner.py\"" } ] },
      { "matcher": "Write", "hooks": [
        { "type": "command", "if": "Write(.env*)", "command": "echo {\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"Writing to .env files is blocked by hook\"}}" } ] }
    ],
    "SessionStart": [
      { "matcher": "", "hooks": [
        { "type": "command", "command": "python \"C:\\Users\\<YOU>\\.claude\\hooks\\inject-bootstrap-skills.py\"" } ] }
    ],
    "PostToolUse": [
      { "matcher": "Edit|Write", "hooks": [
        { "type": "command", "command": "python \"C:\\Users\\<YOU>\\.claude\\hooks\\format-python-files.py\"" } ] }
    ],
    "Stop": [
      { "matcher": "", "hooks": [
        { "type": "command", "command": "powershell -NoProfile -ExecutionPolicy Bypass -File \"C:\\Users\\<YOU>\\.claude\\hooks\\notify-stop.ps1\"" } ] }
    ],
    "UserPromptSubmit": [
      { "matcher": "", "hooks": [
        { "type": "command", "command": "python \"C:\\Users\\<YOU>\\.claude\\hooks\\remind-bootstrap-skills.py\"" } ] }
    ]
  }
}
```

`SessionStart` hook(`inject-bootstrap-skills.py`)是**代码级强制**:每个新会话启动时把两个
skill 全文注入上下文,不依赖 agent 是否主动调用。它与第 4 节的软规则形成**双保险**。

`UserPromptSubmit` hook(`remind-bootstrap-skills.py`)是**每轮兜底**:SessionStart 只在会话
开头注一次全文,且 `/compact` 压缩后会丢、`--resume` 续接可能不触发。本 hook 在**每次提交**注入
一条 ~150 token 的精简指针(重申规则 + skill 名 + "全文丢了就从 `~/.claude/skills/` 回读"),
成本低且能扛过压缩/续接。组合效果:**开场全文一次 + 之后每轮指针在场**。

### 8 个 hook 速查

| # | 事件 / matcher | 脚本 | 作用 |
|---|----------------|------|------|
| 1 | PreToolUse / `Edit\|Write` | `backup-before-edit.py` | 编辑前备份原文件 |
| 2 | PreToolUse / `Bash` | `dangerous-command-blocker.py` | 三级拦截危险命令 |
| 3 | PreToolUse / `Bash` | `secret-scanner.py` | commit 前扫描密钥 |
| 4 | PreToolUse / `Write`(`if`) | (内联 echo) | 禁止写 `.env*` |
| 5 | SessionStart / `""` | `inject-bootstrap-skills.py` | 注入两个基线 skill 全文 |
| 6 | PostToolUse / `Edit\|Write` | `format-python-files.py` | `.py` 跑 black |
| 7 | Stop / `""` | `notify-stop.ps1` | 桌面通知 |
| 8 | UserPromptSubmit / `""` | `remind-bootstrap-skills.py` | 每轮注入基线 skill 精简指针 |

各 hook 详细说明见 `hooks/README.md`。

---

## 6. macOS/Linux 差异

- 所有 `python "C:\\...\\x.py"` 改为 `python3 "$HOME/.claude/hooks/x.py"`(含
  `remind-bootstrap-skills.py`)。`remind-bootstrap-skills.py` 跨平台通用,§3 的
  `cp hooks/*.py` 会自动带上它。
- `notify-stop.ps1`(Stop 通知)无法直接用;换等价命令:
  - mac:`osascript -e 'display notification "Response complete" with title "Claude Code"'`
  - Linux:`notify-send 'Claude Code' 'Response complete'`

---

## 7. 验证

```bash
# 1) 危险命令拦截(应 exit 2 并打印拦截信息)
echo '{"tool_input":{"command":"rm -rf /"}}' | python ~/.claude/hooks/dangerous-command-blocker.py; echo "exit=$?"

# 2) SessionStart 注入(应输出含两个 skill 的 JSON)
echo '{"hookEventName":"SessionStart"}' | python ~/.claude/hooks/inject-bootstrap-skills.py | head -c 200

# 3) settings.json 合法性
python -c "import json;json.load(open(r'C:/Users/<YOU>/.claude/settings.json'));print('settings OK')"
```

最后**开一个新的 Claude Code 会话**:
- 开头上下文应出现 "The following baseline bootstrap skills are ACTIVE..." 加两个 skill 全文
  → 证明 SessionStart hook 生效。
- `SessionStart`/settings 改动只对**新会话**生效,当前会话看不到。

---

## 8. 安全须知

- **绝不提交真实密钥**。`~/.claude/settings.json` 可能含 `ANTHROPIC_AUTH_TOKEN` 等;本仓库只放
  脱敏示例。在新机器填入真实 token 后,该文件留本地。
- `SessionStart` 注入会给**每个**会话增加约 2 万字符上下文,注意 token 成本;不需要时删除该段即可。
- hook 把 stdin 当不可信数据处理,不当作指令执行。

---

## 9. 回滚

- 关闭 SessionStart 注入:删 `settings.json` 里的 `SessionStart` 段。
- 关闭每轮指针注入:删 `settings.json` 里的 `UserPromptSubmit` 段。
- 完全卸载:删 `~/.claude/hooks/` 下脚本 + `settings.json` 的 `hooks` 段 + `CLAUDE.md` 的
  `Baseline skills` 段。
