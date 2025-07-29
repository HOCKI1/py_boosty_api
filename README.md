
# 🚀 PyBoostyAPI

**PyBoostyAPI** is a powerful asynchronous Python library for seamless interaction with [Boosty.to](https://boosty.to) through its internal API. It supports posts, subscribers, dialogs, sales, donations, and detailed statistics.

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py_boosty_api)
![PyPI - License](https://img.shields.io/pypi/l/PyBoostyApi)
![GitHub stars](https://img.shields.io/github/stars/HOCKI1/py_boosty_api?style=social)

---

## ✨ Features

- 🔐 Authentication with token auto-refresh
- 📬 User dialog handling
- 📊 Fetching statistics and sales data
- 💬 Get free and paid subscribers
- 📝 Create and delete posts
- 💰 Get donation and subscription tier info

---

## ⚙️ Installation

```bash
pip install PyBoostyApi
````

Or manually:

```bash
git clone https://github.com/HOCKI1/py_boosty_api.git
cd py_boosty_api
pip install .
```

---

## 🔧 Basic Usage Example

```python
import asyncio
from boosty_api import BoostyAPI

async def main():
    api = await BoostyAPI.create("auth.json")
    try:
        href = await api.get_blog_href()
        print("🔗 Blog href:", href)

        stats = await api.get_blog_stats() # Get stats of your Blog
        print("📊 Stats:", stats)

    finally:
        await api.close()

if __name__ == "__main__":
    asyncio.run(main())

```

---

## 🗂 `auth.json` Structure

```json
{
  "access_token": "your_token",
  "refresh_token": "your_refresh_token",
  "expiresAt": 1722193100,
  "_clientId": "your_uuid"
}
```

---

## 📌 TODO

* [x] Posts
* [x] Subscribers
* [ ] Dialogs
* [x] Donations
* [x] Sales
* [x] Auto token refresh
* [x] Media content (albums, images)
* [ ] More common usable functions

---

## 📄 License

This project is licensed under the **MIT License**. See `LICENSE` for details.

---

## 🤝 Contact

Author: [HOCKI1](https://github.com/HOCKI1)
Email: [hocki1.official@yandex.ru](mailto:hocki1.official@yandex.ru)
Made with ❤️ for the Boosty creator community.

