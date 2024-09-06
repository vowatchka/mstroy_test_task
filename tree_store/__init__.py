from collections.abc import Generator
from typing import Optional

from . import exceptions

MAX_TREE_DEPTH = 900


class TreeStore:
    """Хранилище древовидной структуры."""

    class Item:
        """Элемент дерева."""

        def __init__(self, item: dict, ts: "TreeStore"):
            self._item = item
            self._ts = ts
            self._children_values = list()

            id_ = self._item["id"]
            parent_id = self._item["parent"]

            # ссылка на себя
            if id_ == parent_id:
                raise exceptions.ItemHimselfLinkError(id_)

            # в дереве уже есть корневой элемент
            if self.is_root and self._ts._root_item is not None:
                raise exceptions.MoreRootItemsError(id_)

            # в дереве уже есть элемент с таким же id
            if ts._items_map.get(id_):
                raise exceptions.DuplicatedItemError(id_)

            # слишком большая глубина вложенности дерева
            if len(self.parents) > MAX_TREE_DEPTH:
                raise exceptions.MaxTreeDepthError()

            # получим исключение ItemNotFoundError, если в parent указана
            # ссылка на несуществующий в дереве элемент
            if parent_item := self.parent_item:
                parent_item._children_values.append(self.value)

        @property
        def is_root(self) -> bool:
            """Возвращает `True`, если элемент корневой."""
            return self._item["parent"] == "root"

        @property
        def value(self) -> dict:
            """Возвращает значение элемента."""
            return self._item

        @property
        def parent_item(self) -> Optional["Item"]:
            """Возвращает родительский элемент."""
            return None if self.is_root else self._ts._get_item(self.value["parent"])

        @property
        def parent(self) -> Optional[dict]:
            """Возвращает значение родительского элемента."""
            if parent_item := self.parent_item:
                return parent_item.value
            else:
                return None

        @property
        def parents(self) -> list[dict]:
            """Возвращает список значений всех родительских элементов."""
            if parent_item := self.parent_item:
                return [parent_item.value, *parent_item.parents]
            else:
                return []

        @property
        def children(self) -> list[dict]:
            """Возвращает список значений всех дочерних элементов."""
            return self._children_values

    def __init__(self, items: list[dict]):
        self._root_item = None

        self._items_map = dict()
        self._items = list()
        for item in items:
            _item = self.Item(item, self)

            self._items_map[_item.value["id"]] = _item
            self._items.append(_item)

            if _item.is_root:
                self._root_item = _item

        # не должно быть, чтобы в дереве не было корневого элемента
        assert self._root_item is not None

    @property
    def root(self) -> dict:
        """Возвращает значение корневого элемента."""
        return self._root_item.value

    def iter_all(self) -> Generator[dict, None, None]:
        """Возвращает генератор значений элементов."""
        for item in self._items:
            yield item.value

    def get_all(self) -> list[dict]:
        """Возвращает весь список значений элементов."""
        return list(self.iter_all())

    def _get_item(self, id_) -> Optional["Item"]:
        """
        Возвращает элемент по id или возбуждает исключение, если элемент с таким id не найден.

        :param id_: id искомого элемента.

        :raise ItemNotFoundError: если элемент с таким id не найден.
        """
        try:
            return self._items_map[id_]
        except KeyError:
            raise exceptions.ItemNotFoundError(id_)

    def get_item(self, id_) -> Optional[dict]:
        """
        Возвращает значение элемента по id или возбуждает исключение, если элемент с таким id не найден.

        :param id_: id искомого элемента.

        :raise ItemNotFoundError: если элемент с таким id не найден.
        """
        return self._get_item(id_).value

    def get_children(self, id_) -> list[dict]:
        """
        Возвращает значения всех дочерних элементов элемента по id или возбуждает исключение,
        если элемент с таким id не найден.

        :param id_: id искомого элемента.

        :raise ItemNotFoundError: если элемент с таким id не найден.
        """
        return self._get_item(id_).children

    def get_all_parents(self, id_) -> list[dict]:
        """
        Возвращает значения всех родительских элементов элемента по id или возбуждает исключение,
        если элемент с таким id не найден.

        :param id_: id искомого элемента.

        :raise ItemNotFoundError: если элемент с таким id не найден.
        """
        return self._get_item(id_).parents
