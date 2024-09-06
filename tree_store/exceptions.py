class BaseItemError(Exception):
    def __init__(self, id_):
        self.id = id_

    def __str__(self):
        return repr(self.id)


class ItemNotFoundError(BaseItemError):
    """Элемент не найден по id."""

    def __str__(self):
        return f"item with id {self.id} does not exists"


class ItemHimselfLinkError(BaseItemError):
    """Элемент ссылается сам на себя (id == parent)."""

    def __str__(self):
        return f"item with id {self.id} has link to himself"


class DuplicatedItemError(BaseItemError):
    """Дубль уже существующего элемента (item.id == other.id)."""

    def __str__(self):
        return f"item with id {self.id} already exists"


class MoreRootItemsError(BaseItemError):
    """Не может быть два корневых элемента."""

    def __str__(self):
        return "cannot be more than one root item"


class MaxTreeDepthError(Exception):
    """Превышена максимальная глубина вложенности дерева."""

    def __str__(self):
        return "maximum tree depth exceeded"
