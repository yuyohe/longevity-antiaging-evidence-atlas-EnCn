# 已确认项目决策

## 命名

- GitHub repository: `longevity-antiaging-evidence-atlas-EnCn`
- GitHub visibility: private
- 中文公开名：`长寿抗衰与健康寿命证据图谱`
- English public name: `Longevity Anti-Aging Evidence Atlas EnCn`

## 第一阶段抓取范围

标准版：

- PubMed
- ClinicalTrials.gov
- Crossref

## 操作方式

可以边建立边确认。

GitHub：

- 如果本机安装 Git 并登录 GitHub，我可以在本地初始化仓库、提交、添加 remote、push。
- 如果你使用 GitHub 网页，我可以给你具体页面和字段，你创建私有仓库后把仓库 URL 告诉我。
- 当前机器的 PowerShell 暂时找不到 `git` 命令，所以本地 push 前需要先安装 Git 或修复 PATH。

飞书：

- 飞书自建应用、授权安装、App Secret 获取必须由你登录飞书完成。
- 不要把 `FEISHU_APP_SECRET` 发到聊天里；请填入本地 `.env`。
- 你创建多维表格和四张表后，把 table ID 填入 `.env`，我可以运行同步脚本。

## 待你提供或完成

1. GitHub 用户名或组织名。
2. GitHub 私有仓库 URL，或允许我在你登录后继续指导网页创建。
3. 飞书自建应用的权限是否已开通。
4. `.env` 中是否已填好飞书相关 ID。
5. 是否安装 Git for Windows，并确认 PowerShell 能运行 `git --version`。
