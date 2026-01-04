from email.message import EmailMessage

import aiosmtplib
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.settings import Settings


async def send_verification_code(user: dict, code: str):
    message = EmailMessage()
    message["From"] = Settings.EMAIL_FROM
    message["To"] = user.get('email')
    message["Subject"] = "Tasdiqlash kodi"
    message.set_content(f"Sizning tasdiqlash kodingiz: {code}")

    html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color:#f4f4f7; padding:20px;">
            <table role="presentation" style="max-width:600px; margin:auto; background:white; border-radius:10px; overflow:hidden; box-shadow:0 4px 8px rgba(0,0,0,0.1);">
              <tr>
                <td style="background:#4f46e5; padding:20px; text-align:center; color:white; font-size:24px; font-weight:bold;">
                  🔐 Email Tasdiqlash
                </td>
              </tr>
              <tr>
                <td style="padding:30px; text-align:center; color:#333;">
                  <h2 style="margin-bottom:20px;">Xush kelibsiz!</h2>
                  <p style="font-size:16px; margin-bottom:30px;">
                    Ro‘yxatdan o‘tishni yakunlash uchun quyidagi <strong>tasdiqlash kodini</strong> kiriting:
                  </p>
                  <div style="display:inline-block; padding:15px 30px; background:#4f46e5; color:white; font-size:22px; font-weight:bold; border-radius:8px; letter-spacing:4px;">
                    {code}
                  </div>
                  <p style="margin-top:30px; font-size:14px; color:#666;">
                    Agar siz ro‘yxatdan o‘tmagan bo‘lsangiz, ushbu xabarni e’tiborsiz qoldiring.
                  </p>
                </td>
              </tr>
              <tr>
                <td style="background:#f9fafb; padding:15px; text-align:center; font-size:12px; color:#999;">
                  © 2025 Sizning loyihangiz. Barcha huquqlar himoyalangan.
                </td>
              </tr>
            </table>
          </body>
        </html>
        """

    message.add_alternative(html_content, subtype="html")
    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=Settings.EMAIL_FROM,
        password=Settings.EMAIL_PASSWORD,
    )


async def get_grapes_market(wait: WebDriverWait, url: str) -> dict:
    name = (By.XPATH, "//h1[@class='HeadlineSSemibold title']")
    price = (By.XPATH, "//div[@class='u-currency sell-price']")
    product_data = {
        'name': wait.until(EC.presence_of_element_located(name)).text,
        'current_price': wait.until(EC.presence_of_element_located(price)).text,
        'url': url,
    }
    return product_data


async def get_click_market(wait: WebDriverWait, url: str) -> dict:
    name = (By.XPATH, "(//span[@class='MuiTypography-root MuiTypography-title20 mui-style-9dzjks'])[2]")
    price = (By.XPATH, '(//span[@class="MuiTypography-root MuiTypography-title50 mui-style-1qkd03h"])[2]')
    product_data: dict = {
        'name': wait.until(EC.presence_of_element_located(name)).text,
        'current_price': wait.until(EC.presence_of_element_located(price)).text,
        'url': url,
    }
    return product_data
