

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
        labels={"app": "loguru"},
        batch_size=1000,
        proxy="http://127.0.0.1:8080",  # или None
        verify_ssl=True,
    )

    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # <- Добавили вывод в консоль
            logging.FileHandler('../content_generator.log', encoding='utf-8'),  # <- Добавили запись в файл
            loki_handler,  # <- Добавили отправку на сервер с Loki

        ]
    )

    logger = logging.getLogger(__name__)

    # Настройка для async_loki_handler
    logger.setLevel(logging.DEBUG)

    logger.debug("LokiHandler - logging")
    logger.info("Тестируем logging с библиотекой LokiHandler")
    logger.warning("Тестируем logging с библиотекой LokiHandler")
    logger.error("Тестируем logging с библиотекой LokiHandler")
    logger.critical("Тестируем logging с библиотекой LokiHandler")

    for i in range(1000):
        logger.info(f"Тестируем батчи logging с библиотекой LokiHandler #{i + 1}")

```


* _Пример использования c loguru:

```python
from loguru import logger

from src.async_loki_handler import LokiHandler

# Пример использования с loguru и async_loki_handler
if __name__ == "__main__":

    loki_handler = LokiHandler(
        url="http://127.0.0.1:3100/loki/api/v1/push",
        labels={"app": "logging"},
        batch_size=100,
        proxy="http://127.0.0.1:8080",  # или None
        verify_ssl=True,
    )

    logger.add(loki_handler, level="DEBUG")

    logger.info("hi")

    logger.debug("LokiHandler - loguru")
    logger.info("Тестируем loguru с библиотекой LokiHandler")
    logger.warning("Тестируем loguru с библиотекой LokiHandler")
    logger.error("Тестируем loguru с библиотекой LokiHandler")
    logger.critical("Тестируем loguru с библиотекой LokiHandler")

    for i in range(1000):
        logger.info(f"Тестируем батчи loguru с библиотекой LokiHandler #{i + 1}")

```

