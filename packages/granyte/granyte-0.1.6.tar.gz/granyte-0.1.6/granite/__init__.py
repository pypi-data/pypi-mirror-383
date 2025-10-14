"""Python SDK for the Granyte Protocol"""
import zef

__version__ = '0.1.6'

def hello(name="Granite"):
    return f"Hello, {name}!!"


def launch_studio(port: int=3000):
    from zef import ET, FX, run
    
    # Load HTML content from package data
    try:
        # Python 3.9+
        from importlib.resources import files
        html_content = files('granite').joinpath('studio.html').read_text(encoding='utf-8')
    except (ImportError, AttributeError):
        # Fallback for Python 3.7-3.8
        import importlib.resources as pkg_resources
        html_content = pkg_resources.read_text('granite', 'studio.html', encoding='utf-8')

    domains = {
        '/': ET.HTML(content=html_content),
    }

    FX.StartHTTPServer(
        domains={"localhost": domains},
        port=port,
    ) | run

    FX.OpenInBrowser(url=f'http://localhost:{port}') | run




