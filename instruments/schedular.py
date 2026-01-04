from apscheduler.schedulers.asyncio import AsyncIOScheduler
from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from db.models import Product, Price
from db.sessions import AsyncSessionLocal
from instruments.tasks import get_grapes_market, get_click_market


async def update_product_price():
    async with AsyncSessionLocal() as session:
        option: ChromeOptions = ChromeOptions()
        option.add_argument('--headless')
        option.add_argument('--incognito')
        option.add_argument('--ignore-certificate-errors')
        option.add_argument('window-size=1000,800')
        option.add_argument('--disable-cache')
        option.add_argument('--disable-blink-features=AutomationControlled')
        option.add_argument('--user-agent=Selenium')
        service: Service = Service(executable_path=ChromeDriverManager().install())
        driver: Chrome = Chrome(service=service, options=option)
        wait: WebDriverWait = WebDriverWait(driver, 15, poll_frequency=1)
        products: list[Product] = await Product.all_(session)
        product_data: dict | None = None
        for product in products:
            if product.url.startswith("https://clickbrandshop.robostore.uz"):
                driver.get(product.url)
                product_data: dict = await get_click_market(wait, product.url)
            elif product.url.startswith("https://uzum.uz/uz"):
                driver.get(product.url)
                product_data: dict = await get_grapes_market(wait, product.url)
            current_price: str | None = product_data.get('current_price')
            if current_price and current_price != product.current_price:
                print(f"🔄 {product.name}: {product.current_price} → {current_price}")
                await Product.update(session, product.id, current_price=current_price)
                await Price.create(session, product_id=product.id, price=current_price)
        driver.quit()


def start_scheduler():
    scheduler: AsyncIOScheduler = AsyncIOScheduler()
    scheduler.add_job(update_product_price, "interval", minutes=1)
    scheduler.start()
    print("🕒 Scheduler ishga tushdi (har 10 daqiqada narxlarni tekshiradi)")
    return scheduler
