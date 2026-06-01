import reflex as rx
from reflex_base.plugins.sitemap import SitemapPlugin

config = rx.Config(
    app_name="yasched_web",
    frontend_port=3000,
    backend_port=8000,
    plugins=[SitemapPlugin()],
)
