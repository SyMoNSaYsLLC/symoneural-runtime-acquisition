"""ctypes binding to libsymoneural-llm — the Backend the runtime uses on a target.

Loads ONE explicit library, checks the ABI major before declaring a single
signature, and implements backend.Backend over the C handles: one runtime, one
loaded model per id, one native session per loaded model. Models are named by id;
the C library resolves <registry_root>/<id>.gguf and refuses anything that could
leave that directory. Nothing here takes a filesystem path from a request.

Resolution order for the library: $SYM_LLM_NATIVE (explicit path, for tests and
staging), then the soname on the loader path (the installed package).
"""
from __future__ import annotations

import codecs
import ctypes
import ctypes.util
import os
import queue
import re
import threading
from typing import Iterator

from .backend import Cancelled, GenerateParams, ModelInfo

ABI_MAJOR = 1
SONAME = "libsymoneural-llm.so.1"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,126}$")

OK, EINVAL, ENOSPC, ENOENT, EIO, EBUSY, ECANCELLED, EABI, EBACKEND = 0, -1, -2, -3, -4, -5, -6, -7, -8


class NativeError(RuntimeError):
    def __init__(self, status: int, strerror: str) -> None:
        super().__init__(f"libsymoneural-llm: {strerror} ({status})")
        self.status = status
        self.strerror = strerror


class NativeUnavailable(RuntimeError):
    """The library is not installed here."""


class _RuntimeParams(ctypes.Structure):
    _fields_ = [("size", ctypes.c_uint32), ("registry_root", ctypes.c_char_p),
                ("n_threads", ctypes.c_int), ("gpu_layers", ctypes.c_int)]


class _SessionParams(ctypes.Structure):
    _fields_ = [("size", ctypes.c_uint32), ("n_ctx", ctypes.c_int), ("seed", ctypes.c_uint32)]


class _Sampling(ctypes.Structure):
    _fields_ = [("size", ctypes.c_uint32), ("max_tokens", ctypes.c_int), ("temperature", ctypes.c_float),
                ("top_p", ctypes.c_float), ("top_k", ctypes.c_int), ("repeat_penalty", ctypes.c_float)]


class _Result(ctypes.Structure):
    _fields_ = [("size", ctypes.c_uint32), ("stop_reason", ctypes.c_int),
                ("prompt_tokens", ctypes.c_int), ("output_tokens", ctypes.c_int)]


_TOKEN_CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t, ctypes.c_void_p)


class Native:
    """The narrow FFI. One instance per process; handles are opaque c_void_p."""

    def __init__(self, path: str | None = None) -> None:
        path = path or os.environ.get("SYM_LLM_NATIVE") or ctypes.util.find_library("symoneural-llm") or SONAME
        try:
            self._lib = ctypes.CDLL(path)
        except OSError as e:
            raise NativeUnavailable(str(e)) from None
        L = self._lib
        L.sym_llm_abi_version.restype = ctypes.c_uint32
        abi = L.sym_llm_abi_version()
        if (abi >> 16) != ABI_MAJOR:
            raise NativeError(EABI, f"ABI major {abi >> 16} != {ABI_MAJOR}")
        self.abi_version = abi
        self.path = path
        # signatures declared only after the ABI check
        L.sym_llm_version_string.restype = ctypes.c_char_p
        L.sym_llm_strerror.restype = ctypes.c_char_p
        L.sym_llm_strerror.argtypes = [ctypes.c_int]
        L.sym_llm_capabilities.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
        L.sym_llm_runtime_open.argtypes = [ctypes.POINTER(_RuntimeParams), ctypes.POINTER(ctypes.c_void_p)]
        L.sym_llm_runtime_close.argtypes = [ctypes.c_void_p]
        L.sym_llm_runtime_close.restype = None
        L.sym_llm_model_load.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
        L.sym_llm_model_unload.argtypes = [ctypes.c_void_p]
        L.sym_llm_model_unload.restype = None
        L.sym_llm_model_info.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
        L.sym_llm_session_open.argtypes = [ctypes.c_void_p, ctypes.POINTER(_SessionParams), ctypes.POINTER(ctypes.c_void_p)]
        L.sym_llm_session_close.argtypes = [ctypes.c_void_p]
        L.sym_llm_session_close.restype = None
        L.sym_llm_session_reset.argtypes = [ctypes.c_void_p]
        L.sym_llm_tokenize.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int32), ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
        L.sym_llm_detokenize.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int32), ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t]
        L.sym_llm_generate.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(_Sampling), _TOKEN_CB, ctypes.c_void_p, ctypes.POINTER(_Result)]
        L.sym_llm_cancel.argtypes = [ctypes.c_void_p]

    def strerror(self, st: int) -> str:
        return self._lib.sym_llm_strerror(st).decode()

    def check(self, st: int) -> None:
        if st != OK:
            raise NativeError(st, self.strerror(st))

    def version(self) -> str:
        return self._lib.sym_llm_version_string().decode()

    def capabilities(self) -> list[str]:
        buf = ctypes.create_string_buffer(256)
        self.check(self._lib.sym_llm_capabilities(buf, len(buf)))
        return buf.value.decode().split()


