from typing import Dict, Any, Iterator, Optional, Callable, cast

import boto3
from boto3.dynamodb.conditions import Key

from ..model import KnowledgeBase, Article


def dynamodb_paginator(action: Callable, kwargs: Dict) -> Iterator[Dict]:
    while True:
        response = action(**kwargs)
        for item in response["Items"]:
            yield item
        if "LastEvaluatedKey" in response:
            kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
        else:
            break


class DynamoMultiKnowledgeBase(KnowledgeBase):

    collection: "DynamoMultiKnowledgeBaseCollection"

    def __init__(self, raw_item: Dict[Any, Any], collection: "DynamoMultiKnowledgeBaseCollection") -> None:
        self.name = raw_item[collection.index_pk]
        self.metadata = raw_item["metadata"]
        self.collection = collection

    def __iter__(self) -> Iterator[Article]:
        return self.collection._get_articles(kb_name=self.name)

    def __getitem__(self, __key: str) -> Article:
        article = self.collection._get_article(kb_name=self.name, article_id=__key)
        if not article:
            raise KeyError(f"Could not find article with id {__key} in knowledge base {self.name}")
        return article


class DynamoMultiKnowledgeBaseCollection:

    table_name: str
    index_name: str
    table_pk: str = "pk"
    table_sk: str = "sk"
    index_pk: str = "gsi_pk"
    kb_sk_value: str = "_metadata"

    def __init__(self, table_name: str, index_name: str, **kwargs) -> None:
        self.table_name = table_name
        self.index_name = index_name
        session = (
            kwargs.get("boto3_session")
            or boto3.Session()
        )
        self.table = session.resource("dynamodb").Table(table_name)

    def __iter__(self) -> Iterator[KnowledgeBase]:
        return self._get_knowledge_bases()

    def __getitem__(self, __key: str) -> KnowledgeBase:
        kb = self._get_knowledge_base(kb_name=__key)
        if kb is None:
            raise KeyError(f"Could not find knowledge base with name {__key}.")
        else:
            return kb

    def _get_knowledge_bases(self) -> Iterator[KnowledgeBase]:
        kwargs = { "IndexName": self.index_name }
        for item in dynamodb_paginator(self.table.scan, kwargs):
            yield DynamoMultiKnowledgeBase(raw_item=item, collection=self)

    def _get_knowledge_base(self, kb_name: str) -> Optional[KnowledgeBase]:
        kb_key = { self.table_pk: kb_name, self.table_sk: self.kb_sk_value }
        result = self.table.get_item(Key=kb_key)
        return (
            DynamoMultiKnowledgeBase(raw_item=result["Item"], collection=self)
            if "Item" in result else
            None
        )

    def _get_articles(self, kb_name: str) -> Iterator[Article]:
        kwargs = { "KeyConditionExpression": Key(self.table_pk).eq(kb_name) }
        for item in dynamodb_paginator(self.table.query, kwargs):
            if item[self.table_sk] == self.kb_sk_value:
                continue
            else:
                yield Article(
                    id=item[self.table_sk],
                    text=item["text"],
                    metadata=item.get("metadata", {})
                )

    def _get_article(self, kb_name: str, article_id: str) -> Optional[Article]:
        response = self.table.get_item(Key={self.table_pk: kb_name, self.table_sk: article_id})
        if "Item" not in response:
            return None
        else:
            item = response["Item"]
            return Article(
                id=article_id,
                text=cast(str, item["text"]),
                metadata=cast(dict, item.get("metadata", {})),
            )
