import ast
import asyncio
import json
import platform
import sys
import time
import threading
from queue import Queue, Empty, Full
from dataclasses import dataclass, asdict
from typing import Optional, Dict

import logging


import aiohttp
import os

# Списки фреймворков для автоматического определения
API_FRAMEWORKS = {
    "django", "fastapi", "uvicorn", "flask",
    "sanic", "tornado", "bottle", "quart"
}

BOT_FRAMEWORKS = {
    "aiogram", "telebot", "python-telegram-bot",
    "discord", "discord.py", "pyrogram", "telethon"
}


def analyze_imports_for_frameworks(file_path: Optional[str] = None) -> Dict[str, str]:
    """
    Анализирует импорты в файле и определяет используемые фреймворки.

    Args:
        file_path: Путь к файлу для анализа. Если None, анализирует текущий исполняемый файл.

    Returns:
        Dict с лейблами: {"api": "django", "bot": "aiogram"} или пустой dict
    """
    if file_path is None:
        # Определяем текущий исполняемый файл
        file_path = os.path.abspath(sys.argv[0]) if sys.argv[0] else None

    if not file_path or not os.path.exists(file_path):
        return {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Парсим AST (Abstract Syntax Tree)
        tree = ast.parse(source)

        api_detected = set()
        bot_detected = set()

        # Ищем все импорты
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Обрабатываем простые импорты (import module)
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split('.')[0].lower()
                        if module_name in API_FRAMEWORKS:
                            api_detected.add(module_name)
                        elif module_name in BOT_FRAMEWORKS:
                            bot_detected.add(module_name)

                # Обрабатываем импорты из модуля (from module import ...)
                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module.lower() if node.module else ""
                    # Проверяем корневой модуль
                    root_module = module_name.split('.')[0]
                    if root_module in API_FRAMEWORKS:
                        api_detected.add(root_module)
                    elif root_module in BOT_FRAMEWORKS:
                        bot_detected.add(root_module)

                    # Проверяем импортируемые имена
                    for alias in node.names:
                        import_name = alias.name.lower()
                        # Специальные случаи для подмодулей
                        if import_name in {"app", "asgi", "wsgi"} and root_module in API_FRAMEWORKS:
                            api_detected.add(root_module)

        # Формируем лейблы
        labels = {}
        if api_detected:
            # Берем первый найденный API фреймворк или самый популярный
            primary_api = max(api_detected, key=lambda x: len(x))  # или можно задать приоритет
            labels["api"] = primary_api
        if bot_detected:
            primary_bot = max(bot_detected, key=lambda x: len(x))
            labels["bot"] = primary_bot

        return labels

    except Exception as e:
        print(f"[FrameworkDetector] Error analyzing imports: {e}", file=sys.stderr)
        return {}


def get_framework_labels(file_path: Optional[str] = None) -> Dict[str, str]:
    """
    Возвращает лейблы для Loki на основе анализа фреймворков.

    Args:
        file_path: Путь к файлу для анализа.

    Returns:
        Лейблы: {"api": "django"} или {"bot": "aiogram"} или пустой dict
    """
    framework_info = analyze_imports_for_frameworks(file_path)
    return framework_info


def find_project_root():
    """Находит корневую директорию проекта по характерным файлам"""
    # Маркеры корня проекта (в порядке приоритета)
    markers = [
        'pyproject.toml',
        'setup.py',
        '.env',
        '.venv',
        'setup.cfg',
        '.git',
        'requirements.txt',
        'Pipfile',
        'poetry.lock',
        'pyproject.toml'
        'uv.lock'
    ]

    # Начинаем с директории главного исполняемого файла
    if hasattr(sys.modules.get('__main__'), '__file__'):
        current = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
    else:
        current = os.getcwd()

    # Поднимаемся вверх по дереву директорий
    original = current
    while True:
        # Проверяем наличие хотя бы одного маркера
        for marker in markers:
            if os.path.exists(os.path.join(current, marker)):
                return current

        parent = os.path.dirname(current)

        # Достигли корня файловой системы - возвращаем начальную директорию
        if parent == current:
            return original

        current = parent


class _AsyncBatchSender:
    """
    Живёт в отдельном потоке.
    Поднимает свой asyncio loop + aiohttp.ClientSession и отправляет батчи параллельно с ограничением по семафору.
    """

    def __init__(
        self,
        url: str,
        *,
        max_parallel_batches: int = 4,
        request_timeout: float = 5.0,
        proxy: str | None = None,
        verify_ssl: bool = True,
        headers: dict | None = None,
    ):
        self.url = url
        self.max_parallel_batches = max_parallel_batches
        self.request_timeout = request_timeout
        self.proxy = proxy
        self.verify_ssl = verify_ssl
        self.headers = headers or {"Content-Type": "application/json"}

        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._session: aiohttp.ClientSession | None = None
        self._sem: asyncio.Semaphore | None = None
        self._stop_event = threading.Event()
        self._inflight = set()  # набор Future (threadsafe) для батчей

    # ====== Публичные методы (вызываются из основного потока) ======

    def start(self):
        self._thread = threading.Thread(target=self._run_loop, name="loki-aio-loop", daemon=True)
        self._thread.start()

    def submit(self, payload: dict):
        """
        Отправка батча: прокидываем coroutine в loop через run_coroutine_threadsafe.
        Возвращаем concurrent.futures.Future (можно использовать для ожидания/ошибок).
        """
        if not self._loop:
            raise RuntimeError("Async loop is not started")

        fut = asyncio.run_coroutine_threadsafe(self._send_with_sem(payload), self._loop)
        self._inflight.add(fut)

        # когда future завершится — убрать из набора
        def _done(_):
            self._inflight.discard(fut)
        fut.add_done_callback(_done)

        return fut

    def stop(self, timeout: float = 10.0):
        """
        Корректное завершение: ждём in-flight задачи, закрываем сессию, останавливаем луп и поток.
        """
        self._stop_event.set()
        # Дождаться завершения in-flight (не вечно)
        end = time.time() + timeout
        for fut in list(self._inflight):
            remaining = end - time.time()
            if remaining <= 0:
                break
            try:
                fut.result(timeout=remaining)
            except Exception:
                # ошибки уже будут залогированы ниже в корутине
                pass

        if self._loop:
            # Закрыть session и остановить loop
            asyncio.run_coroutine_threadsafe(self._graceful_close(), self._loop).result(timeout=timeout)
            self._loop.call_soon_threadsafe(self._loop.stop)

        if self._thread:
            self._thread.join(timeout=timeout)

    # ====== Внутренности event-loop-потока ======

    def _run_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loop = loop
        loop.run_until_complete(self._init_runtime())
        try:
            loop.run_forever()
        finally:
            loop.run_until_complete(self._finalize_runtime())
            loop.close()

    async def _init_runtime(self):
        timeout = aiohttp.ClientTimeout(total=self.request_timeout)
        connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
        self._session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        self._sem = asyncio.Semaphore(self.max_parallel_batches)

    async def _finalize_runtime(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _graceful_close(self):
        # просто враппер, чтобы звать из stop() threadsafe
        if self._session and not self._session.closed:
            await self._session.close()

    async def _send_with_sem(self, payload: dict, *, max_retries: int = 3, base_delay: float = 0.5):
        """
        Отправка 1 батча в Loki с ограничением по семафору и ретраями.
        """
        assert self._session is not None
        assert self._sem is not None

        async with self._sem:
            attempt = 0
            last_exc: Exception | None = None
            while attempt <= max_retries:
                try:
                    async with self._session.post(
                        self.url,
                        json=payload,
                        headers=self.headers,
                        proxy=self.proxy,
                    ) as resp:
                        # Loki успешный код = 204
                        if resp.status == 204:
                            return
                        text = await resp.text()
                        raise RuntimeError(f"Loki HTTP {resp.status}: {text[:300]}")
                except Exception as e:
                    last_exc = e
                    if attempt == max_retries:
                        # Логируем в stderr — чтобы не замусоривать основной логгер
                        print(f"❌ AIO Loki send failed after retries: {e}", file=sys.stderr)
                        return
                    await asyncio.sleep(base_delay * (2 ** attempt))
                    attempt += 1


class LokiHandler(logging.Handler):
    """
    Кастомный handler для отправки логов в Loki:
    - собирает логи в буфер из очереди
    - формирует батчи и отправляет ИХ ПАРАЛЛЕЛЬНО через aiohttp в отдельном потоке
    - гарантирует отправку по нескольким условиям + экстренный флаш для ERROR/CRITICAL
    """

    def __init__(
            self,
            url: str,
            labels: dict,
            *,
            analyze_frameworks: bool = True,
            framework_file: Optional[str] = None,
            batch_size: int = 500,
            flush_interval: float = 5.0,
            max_parallel_batches: int = 10,
            request_timeout: float = 5.0,
            proxy: str | None = None,
            verify_ssl: bool = True,

            # новые «гарантии»
            max_bytes: int | None = 256 * 1024,
            max_record_age: float = 2.0,
            queue_maxsize: int = 10_000,
            queue_overflow: str = "drop_oldest",  # "block" | "drop_oldest" | "drop_new"
            flush_on_levels: tuple[str, ...] = (),

            # Новый параметр для дополнительных label-полей из extra
            extra_label_keys: tuple[str, ...] | list[str] = (),
    ):
        super().__init__()

        self.url = url
        self.static_labels = labels.copy()
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        self.max_bytes = max_bytes
        self.max_record_age = max_record_age
        self.flush_on_levels = set(flush_on_levels)

        # Сохраняем список дополнительных ключей для labels
        self.extra_label_keys = set(extra_label_keys) if extra_label_keys else set()

        self.queue_overflow = queue_overflow
        self.queue = Queue(maxsize=queue_maxsize)

        self.buffer: list[dict] = []
        self.buffer_bytes: int = 0
        self._running = True
        self._stopped = False
        self.sent_count = 0

        self.sender = _AsyncBatchSender(
            url,
            max_parallel_batches=max_parallel_batches,
            request_timeout=request_timeout,
            proxy=proxy,
            verify_ssl=verify_ssl,
        )
        self.sender.start()

        self.thread = threading.Thread(target=self._worker, name="loki-dispatcher", daemon=True)
        self.thread.start()

        project_root = find_project_root()
        project_name = os.path.basename(project_root)

        print(f"Project root: {project_root}")
        print(f"Project name: {project_name}")

        self.static_labels["project"] = project_name
        self.static_labels["environment"] = self._determine_environment()

        if analyze_frameworks:
            framework_labels = get_framework_labels(framework_file)
            self.static_labels.update(framework_labels)
            if framework_labels:
                print(f"[LokiHandler] Detected frameworks: {framework_labels}")

        # IP один раз
        self.static_labels.setdefault("ip", "127.0.0.1")
        if self.static_labels["environment"] == "production":
            try:
                import asyncio, aiohttp
                async def get_external_ip():
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5.0)) as session:
                        async with session.get("https://api.ipify.org") as response:
                            if response.status == 200:
                                self.static_labels["ip"] = await response.text()

                loop = asyncio.new_event_loop()
                loop.run_until_complete(get_external_ip())
                loop.close()
            except Exception as e:
                print(f"[LokiHandler] Error getting external IP: {e}", file=sys.stderr)

    def _determine_environment(self) -> str:
        env_override = os.environ.get("ENVIRONMENT", "").lower()
        if env_override in ("dev", "development"): return "dev"
        if env_override in ("prod", "production"): return "production"
        system = platform.system().lower()
        if system == "windows":
            rel = platform.release().lower()
            ver = platform.version().lower()
            return "production" if ("server" in rel or "server" in ver or "200" in rel or "201" in rel) else "dev"
        if system == "darwin": return "dev"
        if system == "linux":
            return "dev" if (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")) else "production"
        return "dev"

    # --- loguru sink ---
    # def __call__(self, message):
    #     record = message.record
    #     labels = self.static_labels.copy()
    #     labels["level"] = record["level"].name
    #     labels["logger"] = record["name"]
    #
    #     # Получаем ТОЛЬКО пользовательские extra (через bind())
    #     # Игнорируем служебные поля loguru
    #
    #     print(f"[DEBUG] raw extra: {record['extra']}")
    #     print(f"[DEBUG] extra keys: {list(record['extra'].keys())}")
    #
    #     extra = {}
    #     for k, v in record["extra"].items():
    #         print(f"  {k}: {v} (type: {type(v)}, len: {len(v) if isinstance(v, dict) else 'N/A'})")
    #
    #         # Пропускаем служебные поля loguru (они часто пустые словари)
    #         if k not in ('extra',) and v is not None:
    #             # Дополнительная проверка на пустые словари
    #             if isinstance(v, dict):
    #                 if len(v) > 0:
    #                     extra[k] = v
    #             else:
    #                 extra[k] = v
    #
    #     always_label_fields = {"service", "component", "environment", "user_id"}
    #     label_fields = always_label_fields | self.extra_label_keys
    #
    #     extra_for_labels = {}
    #     extra_for_json = {}
    #
    #     for k, v in extra.items():
    #         if k in label_fields:
    #             extra_for_labels[k] = str(v)
    #         else:
    #             extra_for_json[k] = v
    #
    #     labels.update(extra_for_labels)
    #
    #     ts = str(int(record["time"].timestamp() * 1_000_000_000))
    #     line = record["message"]
    #
    #     msg_dict = {"message": line}
    #
    #     # Добавляем extra_json только если есть данные
    #     if extra_for_json:
    #         msg_dict["extra_json"] = json.dumps(extra_for_json, ensure_ascii=False)
    #
    #     line = json.dumps(msg_dict, ensure_ascii=False)
    #     self._enqueue(labels, ts, line, level=labels["level"])

    def emit(self, record):
        try:
            labels = self.static_labels.copy()
            labels["level"] = logging.getLevelName(record.levelno)
            labels["logger"] = record.name

            standard_attrs = {
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'pathname', 'process', 'processName', 'relativeCreated',
                'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
                'getMessage', 'message', 'taskName', 'asctime'
            }

            extra_raw = {k: v for k, v in record.__dict__.items() if k not in standard_attrs}

            # Обрабатываем вложенность от loguru
            extra = {}
            for k, v in extra_raw.items():
                if k == "extra" and isinstance(v, dict):
                    # Проверяем двойную вложенность от loguru: {'extra': {'extra': {...}}}
                    if 'extra' in v and isinstance(v['extra'], dict):
                        # Двойная вложенность - берём самый вложенный словарь
                        extra.update(v['extra'])
                    else:
                        # Одинарная вложенность - просто распаковываем
                        extra.update(v)
                else:
                    extra[k] = v

            always_label_fields = {"service", "component", "environment", "user_id"}
            label_fields = always_label_fields | self.extra_label_keys

            extra_for_labels = {}
            extra_for_json = {}

            for k, v in extra.items():
                if k in label_fields:
                    extra_for_labels[k] = str(v)
                else:
                    # Пропускаем пустые словари
                    if not (isinstance(v, dict) and len(v) == 0):
                        extra_for_json[k] = v

            labels.update(extra_for_labels)

            base_msg = self.format(record) if self.formatter else str(record.msg)

            msg_dict = {"message": base_msg}

            if extra_for_json:
                msg_dict["extra_json"] = json.dumps(extra_for_json, ensure_ascii=False)

            msg = json.dumps(msg_dict, ensure_ascii=False)

            ts = str(int(record.created * 1_000_000_000))
            self._enqueue(labels, ts, msg, level=labels["level"])
        except Exception:
            self.handleError(record)

    def _enqueue(self, labels: dict, ts: str, line: str, *, level: str, structured_metadata: dict = None):
        item = {
            "labels": labels,
            "timestamp": ts,
            "line": line,
            "enq_ts": time.monotonic(),
            "structured_metadata": structured_metadata or {},  # ← новое поле
        }
        item["approx_bytes"] = len(line.encode("utf-8")) + len(
            json.dumps(labels, ensure_ascii=False).encode("utf-8")) + 64

        if structured_metadata:
            item["approx_bytes"] += len(json.dumps(structured_metadata, ensure_ascii=False).encode("utf-8"))

        # Экстренная доставка
        if level in self.flush_on_levels:
            payload = self._make_payload([item])
            try:
                self.sender.submit(payload)
                self.sent_count += 1
            except Exception as e:
                print(f"❌ Loki emergency submit failed: {e}", file=sys.stderr)
            return

        # Обычная очередь
        try:
            self.queue.put_nowait(item)
        except Full:
            policy = self.queue_overflow
            if policy == "block":
                self.queue.put(item)
            elif policy == "drop_oldest":
                try:
                    _ = self.queue.get_nowait()
                except Empty:
                    pass
                try:
                    self.queue.put_nowait(item)
                except Full:
                    pass
            elif policy == "drop_new":
                pass

    def _make_payload(self, items: list[dict]) -> dict:
        streams: dict[str, dict] = {}
        for log in items:
            key = json.dumps(log["labels"], sort_keys=True, ensure_ascii=False)
            if key not in streams:
                streams[key] = {"stream": log["labels"], "values": []}

            # Формируем value с structured metadata (если есть)
            value = [log["timestamp"], log["line"]]

            if log.get("structured_metadata"):
                value.append(log["structured_metadata"])

            streams[key]["values"].append(value)

        lines = sum(len(s["values"]) for s in streams.values())
        self.sent_count += lines
        return {"streams": list(streams.values())}
    # --- dispatcher thread ---
    def _worker(self):
        last_flush = time.time()
        while self._running:
            try:
                # забираем порциями
                while not self.queue.empty() and len(self.buffer) < (self.batch_size * 8):
                    it = self.queue.get_nowait()
                    self.buffer.append(it)
                    self.buffer_bytes += it["approx_bytes"]

                now = time.time()
                should = False
                if len(self.buffer) >= self.batch_size:
                    should = True
                if not should and self.buffer and (now - last_flush) >= self.flush_interval:
                    should = True
                if not should and self.max_bytes is not None and self.buffer_bytes >= self.max_bytes:
                    should = True
                if not should and self.buffer:
                    oldest = min(x["enq_ts"] for x in self.buffer)
                    if (time.monotonic() - oldest) >= self.max_record_age:
                        should = True

                if should and self.buffer:
                    chunks = [self.buffer[i:i + self.batch_size] for i in range(0, len(self.buffer), self.batch_size)]
                    self.buffer = []
                    self.buffer_bytes = 0
                    last_flush = now
                    for ch in chunks:
                        payload = self._make_payload(ch)
                        try:
                            self.sender.submit(payload)
                        except Exception as e:
                            # не рушим поток, просто напишем в stderr
                            print(f"❌ submit failed: {e}", file=sys.stderr)

                time.sleep(0.02)
            except Exception as e:
                print(f"Error in Loki dispatcher: {e}", file=sys.stderr)
                time.sleep(0.1)

        # drain при остановке
        try:
            while not self.queue.empty():
                it = self.queue.get_nowait()
                self.buffer.append(it)
                self.buffer_bytes += it["approx_bytes"]
        except Empty:
            pass

        if self.buffer:
            chunks = [self.buffer[i:i + self.batch_size] for i in range(0, len(self.buffer), self.batch_size)]
            self.buffer = []
            self.buffer_bytes = 0
            for ch in chunks:
                payload = self._make_payload(ch)
                try:
                    self.sender.submit(payload)
                except Exception as e:
                    print(f"❌ submit during drain failed: {e}", file=sys.stderr)

    def _make_payload(self, items: list[dict]) -> dict:
        streams: dict[str, dict] = {}
        for log in items:
            key = json.dumps(log["labels"], sort_keys=True, ensure_ascii=False)
            if key not in streams:
                streams[key] = {"stream": log["labels"], "values": []}
            streams[key]["values"].append([log["timestamp"], log["line"]])
        lines = sum(len(s["values"]) for s in streams.values())
        self.sent_count += lines
        return {"streams": list(streams.values())}

    # --- API ---
    def flush(self):
        # форс собрать всё и отправить
        try:
            while not self.queue.empty():
                it = self.queue.get_nowait()
                self.buffer.append(it)
                self.buffer_bytes += it["approx_bytes"]
        except Empty:
            pass

        if self.buffer:
            chunks = [self.buffer[i:i + self.batch_size] for i in range(0, len(self.buffer), self.batch_size)]
            self.buffer = []
            self.buffer_bytes = 0
            for ch in chunks:
                payload = self._make_payload(ch)
                try:
                    self.sender.submit(payload)
                except Exception as e:
                    print(f"❌ submit in flush failed: {e}", file=sys.stderr)

    def stop(self):
        if self._stopped:
            return
        self._running = False
        # дождёмся рабочего потока
        try:
            if self.thread.is_alive():
                self.thread.join(timeout=5.0)
        except Exception:
            pass
        # останавливаем sender (идемпотентно)
        try:
            self.sender.stop()
        except Exception:
            pass
        self._stopped = True

    def close(self):
        # async_loki_handler.shutdown() и loguru.remove() могут звать это несколько раз
        try:
            self.stop()
        finally:
            super().close()


