


import os
import sys
import asyncio
import inspect
import traceback
import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, AsyncGenerator, Awaitable
from aioquic.asyncio.server import serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived
from typing import Any, AsyncGenerator, Union


from gnobjects.net.objects import GNRequest, GNResponse, FileObject, CORSObject, TemplateObject
from gnobjects.net.fastcommands import AllGNFastCommands, GNFastCommand


from ._func_params_validation import register_schema_by_key, validate_params_by_key
from ._cors_resolver import resolve_cors

from ._routes import Route, _compile_path, _ensure_async, _convert_value

from .models import KDCObject


try:
    if not sys.platform.startswith("win"):
        import uvloop # type: ignore
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    print("uvloop не установлен")


import logging

logger = logging.getLogger("GNServer")
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter("[%(name)s] %(levelname)s: %(message)s"))
logger.addHandler(console)


def guess_type(filename: str) -> str:
    """
    Возвращает актуальный MIME-тип по расширению файла.
    Только современные и часто используемые типы.
    """
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''

    mime_map = {
        # 🔹 Текст и данные
        "txt": "text/plain",
        "html": "text/html",
        "css": "text/css",
        "csv": "text/csv",
        "xml": "application/xml",
        "json": "application/json",
        "js": "application/javascript",

        # 🔹 Изображения (актуальные для веба)
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "svg": "image/svg+xml",
        "avif": "image/avif",
        "ico": "image/x-icon",

        # 🔹 Видео (современные форматы)
        "mp4": "video/mp4",
        "webm": "video/webm",

        # 🔹 Аудио (современные форматы)
        "mp3": "audio/mpeg",
        "ogg": "audio/ogg",
        "oga": "audio/ogg",
        "m4a": "audio/mp4",
        "flac": "audio/flac",

        # 🔹 Архивы
        "zip": "application/zip",
        "gz": "application/gzip",
        "tar": "application/x-tar",
        "7z": "application/x-7z-compressed",
        "rar": "application/vnd.rar",

        # 🔹 Документы (актуальные офисные)
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",

        # 🔹 Шрифты
        "woff": "font/woff",
        "woff2": "font/woff2",
        "ttf": "font/ttf",
        "otf": "font/otf",
    }

    return mime_map.get(ext, "application/octet-stream")





