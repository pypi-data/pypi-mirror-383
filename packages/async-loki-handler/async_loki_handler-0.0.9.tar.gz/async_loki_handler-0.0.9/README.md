

Импорт
```
from async_loki_handler import LokiHandler
```

* _Пример использования c logging:

```python
import logging
from src.async_loki_handler import LokiHandler


if __name__ == "__main__":

    loki_handler = LokiHandler(
        url="http://127.0.0.1:3100/loki/api/v1/push",
        labels={"app": "logging"},
        batch_size=1000,
        extra_label_keys=["action", "endpoint", "status_code"],
    )

    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(), # <- Добавили вывод в консоль
            logging.FileHandler('../content_generator.log', encoding='utf-8'), # <- Добавили запись в файл
            loki_handler,  # <- Добавили отправку на сервер с Loki

        ]
    )

    logger = logging.getLogger(__name__)

    # Настройка для async_loki_handler
    logger.setLevel(logging.DEBUG)

    logger.info(
        "API request completed",
        extra={"data": {
            "action": "api_call",  # → label
            "endpoint": "/users/create",  # → label
            "status_code": "200",  # → label
            "response_time": 0.45,  # → extra в JSON
            "user_name": "yehor",  # → extra в JSON
            "custom_field": "value"  # → extra в JSON
        }}
    )
    logger.info(
        "Some event",
        extra={
            "user_id": "12345",  # попадёт (стандартное поле)
            "custom_field": "value"  # НЕ попадёт (не в extra_label_keys)
        }
    )
    logger.debug("LokiHandler - logging", )
    logger.info("Тестируем logging с библиотекой LokiHandler", )

```


* _Пример использования c loguru:

```python
import sys
from loguru import logger
from async_loki_handler import LokiHandler

if __name__ == "__main__":
    logger.remove()

    loki_handler = LokiHandler(
        url="http://127.0.0.1:3100/loki/api/v1/push",
        labels={"app": "loguru"},
        extra_label_keys=["action"],
    )

    # Простой строковый формат (без функции)
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level:<8}</level> | "
        "<cyan>{name}:{function}:{line}</cyan> - "
        "<level>{message:<30}</level>"
        " | <cyan>{extra}</cyan>"  # ← с разделителем и цветом
    )

    logger.add(sys.stderr, format=console_format, colorize=True)
    logger.add(loki_handler, format="{message}")

    # Тесты
    logger.info("Simple message")
    logger = logger.bind(extra={"action": "test", "account": "user"})
    logger.info("Login success")
    logger.warning("Warning message")
    logger.bind(user_id="999").error("Error occurred")

```

