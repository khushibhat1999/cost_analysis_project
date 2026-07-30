"""Generate an ER diagram of chinook.db and save it as chinook_er_diagram.pdf.

Introspects the SQLite database via PRAGMA queries, then renders each table as a
graphviz record with primary-key / foreign-key annotations. Foreign key edges use
crow's-foot-style arrows (crow = many, tee = one).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import graphviz

DB_PATH = Path("chinook.db")
OUT_STEM = "chinook_er_diagram"

HEADER_BG = "#2C3E50"
HEADER_FG = "white"
ROW_BG = "#FDFDFD"
ROW_ALT_BG = "#EFF3F6"
PK_COLOR = "#B03A2E"
FK_COLOR = "#1F618D"


def collect_schema(conn: sqlite3.Connection):
    tables = [
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        )
    ]
    schema = {}
    edges = []
    for t in tables:
        cols = conn.execute(f"PRAGMA table_info({t})").fetchall()
        fks = conn.execute(f"PRAGMA foreign_key_list({t})").fetchall()
        fk_from = {fk[3]: (fk[2], fk[4]) for fk in fks}
        schema[t] = [
            {
                "name": c[1],
                "type": c[2],
                "pk": bool(c[5]),
                "fk_ref": fk_from.get(c[1]),
            }
            for c in cols
        ]
        for fk in fks:
            edges.append((t, fk[3], fk[2], fk[4]))
    return schema, edges


def table_label(name: str, columns: list[dict]) -> str:
    rows = []
    for i, col in enumerate(columns):
        bg = ROW_ALT_BG if i % 2 else ROW_BG
        key_marks = []
        if col["pk"]:
            key_marks.append(f'<FONT COLOR="{PK_COLOR}"><B>PK</B></FONT>')
        if col["fk_ref"]:
            key_marks.append(f'<FONT COLOR="{FK_COLOR}"><B>FK</B></FONT>')
        marks = " ".join(key_marks) or "&nbsp;"
        rows.append(
            f'<TR>'
            f'<TD BGCOLOR="{bg}" ALIGN="LEFT" PORT="{col["name"]}">'
            f'<FONT FACE="Helvetica">{col["name"]}</FONT>'
            f'</TD>'
            f'<TD BGCOLOR="{bg}" ALIGN="LEFT">'
            f'<FONT FACE="Helvetica" POINT-SIZE="10" COLOR="#555555">{col["type"]}</FONT>'
            f'</TD>'
            f'<TD BGCOLOR="{bg}" ALIGN="RIGHT">'
            f'<FONT FACE="Helvetica" POINT-SIZE="10">{marks}</FONT>'
            f'</TD>'
            f"</TR>"
        )
    return (
        "<"
        '<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="6">'
        f'<TR><TD BGCOLOR="{HEADER_BG}" COLSPAN="3" ALIGN="CENTER">'
        f'<FONT COLOR="{HEADER_FG}" FACE="Helvetica-Bold" POINT-SIZE="14">{name}</FONT>'
        "</TD></TR>"
        + "".join(rows)
        + "</TABLE>"
        ">"
    )


def build_graph(schema, edges) -> graphviz.Digraph:
    dot = graphviz.Digraph(
        "Chinook",
        engine="dot",
        graph_attr={
            "rankdir": "LR",
            "splines": "spline",
            "overlap": "false",
            "nodesep": "0.5",
            "ranksep": "0.9",
            "pad": "0.4",
            "bgcolor": "white",
            "label": "Chinook Database — Entity Relationship Diagram",
            "labelloc": "t",
            "fontsize": "18",
            "fontname": "Helvetica-Bold",
        },
        node_attr={
            "shape": "plain",
            "fontname": "Helvetica",
        },
        edge_attr={
            "color": "#34495E",
            "penwidth": "1.2",
            "arrowsize": "0.9",
        },
    )
    for name, cols in schema.items():
        dot.node(name, label=table_label(name, cols))
    for child, child_col, parent, parent_col in edges:
        dot.edge(
            f"{child}:{child_col}",
            f"{parent}:{parent_col}",
            arrowhead="tee",
            arrowtail="crow",
            dir="both",
        )
    return dot


def main() -> None:
    assert DB_PATH.exists(), f"Database not found at {DB_PATH.resolve()}"
    with sqlite3.connect(DB_PATH) as conn:
        schema, edges = collect_schema(conn)
    dot = build_graph(schema, edges)
    out = dot.render(OUT_STEM, format="pdf", cleanup=True)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
