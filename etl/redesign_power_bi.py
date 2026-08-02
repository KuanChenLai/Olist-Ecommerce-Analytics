"""Apply the portfolio dashboard visual system to the extracted PBIX project."""

import json
import uuid
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR / "dashboard" / "customer_analytics_src"
SECTIONS_DIR = PROJECT_DIR / "Report" / "sections"
THEME_PATH = (
    PROJECT_DIR
    / "StaticResources"
    / "SharedResources"
    / "BaseThemes"
    / "CY26SU05.json"
)

COLORS = {
    "navy": "#17324D",
    "blue": "#2F80ED",
    "teal": "#14B8A6",
    "amber": "#F2C94C",
    "orange": "#F2994A",
    "red": "#EB5757",
    "ink": "#1F2937",
    "muted": "#64748B",
    "canvas": "#F5F7FA",
    "card": "#FFFFFF",
    "border": "#D9E2EC",
}

PAGE_NAMES = {
    0: "經營總覽",
    1: "客戶與 RFM 分群",
    2: "商品與賣家績效",
    3: "商品類別明細",
}

VISUAL_TITLES = {
    0: {
        "00000": "總營收",
        "01000": "月營收趨勢",
        "02000": "商品類別營收排行",
        "03000": "賣家營收排行",
    },
    1: {
        "00000": "各客群客戶數",
        "01000": "各客群營收",
        "02000": "客群人數占比",
        "03000": "客戶總數",
        "04000": "回購率",
        "05000": "平均訂單數",
        "06000": "平均消費金額",
        "07000": "回購客戶數",
    },
    2: {
        "00000": "商品類別數",
        "01000": "賣家總數",
        "02000": "平均訂單金額",
        "03000": "平均商品價格",
        "04000": "商品類別營收排行",
        "05000": "賣家營收排行",
        "06000": "月營收趨勢",
    },
    3: {
        "03000": "平均商品價格",
        "04000": "訂單數",
        "05000": "類別營收",
        "06000": "賣家數",
        "07000": "類別月營收趨勢",
        "08000": "此類別營收最高的賣家",
        "09000": "訂單明細",
    },
}

CARD_LABELS = {
    "customer_summary.Total Customers": "客戶總數",
    "customer_summary.Repeat Purchase Rate": "回購率",
    "customer_summary.Average Orders": "平均訂單數",
    "customer_summary.Average Spend": "平均消費金額",
    "customer_summary.Repeat Customers": "回購客戶數",
    "fact_orders.Total Categories": "商品類別數",
    "fact_orders.Total Sellers": "賣家總數",
    "fact_orders.Average Order Value": "平均訂單金額",
    "fact_orders.Average Product Price": "平均商品價格",
    "fact_orders.Category Average Price": "平均商品價格",
    "fact_orders.Category Orders": "訂單數",
    "fact_orders.Category Revenue": "類別營收",
    "fact_orders.Category Sellers": "賣家數",
}


def literal(value):
    return {"expr": {"Literal": {"Value": value}}}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def set_title(single_visual, title):
    title_properties = {
        "show": literal("true"),
        "text": literal(f"'{title}'"),
        "fontColor": {
            "solid": {"color": literal(f"'{COLORS['navy']}'")}
        },
        "textSize": literal("12D"),
        "alignment": literal("'left'"),
    }
    single_visual.setdefault("vcObjects", {})["title"] = [
        {"properties": title_properties}
    ]


def set_card_label(single_visual):
    projections = single_visual.get("projections", {}).get("Data", [])
    if not projections:
        return
    query_ref = projections[0].get("queryRef")
    label = CARD_LABELS.get(query_ref)
    if not label:
        return

    objects = single_visual.setdefault("objects", {})
    labels = objects.setdefault("label", [])
    target = None
    for candidate in labels:
        if candidate.get("selector", {}).get("metadata") == query_ref:
            target = candidate
            break
    if target is None:
        target = {"properties": {}, "selector": {"metadata": query_ref}}
        labels.append(target)
    target.setdefault("properties", {})["text"] = literal(f"'{label}'")


def replace_textbox(config, heading, bullets):
    paragraphs = [
        {
            "textRuns": [
                {
                    "value": heading,
                    "textStyle": {
                        "fontSize": "18pt",
                        "fontWeight": "bold",
                        "color": COLORS["navy"],
                    },
                }
            ]
        }
    ]
    for bullet in bullets:
        paragraphs.append(
            {
                "textRuns": [
                    {
                        "value": f"• {bullet}",
                        "textStyle": {
                            "fontSize": "14pt",
                            "color": COLORS["ink"],
                        },
                    }
                ]
            }
        )
    config["singleVisual"]["objects"] = {
        "general": [{"properties": {"paragraphs": paragraphs}}]
    }


