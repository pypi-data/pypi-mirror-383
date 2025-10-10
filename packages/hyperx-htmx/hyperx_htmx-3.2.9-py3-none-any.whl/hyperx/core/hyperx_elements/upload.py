"""
hx:upload
────────────────────────────────────────────
Declarative uploader linked with AI schema autogen + dataset watcher.
"""

from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape

@register_hx_tag("upload")
def convert_upload(tag, attrs):
    """
    Usage:
      <hx:upload
          post="hyperx:upload_handler"
          accept=".csv,.json"
          autoschema="true"
          label="Upload your dataset"
          target="#upload-status"
      />
    """
    post = attrs.get("post", "hyperx:upload_handler")  # Django route
    accept = attrs.get("accept", ".csv,.json")
    label = escape(attrs.get("label", "Upload file"))
    indicator = attrs.get("indicator", "")
    target = attrs.get("target", "#upload-status")
    autoschema = attrs.get("autoschema", "true").lower() in ("true", "1", "yes")

    autoschema_attr = f'data-autoschema="{str(autoschema).lower()}"'

    return f"""
    <div class="hx-uploader border border-dashed rounded p-4 text-center"
         style="cursor:pointer;" {autoschema_attr}
         onclick="this.querySelector('input[type=file]').click();">
      <i class="fas fa-cloud-upload-alt fa-2x mb-2"></i>
      <p class="mb-1">{label}</p>
      <input type="file" name="file" accept="{accept}" class="d-none"
             hx-post="/{post}" hx-target="{target}" hx-swap="innerHTML"
             hx-indicator="{indicator}" />
    </div>

    <script src="/static/hyperx/js/hyperx-events.js"></script>

    <script>
    const uploader = document.currentScript.previousElementSibling;
    const input = uploader.querySelector('input[type=file]');
    uploader.addEventListener('dragover', e => {{
        e.preventDefault(); uploader.classList.add('bg-light');
    }});
    uploader.addEventListener('dragleave', e => {{
        e.preventDefault(); uploader.classList.remove('bg-light');
    }});
    uploader.addEventListener('drop', e => {{
        e.preventDefault(); input.files = e.dataTransfer.files;
        htmx.trigger(input, 'change');
    }});
    </script>
    """
