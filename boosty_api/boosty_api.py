import aiohttp
import asyncio
import json
import time
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlencode

CLIENT_ID = ""
EXPIRE_THRESHOLD_MS = 6 * 60 * 60 * 1000    # 6 часов
TOKEN_LIFETIME_MS = 7 * 24 * 60 * 60 * 1000  # 7 дней
AUTH_FILE = "auth.json" 

class BoostyAPI:
    BASE_URL = "https://boosty.to"
    BASE_API_URL = "https://api.boosty.to"

    def __init__(self, session_cookie: str, bearer_token: str):
        self.auth_cookie = session_cookie
        self.bearer_token = bearer_token
        self.session: aiohttp.ClientSession | None = None
        self.blog_href: str | None = None
        self._token_task = None

    @staticmethod
    def load_auth(path = AUTH_FILE) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_auth(data: dict, path = AUTH_FILE):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    async def create(cls, path: str) -> "BoostyAPI":
        if not Path(path).exists():
            raise FileNotFoundError(f"Файл авторизации не найден: {path}")
        cls.AUTH_FILE = Path(path)
        data = cls.load_auth(path=path)
        cls.CLIENT_ID = data.get("_clientId", "")
        if not cls.CLIENT_ID:
            raise ValueError("Не указан CLIENT_ID в auth.json")
        obj = cls._from_data(data)
        await obj._start_token_loop()
        return obj

    @classmethod
    def _from_data(cls, data: dict) -> "BoostyAPI":
        encoded_cookie = urllib.parse.quote(json.dumps(data, separators=(",", ":")))
        return cls(encoded_cookie, data["accessToken"])

    async def _start_token_loop(self):
        async def loop():
            print("🔄 Запуск цикла обновления токена...(проверка валидности раз в час)")
            while True:
                await self._check_and_refresh_token()
                await asyncio.sleep(3600)  # Раз в час

        self._token_task = asyncio.create_task(loop())

    async def _check_and_refresh_token(self):
        auth_data = self.load_auth()
        now_ms = int(time.time() * 1000)
        expires_at_ms = int(auth_data.get("expiresAt", "0"))

        if expires_at_ms - now_ms > EXPIRE_THRESHOLD_MS:
            return  # ещё рано

        print("🔄 Обновление токена...")
        url = f"{self.BASE_API_URL}/oauth/token/"
        payload = {
            "device_id": CLIENT_ID,
            "device_os": "web",
            "grant_type": "refresh_token",
            "refresh_token": auth_data["refreshToken"]
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {auth_data['accessToken']}",
            "User-Agent": "Mozilla/5.0"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=headers) as resp:
                if resp.status != 200:
                    print("❌ Не удалось обновить токен:", resp.status)
                    return
                data = await resp.json()

        now = int(time.time() * 1000)
        new_data = {
            "accessToken": data["access_token"],
            "refreshToken": data["refresh_token"],
            "expiresAt": str(now + TOKEN_LIFETIME_MS),
            "isEmptyUser": "0",
            "redirectAppId": "web",
            "_clientId": CLIENT_ID
        }

        self.auth_cookie = urllib.parse.quote(json.dumps(new_data, separators=(",", ":")))
        self.bearer_token = new_data["accessToken"]
        self.save_auth(new_data)
        print("✅ Токен обновлён")

    async def init_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(
                cookies={"auth": self.auth_cookie},
                headers={
                    "Authorization": f"Bearer {self.bearer_token}",
                    "User-Agent": "Mozilla/5.0",
                }
            )

    async def close(self):
        if self._token_task:
            self._token_task.cancel()
        if self.session:
            await self.session.close()
            self.session = None

    async def get_blog_href(self) -> str:
        await self.init_session()
        async with self.session.get(self.BASE_URL) as resp:
            html = await resp.text()
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.find("a", {"data-test-id": "MAINFEED:ownBlogButton"})
        if not tag or not tag.has_attr("href"):
            raise RuntimeError("❌ Кнопка блога не найдена")
        self.blog_href = tag["href"]
        return self.blog_href

    def get_bearer(self) -> str:
        return self.bearer_token

    async def get_blog_stats(self) -> dict:
        if not self.blog_href:
            raise RuntimeError("⚠️ Сначала вызови get_blog_href()")
        url = f"{self.BASE_API_URL}/v1/blog/stat/{self.blog_href}/current"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "X-Currency": "RUB",
            "X-Locale": "ru_RU",
            "X-App": "web"
        }
        async with self.session.get(url, headers=headers) as resp:
            if resp.status != 200:
                raise RuntimeError(f"🚫 Ошибка: {resp.status}")
            return await resp.json()

    async def get_subscribers(self, limit=20, sort_by="on_time", order="gt") -> dict:
        if not self.blog_href:
            raise RuntimeError("⚠️ Сначала вызови get_blog_href()")
        url = (
            f"{self.BASE_API_URL}/v1/blog/{self.blog_href}/subscribers"
            f"?sort_by={sort_by}&limit={limit}&order={order}"
        )
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "X-Currency": "RUB",
            "X-Locale": "ru_RU",
            "X-App": "web"
        }
        async with self.session.get(url, headers=headers) as resp:
            if resp.status != 200:
                raise RuntimeError(f"🚫 Ошибка: {resp.status}")
            return await resp.json()

    async def get_contacts(self, limit: int = 100, sort_by: str = "name", sort_order: str = "asc") -> dict:
        """
        Получает список контактов (пользователей, с которыми есть переписка).
        """
        url = f"{self.BASE_API_URL}/v1/dialog/contacts"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "X-Currency": "RUB",
            "X-Locale": "ru_RU",
            "X-App": "web"
        }
        params = {
            "sort_by": sort_by,
            "sort_order": sort_order,
            "limit": limit
        }

        async with self.session.get(url, headers=headers, params=params) as resp:
            if resp.status != 200:
                raise RuntimeError(f"🚫 Ошибка при получении списка контактов: {resp.status}")
            return await resp.json()

    async def get_user_dialog(self, user_id: int) -> dict:
        """
        Получает чат с конкретным пользователем по ID.
        Если чата не было, он может быть создан автоматически.
        """
        url = f"{self.BASE_API_URL}/v1/dialog"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "X-Currency": "RUB",
            "X-Locale": "ru_RU",
            "X-App": "web"
        }
        params = {
            "user_id": str(user_id)
        }

        async with self.session.get(url, headers=headers, params=params) as resp:
            if resp.status not in (200, 201):
                raise RuntimeError(f"🚫 Ошибка при получении диалога с пользователем {user_id}: {resp.status}")
            
            try:
                return await resp.json()
            except aiohttp.ContentTypeError:
                return {"message": f"✅ Диалог с пользователем {user_id} был создан, но ответ не JSON"}

    async def get_subscription_levels(self, show_deleted: bool = True, show_free_level: bool = True) -> list[dict]:
        """
        Получает все уровни подписки блога.

        :param blog: Слаг блога (например, "makskraftteam")
        :param show_deleted: Включать ли удалённые уровни
        :param show_free_level: Включать ли бесплатный уровень
        :return: Список уровней подписки
        """
        url = f"{self.BASE_API_URL}/v1/blog/{self.blog_href}/subscription_level/"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "X-Currency": "RUB",
            "X-Locale": "ru_RU",
            "X-App": "web"
        }
        params = {
            "show_deleted": str(show_deleted).lower(),       # "true" / "false"
            "show_free_level": str(show_free_level).lower()  # "true" / "false"
        }

        async with self.session.get(url, headers=headers, params=params) as resp:
            if resp.status != 200:
                raise RuntimeError(f"🚫 Ошибка при получении уровней подписки: {resp.status}")
            return await resp.json()

    async def get_blog_metrics(self, time_from: int, time_to: int) -> dict:
        """
        Получает статистику блога за указанный временной период.

        :param blog: Слаг блога (например, "makskraftteam")
        :param time_from: Начало периода (UNIX timestamp)
        :param time_to: Конец периода (UNIX timestamp)
        :return: Статистика (dict)
        """
        url = f"{self.BASE_API_URL}/v1/blog/stat/{self.blog_href}/metrics"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "X-Currency": "RUB",
            "X-Locale": "ru_RU",
            "X-App": "web"
        }
        params = {
            "from": str(time_from),
            "to": str(time_to)
        }

        async with self.session.get(url, headers=headers, params=params) as resp:
            if resp.status != 200:
                raise RuntimeError(f"🚫 Ошибка при получении метрик блога: {resp.status}")
            return await resp.json()

    async def get_donations(self, limit: int = 10, offset: int = 0, sort_by: str = "time", order: str = "gt") -> dict:
        """
        Получает список донатов блога.

        :param limit: Количество записей (по умолчанию 10)
        :param offset: Смещение (для пагинации)
        :param sort_by: Поле сортировки (обычно "time")
        :param order: Направление сортировки ("gt" - по убыванию, "lt" - по возрастанию)
        :return: Словарь с данными по донатам
        """
        if not self.blog_href:
            self.blog_href = await self.get_blog_href()

        url = f"{self.BASE_API_URL}/v1/blog/{self.blog_href}/sales/donation/"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "X-Currency": "RUB",
            "X-Locale": "ru_RU",
            "X-App": "web"
        }
        params = {
            "limit": str(limit),
            "offset": str(offset),
            "sort_by": sort_by,
            "order": order
        }

        async with self.session.get(url, headers=headers, params=params) as resp:
            if resp.status != 200:
                raise RuntimeError(f"🚫 Ошибка при получении донатов: {resp.status}")
            return await resp.json()

    async def get_post_sales(self, limit: int = 10, offset: int = 0, sort_by: str = "time", order: str = "gt") -> dict:
        """
        Получает список продаж постов блога.

        :param limit: Количество записей (по умолчанию 10)
        :param offset: Смещение (для пагинации)
        :param sort_by: Поле сортировки (обычно "time")
        :param order: Направление сортировки ("gt" - новые сверху, "lt" - старые сверху)
        :return: Словарь с данными по продажам постов
        """
        if not self.blog_href:
            self.blog_href = await self.get_blog_href()

        url = f"{self.BASE_API_URL}/v1/blog/{self.blog_href}/sales/post/"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "X-Currency": "RUB",
            "X-Locale": "ru_RU",
            "X-App": "web"
        }
        params = {
            "limit": str(limit),
            "offset": str(offset),
            "sort_by": sort_by,
            "order": order
        }

        async with self.session.get(url, headers=headers, params=params) as resp:
            if resp.status != 200:
                raise RuntimeError(f"🚫 Ошибка при получении продаж постов: {resp.status}")
            return await resp.json()

    async def get_posts(self, blog_name: str = None) -> dict:
        """
        Получает список постов блога.

        :param limit: Количество постов (по умолчанию 10)
        :param offset: Смещение для пагинации
        :return: Словарь с постами
        """
        if not self.blog_href:
            self.blog_href = await self.get_blog_href()
            
        if blog_name is None:
            blog_name = self.blog_href

        url = f"{self.BASE_API_URL}/v1/blog/{blog_name}/post/"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "X-Currency": "RUB",
            "X-Locale": "ru_RU",
            "X-App": "web"
        }

        async with self.session.get(url, headers=headers) as resp:
            if resp.status != 200:
                raise RuntimeError(f"🚫 Ошибка при получении списка постов: {resp.status}")
            return await resp.json()

    async def get_blog_info(self, blog_name: str = None) -> dict:
        """
        Получает информацию о блоге по его имени.
        """

        if not self.blog_href:
            self.blog_href = await self.get_blog_href()
        if blog_name is None:
            blog_name = self.blog_href

        url = f"{self.BASE_API_URL}/v1/blog/{blog_name}"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "X-Currency": "RUB",
            "X-Locale": "ru_RU",
            "X-App": "web"
        }

        async with self.session.get(url, headers=headers) as resp:
            if resp.status != 200:
                raise RuntimeError(f"🚫 Ошибка при получении информации о блоге: {resp.status}")
            return await resp.json()

    async def create_post(
        self,
        title: str,
        content: str,
        subscription_level_id: int,
        price: int = 0,
        tags: str = "",
        deny_comments: bool = False,
        wait_video: bool = False,
        has_chat: bool = False
    ) -> dict:
        url = f"{self.BASE_API_URL}/v1/blog/{self.blog_href}/post/"
        
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "X-Currency": "RUB",
            "X-Locale": "ru_RU",
            "X-App": "web",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": f"https://boosty.to/{self.blog_href}/new-post"
        }

        # Вложенное сериализованное content-поле
        data_field = json.dumps([
            {
                "type": "text",
                "content": json.dumps([content, "unstyled", []], ensure_ascii=False),
                "modificator": ""
            },
            {
                "type": "text",
                "content": "",
                "modificator": "BLOCK_END"
            }
        ], ensure_ascii=False)

        payload = {
            "title": title,
            "data": data_field,
            "subscription_level_id": str(subscription_level_id),
            "price": str(price),
            "teaser_data": "[]",
            "tags": tags,
            "deny_comments": str(deny_comments).lower(),
            "wait_video": str(wait_video).lower(),
            "has_chat": str(has_chat).lower(),
            "advertiser_info": ""
        }

        print("🔄 Создание поста с данными:", payload)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=urlencode(payload, encoding='utf-8')) as response:
                if response.status == 200:
                    return await response.json()
                text = await response.text()
                raise RuntimeError(f"🚫 Ошибка при создании поста: {response.status}, {text}")
            
    async def get_media_posts(
        self,
        blog_name: str = None,
        media_type: str = "all",
        limit: int = 15,
        limit_by: str = "media"
    ) -> dict:
        """
        Получение медиа-постов из альбома блога Boosty.

        :param media_type: Тип медиа ("all", "image", "video", "audio")
        :param limit: Кол-во возвращаемых элементов
        :param limit_by: Критерий ограничения ("media" или "album")
        :return: JSON с медиа-постами
        """
        if not self.blog_href:
            self.blog_href = await self.get_blog_href()
            
        if blog_name is None:
            blog_name = self.blog_href
        
        if media_type not in ["all", "image", "video", "audio"]:
            raise ValueError("❌ Неверный тип медиа. Допустимые значения: 'all', 'image', 'video', 'audio'")

        url = f"https://api.boosty.to/v1/blog/{blog_name}/media_album/"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "X-Currency": "RUB",
            "X-Locale": "ru_RU",
            "X-App": "web",
        }
        params = {
            "type": media_type,
            "limit": str(limit),
            "limit_by": limit_by
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                text = await response.text()
                raise RuntimeError(f"🚫 Ошибка при получении медиа: {response.status}, {text}")