def make_page_title(section_dir, title):
    visual_dir = section_dir / "visualContainers" / "99999_頁面標題"
    visual_dir.mkdir(parents=True, exist_ok=True)
    visual_name = uuid.uuid4().hex[:20]
    position = {
        "x": 20,
        "y": 8,
        "z": 99999,
        "width": 1240,
        "height": 45,
        "tabOrder": 0,
    }
    config = {
        "name": visual_name,
        "layouts": [{"id": 0, "position": position}],
        "singleVisual": {
            "visualType": "textbox",
            "drillFilterOtherVisuals": True,
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {
                                            "value": title,
                                            "textStyle": {
                                                "fontSize": "24pt",
                                                "fontWeight": "bold",
                                                "color": COLORS["navy"],
                                            },
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            },
        },
    }
    container = {key: position[key] for key in ("height", "tabOrder", "width", "x", "y", "z")}
    write_json(visual_dir / "config.json", config)
    write_json(visual_dir / "filters.json", [])
    write_json(visual_dir / "visualContainer.json", container)


def redesign_theme():
    theme = read_json(THEME_PATH)
    theme["dataColors"] = [
        COLORS["blue"],
        COLORS["teal"],
        COLORS["amber"],
        COLORS["orange"],
        COLORS["navy"],
        "#7C3AED",
        COLORS["red"],
        "#38BDF8",
        "#84CC16",
        "#A78BFA",
        "#FB7185",
        "#94A3B8",
    ]
    theme.update(
        {
            "foreground": COLORS["ink"],
            "foregroundNeutralSecondary": COLORS["muted"],
            "foregroundNeutralTertiary": COLORS["border"],
            "background": COLORS["card"],
            "backgroundLight": COLORS["canvas"],
            "backgroundNeutral": COLORS["border"],
            "tableAccent": COLORS["blue"],
        }
    )
    theme["textClasses"] = {
        "callout": {"fontSize": 26, "fontFace": "Segoe UI Semibold", "color": COLORS["navy"]},
        "title": {"fontSize": 12, "fontFace": "Segoe UI Semibold", "color": COLORS["navy"]},
        "header": {"fontSize": 12, "fontFace": "Segoe UI Semibold", "color": COLORS["ink"]},
        "label": {"fontSize": 10, "fontFace": "Segoe UI", "color": COLORS["muted"]},
    }
    styles = theme.setdefault("visualStyles", {})
    wildcard = styles.setdefault("*", {}).setdefault("*", {})
    wildcard["background"] = [
        {"show": True, "color": {"solid": {"color": COLORS["card"]}}, "transparency": 0}
    ]
    wildcard["border"] = [
        {"show": True, "color": {"solid": {"color": COLORS["border"]}}, "radius": 8, "width": 1}
    ]
    wildcard["title"] = [
        {
            "show": True,
            "fontColor": {"solid": {"color": COLORS["navy"]}},
            "fontFamily": "Segoe UI Semibold",
            "fontSize": 12,
            "alignment": "left",
            "titleWrap": True,
        }
    ]
    styles.setdefault("page", {}).setdefault("*", {})["background"] = [
        {"color": {"solid": {"color": COLORS["canvas"]}}, "transparency": 0}
    ]
    styles["page"]["*"]["outspace"] = [
        {"color": {"solid": {"color": COLORS["canvas"]}}}
    ]
    write_json(THEME_PATH, theme)


def redesign_sections():
    section_dirs = sorted(path for path in SECTIONS_DIR.iterdir() if path.is_dir())
    for page_index, section_dir in enumerate(section_dirs):
        section_path = section_dir / "section.json"
        section = read_json(section_path)
        section["displayName"] = PAGE_NAMES[page_index]
        section["height"] = 800
        write_json(section_path, section)

        visual_dirs = sorted((section_dir / "visualContainers").iterdir())
        for visual_dir in visual_dirs:
            if visual_dir.name.startswith("99999_"):
                continue
            config_path = visual_dir / "config.json"
            container_path = visual_dir / "visualContainer.json"
            config = read_json(config_path)
            container = read_json(container_path)

            # Reserve a consistent title band at the top of every page.
            config["layouts"][0]["position"]["y"] += 58
            container["y"] += 58

            prefix = visual_dir.name[:5]
            title = VISUAL_TITLES.get(page_index, {}).get(prefix)
            single_visual = config.get("singleVisual", {})
            if title and single_visual.get("visualType") != "textbox":
                set_title(single_visual, title)
            if single_visual.get("visualType") == "cardVisual":
                set_card_label(single_visual)

            if page_index == 1 and prefix == "08000":
                replace_textbox(
                    config,
                    "客戶分析洞察",
                    [
                        "回購率約為 3.0%，大多數客戶僅完成一次購買。",
                        "沉睡客群人數與累積營收最高，是喚回行銷的優先對象。",
                        "高價值忠誠客戶占比較低，應以會員與二次購買誘因提升留存。",
                        "建議依 RFM 客群設計差異化優惠與再行銷活動。",
                    ],
                )
            elif page_index == 2 and prefix == "07000":
                replace_textbox(
                    config,
                    "商品與賣家洞察",
                    [
                        "美妝與健康為營收最高的商品類別。",
                        "前十大類別構成主要營收來源，適合優先配置行銷資源。",
                        "營收於 2017 年持續成長，並在年底促銷期間達到高峰。",
                        "賣家營收呈長尾分布，應維繫高績效賣家並培育中段賣家。",
                    ],
                )

            write_json(config_path, config)
            write_json(container_path, container)

        make_page_title(section_dir, PAGE_NAMES[page_index])


def main():
    redesign_theme()
    redesign_sections()
    print("Power BI report design updated.")


if __name__ == "__main__":
    main()
