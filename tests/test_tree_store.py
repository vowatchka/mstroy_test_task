import pytest

import tree_store
import tree_store.exceptions as exceptions

pytestmark = [pytest.mark.all]


@pytest.mark.tree_item
@pytest.mark.without_benchmark
class TestTreeStoreItem:
    """Тестирвоание Item."""

    @pytest.mark.parametrize(
        "items, expected_ex",
        [
            (
                [{"id": 1, "parent": 1}],
                pytest.raises(exceptions.ItemHimselfLinkError, match="item with id 1 has link to himself"),
            ),
            (
                [{"id": 1, "parent": "root"}, {"id": 2, "parent": "root"}],
                pytest.raises(exceptions.MoreRootItemsError, match="cannot be more than one root item"),
            ),
            (
                [{"id": 1, "parent": "root"}, {"id": 2, "parent": 1}, {"id": 3, "parent": "root"}],
                pytest.raises(exceptions.MoreRootItemsError, match="cannot be more than one root item"),
            ),
            (
                [{"id": 1, "parent": "root"}, {"id": 2, "parent": 1}, {"id": 1, "parent": 2}],
                pytest.raises(exceptions.DuplicatedItemError, match="item with id 1 already exists"),
            ),
            (
                [{"id": 1, "parent": "root"}, {"id": 2, "parent": 3}],
                pytest.raises(exceptions.ItemNotFoundError, match="item with id 3 does not exists"),
            ),
            (
                [{"id": 1, "parent": "root"}, {"id": 2, "parent": 1}, {"id": 3, "parent": 4}],
                pytest.raises(exceptions.ItemNotFoundError, match="item with id 4 does not exists"),
            ),
        ]
    )
    def test_init_error(self, items, expected_ex):
        """Проверка ошибки инициализации Item."""
        with expected_ex:
            tree_store.TreeStore(items)

    def test_is_root(self):
        """Проверка is_root."""
        ts = tree_store.TreeStore(
            [
                {"id": 1, "parent": "root"},
                {"id": 2, "parent": 1},
            ]
        )

        assert ts._get_item(1).is_root is True
        assert ts._get_item(2).is_root is False

    def test_value(self):
        """Проверка value."""
        ts = tree_store.TreeStore(
            [
                {"id": 1, "parent": "root"},
                {"id": 2, "parent": 1},
            ]
        )

        assert ts._get_item(1).value == {"id": 1, "parent": "root"}
        assert ts._get_item(2).value == {"id": 2, "parent": 1}

    def test_parent_item(self):
        """Проверка parent_item."""
        ts = tree_store.TreeStore(
            [
                {"id": 1, "parent": "root"},
                {"id": 2, "parent": 1},
            ]
        )

        assert ts._get_item(1).parent_item is None
        assert ts._get_item(2).parent_item == ts._get_item(1)

    def test_parent(self):
        """Проверка parent."""
        ts = tree_store.TreeStore(
            [
                {"id": 1, "parent": "root"},
                {"id": 2, "parent": 1},
            ]
        )

        assert ts._get_item(1).parent is None
        assert ts._get_item(2).parent == ts._get_item(1).value

    def test_parents(self):
        """Проверка parents."""
        ts = tree_store.TreeStore(
            [
                {"id": 1, "parent": "root"},
                {"id": 2, "parent": 1},
                {"id": 3, "parent": 2},
            ]
        )

        assert ts._get_item(1).parents == list()
        assert ts._get_item(2).parents == [ts._get_item(1).value]
        assert ts._get_item(3).parents == [ts._get_item(2).value, ts._get_item(1).value]

    def test_children(self):
        """Проверка children."""
        ts = tree_store.TreeStore(
            [
                {"id": 1, "parent": "root"},
                {"id": 2, "parent": 1},
                {"id": 3, "parent": 1},
                {"id": 4, "parent": 2},
            ]
        )

        assert ts._get_item(1).children == [ts._get_item(2).value, ts._get_item(3).value]
        assert ts._get_item(2).children == [ts._get_item(4).value]
        assert ts._get_item(3).children == []
        assert ts._get_item(4).children == []


