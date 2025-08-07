
# 🚀 PyBoostyAPI

**PyBoostyAPI** is a powerful asynchronous Python library for seamless interaction with [Boosty.to](https://boosty.to) through its internal API. It supports posts, subscribers, dialogs, sales, donations, and detailed statistics.

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py_boosty_api)
![PyPI - License](https://img.shields.io/pypi/l/PyBoostyApi)
![GitHub stars](https://img.shields.io/github/stars/HOCKI1/py_boosty_api?style=social)

PyPi page
https://pypi.org/project/PyBoostyApi/

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
  "isEmptyUser": "0",
  "redirectAppId": "web",
  "_clientId": "your_uuid"
}
```
To get this data:
- Copy script below to Tampermonkey

```
// ==UserScript==
// @name         Boosty Auth Extractor
// @namespace    https://boosty.to/
// @version      2.1
// @description  Экспорт полного auth.json
// @author       HOCKI1
// @match        https://boosty.to/*
// @grant        none
// ==/UserScript==

(function () {
    'use strict';

    function createExportButton() {
        if (document.getElementById("export-auth-btn")) return;

        const btn = document.createElement("button");
        btn.id = "export-auth-btn";
        btn.textContent = "📦 Сохранить auth.json";
        btn.style.position = "fixed";
        btn.style.bottom = "20px";
        btn.style.right = "20px";
        btn.style.zIndex = "9999";
        btn.style.padding = "10px 14px";
        btn.style.backgroundColor = "#ff7f00";
        btn.style.color = "#fff";
        btn.style.border = "none";
        btn.style.borderRadius = "8px";
        btn.style.cursor = "pointer";
        btn.style.fontSize = "14px";
        btn.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";

        btn.onclick = () => {
            try {
                const authRaw = localStorage.getItem("auth");
                const clientId = localStorage.getItem("_clientId");

                if (!authRaw) {
                    alert("❌ Не найден ключ 'auth' в localStorage");
                    return;
                }
                if (!clientId) {
                    alert("❌ Не найден ключ '_clientId' в localStorage");
                    return;
                }

                const auth = JSON.parse(authRaw);

                // Гарантируем наличие нужных полей
                auth["_clientId"] = clientId;
                if (!auth.hasOwnProperty("isEmptyUser")) {
                    auth["isEmptyUser"] = "0";
                }
                if (!auth.hasOwnProperty("redirectAppId")) {
                    auth["redirectAppId"] = "web";
                }

                const blob = new Blob([JSON.stringify(auth, null, 2)], { type: "application/json" });
                const link = document.createElement("a");
                link.href = URL.createObjectURL(blob);
                link.download = "auth.json";
                link.click();
            } catch (e) {
                alert("❌ Ошибка при экспорте auth.json: " + e.message);
                console.error(e);
            }
        };

        document.body.appendChild(btn);
    }

    const interval = setInterval(() => {
        if (document.body) {
            clearInterval(interval);
            createExportButton();
        }
    }, 500);
})();
```
- Login to Boosty
- Press button "Сохранить auth.json" in bottom right corner
- Profit!

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

