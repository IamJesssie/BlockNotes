import csv
import os
import math

def sanitize_key(k):
    return (k or "").strip()

def read_responses(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            clean = {}
            for k, v in row.items():
                clean[sanitize_key(k)] = (v or '').strip()
            rows.append(clean)
        return rows

def parse_metrics(rows):
    a_scores = []
    b_scores = []
    rec_counts = {"Version A - NEW": 0, "Version B - OLD": 0}
    perf_counts = {"Version A faster": 0, "No difference": 0, "Version B faster": 0, "Not sure": 0}
    ui_counts = {"Version A - NEW": 0, "Version B - OLD": 0, "Both were equal": 0}

    for r in rows:
        a = r.get("3. How would you rate your overall experience with Version A - NEW", "").strip()
        b = r.get("4. How would you rate your overall experience with Version B - OLD", "").strip()
        try:
            if a:
                a_scores.append(float(a))
        except:
            pass
        try:
            if b:
                b_scores.append(float(b))
        except:
            pass

        rec = r.get("14. Which version would you recommend for production use?", "").strip()
        if rec in rec_counts:
            rec_counts[rec] += 1

        perf = r.get("8. Did you notice any performance differences between the versions?", "").strip().lower()
        if "version a - new is faster" in perf:
            perf_counts["Version A faster"] += 1
        elif "version b - old is faster" in perf:
            perf_counts["Version B faster"] += 1
        elif "no noticeable difference" in perf:
            perf_counts["No difference"] += 1
        elif "not sure" in perf:
            perf_counts["Not sure"] += 1

        ui = r.get("5. Which version had better user interface design?", "").strip()
        if ui in ui_counts:
            ui_counts[ui] += 1

    avg_a = round(sum(a_scores) / len(a_scores), 2) if a_scores else 0.0
    avg_b = round(sum(b_scores) / len(b_scores), 2) if b_scores else 0.0
    return avg_a, avg_b, rec_counts, perf_counts, ui_counts

def svg_bar_horizontal(title, data, width=800, height=400, padding=60, bar_h=24, gap=18, colors=None):
    items = list(data.items())
    max_val = max([v for _, v in items]) if items else 1
    inner_w = width - padding * 2
    inner_h = height - padding * 2
    y_start = padding
    x_start = padding
    svg = []
    svg.append(f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>")
    svg.append(f"<style>text{{font-family:Arial,sans-serif;font-size:13px;fill:#1a1a1a}} .title{{font-size:16px;font-weight:bold}} .label{{fill:#555}} .axis{{stroke:#bbb;stroke-width:1}} .barlabel{{fill:#1a1a1a;font-weight:bold}}</style>")
    svg.append(f"<rect x='0' y='0' width='{width}' height='{height}' fill='#FFFFFF'/>")
    svg.append(f"<text class='title' x='{padding}' y='{padding - 20}'>{title}</text>")
    for i, (label, val) in enumerate(items):
        y = y_start + i * (bar_h + gap)
        w = 0 if max_val == 0 else int((val / max_val) * inner_w)
        color = colors[i % len(colors)] if colors else '#384BFF'
        svg.append(f"<rect x='{x_start}' y='{y}' width='{w}' height='{bar_h}' fill='{color}' rx='6' ry='6'/>")
        svg.append(f"<text class='label' x='{x_start}' y='{y - 6}'>{label}</text>")
        svg.append(f"<text class='barlabel' x='{x_start + w + 8}' y='{y + bar_h - 6}'>{val}</text>")
    for g in range(5):
        gx = x_start + int((g + 1) * inner_w / 5)
        svg.append(f"<line class='axis' x1='{gx}' y1='{y_start - 8}' x2='{gx}' y2='{y_start + inner_h}' opacity='0.45' />")
    svg.append("</svg>")
    return "".join(svg)

def svg_bar_vertical(title, data, width=600, height=420, padding=60, colors=None, y_max=5):
    items = list(data.items())
    inner_w = width - padding * 2
    inner_h = height - padding * 2
    count = len(items)
    bar_w = int(inner_w / max(count, 1) * 0.5)
    gap = int(inner_w / max(count, 1) * 0.5)
    svg = []
    svg.append(f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>")
    svg.append(f"<style>text{{font-family:Arial,sans-serif;font-size:13px;fill:#1a1a1a}} .title{{font-size:16px;font-weight:bold}} .axis{{stroke:#bbb;stroke-width:1}} .ticktext{{fill:#606060}}</style>")
    svg.append(f"<rect x='0' y='0' width='{width}' height='{height}' fill='#FFFFFF'/>")
    svg.append(f"<text class='title' x='{padding}' y='{padding - 20}'>{title}</text>")
    for t in range(1, y_max + 1):
        ty = padding + inner_h - int((t / y_max) * inner_h)
        svg.append(f"<line class='axis' x1='{padding}' y1='{ty}' x2='{padding + inner_w}' y2='{ty}' opacity='0.45' />")
        svg.append(f"<text class='ticktext' x='{padding - 30}' y='{ty + 4}'>{t}</text>")
    for i, (label, val) in enumerate(items):
        bh = int((val / y_max) * inner_h)
        x = padding + i * (bar_w + gap) + gap * 0.5
        y = padding + inner_h - bh
        color = colors[i % len(colors)] if colors else '#   '
        svg.append(f"<rect x='{x}' y='{y}' width='{bar_w}' height='{bh}' fill='{color}' rx='6' ry='6'/>")
        svg.append(f"<text x='{x + bar_w/2 - 20}' y='{y - 8}'>{val}</text>")
        svg.append(f"<text x='{x + bar_w/2 - 36}' y='{padding + inner_h + 18}'>{label}</text>")
    svg.append("</svg>")
    return "".join(svg)

def save_svg(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    csv_path = os.path.join(base, 'UX Improvement Evaluation Form .csv')
    out_dir = os.path.join(base, 'note_app', 'static', 'notes', 'img', 'check_figures')
    rows = read_responses(csv_path)
    avg_a, avg_b, rec_counts, perf_counts, ui_counts = parse_metrics(rows)

    sat_svg = svg_bar_vertical(
        title="Overall Experience (Average Ratings)",
        data={"Version A": avg_a, "Version B": avg_b},
        width=600,
        height=420,
        padding=60,
        colors=["#384BFF", "#A020F0"],
        y_max=5
    )
    save_svg(os.path.join(out_dir, 'satisfaction.svg'), sat_svg)

    rec_svg = svg_bar_horizontal(
        title="Production Recommendation Counts",
        data={"Version A - NEW": rec_counts.get("Version A - NEW", 0), "Version B - OLD": rec_counts.get("Version B - OLD", 0)},
        width=800,
        height=300,
        padding=60,
        bar_h=28,
        gap=22,
        colors=["#384BFF", "#A020F0"]
    )
    save_svg(os.path.join(out_dir, 'production_recommendation.svg'), rec_svg)

    perf_svg = svg_bar_horizontal(
        title="Performance Perception Distribution",
        data=perf_counts,
        width=800,
        height=360,
        padding=60,
        bar_h=24,
        gap=18,
        colors=["#00D9FF", "#384BFF", "#A020F0", "#6EE7B7"]
    )
    save_svg(os.path.join(out_dir, 'performance_distribution.svg'), perf_svg)

    ui_svg = svg_bar_horizontal(
        title="UI Design Preference",
        data=ui_counts,
        width=800,
        height=320,
        padding=60,
        bar_h=26,
        gap=18,
        colors=["#384BFF", "#A020F0", "#00D9FF"]
    )
    save_svg(os.path.join(out_dir, 'ui_design_preference.svg'), ui_svg)

if __name__ == '__main__':
    main()
