# 26 步法 · 阶段 4：逐页生产

> 对应 Nicholas Dulait 原文步骤 16-19

## 阶段目标

**对单个页面，从 keyword 到 published 的完整流程**。
模板给的是骨架；这一步是把骨架填成可发布的页面。

## 步骤 16：单页 Brief（最重要）

**Brief = 写之前给作者/AI 的"作业要求"**。
Brief 越清楚，输出越准。

**Brief 模板**：

```markdown
# Content Brief: [Page Title]

## 元信息
- 目标关键词: [主词]
- 次要关键词: [5-10 个长尾变体]
- 搜索意图: [transactional / commercial / informational]
- 目标 SERP 功能: [Featured Snippet / PAA / Shopping / 无]
- 目标长度: [词数]
- 页面 URL: [目标 slug]

## 排名机会
- 当前 SERP 谁排第 1: [竞品 + 他们的内容长度 + DR]
- 我们能赢的理由: [为什么我们能排上去]
- 内容差异化: [我们比竞品多什么 / 不同什么]

## 用户意图分析
- 用户来这想完成什么任务: [任务]
- 看完后下一步是: [下一步]

## 标题候选（3-5 个）
1. [标题 1] - 60 字符以内
2. [标题 2]
3. [标题 3]

## Meta description
[150 字符以内，包含主词 1 次 + 价值主张]

## H1
[跟 title 略不同]

## 必含内容
- [必须出现的 1 个数据 / 1 个观点 / 1 个表]
- [必须出现的另 1 个元素]
- [避免: 不要这样写 X]

## 必含 Schema
- [Article / Product / ItemList / HowTo / FAQ]

## 必链
- 内链到: [3-5 个站内 URL 模式]
- 外链到: [1-2 个权威源]

## 配图要求
- Hero image: [描述]
- 段落图: [N] 张
- Infographic: [可选]

## CTA
- 主: [具体动作]
- 次: [次要动作]
```

**给 Claude**：

```
请基于我的关键词 [keyword] 写一份**完整的 content brief**。
- 目标词：[main keyword]
- 页面类型：[品类页 / 测评 / 对比 / how-to]
- 我的站：[your-site.com]
- 我的主要竞品：[3 个域名]

Brief 要包含上面的所有 9 个字段。
不要写页面内容本身，**只写 brief**。
```

## 步骤 17：用 brief 写内容

**给 Claude**：

```
现在请按上面这份 brief 写完整页面。

要求：
- 严格按 brief 的 H1 / 结构 / 必含内容
- 不要 AI 套话（"在当今数字化时代..."）
- 段落 ≤ 80 字
- 用具体数据 / 具体例子，不要"很多 / 大量 / 一些"
- 标出**所有标题 / 段落 / 图片位置**
- 文末给 schema markup JSON-LD
```

## 步骤 18：自检 checklist

**写完后跑这 10 项**：

- [ ] 标题含主词 + 60 字符内
- [ ] Meta 150 字符内 + 含主词
- [ ] H1 跟 title 略不同
- [ ] 主词出现 5-10 次（不过度）
- [ ] H2/H3 层级清晰
- [ ] 内链 3-5 个到相关页面
- [ ] 配图都有 alt
- [ ] CTA 出现 1-2 次
- [ ] FAQ 部分覆盖 People Also Ask
- [ ] Schema markup 写好

**给 Claude**：

```
请按这 10 项 checklist 自检上面的页面。
对每项标 ✅ / ⚠️ / ❌。
对 ❌ 和 ⚠️，给具体改法。
```

## 步骤 19：发布 + 监控

- 发布到 CMS
- 24 小时内去 [GSC](https://search.google.com/search-console) 提交索引
- 调本项目的 `audit_page_tool(page_url)` 跑 audit
- 7 天后看 GSC 数据（impressions / position）
- 30 天后看是否开始出词

## 这一阶段你的产物

✅ 1 个完整页面（带 brief + 自检）
✅ GSC 提交索引
✅ 7 天 / 30 天回看计划

## 用本项目工具

- `keyword_research_tool` — 验证主词 + 长尾词数据
- `audit_page_tool(url)` — 发布前 / 后自检
- `gsc_top_queries_tool(site_url, days=7)` — 7 天后看新页面的 query

## 下一阶段

👉 阶段 5：[节奏与规模化（步骤 20-26）](../05_pacing/README.md)
