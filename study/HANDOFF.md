# Frontier 被试实验 · 总交接清单

> 目标：**周日 11/15 21:00 前**，把可以试做的网页链接、方案和预注册草稿发给老师。除了正式招募被试，其他环节全部在这之前完成。
> 方案全文：<https://claude.ai/artifact/7vh3fXiGNK9h3Sc95cwitp>（研究设计以方案为准，这里只管"谁、什么时候、交什么"）。
> 每个人的详细任务：`study/tasks/` 下各自的文件。

---

## 1. 三组怎么分，B 和 C 怎么不打架

| 组 | 成员 | 只负责 | 不碰 |
|---|---|---|---|
| **A · 内容** | CZY、YYH | 案例、培训材料、规则卡、词汇表、AI 预录输出（**内容文件**） | 代码 |
| **B · 文字和检验** | WYQ、WYX | 页面上的说明文字（Welcome、知情同意、抽奖、结束问卷、事后说明）、问老师、预注册、分析脚本、测试和试点（**文字文件 + 检验**） | 代码、案例 |
| **C · 网页和数据** | LYL、ZXH | 网页代码、数据存储、随机分配（**代码**） | 页面上的文字内容 |

**B 和 C 的分界线：B 写"页面上说什么"，C 写"页面怎么运作"。**

- B 只编辑 `study/content/texts/` 下的 `.md` 文字文件，不改任何 `.py`。
- C 的代码从这些文件读取文字并显示，不在代码里写说明文字。
- 文字要改？B 直接改 `.md`，C 不用动代码，刷新网页就能看到。
- 页面需要新增一段文字？C 在群里说"需要 `texts/xxx.md`"，B 来写。

A 和 C 的分界线一样：A 只放内容文件（`content/training/`、`content/cases/`、`content/ai/`），C 的代码读取它们。

---

## 2. 文件放在哪里

### GitHub（公开仓库，任何人都看得到）

```
study/
  HANDOFF.md                 ← 本文件
  tasks/                     ← 每人的任务
  content/
    texts/                   ← B 负责（规则卡、词汇表由 A 负责）
    training/                ← A 负责
    cases/                   ← A 负责
    ai/                      ← A 负责
  app/                       ← C 负责（网页代码）
  analysis/                  ← B 负责（分析脚本，只用假数据）
```

### 共享网盘 `Frontier_Study/`（**不放 GitHub**）

| 文件夹 | 内容 | 谁能看 |
|---|---|---|
| `03_answer_key/` | 出题人的预设答案、最终标准答案 | 专家判断结束前：只有 A 组 + LYL |
| `05_expert/` | 三位专家各自的判断 | 各专家只放自己的，15:00 前不看别人的 |
| `06_data/` | 数据导出、试点数据 | C 组、B 组 |
| `07_prereg/` | 预注册草稿 | 全体 |

**仓库是公开的**，所以答案、专家判断、被试数据、分配表、密钥一律不进 GitHub。

---

## 3. 文件格式约定（A、B 交给 C 的接口）

照这个格式交，C 就不用逐个问。

### 3.1 文字文件（B；规则卡和词汇表由 A）

- 路径：`study/content/texts/<key>.<lang>.md`，`lang` 为 `en` 或 `zh`
- 需要的 key：

| key | 内容 | 负责人 |
|---|---|---|
| `welcome` | 项目一句话介绍、时长、"所有档案都是模拟的" | WYQ |
| `why_fast_track` | "你不是在决定是否批准"那段解释 | WYQ |
| `consent` | 知情同意全文 + 勾选框文字 | WYQ |
| `lottery` | 抽奖规则 | WYQ |
| `rule_card` | 三步规则（找病 → 看来源 → 看时长） | CZY |
| `wrapup_ai` / `wrapup_noai` | 两组各自的结束问卷题目 | WYX |
| `thanks` | 感谢页 | WYX |
| `debrief` | 全部结束后统一发的说明信（不显示在网页上） | WYX |

- 词汇表：`study/content/texts/glossary.yaml`（CZY），格式：
  ```yaml
  MRI:
    en: "A scan that shows detailed pictures of the inside of the body."
    zh: "核磁共振：一种拍摄身体内部详细图像的检查。"
  ```

### 3.2 培训材料（A · CZY）

- `study/content/training/T1.<lang>.md`：学习案例
- `study/content/training/Q1.<lang>.md`、`Q2.<lang>.md`：资格测试案例
- `study/content/training/training_key.yaml`：三个案例的答案和讲解（培训答案可以公开）

### 3.3 正式案例（A · YYH 写英文，CZY 出中文）

- `study/content/cases/C1.<lang>.md` … `C6.<lang>.md`
- 每份文件之间用单独一行 `---page---` 分页；每页第一行写文件标题（如 `## Northgate Family Medicine · Progress Note`）
- 需要悬停解释的词写成 `[[MRI]]`，词必须在 `glossary.yaml` 里有
- **案例文件里不写答案**

### 3.4 AI 预录输出（A · YYH 英文，CZY 中文）