_instance: Native | None = None


def load(path: str | None = None) -> Native:
    global _instance
    if _instance is None:
        _instance = Native(path)
    return _instance


def available() -> bool:
    try:
        load()
        return True
    except NativeUnavailable:
        return False


class _Loaded:
    __slots__ = ("model", "session", "info", "vocab_only", "lock")

    def __init__(self, model: ctypes.c_void_p, info: dict) -> None:
        self.model = model
        self.session: ctypes.c_void_p | None = None
        self.info = info
        self.vocab_only = bool(info.get("vocab_only"))
        self.lock = threading.Lock()


class LlamaBackend:
    """backend.Backend over libsymoneural-llm.

    The registry root is a directory of <id>.gguf files. models() lists the ids the
    directory holds (context_length is known once a model is loaded); load() opens
    the model and, unless it is vocabulary-only, a native session with n_ctx.
    generate() runs the blocking native call on a worker thread and yields decoded
    pieces as they arrive; the cancel Event is honoured at the next token through
    the ABI's callback return and sym_llm_cancel.
    """

    def __init__(self, registry_root: str, *, n_threads: int = 0, n_ctx: int = 4096, seed: int = 0,
                 native: Native | None = None) -> None:
        self._n = native or load()
        self._root = os.path.abspath(registry_root)
        self._n_ctx = int(n_ctx)
        self._seed = int(seed) & 0xFFFFFFFF
        self._loaded: dict[str, _Loaded] = {}
        self._infos: dict[str, ModelInfo] = {}
        rt = ctypes.c_void_p()
        p = _RuntimeParams(ctypes.sizeof(_RuntimeParams), self._root.encode(), int(n_threads), 0)
        self._n.check(self._n._lib.sym_llm_runtime_open(ctypes.byref(p), ctypes.byref(rt)))
        self._rt = rt

    # -- registry view -----------------------------------------------------------
    def registry_ids(self) -> list[str]:
        try:
            names = os.listdir(self._root)
        except OSError:
            return []
        return sorted(f[:-5] for f in names if f.endswith(".gguf") and ID_RE.match(f[:-5]))

    def models(self) -> list[ModelInfo]:
        out = []
        for mid in self.registry_ids():
            out.append(self._infos.get(mid) or ModelInfo(mid, 0, frozenset({"text"})))
        return out

    # -- Backend protocol ------------------------------------------------------------
    def load(self, model_id: str) -> None:
        if model_id in self._loaded:
            return
        if not ID_RE.match(model_id):
            raise KeyError(model_id)
        h = ctypes.c_void_p()
        st = self._n._lib.sym_llm_model_load(self._rt, model_id.encode(), ctypes.byref(h))
        if st == ENOENT:
            raise KeyError(model_id)
        self._n.check(st)
        buf = ctypes.create_string_buffer(2048)
        self._n.check(self._n._lib.sym_llm_model_info(h, buf, len(buf)))
        import json
        info = json.loads(buf.value.decode())
        ld = _Loaded(h, info)
        if not ld.vocab_only:
            s = ctypes.c_void_p()
            sp = _SessionParams(ctypes.sizeof(_SessionParams), self._n_ctx, self._seed)
            st = self._n._lib.sym_llm_session_open(h, ctypes.byref(sp), ctypes.byref(s))
            if st != OK:
                self._n._lib.sym_llm_model_unload(h)
                self._n.check(st)
            ld.session = s
        self._loaded[model_id] = ld
        caps = {"text", "tokenize"} if not ld.vocab_only else {"tokenize"}
        self._infos[model_id] = ModelInfo(model_id, int(info.get("n_ctx_train") or 0), frozenset(caps))

    def unload(self, model_id: str) -> None:
        ld = self._loaded.pop(model_id, None)
        if ld is None:
            return
        if ld.session is not None:
            self._n._lib.sym_llm_session_close(ld.session)
        self._n._lib.sym_llm_model_unload(ld.model)

    def info(self, model_id: str) -> dict:
        return dict(self._loaded[model_id].info)

    def tokenize(self, model_id: str, text: str) -> list[int]:
        ld = self._loaded[model_id]
        n = ctypes.c_size_t(0)
        st = self._n._lib.sym_llm_tokenize(ld.model, text.encode(), None, 0, ctypes.byref(n))
        if st not in (OK, ENOSPC):
            self._n.check(st)
        arr = (ctypes.c_int32 * max(int(n.value), 1))()
        self._n.check(self._n._lib.sym_llm_tokenize(ld.model, text.encode(), arr, int(n.value), ctypes.byref(n)))
        return list(arr[: n.value])

    def detokenize(self, model_id: str, tokens: list[int]) -> str:
        ld = self._loaded[model_id]
        arr = (ctypes.c_int32 * max(len(tokens), 1))(*tokens)
        cap = 64 + 16 * len(tokens)
        while True:
            buf = ctypes.create_string_buffer(cap)
            st = self._n._lib.sym_llm_detokenize(ld.model, arr, len(tokens), buf, cap)
            if st == ENOSPC and cap < 1 << 22:
                cap *= 4
                continue
            self._n.check(st)
            return buf.value.decode("utf-8", errors="replace")

    def generate(self, model_id: str, prompt: str, params: GenerateParams, cancel: threading.Event) -> Iterator[str]:
        ld = self._loaded[model_id]
        if ld.session is None:
            raise RuntimeError(f"{model_id} is vocabulary-only; it cannot generate")
        if not ld.lock.acquire(blocking=False):
            raise RuntimeError(f"{model_id} is busy")
        q: queue.Queue[bytes | None] = queue.Queue()
        result = _Result(ctypes.sizeof(_Result), 0, 0, 0)
        status: list[int] = []

        def on_piece(ptr, n, _user):
            if cancel.is_set():
                return 1
            q.put(ctypes.string_at(ptr, n))
            return 0

        cb = _TOKEN_CB(on_piece)          # kept alive for the duration of the call
        smp = _Sampling(ctypes.sizeof(_Sampling), int(params.max_tokens), float(params.temperature),
                        float(params.top_p), 40, 1.0)

        def run():
            try:
                status.append(self._n._lib.sym_llm_generate(ld.session, prompt.encode(), ctypes.byref(smp),
                                                            cb, None, ctypes.byref(result)))
            finally:
                q.put(None)

        t = threading.Thread(target=run, name="symoneural-llm-generate", daemon=True)
        t.start()
        dec = codecs.getincrementaldecoder("utf-8")(errors="replace")
        try:
            while True:
                if cancel.is_set():
                    self._n._lib.sym_llm_cancel(ld.session)
                item = q.get()
                if item is None:
                    break
                text = dec.decode(item)
                if text:
                    yield text
            tail = dec.decode(b"", final=True)
            if tail:
                yield tail
            t.join()
            st = status[0] if status else EBACKEND
            if st == ECANCELLED:
                raise Cancelled()
            self._n.check(st)
            self.last_result = {"stop_reason": int(result.stop_reason), "prompt_tokens": int(result.prompt_tokens),
                                "output_tokens": int(result.output_tokens)}
        finally:
            ld.lock.release()

    def close(self) -> None:
        for mid in list(self._loaded):
            self.unload(mid)
        if self._rt:
            self._n._lib.sym_llm_runtime_close(self._rt)
            self._rt = None
