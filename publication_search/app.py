"""Streamlit UI for the publication search application."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List

import streamlit as st

from .config import DataSource, DataSourceConfig, get_config
from .dedup import Deduplicator
from .models import Publication, SearchFilters
from .sources import BaseSource, get_source
from .utils import chicago_citation, normalise_list

st.set_page_config(page_title="Publication Scout", layout="wide")

CONFIG = get_config()
DEDUP = Deduplicator()


def sidebar_filters() -> SearchFilters:
    st.sidebar.header("搜索与过滤")
    keywords = st.sidebar.text_input("关键词 (逗号分隔)")
    authors = st.sidebar.text_input("作者 (逗号分隔)")
    languages = st.sidebar.text_input("语言 (逗号分隔，例如 en, zh)")
    publication_types = st.sidebar.text_input("类型/格式 (逗号分隔)")
    date_range = st.sidebar.date_input(
        "发布日期范围",
        value=(datetime(2018, 1, 1).date(), datetime.now().date()),
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = None

    return SearchFilters(
        keywords=normalise_list(keywords.split(",")),
        authors=normalise_list(authors.split(",")),
        languages=normalise_list(languages.split(",")),
        publication_types=normalise_list(publication_types.split(",")),
        start_date=datetime.combine(start_date, datetime.min.time()) if start_date else None,
        end_date=datetime.combine(end_date, datetime.min.time()) if end_date else None,
    )


def load_sources(config: DataSourceConfig) -> List[DataSource]:
    sources = config.list_sources()
    return [source for source in sources if source.enabled]


def select_sources(available_sources: List[DataSource]) -> List[DataSource]:
    st.sidebar.subheader("抓取范围")
    all_selected = st.sidebar.checkbox("全部数据源", value=True)
    if all_selected:
        return available_sources

    selected_names = st.sidebar.multiselect(
        "选择数据源",
        options=[source.name for source in available_sources],
    )
    return [source for source in available_sources if source.name in selected_names]


def add_new_source(config: DataSourceConfig) -> None:
    st.sidebar.subheader("新增数据源")
    with st.sidebar.expander("添加自定义 RSS/Atom"):
        with st.form("add_source_form"):
            name = st.text_input("名称")
            url = st.text_input("Feed 地址")
            language = st.text_input("语言 (可选)")
            format_hint = st.text_input("类型/格式 (可选)")
            submitted = st.form_submit_button("保存数据源")
            if submitted and name and url:
                source = DataSource(
                    name=name,
                    type="rss",
                    options={"url": url, "language": language, "format": format_hint, "name": name},
                )
                existing = config.list_sources()
                existing.append(source)
                config.save_sources(existing)
                st.success(f"已保存 {name}")
                st.experimental_rerun()


def fetch_publications(sources: List[DataSource], filters: SearchFilters) -> List[Publication]:
    publications: List[Publication] = []
    for source in sources:
        try:
            implementation: BaseSource = get_source(source.type, options=source.options)
        except KeyError:
            st.warning(f"未知的数据源类型：{source.type}")
            continue
        results = list(implementation.search(filters))
        for publication in results:
            publication.source = source.name or publication.source
        publications.extend(results)
    unique_results = []
    for publication in publications:
        if DEDUP.is_seen(publication):
            continue
        unique_results.append(publication)
    DEDUP.mark_seen(unique_results)
    return unique_results


def display_results(results: List[Publication]) -> None:
    st.header("搜索结果")
    if not results:
        st.info("没有找到符合条件的文献。")
        return

    columns = st.columns([2, 1])
    with columns[0]:
        for publication in results:
            with st.container():
                st.subheader(publication.title)
                meta = []
                if publication.authors:
                    meta.append("，".join(publication.authors))
                if publication.publisher:
                    meta.append(publication.publisher)
                if publication.year:
                    meta.append(publication.year)
                if publication.language:
                    meta.append(f"语言：{publication.language}")
                st.caption(" | ".join(meta))
                if publication.abstract:
                    st.markdown(publication.abstract)
                if publication.url:
                    st.markdown(f"[获取链接]({publication.url})")
                st.divider()

    chicago_map: Dict[str, str] = {
        publication.title: chicago_citation(publication) for publication in results
    }
    with columns[1]:
        st.subheader("引用导出")
        selected_titles = st.multiselect(
            "选择需要导出的文献",
            options=list(chicago_map.keys()),
            default=list(chicago_map.keys()),
        )
        selected_citations = "\n".join(chicago_map[title] for title in selected_titles)
        st.text_area("芝加哥格式引用", selected_citations, height=200)
        if st.button("复制引用到剪贴板"):
            copy_to_clipboard(selected_citations)
        st.download_button(
            label="下载引用 (TXT)",
            data=selected_citations.encode("utf-8"),
            file_name="citations.txt",
            mime="text/plain",
        )


def copy_to_clipboard(text: str) -> None:
    payload = json.dumps(text)
    st.components.v1.html(
        f"""
        <script>
        const text = {payload};
        navigator.clipboard.writeText(text).then(function() {{
            window.parent.postMessage({{isStreamlitMessage: true, type: 'streamlit:setComponentValue', value: 'copied'}}, '*');
        }});
        </script>
        """,
        height=0,
    )
    st.success("已复制到剪贴板")


def main() -> None:
    filters = sidebar_filters()
    add_new_source(CONFIG)
    available_sources = load_sources(CONFIG)
    selected_sources = select_sources(available_sources)

    if st.sidebar.button("开始搜索"):
        with st.spinner("正在检索文献..."):
            results = fetch_publications(selected_sources, filters)
        display_results(results)
    else:
        st.header("请在左侧设置条件后点击“开始搜索”")


if __name__ == "__main__":
    main()
