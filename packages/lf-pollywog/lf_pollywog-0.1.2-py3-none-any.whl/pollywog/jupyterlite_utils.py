"""
JupyterLite utilities for browser-based file operations.
"""

def download_file(content, filename, content_type="application/octet-stream"):
    """
    Trigger a file download in JupyterLite/browser environment.
    
    Args:
        content (str or bytes): File content to download
        filename (str): Name of the file to download
        content_type (str): MIME type of the file
    """
    try:
        from IPython.display import Javascript, display
        import base64
        
        # Convert content to base64 for JavaScript
        if isinstance(content, str):
            content_b64 = base64.b64encode(content.encode('utf-8')).decode('ascii')
        else:
            content_b64 = base64.b64encode(content).decode('ascii')
        
        # JavaScript code to trigger download (handles binary data correctly)
        js_code = f"""
        (function() {{
            const b64 = '{content_b64}';
            const binary = atob(b64);
            const bytes = new Uint8Array(binary.length);
            for (let i = 0; i < binary.length; i++) {{
                bytes[i] = binary.charCodeAt(i);
            }}
            const blob = new Blob([bytes], {{type: '{content_type}'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = '{filename}';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }})();
        """
        
        display(Javascript(js_code))
        print(f"Download triggered: {filename}")
        
    except ImportError:
        # Fallback: save to current directory if not in browser
        with open(filename, 'w' if isinstance(content, str) else 'wb') as f:
            f.write(content)
        print(f"File saved: {filename}")

def is_jupyterlite():
    """
    Check if running in JupyterLite environment.
    """
    try:
        import sys
        return 'pyodide' in sys.modules
    except:
        return False