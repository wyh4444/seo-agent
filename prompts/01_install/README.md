# 26 步法 · 阶段 1：安装与设置

> 对应 Nicholas Dulait 原文步骤 1-4

## 阶段目标

把 Claude（或 ChatGPT）武装成一个能跟你"聊 SEO"的工作搭档：
- 知道你的网站 / CMS / 目标
- 能直接读你目录里的文件
- 卡住时能看你的截图

## 步骤 1-4（原文逐条）

### 1. 安装 Claude Desktop，Code 模块开启
- macOS：https://claude.ai/download
- Windows / Linux：同上
- 启动后 Settings → Features → 启用 Code（Developer mode）
- 给 Claude 一个**本地文件夹**访问权（这步关键，**没有文件夹权限 Claude 改不了你的网站文件**）

### 2. 第一条消息
把下面这段**直接复制发给 Claude**（替换方括号内容）：

```
你是一位 SEO 总监。

我的项目信息：
- 网站 URL：[你的网站，比如 https://example.com/]
- CMS：[WordPress / Shopify / Webflow / Next.js / 其他]
- 业务目标：[列 1-3 个，比如「卖 SaaS 订阅」「获取 demo 申请」「品牌曝光」]
- 关键词研究语言：[zh / en / 其他]
- 主要市场：[US / CN / 全球 / 其他]
- 现有 SEO 痛点：[如「流量不增长」「索引慢」「某品类页面一直不排」]

请你做以下事情：
1. 总结我给你的信息，确认你理解了
2. 列出你会按 26 步法给我的 SEO 顾问流程
3. 第一步你要从我这里拿什么数据
```

### 3. 卡住了？**发截图**
任何 UI 步骤卡住时：
- macOS：`Cmd+Shift+4` 选区截图
- Windows：`Win+Shift+S`
- 直接粘到 Claude 对话里
- Claude 视觉能直接看图

### 4. 不认识你的 CMS？
- Chrome / Firefox 装 **Wappalyzer** 扩展（免费）
- 打开你的网站 → 点 Wappalyzer 图标 → 截图发给 Claude
- Claude 知道是 WordPress / Shopify / Next.js 后会切换工作流

---

## 这一阶段你的产物

✅ Claude 知道你的网站
✅ Claude 知道你的 CMS
✅ Claude 知道你的业务目标
✅ Claude 有文件夹权限

## 下一阶段

👉 阶段 2：[关键词研究（步骤 5-7）](02_keywords/01-google-suggest.md)
