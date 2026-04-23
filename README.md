# frequent-skill

AI Coding Agent Skills Framework - 常用技能集合

## 概述

本仓库汇集了用于 AI 编码代理的技能框架和工具，帮助开发者构建更高效、更系统的软件开发工作流。

## 目录结构

```
frequent-skill/
├── superpowers-main/          # 完整的 Superpowers 开发方法论
│   ├── skills/                # 核心技能集合
│   ├── tests/                 # 测试套件
│   └── docs/                  # 文档和设计规范
├── andrej-karpathy-skills-main/  # Karpathy 技能指南
└── backup_skills/             # 技能备份
```

## 技能列表

### Superpowers 核心技能

| 技能 | 描述 |
|------|------|
| **brainstorming** | 头脑风暴技能 - 用于激发创意和探索问题空间 |
| **subagent-driven-development** | 子代理驱动开发 - 多代理协作完成复杂任务 |
| **test-driven-development** | 测试驱动开发 - TDD 工作流 |
| **systematic-debugging** | 系统化调试 - 结构化问题定位和修复 |
| **writing-plans** | 计划编写 - 创建清晰可执行的实施计划 |
| **executing-plans** | 计划执行 - 按计划推进项目 |
| **finishing-a-development-branch** | 分支完成 - 规范合并流程 |
| **requesting-code-review** | 请求代码审查 - 获取高质量反馈 |
| **receiving-code-review** | 接收代码审查 - 有效处理审查意见 |
| **dispatching-parallel-agents** | 并行代理调度 - 多任务并行处理 |
| **verification-before-completion** | 完成前验证 - 确保交付质量 |
| **using-git-worktrees** | Git Worktrees 使用 - 高效多分支开发 |
| **using-superpowers** | Superpowers 使用指南 |
| **writing-skills** | 技能编写 - 创建新的自定义技能 |

### 其他技能

| 技能 | 描述 |
|------|------|
| **karpathy-guidelines** | Andrej Karpathy 编码指南 |

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/Destiny916/frequent-skill.git

# 进入目录
cd frequent-skill
```

### 在 Claude Code 中使用

```bash
/plugin install superpowers@claude-plugins-official
```

## 核心概念

### 技能触发

技能会自动检测上下文并触发，无需手动调用。当 AI 代理识别到相关场景时，会自动激活相应技能。

### 开发流程

1. **规划阶段** - 使用 brainstorming 和 writing-plans 明确目标和方案
2. **执行阶段** - 使用 subagent-driven-development 驱动实现
3. **验证阶段** - 使用 test-driven-development 和 verification-before-completion 确保质量
4. **审查阶段** - 使用 requesting-code-review 和 receiving-code-review 持续改进

## 文档

更多详细文档请参考：
- Superpowers 完整文档: superpowers-main/README.md
- 各技能详细说明: superpowers-main/skills/

## 许可证

本项目遵循各技能对应的开源许可证。
