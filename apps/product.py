from typing import Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from apps.depends import SessionDep
from db.models import Product, Price
from instruments.login import UserSession
from instruments.tasks import get_grapes_market, get_click_market
from schemas import UrlSchema, ProductResponseSchema, PriceResponseSchema

router = APIRouter()

response: dict[str, Any] = {
    "status_code": status.HTTP_205_RESET_CONTENT
}


@router.post('/products/', response_model=ProductResponseSchema, status_code=status.HTTP_201_CREATED)
async def get_product_title(session: SessionDep, form: UrlSchema, user: UserSession):
    option: ChromeOptions = ChromeOptions()
    option.add_argument('--headless')
    option.add_argument('--incognito')
    option.add_argument('--ignore-certificate-errors')
    option.add_argument('window-size=1000,800')
    option.add_argument('--disable-cache')
    option.add_argument('--disable-blink-features=AutomationControlled')
    option.add_argument('--user-agent=Selenium')
    service = Service(executable_path=ChromeDriverManager().install())
    driver: Chrome = Chrome(service=service, options=option)
    wait: WebDriverWait = WebDriverWait(driver, 15, poll_frequency=1)
    product_data = None
    if form.url.host == 'uzum.uz':
        driver.get(str(form.url))
        product_data = await get_grapes_market(wait, str(form.url))
    if form.url.host == 'clickbrandshop.robostore.uz':
        driver.get(str(form.url))
        product_data = await get_click_market(wait, str(form.url))
    query: Product | None = await Product.get(session, url=product_data.get('url'))
    if query:
        price_data = {
            'product_id': query.id,
            'price': product_data.get('current_price')
        }
        await Price.create(session, **price_data)
        driver.quit()
        return query
    products: Product = await Product.create(session, **product_data, user_id=user.id)
    price_data = {
        'product_id': products.id,
        'price': product_data.get('current_price')
    }
    await Price.create(session, **price_data)
    driver.quit()
    return product_data


@router.get('/all/products/', response_model=list[ProductResponseSchema])
async def get_all_products(session: SessionDep, user: UserSession):
    products = await Product.all_(session)
    return products


@router.get('/products/{id}/', response_model=ProductResponseSchema)
async def get_one_product(session: SessionDep, pk: int, user: UserSession):
    product_one = await Product.get(session, id=pk)
    return product_one


@router.get('products/prices/all/{pk}', response_model=list[PriceResponseSchema])
async def get_all_prices(session: SessionDep, pk: int, user: UserSession):
    prices = Price.filter(session, Price.product_id == pk)
    return prices


@router.delete("/products/{id}/", **response)
async def delete_product(session: SessionDep, pk: int, user: UserSession):
    await Product.delete(session, pk)
    return JSONResponse({'message': 'Product deleted successfully'})
