from typing import Any, ItemsView, Iterator, KeysView, ValuesView, Mapping, MutableMapping

from pyknowbase.model import Article

from ..model import KnowledgeBase, MutableKnowledgeBase, Article

class DynamoKnowledgeBaseValuesView(ValuesView):

    def __init__(self, mapping) -> None:
        self._mapping = mapping

    def __contains__(self, v: object) -> bool:
        for data in self._mapping.scan():
            article = Article.model_validate(data)
            if v is article or v == article:
                return True
        return False

    def __iter__(self) -> Iterator:
        for data in self._mapping.scan():
            yield Article.model_validate(data)


class DynamoKnowledgeBaseItemsView(ItemsView):

    def __init__(self, mapping: Mapping) -> None:
        self._mapping = mapping

    def __iter__(self) -> Iterator:
        for keys, data in self._mapping.items():
            yield (keys, Article.model_validate(data))


class DynamoKnowledgeBase(KnowledgeBase):

    _mapping: MutableMapping[str, Any]

    def __init__(self, table_name: str) -> None:
        try:
            from dynamodb_mapping import DynamoDBMapping
        except ImportError:
            raise ValueError(
                "Could not import dynamodb_mapping python package. "
                "Please install it with `pip install dynamodb_mapping`."
            )
        self._mapping = DynamoDBMapping(table_name=table_name)

    def __iter__(self) -> Iterator[str]:
        return iter(self._mapping.keys())

    def keys(self) -> KeysView[str]:
        return self._mapping.keys()

    def values(self) -> ValuesView[Article]:
        return DynamoKnowledgeBaseValuesView(self._mapping)

    def items(self) -> ItemsView[str, Article]:
        return DynamoKnowledgeBaseItemsView(self._mapping)

    def __len__(self) -> int:
        return len(self._mapping)

    def __getitem__(self, __key: str) -> Article:
        return self._mapping[__key]


class MutableDynamoKnowledgeBase(DynamoKnowledgeBase, MutableKnowledgeBase):

    def __setitem__(self, __key: str, __value: Article) -> None:
        self._mapping[__key] = __value.model_dump(mode="json")

    def __delitem__(self, __key: str) -> None:
        del self._mapping[__key]