- `study/content/ai/C1.<lang>.json` … `C6.<lang>.json`
  ```json
  {
    "recommendation": "yes",
    "summary": "Meets the spinal cord rule based on the rehab note.",
    "findings": [
      {"quote": "complete loss of function of both legs", "page": 2}
    ],
    "flags": ["Report on page 3 was handed in by the applicant."]
  }
  ```
- `quote` 必须和案例里的原文**一字不差**（中文版对中文案例）
- 哪些案例故意给错建议，只写在网盘的私密蓝图 `03_answer_key/case_blueprint.md` 里，不写进任何 GitHub 文件

### 3.5 数据（C · ZXH）

Google Sheet 三张表：`responses`（每个判断一行）、`contacts`（姓名邮箱，只用来抽奖）、`allocation`（分配表）。`responses` 的列：

`participant_id, lang, arm, case_id, case_order, answer, confidence, seconds, started_at, submitted_at, training_attempts, heard_about_study`

（`correct` 列不写进网页数据，分析时再用标准答案算，避免答案出现在网页里。）

---

## 4. 时间表和交接

每个时段只有一组用 lab，其他组远程。**交接 = 文件放进指定位置 + 在群里 @ 下一棒。**

| # | 时间 | lab | 谁 → 谁 | 交接什么 | 完成标准 |
|---|---|---|---|---|---|
| 0 | 周五 15:00 | — | 全体 | 认领本清单，建好共享网盘 `Frontier_Study/` | 每人回复"已读" |
| 1 | 周五 18:00 | C | C → 全体 | 网页骨架预览链接（占位内容） | 能从 Welcome 点到结束页 |
| 2 | 周五 21:00 | A | A → C | `content/training/` 全部 + `rule_card` + `glossary.yaml` | 文件格式符合第 3 节 |
| 3 | 周五 21:00 | — | B → C | `welcome`、`why_fast_track`、`consent`、`lottery`（中英） | 同上 |
| 4 | 周五 21:00 | — | WYQ → 全体 | 已发邮件问老师礼品卡和 IRB（转发到群里） | 邮件已发 |
| 5 | 周六 12:00 | A | A → 专家 | 6 个英文案例 `content/cases/C*.en.md`；预设答案只放 `03_answer_key/` | 专家能打开、看不到答案 |
| 6 | 周六 15:00 | B | 专家 → A | 三份独立判断放 `05_expert/`，15:00 一起对照 | 三人一致 = 标准答案，写进 `03_answer_key/final.csv` |
| 7 | 周六 17:00 | — | A → C | 有分歧的案例改好（若有） | 改后的案例再给专家确认 |
| 8 | 周六 18:00 | C | C → B | 英文版网页能从头做到尾，数据写进 Sheet | B 能完整走一遍 |
| 9 | 周六 21:00 | A | A → C | 中文案例 `C*.zh.md` + 全部 `content/ai/*.json` | `quote` 都能在原文里找到 |
| 10 | 周六 23:00 | B | B → C | 英文版问题清单 + `wrapup_*`、`thanks`、`debrief` | 清单发群里 |
| 11 | 周日 12:00 | C | C → B | 中英文完整版网页 | 两种语言、两组都能走完 |
| 12 | 周日 15:00 | B | B → C | 试点报告：组外 2 人（一中一英）的用时和问题；数据检查结果 | 两人都 ≤ 15 分钟，或写明哪里超时 |
| 13 | 周日 18:00 | C | C → LYL | 按试点修改完的最终版链接；清空试点数据 | Sheet 里没有测试数据 |
| 14 | 周日 18:00 | — | B → LYL | 预注册草稿定稿（`07_prereg/`） | 有假设、回归、排除规则 |
| 15 | 周日 21:00 | — | LYL → 老师 | 网页链接 + 方案链接 + 预注册草稿 | 邮件已发 |

---

## 5. 发给老师前的总检查

- [ ] 专家组三人对 6 个案例的答案一致（`03_answer_key/final.csv`）
- [ ] 中英两版案例信息一致（数字、日期、来源），AI 输出的引用都能在原文找到
- [ ] 两组页面除 AI 面板外完全一样（规则卡、悬停解释、文件格式）
- [ ] 无 AI 组页面上没有任何关于 AI 的字样
- [ ] 试点两人都在 15 分钟内完成
- [ ] 数据写进 Google Sheet，重新部署后不丢失
- [ ] GitHub 上没有答案、专家判断、被试数据、分配表、密钥
- [ ] 预注册草稿完成（老师批准后再正式提交 OSF）
- [ ] 开奖日期写进 `lottery`（礼品卡未获批就写"待确认"）

## 6. 出问题找谁

| 问题 | 找谁 |
|---|---|
| 案例内容、答案、AI 输出 | YYH（英文）/ CZY（中文、培训） |
| 页面文字、知情同意、抽奖 | WYQ |
| 结束问卷、预注册、分析、测试 | WYX |
| 网页页面、部署 | LYL |
| 数据、分配、计时 | ZXH |
| 卡住超过 30 分钟 | 直接在群里说，不要等到交接时间 |