class App:
    def __init__(self):
        self._routes: List[Route] = []
        self._cors: Optional[CORSObject] = None
        self._events: Dict[str, List[Dict[str, Union[Any, Callable]]]] = {}

        self.domain: str = None # type: ignore

        self.__allowed_modes = (1, 2, 4)

        self._kdc: Optional[KDCObject] = None

    def setKDC(self, kdc: KDCObject):
        self._kdc = kdc

    def route(self, method: str, path: str, cors: Optional[CORSObject] = None):
        if path == '/':
            path = ''
        def decorator(fn: Callable[..., Any]):
            regex, param_types = _compile_path(path)
            self._routes.append(
                Route(
                    method.upper(),
                    path,
                    regex,
                    param_types,
                    _ensure_async(fn),
                    fn.__name__,
                    cors
                )
            )
            register_schema_by_key(fn)
            return fn
        return decorator

    def get(self, path: str, *, cors: Optional[CORSObject] = None):
        return self.route("GET", path, cors)

    def post(self, path: str, *, cors: Optional[CORSObject] = None):
        return self.route("POST", path, cors)

    def put(self, path: str, *, cors: Optional[CORSObject] = None):
        return self.route("PUT", path, cors)

    def delete(self, path: str, *, cors: Optional[CORSObject] = None):
        return self.route("DELETE", path, cors)

    
    def setRouteCors(self, cors: Optional[CORSObject] = None):
        self._cors = cors


    def addEventListener(self, name: str):
        def decorator(fn: Callable[[Callable[[dict | None], Awaitable[Any]]], None]):
            events = self._events.get(name, [])
            events.append({
                'func': fn,
                'async': inspect.iscoroutinefunction(fn),
                'parameters': inspect.signature(fn).parameters
                })
            self._events[name] = events
            
            return fn
        return decorator
    
    async def dispatchEvent(self, name: str, payload: Optional[str] = None) -> None:
        data_list = self._events.get(name, None)
        if data_list:
            for data in data_list:
                func: Callable = data['func']
                is_async = data['async']

                if not is_async:
                    if payload in data['parameters']: # type: ignore
                        func(payload=payload)
                    else:
                        func()
                else:
                    if payload in data['parameters']: # type: ignore
                        await func(payload=payload)
                    else:
                        await func()



    async def dispatchRequest(
        self, request: GNRequest
    ) -> Union[GNResponse, AsyncGenerator[GNResponse, None]]:
        path    = request.url.path
        method  = request.method.upper()
        cand    = {path, path.rstrip("/") or "/", f"{path}/"}
        allowed = set()

        for r in self._routes:
            m = next((r.regex.fullmatch(p) for p in cand if r.regex.fullmatch(p)), None)
            if not m:
                continue

            allowed.add(r.method)
            if r.method != method:
                continue

            resolve_cors(request, r.cors)

            sig = inspect.signature(r.handler)
            def _ann(name: str):
                param = sig.parameters.get(name)
                return param.annotation if param else inspect._empty

            kw: dict[str, Any] = {
                name: _convert_value(val, _ann(name), r.param_types.get(name, str))
                for name, val in m.groupdict().items()
            }

            for qn, qvals in request.url.params.items():
                if qn in kw:
                    continue
                if isinstance(qvals, int):
                    kw[qn] = qvals
                else:
                    raw = qvals if len(qvals) > 1 else qvals[0]
                    kw[qn] = _convert_value(raw, _ann(qn), str)

            
            params = set(sig.parameters.keys())
            kw = {k: v for k, v in kw.items() if k in params}

            
            rv = validate_params_by_key(kw, r.handler)
            if rv is not None:
                raise AllGNFastCommands.UnprocessableEntity({'dev_error': rv, 'user_error': f'Server request error {self.domain}'})

            if "request" in sig.parameters:
                kw["request"] = request

            if inspect.isasyncgenfunction(r.handler):
                return r.handler(**kw)

            result = await r.handler(**kw)
            if result is None:
                result = AllGNFastCommands.ok()
            if isinstance(result, GNResponse):
                if r.cors is None:
                    if result._cors is None:
                        result._cors = self._cors
                else:
                    result._cors = r.cors

                resolve_cors(request, result._cors)

                return result
            else:
                raise TypeError(
                    f"{r.handler.__name__} returned {type(result)}; GNResponse expected"
                )

        if allowed:
            raise AllGNFastCommands.MethodNotAllowed()
        raise AllGNFastCommands.NotFound()


    def fastFile(self, path: str, file_path: str, cors: Optional[CORSObject] = None, template: Optional[TemplateObject] = None, payload: Optional[dict] = None):
        @self.get(path)
        async def r_static():
            nonlocal file_path
            if file_path.endswith('/'):
                file_path = file_path[:-1]
                
            if not os.path.isfile(file_path):
                raise AllGNFastCommands.NotFound()

            fileObject = FileObject(file_path, template)
            return GNResponse('ok', payload=payload, files=fileObject, cors=cors)


    def static(self, path: str, dir_path: str, cors: Optional[CORSObject] = None, template: Optional[TemplateObject] = None, payload: Optional[dict] = None):
        @self.get(f"{path}/{{_path:path}}")
        async def r_static(_path: str):
            file_path = os.path.join(dir_path, _path)
            
            if file_path.endswith('/'):
                file_path = file_path[:-1]
                
            if not os.path.isfile(file_path):
                raise AllGNFastCommands.NotFound()
            
            fileObject = FileObject(file_path, template)
            return GNResponse('ok', payload=payload, files=fileObject, cors=cors)




    def _init_sys_routes(self):
        @self.post('/!gn-vm-host/ping', cors=CORSObject(allow_client_types=['server']))
        async def r_ping(request: GNRequest):
            if request.client.ip != '127.0.0.1':
                raise AllGNFastCommands.Forbidden()
            return GNResponse('ok', {'time': datetime.datetime.now(datetime.UTC).isoformat()})



    class _ServerProto(QuicConnectionProtocol):
        def __init__(self, *a, api: "App", **kw):
            super().__init__(*a, **kw)
            self._api = api
            self._buffer: Dict[int, bytearray] = {}
            self._streams: Dict[int, Tuple[asyncio.Queue[Optional[GNRequest]], bool]] = {}

        def quic_event_received(self, event: QuicEvent):
            if isinstance(event, StreamDataReceived):
                buf = self._buffer.setdefault(event.stream_id, bytearray())
                buf.extend(event.data)

                # пока не знаем, это стрим или нет

                if len(buf) < 8: # не дошел даже frame пакета
                    logger.debug(f'Пакет отклонен: {buf} < 8. Не доставлен фрейм')
                    return
                
                    
                # получаем длинну пакета
                mode, stream, lenght = GNRequest.type(buf)

                if mode not in self._api._App__allowed_modes: # не наш пакет # type: ignore
                    logger.debug(f'Пакет отклонен: mode пакета {mode}. Разрешен 1, 2, 4')
                    return
                
                stream_id = event.stream_id

                if not stream: # если не стрим, то ждем конец quic стрима и запускаем обработку ответа
                    if event.end_stream:
                        asyncio.create_task(self._resolve_raw_request(stream_id, buf, mode))
                    return
                
                # если стрим, то смотрим сколько пришло данных
                if len(buf) < lenght: # если пакет не весь пришел, пропускаем
                    return

                # первый в буфере пакет пришел полностью
        
                # берем пакет
                data = buf[:lenght]

                # удаляем его из буфера
                del buf[:lenght]

                # формируем запрос

                asyncio.create_task(self.sendRawResponse(stream_id, AllGNFastCommands.NotImplemented().serialize(mode=mode)))
                return
                
                if self._api._kdc is not None:
                    data, domain = self._api._kdc.decode(data)
                else:
                    domain = None
                request = GNRequest.deserialize(data, mode)
                if domain is not None:
                    request.client._data['domain'] = domain

                logger.debug(request, f'event.stream_id -> {event.stream_id}')

                request.stream_id = event.stream_id  # type: ignore

                queue, inapi = self._streams.setdefault(event.stream_id, (asyncio.Queue(), False))

                if request.method == 'gn:end-stream':
                    if event.stream_id in self._streams:
                        _ = self._streams.get(event.stream_id)
                        if _ is not None:
                            queue, inapi = _
                            if inapi:
                                queue.put_nowait(None)
                                self._buffer.pop(event.stream_id)
                                self._streams.pop(event.stream_id)
                                return

                queue.put_nowait(request)

                # отдаем очередь в интерфейс
                if not inapi:
                    self._streams[event.stream_id] = (queue, True)

                    async def w():
                        while True:
                            chunk = await queue.get()
                            if chunk is None:
                                break
                            yield chunk

                    request._stream = w  # type: ignore
                    asyncio.create_task(self._handle_request(request, mode))

        async def _resolve_raw_request(self, stream_id: int, data: bytes, mode: int):

            if self._api._kdc is not None:
                data, domain = await self._api._kdc.decode(bytes(data))
            else:
                domain = None
            
            if data is None:
                self._buffer.pop(stream_id, None)
                raise Exception('Не удалось расшифровать от KDC')
        
            try:
                request = GNRequest.deserialize(data, mode)
                if domain is not None:
                    request.client._data['domain'] = domain
            except:
                self._buffer.pop(stream_id, None)
                await self.sendRawResponse(stream_id, AllGNFastCommands.KDCDecryptRequestFailed().serialize(mode=mode))
                return

            logger.debug(f'[<] Request: {request.method} {request.url}')
            
            request.client._data['remote_addr'] = self._quic._network_paths[0].addr
            request.stream_id = stream_id   # type: ignore

            self._buffer.pop(stream_id, None)
            await self._handle_request(request, mode)


        async def _handle_request(self, request: GNRequest, mode: int):


            try:
                response = await self._api.dispatchRequest(request)

                if inspect.isasyncgen(response):
                    async for chunk in response:  # type: ignore[misc]
                        chunk._stream = True
                        await self.sendResponse(request, chunk, mode, False)
                        
                    resp = GNResponse('gn:end-stream')
                    resp._stream = True

                    await self.sendResponse(request, resp, mode)
                    return

                if not isinstance(response, GNResponse):
                    await self.sendResponse(request, AllGNFastCommands.InternalServerError(), mode)
                    return

                await self.sendResponse(request, response, mode)
            except Exception as e:
                if isinstance(e, (GNRequest, GNFastCommand)):
                    await self.sendResponse(request, e, mode)
                else:
                    logger.error('InternalServerError:\n'  + traceback.format_exc())

                    await self.sendResponse(request, AllGNFastCommands.InternalServerError(), mode)
            

        
        async def sendResponse(self, request: GNRequest, response: GNResponse, mode: int, end_stream: bool = True):
            await response.assembly()

            
            logger.debug(f'[>] Response: {request.method} {request.url} -> {response.command} {response.payload if len(str(response.payload)) < 256 else ''}')
            
            blob = response.serialize(mode)


            if self._api._kdc is not None:
                blob = await self._api._kdc.encode(request.client.domain, blob)

            await self.sendRawResponse(request.stream_id, blob=blob, end_stream=end_stream)

        async def sendRawResponse(self, stream_id: int, blob: bytes, end_stream: bool = True):
            self._quic.send_stream_data(stream_id, blob, end_stream=end_stream) # type: ignore
            self.transmit()

    def run(
        self,
        domain: str,
        port: int,
        cert_path: str,
        key_path: str,
        *,
        host: str = '0.0.0.0',
        idle_timeout: float = 20.0,
        wait: bool = True,
        run: Optional[Callable] = None
    ):
        """
        # Запустить сервер

        Запускает сервер в главном процессе asyncio.run()
        """

        self.domain = domain


        self._init_sys_routes()

        cfg = QuicConfiguration(
            alpn_protocols=["gn:backend"], is_client=False, idle_timeout=idle_timeout
        )
        cfg.load_cert_chain(cert_path, key_path) # type: ignore

        async def _main():
            
            await self.dispatchEvent('start')

            await serve(
                host,
                port,
                configuration=cfg,
                create_protocol=lambda *a, **kw: App._ServerProto(*a, api=self, **kw),
                retry=False,
            )
            
            if run is not None:
                await run()

            logger.debug('Server startup completed')
            if wait:
                await asyncio.Event().wait()

        asyncio.run(_main())


    def runByVMHost(self):
        """
        # Запусить через VM-host

        Заупскает сервер через процесс vm-host
        """
        argv = sys.argv[1:]
        command = argv[0]
        if command == 'gn:vm-host:start':
            domain = argv[1]
            port = int(argv[2])
            cert_path = argv[3]
            key_path = argv[4]
            host = argv[5]

            self.run(
                domain=domain,
                port=port,
                cert_path=cert_path,
                key_path=key_path,
                host=host
            )