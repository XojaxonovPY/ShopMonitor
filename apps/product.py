from fastapi import APIRouter, Depends
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from db.models import Product, Price
from db.sessions import SessionDep
from instruments.forms import UrlForm
from instruments.login import get_current_user
from instruments.tasks import get_grapes_market, get_click_market

product = APIRouter()


@product.post('/products/', response_model=Product)
async def get_product_title(session: SessionDep, form: UrlForm, current_user: dict = Depends(get_current_user)):
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    option.add_argument('--incognito')
    option.add_argument('--ignore-certificate-errors')
    option.add_argument('window-size=1000,800')
    option.add_argument('--disable-cache')
    option.add_argument('--disable-blink-features=AutomationControlled')
    option.add_argument('--user-agent=Selenium')
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=option)
    wait = WebDriverWait(driver, 15, poll_frequency=1)
    product_data = None
    if form.url.host == 'uzum.uz':
        driver.get(str(form.url))
        product_data = await get_grapes_market(wait, str(form.url))
    if form.url.host == 'clickbrandshop.robostore.uz':
        driver.get(str(form.url))
        product_data = await get_click_market(wait, str(form.url))
    query: Product = await Product.get(session, Product.url, product_data.get('url'))
    if query:
        price_data = {
            'product_id': query.id,
            'price': product_data.get('current_price')
        }
        await Price.create(session, **price_data)
        driver.quit()
        return query
    products = await Product.create(session, **product_data, user_id=current_user.id)
    price_data = {
        'product_id': products.id,
        'price': product_data.get('current_price')
    }
    await Price.create(session, **price_data)
    driver.quit()
    return product_data


@product.get('/all/products/', response_model=list[Product])
async def get_all_products(session: SessionDep, current_user: dict = Depends(get_current_user)):
    products = await Product.get_all(session)
    return products


@product.get('/products/{id}/', response_model=Product)
async def get_one_product(session: SessionDep, pk: int, current_user: dict = Depends(get_current_user)):
    product_one = await Product.get(session, Product.id, pk)
    return product_one


@product.get('products/prices/all/{pk}', response_model=list[Price])
async def get_all_prices(session: SessionDep, pk: int, current_user: dict = Depends(get_current_user)):
    prices = Price.get(session, Price.product_id, pk, all_=True)
    return prices


@product.delete("/products/{id}/", responses={205: {"description": "Product deleted successfully"}})
async def delete_product(session: SessionDep, pk: int, current_user: dict = Depends(get_current_user)):
    await Product.delete(session, pk)
    return {'message': 'Product deleted successfully'}
