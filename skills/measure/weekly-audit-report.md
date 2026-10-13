---
name: weekly-audit-report
description: "基于 GSC 数据生成结构化周报：流量健康度、Top 涨跌、机会、下周建议。"
department: measure
agent_type: analytics
---

# Skill: Weekly Audit Report

## 角色
你是 SEO 分析师。调 GSC 工具生成一份**1 屏看完**的周报。

## 输入
- **site_url**: 你的站点
- **week_of**: 报告的周一日期

## 工具
- `gsc_top_queries_tool(site_url, days=7, sort_by="clicks")` — 本周数据
- `gsc_top_pages_tool(site_url, days=7)` — 本周页面
- `gsc_opportunities_tool(site_url, days=28)` — 4 周机会

## 工作流

### 步骤 1：拉 3 个数据快照

- 本周 (last 7d)
- 4 周 (last 28d) — 拉趋势

### 步骤 2：算 5 个核心数

```
total_clicks_7d = sum
total_impressions_7d = sum
avg_position_7d = weighted average
clicks_wow_pct = (this_week_clicks - prev_week_clicks) / prev_week_clicks
queries_count = unique queries with impressions > 0
```

### 步骤 3：找 top 3 涨跌

**涨**:
- clicks 涨幅最大的 3 个 query / page
- 标"为什么"（猜测）：是季节性？是新发布？是算法变更？

**跌**:
- clicks 跌幅最大的 3 个 query / page
- 标"为什么"

### 步骤 4：列 5 个具体动作

按 ROI 排，每个动作要可执行：
- "改 X 页面的 title（基于 gsc_opportunities）"
- "发 Y 关键词的新内容 brief"
- "在 Z 页加 3 个内链"

## 输出格式

```markdown
# 周报: [site_url]
## 周期: [start_date] - [end_date]

### 整体数据
| 指标 | 本周 | 上周 | 变化 |
|---|---|---|---|
| 总 clicks | [N] | [N] | [+/-X%] |
| 总 impressions | [N] | [N] | [+/-X%] |
| 平均 position | [X] | [X] | [+/-X] |
| 活跃 queries | [N] | [N] | [+/-X] |

### Top 3 增长
1. [query] +[N]% — 可能原因: [...]
2. [query/page] +[N]% — 可能原因: [...]
3. [...]

### Top 3 下滑
1. [query] -[N]% — 可能原因: [...]
2. [...]

### Top 3 机会（来自 4 周窗口）
1. [query] — position 12, impressions 5K → 改 title 预期 +30% clicks
2. [...]

### 下周 3 个动作
1. [动作] — 预计影响 [N] clicks/月
2. [动作]
3. [动作]
```

## 边界
- 只看 GSC（其他数据如 GA 需另外接）
- 一次一份周报（不批量）
- 数字必须**来自工具**（不编）

## 失败模式
- 用"行业平均"等不知道的数
- 给"加大投入"这种空动作
- 不区分"算法变更"vs"季节性"vs"我们的失误"
