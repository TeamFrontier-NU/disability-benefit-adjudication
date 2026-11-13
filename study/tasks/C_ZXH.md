# ZXH · C 组（网页和数据）· 数据、随机分配、计时

搭档：LYL（页面）。lab 时段：周五 15–18、周六 15–18、周日 09–12、周日 15–18。
总清单：`study/HANDOFF.md`。你是**专家组**成员：**周六 12–15 点先做完专家判断，再去接入案例。**

## 你要交的东西

| # | 交什么 | 放哪里 | 截止 | 交给 |
|---|---|---|---|---|
| 1 | Google Sheet（`responses`、`contacts`、`allocation` 三张表）+ 写入函数；服务账号密钥放 Streamlit Secrets | `study/app/data.py` | 周五 18:00 | LYL |
| 2 | 分配表（分区随机，每 2 人 1 个 AI、1 个无 AI，事先生成 200 行）+ 随机种子记录 | Sheet 的 `allocation` 表 + 网盘 `06_data/seed.txt`（**不放 GitHub**） | 周五 18:00 | LYL |
| 3 | 分配函数、计时函数、案例顺序随机函数 | `study/app/assign.py` | 周五 18:00 | LYL |
| 4 | 假数据生成器（30 人 × 6 个案例） | `study/analysis/fake_data.py` | 周六 18:00 | WYX |
| 5 | 专家判断 | 网盘 `05_expert/ZXH.csv` | 周六 15:00 | 15:00 对照 |
| 6 | 测试用"强制分组"开关（只有组员知道） | `study/app/` | 周六 18:00 | B 组 |
| 7 | 清空试点和测试数据 | Sheet | 周日 18:00 | LYL |

## 细节

- **分配**：第 n 个通过资格测试的人拿 `allocation` 表第 n 行；用 Sheet 记下已用到第几行，避免两人同时进来拿到同一行。分配一旦给出不能改。
- **案例顺序**：每人 6 个案例随机打乱，顺序写进 `case_order`。
- **计时**：案例显示时开始，提交时结束，记秒数；同时记下 `started_at`、`submitted_at`。
- **每提交一个案例就写一行**，不要等全部做完（Streamlit 重启会丢内存里的数据）。
- **姓名邮箱只写进 `contacts`**，`responses` 里只有参与者编号。
- 列名照 `HANDOFF.md` 第 3.5 节，不要自己加改。

## 专家判断

1. 周六 12:00 后打开 `study/content/cases/C*.en.md`。
2. 自己做，不商量，不看 AI 输出和答案；周五接入代码时用占位案例，不要提前打开正式案例。
3. 存成 `05_expert/ZXH.csv`：`case_id,answer,reason`。
4. 15:00 和 WYQ、WYX 对照。

## 不要做

- 不要把密钥、分配表、随机种子、被试数据放进 GitHub。
- 不要改现有平台（`platform/`）。
