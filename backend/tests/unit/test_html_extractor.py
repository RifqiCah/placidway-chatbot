from backend.app.infrastructure.ingestion.html_extractor import HtmlContentExtractor


def test_extractor_removes_navigation_scripts_and_duplicates() -> None:
    html = """
    <html><head><title>Clinic Page</title><script>ignore()</script></head>
    <body><nav>Navigation noise</nav><main>
      <h1>Treatment package</h1><p>Price starts at $100 USD.</p><p>Price starts at $100 USD.</p>
    </main><footer>Footer noise</footer></body></html>
    """
    page = HtmlContentExtractor().extract(html)
    assert page.title == "Clinic Page"
    assert page.blocks == ("Treatment package", "Price starts at $100 USD.")

