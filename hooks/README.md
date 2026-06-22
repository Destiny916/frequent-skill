# Claude Code Hooks — 这套配置是什么 & 怎么装

本目录 `hooks/` 收录了一套用于 Claude Code 的 hook 脚本,配合 `building-claude-code-hooks`
skill 一起使用。本文件说明**每个 hook 是什么、做什么、如何注册到 `settings.json`**,
方便在其他机器上快速复用。

> ⚠️ **安全提醒**:你自己的 `~/.claude/settings.json` 里可能含有真实 API token
> (如 `ANTHROPIC_AUTH_TOKEN`)。本仓库**只收录脱敏的注册片段**,绝不包含真实密钥。
> 在新机器套用时,把下面的 `hooks` 段合并进你已有的 `settings.json`,不要覆盖整文件。

---

## 一、hook 是什么(背景)

Claude Code 在生命周期的关键节点会调用外部命令(hook)。每个 hook:
- 从 **stdin** 读取一段事件 JSON;
- 通过 **退出码** 表达意图(`0`=放行,`2`=拦截并把 stderr 作为理由展示);
- 可选地向 **stdout** 打印结构化 JSON 实现更强控制(拦截决定 / 注入上下文)。

详见同目录 `../building-claude-code-hooks/SKILL.md`。

---

## 二、本套 8 个 hook 注册项一览

| # | 事件 / matcher | 脚本 | 作用 | 行为 |
|---|----------------|------|------|------|
| 1 | PreToolUse / `Edit\|Write` | `backup-before-edit.py` | 编辑前把原文件备份为 `<file>.backup.<时间戳>` | 尽力而为,绝不阻断 |
| 2 | PreToolUse / `Bash` | `dangerous-command-blocker.py` | 三级拦截危险 shell 命令 | 命中灾难/关键路径模式 → 退出 2 拦截 |
| 3 | PreToolUse / `Bash` | `secret-scanner.py` | `git commit` 前扫描暂存文件里的密钥 | 检出密钥 → 退出 2 拦截提交 |
| 4 | PreToolUse / `Write` (`if: Write(.env*)`) | (内联 echo) | 禁止写入 `.env*` 文件 | 直接 deny |
| 5 | SessionStart / `""` | `inject-bootstrap-skills.py` | 每个新会话注入两个基线 skill 全文 | 打印 additionalContext |
| 6 | PostToolUse / `Edit\|Write` | `format-python-files.py` | 编辑后对 `.py` 跑 `black` 格式化 | 尽力而为,缺 black 则静默跳过 |
| 7 | Stop / `""` | `notify-stop.ps1` | 回合结束弹 Windows 桌面气泡通知 | 尽力而为 |
| 8 | UserPromptSubmit / `""` | `remind-bootstrap-skills.py` | 每轮用户提交时注入基线 skill 精简指针(~150 tokens) | 尽力而为,绝不阻断 |

### 各 hook 详解

**1. backup-before-edit.py** — `PreToolUse(Edit|Write)`
读取 hook JSON 拿到 `file_path`,若文件已存在则 `copy2` 成
`<file>.backup.<unixtime>`。任何异常都吞掉,从不阻断编辑。适合给自动编辑加一层
本地快照,误改可回滚。

**2. dangerous-command-blocker.py** — `PreToolUse(Bash)`
三级防护:
- L1 灾难命令(`rm -rf /`、`rm` 配 `*`/`~`、`dd`、`mkfs`、fork bomb、向磁盘直写、
  `chmod 777 /` 等)→ **退出 2 拦截**;
- L2 关键路径(对 `.claude` / `.git` / `node_modules` / `.env` / 各类 lockfile、
  manifest 执行 `rm`/`mv`)→ **退出 2 拦截**;
- L3 可疑模式(链式 `rm &&`、`rm` 带通配、`find -delete`、`xargs rm`)→ 仅告警,放行。

**3. secret-scanner.py** — `PreToolUse(Bash)`
只在命令含 `git commit` 时触发。解析暂存文件(含 `-a` 与链式 `git add ... && commit`
两种情形),用一大批正则匹配 AWS/Anthropic/OpenAI/GitHub/Stripe/私钥/数据库连接串/
JWT 等密钥;检出则按严重级别打印并 **退出 2 拦截提交**。带例外:`.env.example` 等
模板文件、含 "example"/"placeholder" 的注释行会跳过。

