from inspector_commons.bridge.bridge_browser import BrowserBridge  # type: ignore
from inspector_commons.utils import force_kill_process  # type: ignore
from inspector.windows.base import Window


class BrowserWindow(Window):
    BRIDGE = BrowserBridge
    DEFAULTS = {
        "title": "Robocorp - Web Locators",
        "url": "browser.html",
        "width": 560,
        "height": 560,
        "on_top": True,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._force_closing = False

    def on_closing(self):
        super().on_closing()

        self.logger.debug("The Browser PID (on closing): %s", self._bridge.browser_pid)
        # force closing the entire app if the close app button is pressed
        force_kill_process(logger=self.logger)
