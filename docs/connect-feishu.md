# 如何连接飞书并发布“长寿抗衰与健康寿命证据图谱”

## 推荐架构

```text
GitHub = 唯一事实源头
Codex = 维护 GitHub
飞书多维表格 = 中文结构化展示
飞书知识库/云文档 = 中文阅读展示
```

正式流程：

```text
Codex 修改仓库 → 你 review PR → merge → GitHub Action 同步飞书
```

## 第一步：创建飞书自建应用

1. 打开飞书开放平台。
2. 进入开发者后台 / Console。
3. 创建企业自建应用。
4. 保存：

```text
App ID
App Secret
```

5. 根据场景申请权限：

```text
多维表格 / Base / Bitable：读取、写入记录
云文档 / Docs：读取、创建、导入文档
云空间 / Drive：上传、导入文件
知识库 / Wiki：创建或管理节点，视权限而定
```

6. 发布或安装应用到当前租户。

## 第二步：创建飞书多维表格

建议名称：

```text
长寿抗衰与健康寿命证据图谱
```

建议先手动创建四张表：

```text
文献总表
候选文献
主题库
发布日志
```

字段请参考：`docs/feishu-field-mapping.md` 和 `docs/feishu-base-schema.md`。

保存：

```text
FEISHU_BITABLE_APP_TOKEN
FEISHU_SOURCE_TABLE_ID
FEISHU_CANDIDATE_TABLE_ID
FEISHU_TOPIC_TABLE_ID
FEISHU_PUBLISH_LOG_TABLE_ID
```

## 第三步：配置环境变量

复制：

```bash
cp .env.example .env
```

填入：

```text
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_BITABLE_APP_TOKEN=bascn_xxx
FEISHU_SOURCE_TABLE_ID=tblxxx
```

## 第四步：同步证据矩阵到飞书

```bash
python scripts/sync_feishu_bitable.py
```

该脚本会读取：

```text
data/evidence_matrix.csv
config/feishu_field_mapping.json
```

并按 `paper_id` upsert 到飞书多维表格。

## 第五步：让 Codex 通过飞书 MCP 操作

如果你希望 Codex 临时直接操作飞书，可以配置 MCP。示例见：`docs/codex-mcp-feishu.toml.example`。

注意：飞书 MCP 更适合临时操作；生产发布建议仍使用脚本同步。
