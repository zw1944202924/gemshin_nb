# 仓库指令

凡是修改本仓库文件或汇报交付状态的任务，都必须使用 `git-branch-discipline`。
开始这些任务前，必须先读取 `git-branch-discipline`；这是强制前置步骤，不是可选参考。
如果你把这类任务转交给其他 agent，必须在指令里显式要求对方先读取 `git-branch-discipline`，再开始分析、修改、提交或交付汇报。
本仓库中新增或修改的文档统一使用中文；只有用户明确要求其他语言时才例外。
编写代码时，对不直观的业务规则、状态约束和关键分支按需补充简洁中文注释，方便后续阅读。

## 基线分支

- 如果用户或 issue 明确指定了基线分支，优先服从该要求。
- 如果没有明确指定，则使用仓库真实默认分支。
- 对 `gemshin_nb` 来说，截至 2026-05-27，远端默认分支是 `main`，且没有远端 `dev` 分支。

## 分支规则

- 不要直接在 `main` 上修改并交付。
- 第一次提交前，必须从批准的基线创建可读任务分支；即使 checkout 起点是 `agent/agent/...` 也一样。
- 推荐命名：`feature/<scope>`、`fix/<scope>`、`docs/<scope>`、`chore/<scope>`。

## 合并与审批规则

- 未经用户明确批准，不得合并到 `main`。
- 如果项目后续引入 `dev` 之类的集成分支，且用户没有另行说明，则优先先落到集成分支。

## 完成交付证据

任何代码或文档任务的“已完成”汇报都必须包含：

- repository name
- baseline branch
- task branch
- commit hash，或明确写出 `local only, uncommitted`
- modified file paths
- 当前落点，例如 branch head 或 PR

如果缺少以上信息，就不能把任务汇报为已完成。
