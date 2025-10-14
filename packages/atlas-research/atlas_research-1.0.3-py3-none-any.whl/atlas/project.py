# src/atlas/project.py
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, Iterable
from pathlib import Path
import inspect
import os

from .graph_store import GraphStore
from .ingest.basic import Ingestor
from .link.basic import Linker
from .query.api import QueryAPI
from .viz.pyvis_viz import Visualizer
from .export.report import Reporter
from .types import NodeType


class NodeType(str, Enum):
    PAPER = "Paper"
    CODEREPO = "CodeRepo"
    DATASET = "Dataset"
    CONCEPT = "Concept"
    AUTHOR = "Author"
    VENUE = "Venue"


@dataclass
class Atlas:
    name: str = "atlas-project"
    store: GraphStore = None

    def __post_init__(self):
        self.store = self.store or GraphStore()
        self.ingest = Ingestor(self.store)
        self.link = Linker(self.store)
        self.query = QueryAPI(self.store)
        self.viz = Visualizer(self.store)
        self.export = Reporter(self.store)

    # --- Convenience methods ---
    def add_node(self, ntype: NodeType, id: str, **attrs):
        return self.store.add_node(ntype, id, **attrs)

    def add_edge(self, src: str, dst: str, etype: str = "RELATES_TO", **attrs):
        return self.store.add_edge(src, dst, etype, **attrs)

    def save(self, path: str):
        self.store.save(path)

    def load(self, path: str):
        self.store.load(path)

    # --- CLI용 실행 파이프라인 ---
    def run(self, query: str):
        """
        Run the full Atlas pipeline for a given query.
        Adapts to module method names and prevents duplicate 'outputs/' paths.
        """
        print(f"[Atlas] Running research network analysis for: '{query}'")

        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        # 1️⃣ 데이터 수집 단계
        print("[Atlas] Step 1: Ingesting data...")
        data = None
        for method in ("fetch", "run", "ingest"):
            if hasattr(self.ingest, method):
                func = getattr(self.ingest, method)
                try:
                    data = func(query)
                    print(f"[Atlas] → Ingestor.{method}() executed.")
                    break
                except TypeError:
                    continue
        if data is None:
            print(
                "⚠️ Warning: No valid ingestion method found. Skipping ingestion step."
            )

        # 2️⃣ 엔티티 연결 단계
        print("[Atlas] Step 2: Linking entities...")
        graph = None
        for method in ("build", "run", "link"):
            if hasattr(self.link, method):
                func = getattr(self.link, method)
                try:
                    graph = func(data)
                    print(f"[Atlas] → Linker.{method}() executed.")
                    break
                except TypeError:
                    continue
        if graph is None:
            print("⚠️ Warning: No valid linking method found.")

        # 3️⃣ 시각화 단계
        print("[Atlas] Step 3: Visualizing network...")
        graph_html = Path("graph_result.html")  # ⚡ 핵심 변경 — outputs 제거
        viz_func = None
        for method in ("render", "run", "visualize"):
            if hasattr(self.viz, method):
                viz_func = getattr(self.viz, method)
                break

        if viz_func:
            params = inspect.signature(viz_func).parameters
            arg_name = next(
                (
                    p
                    for p in (
                        "output_path",
                        "output",
                        "path",
                        "filename",
                        "save_path",
                        "outfile",
                        "filepath",
                    )
                    if p in params
                ),
                None,
            )

            # 내부에서 자동으로 'outputs/' 경로 붙일 경우 대비
            try:
                if arg_name:
                    viz_func(**{arg_name: str(graph_html.name)})
                else:
                    viz_func()
                print(f"[Atlas] → Visualization rendered (handled internally)")
            except FileNotFoundError:
                # fallback: outputs/graph_result.html 강제 생성
                safe_path = output_dir / "graph_result.html"
                if arg_name:
                    viz_func(**{arg_name: str(safe_path)})
                    print(f"[Atlas] → Visualization saved manually to {safe_path}")
                else:
                    raise
            except Exception as e:
                print(f"⚠️ Visualization failed: {e}")
        else:
            print("⚠️ Warning: No visualization function found.")

        # 4️⃣ 보고서 생성
        print("[Atlas] Step 4: Exporting report...")
        report_path = output_dir / "insight_report.json"
        if hasattr(self.export, "generate"):
            self.export.generate(report_path)
        elif hasattr(self.export, "run"):
            self.export.run(report_path)
        else:
            print("⚠️ Warning: No export/report generator found.")

        print(
            f"[Atlas] ✅ Analysis complete — check the 'outputs/' directory for results."
        )
