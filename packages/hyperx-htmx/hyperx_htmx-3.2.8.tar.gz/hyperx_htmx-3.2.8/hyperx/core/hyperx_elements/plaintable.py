from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape



@register_hx_tag("plaintable")
def convert_plaintable(tag, attrs):
    """
    Render a plain Bootstrap-style table with no CRUD logic.
    Example:
      <hx:plaintable fields="id,username,email" data-target="#users-table" />
    """
    fields = [f.strip() for f in attrs.get("fields", "").split(",") if f.strip()]
    table_class = attrs.get("class", "table table-striped table-hover align-middle")
    caption = attrs.get("caption", "")

    # Build header
    header_html = "".join(f"<th>{f.title()}</th>" for f in fields)

    html = f"""
    <table class="{table_class}">
        {"<caption>" + caption + "</caption>" if caption else ""}
        <thead><tr>{header_html}</tr></thead>
        <tbody>
            <tr><td colspan="{len(fields)}" class="text-center text-muted py-3">
                <i class="fas fa-info-circle me-2"></i>No data available.
            </td></tr>
        </tbody>
    </table>
    """
    return html