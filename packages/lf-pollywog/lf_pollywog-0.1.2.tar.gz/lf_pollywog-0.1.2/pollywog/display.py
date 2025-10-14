_DISPLAY_THEME = "light"


def set_theme(theme):
    """
    Set the global theme for display_calcset ("light" or "dark").
    """
    global _DISPLAY_THEME
    if theme not in ("light", "dark"):
        raise ValueError("Theme must be 'light' or 'dark'.")
    _DISPLAY_THEME = theme


def display_calcset(calcset, theme=None, colors=None, display_output=True):
    """
    Display a CalcSet in a Jupyter notebook with a visual style similar to Leapfrog, rendering equations and logic blocks visually.
    Supports 'theme' ("light" or "dark") and custom color palettes via 'colors' dict. If theme is None, uses global setting from set_theme().
    """
    from IPython.display import display, HTML
    import html

    # Default color palettes
    default_colors = {
        "light": {
            "background": "#eee",
            "text": "#222",
            "variable": "#0057b7",
            "label": "#222",
            "if": "#0057b7",
            "arrow": "#222",
            "comment": "#999",
            "var_ref": "#b77",
        },
        "dark": {
            "background": "#222",
            "text": "#eee",
            "variable": "#7abaff",
            "label": "#eee",
            "if": "#7abaff",
            "arrow": "#eee",
            "comment": "#bbb",
            "var_ref": "#ffb77a",
        },
    }
    use_theme = theme if theme is not None else _DISPLAY_THEME
    palette = default_colors.get(use_theme, default_colors["light"]).copy()
    if colors:
        palette.update(colors)

    def render_expression(expr, indent=0):
        pad = "&nbsp;" * (indent * 4)
        if isinstance(expr, str):
            expr = html.escape(expr)
            expr = expr.replace(
                "[", f'<span style="color:{palette["var_ref"]};">['
            ).replace("]", "]</span>")
            return pad + f'<span style="color:{palette["text"]};">{expr}</span>'
        elif isinstance(expr, list):
            return "<br>".join(render_expression(e, indent) for e in expr)
        if isinstance(expr, dict):
            typ = expr.get("type")
            if typ == "if":
                rows = expr.get("rows", [])
                otherwise = expr.get("otherwise", {}).get("children", [])
                html_rows = []
                for row in rows:
                    cond = row.get("test", {}).get("children", [])
                    res = row.get("result", {}).get("children", [])
                    html_rows.append(
                        f'<div style="margin-left:{indent*24}px;border-left:2px solid {palette["if"]};padding-left:8px;">'
                        f'<span style="color:{palette["if"]};">if</span> '
                        f"{render_expression(cond, 0)} "
                        f'<span style="color:{palette["arrow"]};">&rarr;</span> '
                        f"{render_expression(res, indent+1)}"
                        f"</div>"
                    )
                if otherwise:
                    html_rows.append(
                        f'<div style="margin-left:{indent*24}px;border-left:2px solid {palette["if"]};padding-left:8px;">'
                        f'<span style="color:{palette["if"]};">otherwise</span> '
                        f'<span style="color:{palette["arrow"]};">&rarr;</span> '
                        f"{render_expression(otherwise, indent+1)}"
                        f"</div>"
                    )
                return "".join(html_rows)
            elif typ == "if_row":
                cond = expr.get("test", {}).get("children", [])
                res = expr.get("result", {}).get("children", [])
                return (
                    f'<div style="margin-left:{indent*24}px;border-left:2px solid {palette["if"]};padding-left:8px;">'
                    f'<span style="color:{palette["if"]};">if</span> '
                    f"{render_expression(cond, 0)} "
                    f'<span style="color:{palette["arrow"]};">&rarr;</span> '
                    f"{render_expression(res, indent+1)}"
                    f"</div>"
                )
            elif typ == "list":
                children = expr.get("children", [])
                return render_expression(children, indent)
            else:
                return (
                    pad
                    + f'<span style="color:{palette["text"]};">{html.escape(str(expr))}</span>'
                )
        else:
            return (
                pad
                + f'<span style="color:{palette["text"]};">{html.escape(str(expr))}</span>'
            )

    def render_equation(eq):
        if isinstance(eq, dict) and eq.get("type") == "equation":
            statement = eq["statement"]
            comment = eq.get("comment", "")
            expr_html = render_expression(statement)
            comment_html = (
                f'<span style="color:#999;">{html.escape(comment)}</span>'
                if comment
                else ""
            )
            return f'<div style="margin-left:1em;color:#555;">{expr_html} {comment_html}</div>'
        return html.escape(str(eq))

    def render_item(item):
        d = item.to_dict() if hasattr(item, "to_dict") else item
        name = d.get("name", "")
        typ = d.get("type", "")
        eq = d.get("equation", None)
        comment = d.get("comment", "")
        html_block = f'<div style="margin-bottom:0.5em;">'
        html_block += f'<b style="color:#0057b7;">{html.escape(name)}</b> '
        # Show calculation_type for calculation items
        calc_type = d.get("calculation_type")
        label = typ
        if typ == "calculation" and calc_type:
            label = calc_type
        html_block += f'<span style="background:#eee;border-radius:4px;padding:2px 6px;color:#222;">{html.escape(label)}</span>'
        if eq:
            html_block += render_equation(eq)
        if comment:
            html_block += (
                f'<div style="color:#999;margin-left:1em;">{html.escape(comment)}</div>'
            )
        html_block += "</div>"
        return html_block

    def section(title, items):
        if not items:
            return ""
        html_items = "".join(render_item(item) for item in items)
        return f'<details open><summary style="font-size:1.1em;font-weight:bold;color:{palette["variable"]};">{title}</summary>{html_items}</details>'

    variables = [
        i for i in calcset.items if getattr(i, "item_type", None) == "variable"
    ]
    calculations = [
        i for i in calcset.items if getattr(i, "item_type", None) == "calculation"
    ]
    filters = [i for i in calcset.items if getattr(i, "item_type", None) == "filter"]

    html_out = (
        f'<div style="font-family:sans-serif;max-width:900px;color:{palette["text"]};">'
    )
    html_out += section("Variables", variables)
    html_out += section("Calculations", calculations)
    html_out += section("Filters", filters)
    html_out += "</div>"
    if display_output:
        display(HTML(html_out))
    else:
        return html_out