@pytest.mark.from_task
@pytest.mark.without_benchmark
class TestTreeStoreFromTask:
    """Тестирование TreeStore на примерах ТЗ."""

    ITEMS = [
        {"id": 1, "parent": "root"},
        {"id": 2, "parent": 1, "type": "test"},
        {"id": 3, "parent": 1, "type": "test"},
        {"id": 4, "parent": 2, "type": "test"},
        {"id": 5, "parent": 2, "type": "test"},
        {"id": 6, "parent": 2, "type": "test"},
        {"id": 7, "parent": 4, "type": None},
        {"id": 8, "parent": 4, "type": None},
    ]

    @pytest.fixture(scope="session")
    def ts(self):
        yield tree_store.TreeStore(self.ITEMS)

    @pytest.mark.from_task_get_all
    def test_get_all(self, ts: tree_store.TreeStore):
        """Тестирование метода get_all."""
        assert ts.get_all() == self.ITEMS

    @pytest.mark.parametrize(
        "id_",
        [7]
    )
    @pytest.mark.from_task_get_item
    def test_get_item(self, ts: tree_store.TreeStore, id_):
        """Тестирование метода get_item."""
        assert ts.get_item(id_) == tuple(filter(lambda x: x["id"] == id_, self.ITEMS))[0]

    @pytest.mark.parametrize(
        "id_",
        [4, 5]
    )
    @pytest.mark.from_task_get_children
    def test_get_children(self, ts: tree_store.TreeStore, id_):
        """Тестирование метода get_children."""
        assert ts.get_children(id_) == list(filter(lambda x: x["parent"] == id_, self.ITEMS))

    @pytest.mark.parametrize(
        "id_",
        [7]
    )
    @pytest.mark.from_task_get_all_parents
    def test_get_all_parents(self, ts: tree_store.TreeStore, id_):
        """Тестирование метода get_all_parents."""

        def get_item(id_):
            return tuple(filter(lambda x: x["id"] == id_, self.ITEMS))[0]

        def get_all_parents(id_):
            """Получить все родительские элемента элемента с id."""
            item = get_item(id_)
            if item["parent"] == "root":
                return list()
            else:
                return [get_item(item["parent"]), *get_all_parents(item["parent"])]

        assert ts.get_all_parents(id_) == get_all_parents(id_)


@pytest.mark.simple
@pytest.mark.without_benchmark
class TestTreeStoreSimple:
    """Простое тестирование TreeStore."""

    ITEMS = [
        {"id": 1, "parent": "root"},
        {"id": 2, "parent": 1, "type": "test"},
        {"id": 3, "parent": 1, "type": "test"},
        {"id": 4, "parent": 2, "type": "test"},
        {"id": 5, "parent": 2, "type": "test"},
        {"id": 6, "parent": 2, "type": "test"},
        {"id": 7, "parent": 4, "type": None},
        {"id": 8, "parent": 4, "type": None},
    ]

    @pytest.fixture(scope="session")
    def ts(self):
        yield tree_store.TreeStore(self.ITEMS)

    def test_root(self, ts: tree_store.TreeStore):
        """Проверка root."""
        assert ts.root == tuple(filter(lambda x: x["parent"] == "root", self.ITEMS))[0]

    @pytest.mark.simple_get_all
    def test_get_all(self, ts: tree_store.TreeStore):
        """Тестирование метода get_all."""
        assert ts.get_all() == self.ITEMS

    @pytest.mark.parametrize(
        "id_",
        [item["id"] for item in ITEMS]
    )
    @pytest.mark.simple_get_item
    def test_get_item(self, ts: tree_store.TreeStore, id_):
        """Тестирование метода get_item."""
        assert ts.get_item(id_) == tuple(filter(lambda x: x["id"] == id_, self.ITEMS))[0]

    @pytest.mark.simple_get_item
    def test_get_item_with_unknown_id(self, ts: tree_store.TreeStore):
        """Тестирование метода get_item с неизвестным id."""
        with pytest.raises(exceptions.ItemNotFoundError, match="item with id 100500 does not exists"):
            ts.get_item(100500)

    @pytest.mark.parametrize(
        "id_",
        [item["id"] for item in ITEMS]
    )
    @pytest.mark.simple_get_children
    def test_get_children(self, ts: tree_store.TreeStore, id_):
        """Тестирование метода get_children."""
        assert ts.get_children(id_) == list(filter(lambda x: x["parent"] == id_, self.ITEMS))

    @pytest.mark.simple_get_children
    def test_get_empty_children(self, ts: tree_store.TreeStore):
        """Тестирование метода get_children, когда нет дочерних."""
        assert ts.get_children(7) == list()

    @pytest.mark.parametrize(
        "id_",
        [item["id"] for item in ITEMS]
    )
    @pytest.mark.simple_get_all_parents
    def test_get_all_parents(self, ts: tree_store.TreeStore, id_):
        """Тестирование метода get_all_parents."""

        def get_item(id_):
            return tuple(filter(lambda x: x["id"] == id_, self.ITEMS))[0]

        def get_all_parents(id_):
            """Получить все родительские элемента элемента с id."""
            item = get_item(id_)
            if item["parent"] == "root":
                return list()
            else:
                return [get_item(item["parent"]), *get_all_parents(item["parent"])]

        assert ts.get_all_parents(id_) == get_all_parents(id_)

    @pytest.mark.simple_get_all_parents
    def test_get_empty_all_parents(self, ts: tree_store.TreeStore):
        """Тестирование метода get_all_parents, когда нет родителей."""
        assert ts.get_all_parents(1) == list()


