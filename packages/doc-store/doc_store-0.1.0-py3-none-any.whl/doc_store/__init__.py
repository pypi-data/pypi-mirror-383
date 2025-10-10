import importlib
import typing
from functools import lru_cache

__lazy_attrs__ = {
    "BlockType": (".structs", "BlockType"),
    "ContentBlock": (".structs", "ContentBlock"),
    "PDFDocument": (".pdf_doc", "PDFDocument"),
    "DocStore": (".doc_store", "DocStore"),
    "Doc": (".doc_store", "Doc"),
    "Page": (".doc_store", "Page"),
    "Layout": (".doc_store", "Layout"),
    "Block": (".doc_store", "Block"),
    "Content": (".doc_store", "Content"),
    "Task": (".doc_store", "Task"),
    "ElementExistsError": (".doc_store", "ElementExistsError"),
    "DocExistsError": (".doc_store", "DocExistsError"),
}

if typing.TYPE_CHECKING:
    from .doc_store import (
        Block,
        Content,
        Doc,
        DocExistsError,
        DocStore,
        ElementExistsError,
        Layout,
        Page,
        Task,
    )
    from .pdf_doc import PDFDocument
    from .structs import BlockType, ContentBlock

    store: DocStore


@lru_cache(maxsize=1)
def _store():
    from .doc_store import DocStore

    return DocStore()


def __getattr__(name: str):
    if name == "store":
        return _store()
    if name in __lazy_attrs__:
        module_name, attr_name = __lazy_attrs__[name]
        module = importlib.import_module(module_name, __name__)
        return getattr(module, attr_name)
    raise AttributeError(f"Module '{__name__}' has no attribute '{name}'")


__all__ = [
    "BlockType",
    "ContentBlock",
    "PDFDocument",
    "store",
    "DocStore",
    "Doc",
    "Page",
    "Layout",
    "Block",
    "Content",
    "Task",
    "ElementExistsError",
    "DocExistsError",
]
