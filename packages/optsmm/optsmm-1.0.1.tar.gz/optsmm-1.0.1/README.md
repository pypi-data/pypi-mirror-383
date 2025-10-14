
---

# OptSMM

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

Python-клиент для работы с SMM-сервисом [OptSMM](https://optsmm.ru). Позволяет получать баланс, создавать и управлять заказами, получать список услуг и искать сервисы по названию.

---

## Установка

```bash
pip install aiohttp
pip install optsmm
```

---

## Использование

```python
import asyncio
from optsmm import OptSMM

async def main():
    api_key = "ВАШ_API_KEY"
    client = OptSMM(api_key)

    balance, currency = await client.balance()
    print(f"Баланс: {balance} {currency}")

    services = await client.services()
    print("Доступные услуги:", services)

    order_id = await client.create_order(service=1, link="https://instagram.com/example", quantity=1000)
    print("Создан заказ:", order_id)

    status = await client.order_status(order_id)
    print("Статус заказа:", status)

    search_results = await client.search_services("Подписчики")
    print("Найденные сервисы:", search_results)

    cancelled = await client.order_cancel(order_id)
    print("Заказ отменен:", cancelled)

asyncio.run(main())
```

---

## Методы

* `balance()` – возвращает текущий баланс и валюту.
* `services()` – возвращает список всех доступных услуг.
* `search_services(query)` – поиск услуг по названию.
* `create_order(service, link, quantity, **kwargs)` – создание заказа.
* `order_status(order_id)` – получение статуса заказа.
* `order_cancel(order_id)` – отмена заказа.

---

## Примеры использования

### Получение баланса

```python
balance, currency = await client.balance()
print(f"Баланс: {balance} {currency}")
```

### Создание заказа

```python
order_id = await client.create_order(service=5, link="https://t.me/example", quantity=500)
```

### Проверка статуса заказа

```python
status = await client.order_status(order_id)
```

### Поиск сервиса

```python
results = await client.search_services("Лайки")
```

### Отмена заказа

```python
await client.order_cancel(order_id)
```

