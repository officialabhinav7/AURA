from playwright.async_api import async_playwright


class BrowserController:

    def __init__(self):
        # Playwright instance.
        self.playwright = None

        # Chromium browser instance.
        self.browser = None

        # Current browser page/tab.
        self.page = None

    async def start(self):
        # Start Playwright.
        self.playwright = await async_playwright().start()

        # Launch Chromium.
        # headless=False allows us to see the browser.
        self.browser = await self.playwright.chromium.launch(
            headless=False
        )

        # Create a new browser tab.
        self.page = await self.browser.new_page()

    async def open(self, url):
        # Open the webpage.
        #
        # domcontentloaded tells Playwright to continue
        # once the basic HTML document has loaded.
        #
        # We don't wait for every image, advertisement,
        # analytics script, etc.
        await self.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        # Return basic information about the webpage.
        return {
            "url": self.page.url,
            "title": await self.page.title()
        }

    async def close(self):
        # Close the browser if it was started.
        if self.browser:
            await self.browser.close()

        # Stop Playwright.
        if self.playwright:
            await self.playwright.stop()