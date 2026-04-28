# 如何连接飞书并发布证据图谱 / Feishu Publishing Setup

## 推荐架构

```text
GitHub = 唯一事实源
Codex = 维护 GitHub 和生成发布草稿
飞书多维表格 = 中文结构化展示和审核看板
飞书知识库/云文档 = 中文阅读展示
```

## 飞书表格

建议表名：

```text
长寿抗衰与健康寿命证据图谱
```

建议数据表：

```text
文献总表
候选文献
主题库
发布日志
```

## 环境变量

在 `.env` 中配置：

```text
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_BITABLE_APP_TOKEN=真实多维表格 token
FEISHU_BITABLE_WIKI_NODE_TOKEN=wiki 链接里的 node token，可选
FEISHU_SOURCE_TABLE_ID=文献总表 table id
FEISHU_CANDIDATE_TABLE_ID=候选文献 table id
FEISHU_TOPIC_TABLE_ID=主题库 table id
FEISHU_PUBLISH_LOG_TABLE_ID=发布日志 table id
```

如果多维表格 URL 是 `https://xxx.feishu.cn/wiki/{node_token}?table=tbl...`，脚本会通过 Wiki `get_node` 接口把 `{node_token}` 转换为真实多维表格 `obj_token`。

## 同步命令

```bash
python scripts/sync_feishu_candidates.py --update-existing
python scripts/sync_feishu_findings_to_candidates.py
python scripts/sync_feishu_topics.py
python scripts/sync_feishu_bitable.py
python scripts/sync_feishu_publish_log.py
```

## 飞书知识库发布包

当前项目先生成 Markdown 发布包：

```bash
python scripts/prepare_feishu_docs.py
```

输出目录：

```text
build/feishu-docs/
```

如果后续开放了飞书 Docs/Wiki 创建页面权限，可以把这个目录作为 API 导入源。
