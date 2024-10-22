import time

from playwright.sync_api import sync_playwright


class OzonSellerParse:
    def __init__(self, keyword: str):
        self.context = None
        self.keyword = keyword
        self.list_seller_name = []

    def __scroll_down(self, page):
        page.evaluate('''
                                const scrollStep = 200; // Размер шага прокрутки (в пикселях)
                                const scrollInterval = 100; // Интервал между шагами (в миллисекундах)

                                const scrollHeight = document.documentElement.scrollHeight;
                                let currentPosition = 0;
                                const interval = setInterval(() => {
                                    window.scrollBy(0, scrollStep);
                                    currentPosition += scrollStep;

                                    if (currentPosition >= scrollHeight) {
                                        clearInterval(interval);
                                    }
                                }, scrollInterval);
                            ''')

    def __get_seller_name(self, url: str):
        page2 = self.context.new_page()
        page2.goto(url)
        self.__scroll_down(page=page2)

        seller_name = page2.locator("//div[@data-widget='webCurrentSeller']//a[@title]").get_attribute("title")
        print(seller_name)

    def __get_links(self):
        self.page.wait_for_selector("#paginatorContent")
        self.__scroll_down(page=self.page)
        self.page.wait_for_selector(f':text("Дальше")')

        search_result = self.page.locator("//div[@id='paginatorContent']")
        links = search_result.locator(".tile-hover-target").all()
        print(len(links))

        count = 0

        for link in links:
            if count > 5:
                break
            url = "https://ozon.ru" + link.get_attribute("href")
            self.__get_seller_name(url=url)
            count += 1

    def parse(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
            self.context = browser.new_context()
            self.page = self.context.new_page()
            self.page.goto("https://ozon.ru")
            time.sleep(2)
            self.page.reload()

            time.sleep(1)
            self.page.get_by_placeholder("Искать на Ozon").type(text=self.keyword, delay=0.3)
            self.page.locator("//button[@type='submit']").click()
            time.sleep(1)
            self.__get_links()


if __name__ == "__main__":
    parser = OzonSellerParse("Вентилятор").parse()