**4. .env 写入拦截** — `PreToolUse(Write)`,带 `if: Write(.env*)`
不是脚本,而是 settings.json 里的内联命令,直接返回 deny 决定,禁止写 `.env*`。

**5. inject-bootstrap-skills.py** — `SessionStart`
每个新会话启动时,读取 `~/.claude/skills/` 下 `using-superpowers` 与
`general-agent-operating-guidelines` 两个 SKILL.md,拼成一段 `additionalContext`
打印出来,由 Claude Code 注入会话上下文。这让"每次对话都加载基线 skill"成为
**代码强制**,不依赖模型是否主动调用。代价:每会话固定多注入约 2 万字符。

**6. format-python-files.py** — `PostToolUse(Edit|Write)`
编辑后若目标是 `.py` 且 `black` 可用,则原地格式化(30s 超时)。缺 black 或出错
一律静默跳过,从不失败。

**7. notify-stop.ps1** — `Stop`
回合结束时用 `System.Windows.Forms.NotifyIcon` 弹一个桌面气泡通知。纯 Windows 可用,
尽力而为。

**8. remind-bootstrap-skills.py** — `UserPromptSubmit`
SessionStart 注入(hook 5)只在**会话开头跑一次**,且已知在 `/compact` 压缩后会丢失、
`--resume`/`--continue` 续接时可能不触发。本 hook 在**每次用户提交**时注入一条**精简指针**
(~150 tokens,不是全文):重申两个基线 skill 生效、应用顺序、以及"全文若已不在上下文就从
`~/.claude/skills/` 回读对应 SKILL.md"。与 hook 5 形成**全文一次 + 每轮兜底**的组合:开场有
全文,之后每轮低成本保持在场并能扛过压缩/续接。读不到 skill 文件则静默跳过,绝不阻断提交。

---

## 三、安装步骤(新机器)

1. 把本目录 `hooks/` 里的脚本拷到 `~/.claude/hooks/`(Windows:`C:\Users\<你>\.claude\hooks\`)。
2. 确保 Python 在 PATH;若要用格式化 hook,`pip install black`。
3. 把下面的 `hooks` 段**合并**进 `~/.claude/settings.json`(已有 settings 就只加 `hooks`
   键,注意把路径里的用户名换成你自己的,反斜杠保持转义 `\\`)。
4. 逐个测试:`echo '{"tool_input":{"command":"rm -rf /"}}' | python ~/.claude/hooks/dangerous-command-blocker.py; echo "exit=$?"`(应被拦截、exit=2)。
5. `SessionStart` 改动对**下一个**新会话生效,开新会话验证注入。

### 脱敏的 settings.json 注册片段(只含 hooks 段,密钥用占位符)

```jsonc
{
  // ... 你已有的 env / permissions / model 等保持不动;env 里的 token 用你自己的真实值,切勿提交 ...
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "python \"C:\\Users\\<YOU>\\.claude\\hooks\\backup-before-edit.py\"" }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python \"C:\\Users\\<YOU>\\.claude\\hooks\\dangerous-command-blocker.py\"" },
          { "type": "command", "command": "python \"C:\\Users\\<YOU>\\.claude\\hooks\\secret-scanner.py\"" }
        ]
      },
      {
        "matcher": "Write",
        "hooks": [
          { "type": "command", "if": "Write(.env*)", "command": "echo {\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"Writing to .env files is blocked by hook\"}}" }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "python \"C:\\Users\\<YOU>\\.claude\\hooks\\inject-bootstrap-skills.py\"" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "python \"C:\\Users\\<YOU>\\.claude\\hooks\\format-python-files.py\"" }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "powershell -NoProfile -ExecutionPolicy Bypass -File \"C:\\Users\\<YOU>\\.claude\\hooks\\notify-stop.ps1\"" }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "python \"C:\\Users\\<YOU>\\.claude\\hooks\\remind-bootstrap-skills.py\"" }
        ]
      }
    ]
  }
}
```

> macOS/Linux 用户:把 `python "C:\\Users\\...\\x.py"` 换成
> `python3 "$HOME/.claude/hooks/x.py"`;`notify-stop.ps1` 需换成等价的
> `osascript`(mac)或 `notify-send`(Linux)实现。
