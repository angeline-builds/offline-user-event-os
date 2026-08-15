# 线下活动运营 OS

[English](README.md) | **简体中文**

一套可复用的 Codex Skill：把已有活动策划书或活动 Brief 整理成按照“活动前—活动中—活动后”运行的运营工具包，适用于品牌、社区、客户、员工与用户活动。

> 这是独立完成的个人作品集项目，与任何模型厂商、协作平台或活动服务公司不存在隶属或背书关系。

## 为什么做这个项目

活动团队往往在文档里策划、在零散消息里执行、在活动结束后重新整理报表。这个 Skill 保留原策划书的可编辑性，同时把准备、现场执行、真实结果、经验复盘和归档条件连接成一条可重复使用的工作链路。

## 活动生命周期

- 活动前：人员、物料、流程、用户安排、预算、活动收费与计划收入。
- 活动中：现场联系人、当前流程、现场任务、突发情况、修改与跟进。
- 活动后：签到与满意度、实际收入与成本、实际 ROI、Case、供应商付款节点、UGC、反馈闭环、复盘和归档。

仓库中的示例全部为虚构数据，并标记为 `SIMULATED`，不包含真实联系方式、API 凭证、参与者信息或供应商资料。

## 证据标签

- `PLANNED`：未来目标、估算或已批准的计划。
- `ACTUAL`：已有当前活动证据支持的真实结果。
- `SIMULATED`：用于演示或测试的虚构数据。
- `TO_VALIDATE`：信息不完整、仍需确认的项目。

## 安装

把 `offline-user-event-os` 文件夹复制到个人 Codex Skill 目录，然后重新打开一个 Codex 任务：

- Windows：`%USERPROFILE%\.codex\skills\offline-user-event-os`
- macOS / Linux：`~/.codex/skills/offline-user-event-os`

## 使用

明确调用 Skill：

```text
使用 $offline-user-event-os 把这份活动 Brief 整理成按照活动前、中、后执行的运营工具包。
```

也可以直接测试确定性生成器：

```powershell
python offline-user-event-os/scripts/generate_event_kit.py `
  --brief offline-user-event-os/assets/brief.example.json `
  --output generated/example
```

生成器会创建 13 个可编辑的 Markdown、CSV 和 JSON 文件。除非明确传入 `--force`，否则不会覆盖已有工具包。

无需额外依赖即可校验仓库：

```powershell
python scripts/validate_skill.py
```

## 项目结构

```text
.
├── .github/workflows/validate.yml
├── README.md
├── README.zh-CN.md
├── LICENSE
├── SECURITY.md
├── scripts/validate_skill.py
└── offline-user-event-os/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── assets/brief.example.json
    ├── references/
    │   ├── brief-schema.md
    │   └── quality-gates.md
    └── scripts/generate_event_kit.py
```

## 安全与限制

- 生成结果是工作草稿，不代表已经授权外联、支出、签署合同、退款、发布内容、处理参与者数据或作出现场安全决定。
- 计划数据和实际数据必须分开；总体报告中的实际 ROI 应使用实际收入与实际成本。
- 不得公开 API Key、手机号、个人邮箱、报名名单、原始客诉、支付信息、保密合同或未经授权的人像。
- 公开示例只能使用虚构或脱敏数据。
- 真实活动仍需结合当地法律、隐私、无障碍、场地和应急要求进行人工审查。

## License

本项目采用 [MIT License](LICENSE)。