def generate_items(count):
    items = [
        {
            "id": 1,
            "parent": "root",
            "type": "test",
        },
        *(
            {
                "id": i,
                "parent": i - 1,
                "type": "test",
            }
            for i in range(2, count + 1)
        )
    ]
    return items


@pytest.mark.with_benchmark
class TestTreeStoreStress:
    """Тестирование TestStore при больших объемах данных."""

    ITEMS_10 = generate_items(10)
    ITEMS_100 = generate_items(100)
    ITEMS_1000 = generate_items(1000)
    ITEMS_10000 = generate_items(10000)
    ITEMS_100000 = generate_items(100000)
    ITEMS_1000000 = generate_items(1000000)
    ITEMS_MAX_TREE_DEPTH = generate_items(tree_store.MAX_TREE_DEPTH)

    @pytest.mark.parametrize(
        "items",
        [
            ITEMS_1000,
            ITEMS_10000,
            ITEMS_100000,
            ITEMS_1000000,
        ]
    )
    def test_max_tree_depth_error(self, items):
        """Тестирование ошибки при превышении максимальной глубины дерева."""
        with pytest.raises(exceptions.MaxTreeDepthError, match="maximum tree depth exceeded"):
            tree_store.TreeStore(items)

    @pytest.mark.parametrize(
        "items",
        [
            ITEMS_10,
            ITEMS_100,
            ITEMS_MAX_TREE_DEPTH,
        ]
    )
    @pytest.mark.benchmark_init
    def test_init(self, items, benchmark):
        """Тестирование инициализации get_all."""
        benchmark(tree_store.TreeStore, items)

    @pytest.mark.parametrize(
        "items",
        [
            ITEMS_10,
            ITEMS_100,
            ITEMS_MAX_TREE_DEPTH,
        ]
    )
    @pytest.mark.benchmark_get_all
    def test_get_all(self, items, benchmark):
        """Тестирование метода get_all."""
        ts = tree_store.TreeStore(items)
        benchmark(ts.get_all)

    @pytest.mark.parametrize(
        "id_, items",
        [
            (1, ITEMS_10),
            (len(ITEMS_10) // 2, ITEMS_10),
            (len(ITEMS_10), ITEMS_10),
            (1, ITEMS_100),
            (len(ITEMS_100) // 2, ITEMS_100),
            (len(ITEMS_100), ITEMS_100),
            (1, ITEMS_MAX_TREE_DEPTH),
            (len(ITEMS_MAX_TREE_DEPTH) // 2, ITEMS_MAX_TREE_DEPTH),
            (len(ITEMS_MAX_TREE_DEPTH), ITEMS_MAX_TREE_DEPTH),
        ]
    )
    @pytest.mark.benchmark_get_item
    def test_get_item(self, id_, items, benchmark):
        """Тестирование метода get_item."""
        ts = tree_store.TreeStore(items)
        benchmark(ts.get_item, id_)

    @pytest.mark.parametrize(
        "id_, items",
        [
            (1, ITEMS_10),
            (len(ITEMS_10) // 2, ITEMS_10),
            (len(ITEMS_10), ITEMS_10),
            (1, ITEMS_100),
            (len(ITEMS_100) // 2, ITEMS_100),
            (len(ITEMS_100), ITEMS_100),
            (1, ITEMS_MAX_TREE_DEPTH),
            (len(ITEMS_MAX_TREE_DEPTH) // 2, ITEMS_MAX_TREE_DEPTH),
            (len(ITEMS_MAX_TREE_DEPTH), ITEMS_MAX_TREE_DEPTH),
        ]
    )
    @pytest.mark.benchmark_get_children
    def test_get_children(self, id_, items, benchmark):
        """Тестирование метода get_children."""
        ts = tree_store.TreeStore(items)
        benchmark(ts.get_children, id_)

    @pytest.mark.parametrize(
        "id_, items",
        [
            (1, ITEMS_10),
            (len(ITEMS_10) // 2, ITEMS_10),
            (len(ITEMS_10), ITEMS_10),
            (1, ITEMS_100),
            (len(ITEMS_100) // 2, ITEMS_100),
            (len(ITEMS_100), ITEMS_100),
            (1, ITEMS_MAX_TREE_DEPTH),
            (len(ITEMS_MAX_TREE_DEPTH) // 2, ITEMS_MAX_TREE_DEPTH),
            (len(ITEMS_MAX_TREE_DEPTH), ITEMS_MAX_TREE_DEPTH),
        ]
    )
    @pytest.mark.benchmark_get_all_parents
    def test_get_all_parents(self, id_, items, benchmark):
        """Тестирование метода get_all_parents."""
        ts = tree_store.TreeStore(items)
        benchmark(ts.get_all_parents, id_)
