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
- 新版飞书中多维表格链接可能是 `wiki/{node_token}`。此时需要用 Wiki `get_node` API 解析 `obj_token`，它才是 Bitable `app_token`。

## 待你提供或完成

1. GitHub 用户名或组织名。
2. GitHub 私有仓库 URL，或允许我在你登录后继续指导网页创建。
3. 飞书自建应用的权限是否已开通。
4. `.env` 中是否已填好飞书相关 ID。
5. 是否安装 Git for Windows，并确认 PowerShell 能运行 `git --version`。

## 已完成连接

- GitHub private repository: `yuyohe/longevity-antiaging-evidence-atlas-EnCn`
- Local repository: `D:\longevity\longevity-antiaging-evidence-atlas-EnCn`
- Feishu Wiki node token: stored locally in `.env`
- Resolved Feishu Bitable app token: stored locally in `.env`
- Feishu source table: `文献总表`
- Feishu candidate table: `候选文献`
- Feishu topic table: `主题库`
- Feishu publish log table: `发布日志`

## 飞书排查记录

新版飞书多维表格链接可能是 `https://xxx.feishu.cn/wiki/{node_token}?table=tbl...`。这个 `{node_token}` 不是 Bitable `app_token`。正确流程是：

```text
Wiki node_token
→ /open-apis/wiki/v2/spaces/get_node
→ data.node.obj_token
→ Bitable app_token
```

如果 API 返回 `99991673 unauthorized app`，优先检查 `.env` 里的 `FEISHU_APP_ID` / `FEISHU_APP_SECRET` 是否对应当前已启用、已安装、已添加为文档应用的飞书应用。这个错误不是普通字段权限错误；普通缺少 API scope 更常见是 `99991672`。

当前已经验证：

- `tenant_access_token` 获取成功。
- Wiki `get_node` 成功。
- Bitable metadata / table list / record list 成功。
- `scripts/sync_feishu_bitable.py` 已成功向 `文献总表` 写入占位记录。
