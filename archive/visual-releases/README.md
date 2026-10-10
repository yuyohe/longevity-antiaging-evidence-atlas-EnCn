# 宇多Yul细胞/yulcell 历史视觉归档 / Historical Visual Archives

最近新增 / Latest addition: **2026-10-10**

这里保存被替代版本的大型自包含 HTML 与原始 PNG。不是当前结论。最新版本见[资产总目录 / Current asset catalog](../../docs/asset-catalog.md)。

These ZIP files preserve superseded self-contained reports and PNGs. Do not treat historical grades as current conclusions.

## 恢复方法 / Restore

1. 下载所需月份 ZIP，使用 [SHA256SUMS.txt](SHA256SUMS.txt) 校验整个压缩包。
2. 解压到一个新的空文件夹，不覆盖当前工作目录。
3. 按 ZIP 内原路径打开 HTML 或 PNG。`MANIFEST.json` 保存每个文件的路径、字节数和 SHA-256。
4. 需要发布时整个项目的上下文，可打开清单中的 `source_commit` 对应 Git 版本。

1. Download the required ZIP and verify its checksum.
2. Extract into a new empty directory; do not overwrite current files.
3. Open the original paths. The internal manifest records each file's exact bytes and hash.
4. Use the manifest's frozen Git commit for the full project context.

所有包在移出展开目录前已逐文件读取并校验。原件仍可从 Git 提交 `2cebd911c985a11e69cff975ea03799eae5805a7` 恢复。9 月包只归档已被替代的中旬报告和面板；9 月下旬与 10 月当前版继续直接可用。

All files were verified before retirement. The September package covers superseded mid-month HTML only; late September and current October remain directly available.

本轮新增 [2026-10-01 完整视觉包](visual-release-2026-10-01.zip)：57 张 PNG 和两个自包含 HTML，共 59 个原件；冻结来源是 Git `9dc9f4f7eb5616b856cbcd732c0f4dc09c04a26c`。10 月 1 日报告和面板原路径保留归档提示。`docs/assets/visual-assets/2026-10/` 现在指向最新 10 月 10 日图片，不能再用这个活动路径复现 10 月 1 日图。

The October 1 package preserves all 59 visual originals. Its HTML paths now show archive notices. The active October image directory represents October 10; recover earlier October PNGs from this archive or its frozen commit.

验证已有视觉包 / Verify all existing visual archives:

```powershell
python -X utf8 scripts/archive_legacy_visuals.py --apply
```

无新增待归档原件时，该命令只复核已有包并刷新清单，不重写已有 ZIP。如检测到同名包和新原件并存会停止，避免覆盖历史版本。

With no new source files, the command verifies existing archives without replacing ZIPs. It refuses to overwrite an existing package with new sources.
