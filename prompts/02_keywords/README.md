# 26 步法 · 阶段 2：关键词研究

> 对应 Nicholas Dulait 原文步骤 5-7

## 阶段目标

挖出"真实在搜的关键词" + 验证搜索意图 + 建"关键词 → 页面"的树状结构。

## 步骤 5：用 Google Suggest + 星号挖词

**Google Suggest 技巧**：

```
best crm *           → best crm for、best crm software、best crm for small business
* crm for small      → best crm for small、free crm for small、hubspot crm for small
```

打开 Google → 输 `best crm ` 后面加 `*`（星号） → 看 Google 自动补全

**Copy-paste 给 Claude**：

```
你是我的 SEO 关键词研究助手。

我的项目：[阶段 1 设置的信息]

请用 Google Suggest + 星号技巧帮我挖 20-30 个"我的真实用户可能在搜"的关键词：

[把 Google Suggest 自动补全的结果列在这里，每个一行]

要求：
- 只列 query 本身，不要解释
- 按搜索意图分组：transactional / commercial / informational / navigational
- 标出每个的"竞争激烈程度"（凭你的判断，不查数据）
```

## 步骤 6：验证搜索意图

**搜索意图 4 类**：

| 意图 | 例子 | 页面类型 |
|---|---|---|
| **Transactional** | "buy mailchimp"、"hubspot pricing" | 品类页 / 产品页 / 落地页 |
| **Commercial** | "best crm 2026"、"crm vs hubspot" | 对比 / 测评 / 列表页 |
| **Informational** | "what is crm"、"how to use crm" | 博客 / How-to / 指南 |
| **Navigational** | "mailchimp login"、"hubspot help" | 通常不打，跳过 |

**判断方法**（手工 + Claude）：

```
搜：[keyword]
看：
- 前 3 个结果是 ads → 商业意图
- 前 3 个结果是品类页 → 商业意图  
- 前 3 个结果是博客 → 信息意图
- 看到 Shopping 框 → 强商业
- 看到百科 / WIKI 框 → 强信息
```

**给 Claude 的 prompt**：

```
这是我的候选关键词清单：
[列 30 个]

请：
1. 按搜索意图分 4 组（transactional / commercial / informational / navigational）
2. 对每组，给"建议页面类型"（什么形式的页面去打这个词）
3. 标出"**信息意图的不要打**"的（避开 99% 是定义/科普的）
4. 输出关键词 → 页面 的树状结构：
   - 根词（首页打）
   - 分类词（品类页打）
   - 长尾词（文章页打）
```

## 步骤 7：构建关键词 → 页面的树

**结构**：

```
首页（不专门打关键词，靠自然流量 + 内链权重）
  └── 品类页 1：主词 [high volume, e.g. "best crm"]
  │     └── 文章页 1.1：长尾 [e.g. "best crm for real estate"]
  │     └── 文章页 1.2：长尾 [e.g. "best crm for solopreneur"]
  └── 品类页 2：主词 [e.g. "free crm"]
        └── 文章页 2.1：长尾
        └── ...
```

**给 Claude**：

```
基于上面的关键词清单和搜索意图分析，请输出"关键词 → 页面"树状图：

- 哪些词由首页打
- 哪些词由品类页打
- 哪些词由单篇文章打
- 哪些词不打（信息意图 + 量不够大）
```

---

## 这一阶段你的产物

✅ 30-50 个验证过的关键词（按意图分类）
✅ 关键词 → 页面 的树状结构

## 用本项目工具

可以用 `keyword_research_tool`（mock 模式）让 Claude 查某个关键词的 volume / difficulty / intent：

> "用 keyword_research_tool 查 'best crm for real estate' 的 volume 和 difficulty"

⚠️ 当前为 mock，结果含 `_source: "mock"`，等接入 DataForSEO 后才是真实数据。

## 下一阶段

👉 阶段 3：[页面模板（步骤 8-15）](../03_template/README.md)
