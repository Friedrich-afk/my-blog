# Publication Scout

一个可配置的文献检索与去重工具，支持多数据源搜索、过滤与引用导出。

## 功能特性

- 按关键词、作者、语言、类型与发布日期范围过滤。
- 支持 Crossref、arXiv 以及自定义 RSS/Atom 数据源，可保存新增数据源。
- 抓取范围可选择全部或部分数据源。
- 三级去重策略（DOI → 标题+年份 → URL 哈希），记录在用户目录下的 `~/.publication_scout/seen.sqlite` 中。
- 搜索结果展示完整元数据与原文链接。
- 右侧面板支持多选、全选导出芝加哥格式引用，支持复制到剪贴板与导出 TXT。

## 运行方式

```bash
pip install -r requirements-publication.txt
streamlit run publication_search/app.py
```

首次运行会在用户主目录下的 `~/.publication_scout/` 目录生成 `seen.sqlite` 与数据源配置文件。

## 数据源配置

数据源配置默认会复制至 `~/.publication_scout/data_sources.json`，可通过界面新增 RSS 数据源或手动编辑该文件。

## 打包为 Windows 可执行文件

1. 安装依赖：

   ```bash
   pip install -r requirements-publication.txt
   ```

2. 运行打包脚本：

   ```bash
   python -m publication_search.build_exe
   ```

   该脚本会调用 PyInstaller 生成 `PublicationScout.exe`，输出路径位于 `publication_search/dist/`。首次运行后，应用数据仍会存放在 `~/.publication_scout/` 目录。
