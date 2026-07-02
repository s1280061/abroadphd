#!/usr/bin/env python3
"""book.md（通し読み版）を各事例ファイル・summary.md・集計/統計.md から自動生成する。

事例ファイルを直接編集した場合や新規事例を追加した場合は、このスクリプトを
再実行して book.md を更新すること。

    python3 scripts/build_book.py

「海外・退職して博士」の事例だけ、見出しに 🔴 マーカーと色（EPUB/対応リーダー向け）
を付けて他カテゴリと区別できるようにしている。
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

HEADER = """# 📖 社会人からの博士課程進学 事例集（通し読み版）

> このファイルは全内容を1つにまとめた通し読み版です。スマホでの連続閲覧用。個別ページは [README.md](README.md) の目次から。
> 🔴 マークは「社会人を辞めて海外の博士課程に進学した」事例です。

---

"""

# (フォルダパス, 部タイトル, 色マーカーを付けるか)
PARTS = [
    ("国内/社会人を続けながら博士", "第1部　国内・社会人を続けながら博士", False),
    ("国内/退職して博士", "第2部　国内・退職して博士", False),
    ("海外/退職して博士", "第3部　海外・退職して博士", True),
    ("海外/社会人を続けながら博士", "第4部　海外・社会人を続けながら博士", False),
    ("海外/その他", "第5部　海外・その他", False),
]

HIGHLIGHT_COLOR = "#c0392b"


def mark_heading(text: str) -> str:
    """本文冒頭の '# 見出し' 行に 🔴 マーカーと色付けを追加する。"""
    lines = text.split("\n", 1)
    heading = lines[0]
    rest = lines[1] if len(lines) > 1 else ""
    assert heading.startswith("# "), f"unexpected heading: {heading!r}"
    title = heading[2:]
    marked = f'# <span style="color:{HIGHLIGHT_COLOR}">🔴 {title}</span>'
    return marked + "\n" + rest


def read_clean(path: pathlib.Path) -> str:
    text = path.read_text(encoding="utf-8").rstrip("\n")
    return text


def main() -> None:
    # 各要素は (block_text, is_part_title)。is_part_title の直後の要素は
    # "---" 区切りなしで連結する（元の book.md のレイアウトに合わせる）。
    units: list[tuple[str, bool]] = [(HEADER.rstrip("\n"), False)]

    summary = read_clean(ROOT / "summary.md")
    stats = read_clean(ROOT / "集計" / "統計.md")
    units.append((summary, False))
    units.append((stats, False))

    for folder, title, highlight in PARTS:
        units.append((f"# {title}", True))
        case_dir = ROOT / folder
        files = sorted(case_dir.glob("*.md"))
        for f in files:
            body = read_clean(f)
            if highlight:
                body = mark_heading(body)
            units.append((body, False))

    references = read_clean(ROOT / "references" / "references.md")
    units.append((references, False))

    parts_out = [units[0][0]]
    for i in range(1, len(units)):
        sep = "\n\n" if units[i - 1][1] else "\n\n---\n\n"
        parts_out.append(sep)
        parts_out.append(units[i][0])

    book = "".join(parts_out) + "\n"
    (ROOT / "book.md").write_text(book, encoding="utf-8")
    print(f"book.md written ({len(book.splitlines())} lines)")


if __name__ == "__main__":
    main()
