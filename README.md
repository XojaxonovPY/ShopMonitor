# 🛍️ Product Price Tracker

**Product Price Tracker** — bu foydalanuvchilarga turli onlayn-do‘konlardagi mahsulotlarni kuzatish, ularning narxlari
o‘zgarishini real vaqtda monitoring qilish imkonini beruvchi FastAPI asosidagi tizimdir.  
Loyiha narx tarixini saqlaydi, jadval asosida (scheduler yordamida) avtomatik yangilab turadi va WebSocket orqali
real-time ma’lumotlarni ko‘rsatadi.

---

## ⚙️ Asosiy xususiyatlar

- 🧠 **Autentifikatsiya** — JWT token orqali foydalanuvchi autentifikatsiyasi
- 🕐 **APScheduler** — narxlarni avtomatik ravishda yangilab turadi
- 🔄 **WebSocket** — mahsulotlar va narx tarixini real vaqtda yangilab ko‘rsatadi
- 💾 **PostgreSQL** — asosiy ma’lumotlar bazasi
- 🧩 **SQLAlchemy ORM** — model va so‘rovlarni boshqarish
- 📡 **Fast API** — CRUD operatsiyalar uchun to‘liq endpointlar
- 🤝 **Scheduler + WebSocket integratsiyasi** — avtomatik narx yangilanishlarini jonli tarzda uzatish
- 🧰 **Modullar arxitekturasi** — har bir funksiya alohida modullarga ajratilgan

---


---

## 🧰 Texnologiyalar

| Texnologiya            | Tavsif                            |
|------------------------|-----------------------------------|
| **FastAPI**            | Asosiy backend framework          |
| **SQLAlchemy**         | ORM modeli                        |
| **PostgreSQL**         | Ma’lumotlar bazasi                |
| **APScheduler**        | Avtomatik ishlarni rejalashtirish |
| **WebSocket**          | Real-time data uzatish            |
| **Pydantic**           | Ma’lumotlarni validatsiya qilish  |
| **Uvicorn**            | ASGI server                       |
| **Docker (ixtiyoriy)** | Deploy uchun konteynerizatsiya    |

---

## 🛠️ O'rnatish va ishga tushirish

```bash
git clone https://github.com/XojaxonovPY/Fast-API-Game.git
cd ShopMonitor
```

2. Virtual muhit yaratish va kutubxonalarni o'rnatish

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

4. Ma'lumotlar bazasini migratsiya qilish

```bash
alembic upgrade head
```

5. Ilovani ishga tushirish

```bash
uvicorn main:app --reload
```

Ilova http://127.0.0.1:8000/docs/ manzilida ishga tushadi.

## 📄 Litsenziya

Loyiha MIT litsenziyasi asosida tarqatiladi.