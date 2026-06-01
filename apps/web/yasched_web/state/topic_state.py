"""Topic page state: selection, expansion, view mode, computed tree/radial layouts."""

from __future__ import annotations

import math

import reflex as rx
from pydantic import BaseModel

from .app_state import AppState, TopicData


class FlatTopicNode(BaseModel):
    id: str
    name: str
    depth: int
    has_children: bool
    is_expanded: bool
    is_selected: bool


class RadialNode(BaseModel):
    id: str
    name: str
    x: int
    y: int
    depth: int
    is_selected: bool


class RadialEdge(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int


class TopicState(AppState):
    selected_topic_id: str = ""
    expanded_ids: list[str] = []
    view_mode: str = "tree"  # "tree" | "radial"

    # ------------------------------------------------------------------ actions

    def select_topic(self, topic_id: str) -> None:
        self.selected_topic_id = topic_id

    def toggle_expand(self, topic_id: str) -> None:
        if topic_id in self.expanded_ids:
            self.expanded_ids = [t for t in self.expanded_ids if t != topic_id]
        else:
            self.expanded_ids = self.expanded_ids + [topic_id]

    def set_view_mode(self, mode: str) -> None:
        self.view_mode = mode

    # ------------------------------------------------------------------ computed: flat tree

    @rx.var
    def flat_tree(self) -> list[FlatTopicNode]:
        nodes: list[FlatTopicNode] = []
        expanded = set(self.expanded_ids)

        def visit(tid: str, depth: int) -> None:
            data: TopicData | None = self.topics_map.get(tid)
            if data is None:
                return
            is_expanded = tid in expanded
            nodes.append(
                FlatTopicNode(
                    id=tid,
                    name=data.name,
                    depth=depth,
                    has_children=len(data.child_ids) > 0,
                    is_expanded=is_expanded,
                    is_selected=tid == self.selected_topic_id,
                )
            )
            if is_expanded:
                for child_id in data.child_ids:
                    visit(child_id, depth + 1)

        for root_id in self.root_topic_ids:
            visit(root_id, 0)
        return nodes

    # ------------------------------------------------------------------ computed: radial

    @rx.var
    def radial_nodes(self) -> list[RadialNode]:
        nodes: list[RadialNode] = []
        topics = self.topics_map
        roots = self.root_topic_ids
        if not topics or not roots:
            return nodes

        cx, cy = 300, 300
        base_r = 100

        def subtree_size(tid: str, visited: set) -> int:
            if tid in visited or tid not in topics:
                return 1
            visited.add(tid)
            children = topics[tid].child_ids
            return 1 + sum(subtree_size(c, visited) for c in children)

        positions: dict[str, tuple[int, int]] = {}

        def place(tid: str, a_start: float, a_end: float, depth: int, visited: set) -> None:
            if tid in visited or tid not in topics:
                return
            visited.add(tid)
            angle = (a_start + a_end) / 2.0
            r = depth * base_r
            x = round(cx + r * math.cos(angle))
            y = round(cy + r * math.sin(angle))
            positions[tid] = (x, y)
            nodes.append(
                RadialNode(
                    id=tid,
                    name=topics[tid].name,
                    x=x,
                    y=y,
                    depth=depth,
                    is_selected=tid == self.selected_topic_id,
                )
            )
            children = topics[tid].child_ids
            if not children:
                return
            total = sum(subtree_size(c, set()) for c in children if c in topics)
            if total == 0:
                return
            cur = a_start
            for cid in children:
                if cid not in topics:
                    continue
                size = subtree_size(cid, set())
                end = cur + (a_end - a_start) * size / total
                place(cid, cur, end, depth + 1, visited)
                cur = end

        total_root = sum(subtree_size(r, set()) for r in roots if r in topics)
        cur_angle = -math.pi / 2  # start from top
        for rid in roots:
            if rid not in topics:
                continue
            size = subtree_size(rid, set())
            end_angle = cur_angle + 2 * math.pi * size / total_root
            place(rid, cur_angle, end_angle, 1, set())
            cur_angle = end_angle

        return nodes

    @rx.var
    def radial_edges(self) -> list[RadialEdge]:
        edges: list[RadialEdge] = []
        nodes_by_id = {n.id: n for n in self.radial_nodes}
        topics = self.topics_map
        visited: set[str] = set()

        def collect(tid: str) -> None:
            if tid in visited or tid not in topics or tid not in nodes_by_id:
                return
            visited.add(tid)
            parent_node = nodes_by_id[tid]
            for cid in topics[tid].child_ids:
                if cid in nodes_by_id:
                    child_node = nodes_by_id[cid]
                    edges.append(
                        RadialEdge(
                            x1=int(parent_node.x),
                            y1=int(parent_node.y),
                            x2=int(child_node.x),
                            y2=int(child_node.y),
                        )
                    )
                    collect(cid)

        for rid in self.root_topic_ids:
            collect(rid)
        return edges

    @rx.var
    def selected_topic(self) -> TopicData | None:
        if not self.selected_topic_id:
            return None
        return self.topics_map.get(self.selected_topic_id)
