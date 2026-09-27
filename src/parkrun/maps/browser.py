from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import time
import webbrowser

logger = logging.getLogger(__name__)

# How long to wait for the browser to request the page before giving up
BROWSER_TIMEOUT_SECS: int = 30


def show_in_browser(html: str) -> None:
    """
    Open the given HTML page in the browser, returning once it has loaded.

    OpenStreetMap's tile servers block requests without a Referer header, which
    a page opened from file:// (like Map.show_in_browser does) never sends. So
    serve the page once from localhost instead. Only the page itself comes from
    this server, so it can stop straight away, although refreshing the page
    will then fail.
    """

    page: bytes = html.encode("utf-8")
    served: bool = False

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal served
            if self.path != "/":
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)
            served = True

        def log_message(self, format, *args):
            logger.debug(format, *args)

    # Port 0 picks any free port
    with HTTPServer(("127.0.0.1", 0), Handler) as server:
        webbrowser.open(f"http://127.0.0.1:{server.server_port}/")
        # Keep handling requests in case the browser asks for something else
        # first, like a favicon
        deadline: float = time.monotonic() + BROWSER_TIMEOUT_SECS
        while not served and time.monotonic() < deadline:
            server.timeout = deadline - time.monotonic()
            server.handle_request()

    if not served:
        logger.warning("Browser didn't load the map within %d seconds", BROWSER_TIMEOUT_SECS)
