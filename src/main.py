import asyncio
import random

from playwright import async_api
from playwright.async_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
from playwright_stealth import stealth_async

from .errors import AutomationError
from loguru import logger


VIEWPORTS = [
    {"width": 2560, "height": 1440},
    {"width": 1920, "height": 1200},
    {"width": 1920, "height": 1080},
    {"width": 1760, "height": 990},
    {"width": 1680, "height": 1050},
    {"width": 1600, "height": 1200},
    {"width": 1600, "height": 900},
    {"width": 1366, "height": 768},
    {"width": 1280, "height": 720},
    {"width": 1128, "height": 634},
    {"width": 1024, "height": 768},
    {"width": 800, "height": 600},
]


class Automation:
    def __init__(
            self,
            title: str,
            url: str,
            proxy: str = None,
    ):
        self.title: str = title
        self.url: str = url
        self.proxy: str = proxy
        logger.info(f"Initiated session with title: {self.title} and url: {self.url}")

        self.playwright: async_api.Playwright = None  # type: ignore
        self.browser: async_api.Browser = None  # type: ignore
        self.context: async_api.BrowserContext = None  # type: ignore
        self.page: async_api.Page = None  # type: ignore
        self.viewport: dict = random.choice(VIEWPORTS)
        logger.info(f"Viewport: {self.viewport['width']}x{self.viewport['height']}")


    async def setup_browser(self) -> None:
        self.playwright = await async_api.async_playwright().start()

        if self.proxy:
            ip, port, username, password = self.proxy.split(":")
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                proxy={
                    "server": f"http://{ip}:{port}",
                    "username": username,
                    "password": password,
                }
            )
        else:
            self.browser = await self.playwright.chromium.launch(
                headless=False,
            )

        self.context = await self.browser.new_context(viewport=self.viewport)
        self.page = await self.context.new_page()
        await stealth_async(self.page)


    def get_random_actions(self) -> list[callable]:
        actions = [
            self.open_product_reviews,
            self.show_more_reviews,
            self.share_product,
            self.add_product_to_wishlist,
            # self.delete_product_from_wishlist,
            self.product_specification,
            self.compare_with_others_items,
            self.scroll_images_carousel,
            self.dynamic_scroll,
        ]
        random.shuffle(actions)
        return actions


    @staticmethod
    async def random_sleep() -> None:
        await asyncio.sleep(random.randint(4, 10))

    async def start_actions(self) -> None:
        try:
            logger.info("Closing dialog and selecting page language..")
            await self.page.goto("https://www.bol.com")
            await self.random_sleep()

            await self.close_modal_dialog()
            await self.select_page_language_and_country()
            logger.info("Searching item..")
            await self.search_item(
                title=self.title,
                url=self.url
            )

            logger.info("Starting random actions..")
            await self.random_sleep()
            for action in self.get_random_actions():
                try:
                    logger.info(f"Doing action: {action.__name__}")
                    await action()

                except (AutomationError, PlaywrightError, PlaywrightTimeoutError) as error:
                    logger.error(f"Error while doing action: {action.__name__}: {error}")


        except (AutomationError, PlaywrightError, PlaywrightTimeoutError) as error:
            logger.error(f"Error while doing actions: {error}")


        logger.success("Automation finished")



    async def close_modal_dialog(
            self,
            accept_button_selector: str = "#js-first-screen-accept-all-button"
    ) -> None:
        """Close modal dialog by clicking on accept button."""
        try:
            element = await self.page.wait_for_selector(accept_button_selector, timeout=3000)
            await element.click(delay=2000)
            await self.random_sleep()

        except PlaywrightTimeoutError:
            return


    async def select_page_language_and_country(
            self,
            continue_button_selector: str = "button[data-test='continue-button']",
    ) -> None:
        """Select page language and country by clicking on continue button."""
        try:
            element = await self.page.wait_for_selector(continue_button_selector, timeout=3000)
            await element.click(delay=2000)
            await self.random_sleep()

        except PlaywrightTimeoutError:
            return

    async def search_item(
            self,
            title: str,
            url: str,
            search_input_selector: str = "#searchfor",
    ):
        try:
            element = await self.page.wait_for_selector(search_input_selector, timeout=3000)
            await element.click(delay=2000)
            await element.fill(title, timeout=3000)
            await element.press("Enter", delay=1000)

            await self.random_sleep()
            await self.dynamic_scroll()

            products = await self.get_products_list()
            await self.click_product_if_match(products, url)

            page = 1
            while page <= 20:
                page += 1
                page_selector = f".js_pagination_item[data-page-number='{page}']"
                element = await self.page.wait_for_selector(page_selector, timeout=3000)
                await element.scroll_into_view_if_needed()
                await element.click(delay=2000)

                await self.random_sleep()
                await self.dynamic_scroll()

                await self.click_product_if_match(products, url)

        except (PlaywrightTimeoutError, PlaywrightError):
            await self.page.goto(url, wait_until="load")

    async def click_product_if_match(self, products: list[tuple[str, async_api.ElementHandle]], url: str):
        for el_url, product in products:
            if url == el_url:

                try:
                    await product.scroll_into_view_if_needed()
                    await product.click(delay=2000)

                except (PlaywrightTimeoutError, PlaywrightError):
                    logger.error(f"Error while clicking on product element, going to page directly")
                    await self.page.goto(url, wait_until="load")


    async def scroll_page(self, x: int = None, y: int = None) -> None:
        await self.page.mouse.wheel(
            x if x else random.randint(100, self.page.viewport_size["height"]),
            y if y else random.randint(100, self.page.viewport_size["width"])
        )
        await self.random_sleep()


    async def open_product_reviews(
            self,
            reviews_selector: str = "div[data-test='rating-suffix']",
    ) -> None:
        try:
            await self.random_sleep()
            element = await self.page.wait_for_selector(reviews_selector, timeout=3000)
            await element.scroll_into_view_if_needed(timeout=3000)
            await element.click(delay=2000)
            await self.random_sleep()

        except PlaywrightTimeoutError:
            raise AutomationError("Reviews not found.")


    async def show_more_reviews(
            self,
            show_more_button_selector: str = "#show-more-reviews",
            max_reviews: int = 2,
    ) -> None:
        """Click on show more button to show more reviews until max_reviews."""

        try:
            reviews_count = 0
            while await self.page.is_visible(show_more_button_selector, timeout=3000) and reviews_count < max_reviews:
                element = await self.page.wait_for_selector(show_more_button_selector, timeout=3000)
                await element.scroll_into_view_if_needed()
                await element.click(delay=2000)

                reviews_count += 1
                await self.random_sleep()

        except PlaywrightTimeoutError:
            return



    async def get_products_list(
            self,
            list_selector: str = "#js_items_content",
    ) -> list[tuple[str, async_api.ElementHandle]]:
        products_links = []
        try:
            element = await self.page.wait_for_selector(list_selector, timeout=3000)
            products = await element.query_selector_all("a[data-test='product-title']")
            for product in products:
                products_links.append(
                    (
                        str(f'https://www.bol.com{await product.get_attribute("href")}'),
                        product
                    )
                )

            return products_links

        except PlaywrightTimeoutError:
            raise AutomationError("Products list not found.")


    async def share_product(
            self,
            share_button_selector: str = "button[aria-label='Delen']",
            href_selector: str = "a[title='Kopieer link']",
    ) -> None:
        try:
            element = await self.page.wait_for_selector(share_button_selector, timeout=3000)
            await element.scroll_into_view_if_needed()
            await element.click(delay=2000)
            await asyncio.sleep(3, 10)

            try:
                element = await self.page.wait_for_selector(href_selector, timeout=3000)
                await element.click(delay=2000)

            except PlaywrightTimeoutError:
                raise AutomationError("Share link not found.")

        except PlaywrightTimeoutError:
            raise AutomationError("Share button not found.")


    async def add_product_to_wishlist(
            self,
            wishlist_button_selector: str = "#buy-block > div.buy-block__options.js_basket_button_row.js_multiple_basket_buttons_page.u-mb--m > span > wsp-wishlist-button",
            close_button_selector: str = "button[data-test='button']",
    ) -> None:
        try:
            await self.scroll_page()

            element = await self.page.wait_for_selector(wishlist_button_selector, timeout=3000)
            await element.scroll_into_view_if_needed()
            await element.click(delay=2000)
            await asyncio.sleep(4, 8)

            try:
                element = await self.page.wait_for_selector(close_button_selector, timeout=3000)
                await element.click(delay=2000)
                await self.random_sleep()

            except PlaywrightTimeoutError:
                raise AutomationError("Close button not found.")

        except PlaywrightTimeoutError:
            raise AutomationError("Wishlist button not found.")


    async def delete_product_from_wishlist(
            self,
            delete_button_selector: str = "#buy-block > div.buy-block__options.js_basket_button_row.js_multiple_basket_buttons_page.u-mb--m > span > wsp-wishlist-button > button",
    ) -> None:
        try:
            element = await self.page.wait_for_selector(delete_button_selector, timeout=3000)
            await element.scroll_into_view_if_needed(timeout=3000)
            await element.click(delay=2000)

        except PlaywrightTimeoutError:
            raise AutomationError("Delete button not found.")



    async def product_specification(
            self,
            specification_selector: str = "#main-specs > div > div > wsp-scroll-to",
            show_more_button_selector: str = "a[data-test='show-more']",
            show_less_button_selector: str = "a[data-test='show-less']",
    ) -> None:
        try:
            element = await self.page.wait_for_selector(specification_selector, timeout=3000)
            await element.scroll_into_view_if_needed()
            await element.click(delay=2000)

            await self.random_sleep()
            await self.scroll_page(x=random.randint(100, 300), y=random.randint(300, 800))

            try:
                element = await self.page.wait_for_selector(show_more_button_selector, timeout=3000)
                await element.scroll_into_view_if_needed()
                await element.click(delay=2000)
                await asyncio.sleep(5, 20)

                try:
                    element = await self.page.wait_for_selector(show_less_button_selector, timeout=3000)
                    await element.scroll_into_view_if_needed()
                    await element.click(delay=2000)

                    await self.scroll_page(x=random.randint(100, 300), y=random.randint(300, 800))
                    await self.random_sleep()

                except PlaywrightTimeoutError:
                    raise AutomationError("Show less button not found.")

            except PlaywrightTimeoutError:
                raise AutomationError("Show more button not found.")

        except PlaywrightTimeoutError:
            raise AutomationError("Specification button not found.")


    async def compare_with_others_items(
            self,
            compare_button_selector: str = 'div[data-test="compare-checkbox"]',
    ) -> None:
        try:
            await self.scroll_page(x=random.randint(100, 300), y=random.randint(100, 300))
            await self.random_sleep()

            element = await self.page.wait_for_selector(compare_button_selector, timeout=3000)
            await element.scroll_into_view_if_needed(timeout=3000)
            await element.click(delay=2000)
            await self.random_sleep()

        except PlaywrightTimeoutError:
            raise AutomationError("Compare button not found.")



    async def scroll_images_carousel(
            self,
            carousel_next_selector: str = "button[data-test='carousel-next']",
            carousel_prev_selector: str = "button[data-test='carousel-back']",
    ) -> None:
        try:
            element = await self.page.wait_for_selector(carousel_next_selector, timeout=3000)
            await element.scroll_into_view_if_needed()
            await element.click(delay=2000)

            await self.random_sleep()
            # await self.scroll_page(x=random.randint(100, 300), y=random.randint(100, 300))

            try:
                element = await self.page.wait_for_selector(carousel_prev_selector, timeout=3000)
                await element.click(delay=2000)
                await self.random_sleep()
                # await self.dynamic_scroll()

            except PlaywrightTimeoutError:
                raise AutomationError("Carousel prev button not found.")

        except PlaywrightTimeoutError:
            raise AutomationError("Carousel next button not found.")



    async def dynamic_scroll(self) -> None:
        count = random.randint(2, 4)
        for _ in range(count):
            await self.scroll_page(0, random.randint(200, 1000))



    async def start(self):
        await self.setup_browser()
        await self.start_actions()
        await self.browser.close()
        await self.playwright.stop()


# async def main():
#     client = Automation(
#         title="Wimperserum",
#         url="https://www.bol.com/nl/nl/p/kingsowned-wimperserum-extra-sterk-het-unieke-kingsowned-lash-serum/9300000161235462/"
#     )
#     await client.setup_browser()
#     await client.start_actions()
