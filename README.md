# FDE黄师傅 · 个人履历与作品索引平台

> 把前沿科技，翻译成人能听懂、企业能用上的内容资产。
> FDE = Forward Deployed Engineer —— 不交付概念，只交付跑得起来的东西。

**线上地址**：https://edwardchina2023-max.github.io/huangshifu/

这个站点是黄汪传（黄师傅）在**面试、谈合作、项目融资、授课**四个场景下的统一入口。
所有作品与资料的原件都收录在 `assets/files/` 下，可通过站内链接直接打开查看。

---

## 页面结构

| 页面 | 内容 |
|---|---|
| `index.html` | 首页 · 定位、核心数据、四条能力线、精选案例 |
| `resume.html` | 履历 · 按简历结构：简介、核心数据、工作经历、项目经历、教育、现场影像 |
| `capabilities.html` | 能力边界 · 四条能力线详解、可独立交付 / 需协作 / 不承接、交付物清单、工作方式 |
| `works.html` | 作品集 · C1–C7 七组案例，可点开原件；客户敏感案例脱敏处理 |
| `toolkit.html` | 工具库 · 15 类提示词模板、3 套智能体技能、7 个自动化脚本、3 份方法论 |
| `visual.html` | 视觉资产 · 主品牌与「实验室前线」栏目全套视觉，支持点击放大 |
| `services.html` | 服务与合作 · 按来访者身份分入口（招聘方 / 合作伙伴 / 客户 / 学员），六项服务清单 |
| `contact.html` | 联系 · 联系方式、邮件模板、脱敏案例查看申请 |

## 目录结构

```
huangshifu/
├── index.html resume.html capabilities.html works.html
├── toolkit.html visual.html services.html contact.html
├── assets/
│   ├── css/style.css        站点样式（深墨蓝 + 陶土红 + 暖白）
│   ├── js/main.js           导航、灯箱、当前页高亮
│   ├── img/                 profile / brand / labfront / article
│   └── files/               作品与资料原件
│       ├── 01_提示词库      15 类可复用提示词模板
│       ├── 02_智能体与技能   新科学写作 skill、视频剪辑 skill、公众号创作 prompt
│       ├── 03_自动化脚本     抓取、生成、剪映自动化等 7 个脚本
│       ├── 04_方法论        日报工作流、IP 策划案、提示词使用说明
│       ├── 05_情报简报      AI 流水线产出样本
│       ├── 06_实验室雷达     早报样本与工作流
│       ├── 07_实验室IP       IP 策划案、七期视频脚本、商标策略
│       ├── 08_文章脚本       长文、手记、拍摄脚本原件
│       └── 09_简历与手册     简历 PDF、样书 PDF
└── .nojekyll                绕过 Jekyll，直接服务静态文件
```

## 内容脱敏原则

涉及客户商业信息、技术细节与第三方署名版权的材料**不上传公开仓库**，
在作品集中以脱敏卡片形式呈现（说明行业、挑战、角色、方法、成果），
完整原件可在签署保密协议后邮件索取。

已移除的内容包括：客户品牌全案原件、企业访谈方案、第三方机构署名文档、
视频母带、个人财务与主体架构规划。

## 本地预览

```bash
cd huangshifu
python3 -m http.server 8000
# 浏览器打开 http://localhost:8000
```

## 更新方式

修改文件后：

```bash
git add -A
git commit -m "更新说明"
git push
```

GitHub Pages 会在 1–2 分钟内自动重新部署。

---

黄汪传（黄师傅）· 北京 · edwardchina2023@gmail.com
