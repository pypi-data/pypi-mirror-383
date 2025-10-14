import aiohttp, asyncio
class OptSMM:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://optsmm.ru/api/v2"
    async def balance(self) -> float:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}?action=balance&key={self.api_key}") as response:
                data = await response.json()
                if data.get("balance", "None") != "None":
                    return float(data["balance"]), data.get("currency", "None")
                else:
                    raise Exception(f"Не получилось получить баланс: {data['error']}")
    async def create_order(self, service: int, link: str, quantity: int, **kwargs) -> int:
        services = await self.services()
        target = next((s for s in services if s["service"] == service), None)
        if not target:
            raise Exception("Сервис не найден")
        rate = float(target["rate"])
        cost = rate * quantity / 1000
        balance, _ = await self.balance()
        if balance < cost:
            return {"error": f"Недостаточно средств. Нужно {cost}, на балансе {balance}"}
        if quantity < int(target["min"]):
            raise Exception(f"Минимальное количество для этого сервиса: {target['min']}")
        params = {"action": "add", "key": self.api_key, "service": service, "link": link, "quantity": quantity}
        params.update(kwargs)
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                data = await response.json()
                if data.get("order", "None") != "None":
                    return int(data["order"])
                else:
                    raise Exception(f"Не получилось создать заказ: {data['error']}")
    async def order_status(self, order_id: int) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}?action=status&order={order_id}&key={self.api_key}") as response:
                data = await response.json()
                if data.get("status", "None") != "None":
                    return data
                else:
                    raise Exception(f"Не получилось получить статус заказа: {data['error']}")
    async def services(self) -> list:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}?action=services&key={self.api_key}") as response:
                data = await response.json()
                if isinstance(data, list):
                    return data
                else:
                    raise Exception(f"Не получилось получить список услуг: {data['error']}")
    async def search_services(self, query: str) -> list:
        services = await self.services()
        return [s for s in services if query.lower() in s["name"].lower()]
    async def order_cancel(self, order_id: int) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}?action=cancel&order={order_id}&key={self.api_key}") as response:
                data = await response.json()
                if data.get("status", "None") == "success":
                    return True
                else:
                    raise Exception(f"Не получилось отменить заказ: {data['error']}")