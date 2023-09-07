from typing import Dict, Any, Iterator, Optional, Callable, cast

import boto3
from boto3.dynamodb.conditions import Key

from pyknowbase.model import Article

from ..model import KnowledgeBase, MutableKnowledgeBase, Article


def dynamodb_paginator(action: Callable, kwargs: Dict) -> Iterator[Dict]:
    while True:
        response = action(**kwargs)
        for item in response["Items"]:
            yield item
        if "LastEvaluatedKey" in response:
            kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
        else:
            break


class DynamoMultiKnowledgeBase(MutableKnowledgeBase):

    collection: "DynamoMultiKnowledgeBaseCollection"

    def __init__(self,
        collection: "DynamoMultiKnowledgeBaseCollection",
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        self.name = name
        self.metadata = metadata or {}
        self.collection = collection

    def __iter__(self) -> Iterator[Article]:
        return self.collection._get_articles(kb_name=self.name)

    def __getitem__(self, __key: str) -> Article:
        article = self.collection._get_article(kb_name=self.name, article_id=__key)
        if not article:
            raise KeyError(f"Could not find article with id {__key} in knowledge base {self.name}")
        return article

    def __setitem__(self, __key: str, __value: Article) -> None:
        self.collection._put_article(kb_name=self.name, article=__value, article_id=__key)

    def __delitem__(self, __key: str) -> None:
        self.collection._delete_article(kb_name=self.name, article_id=__key)


class DynamoMultiKnowledgeBaseCollection:

    table_name: str
    """The name of the DynamoDB table backing this collection."""

    index_name: str
    """The name of the global secondary index of the table that manages knowledge base entities."""

    table_pk: str = "pk"
    """The name of the primary key (hash key) of the table. The primary key value is the name
    of the knowledge base."""

    table_sk: str = "sk"
    """The name of the secondary key (sort key) of the table. The secondary key value is the
    identifier of the articles, or kb_sk_value in the case the item represents a knowledge base."""

    index_pk: str = "gsi_pk"
    """The name of the primary key (hash key) of the global secondary index of the table."""

    kb_sk_value: str = "_knowledgebase"
    """The value of the secondary key if this item represents a knowledge base entity."""

    kb_metadata_attrib_name = "metadata"
    """The name of the knowledge base attribute that contains the metadata."""

    article_metadata_attrib_name = "metadata"
    """The name of the article attribute that contains the metadata."""

    def __init__(self, table_name: str, index_name: str, **kwargs) -> None:
        self.table_name = table_name
        self.index_name = index_name
        session = (
            kwargs.get("boto3_session")
            or boto3.Session()
        )
        self.dynamodb = session.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def __iter__(self) -> Iterator[MutableKnowledgeBase]:
        return self._get_knowledge_bases()

    def __getitem__(self, __key: str) -> MutableKnowledgeBase:
        kb = self._get_knowledge_base(kb_name=__key)
        if kb is None:
            raise KeyError(f"Could not find knowledge base with name {__key}.")
        else:
            return kb

    def __setitem__(self, __key: str, __value: KnowledgeBase) -> None:
        self.put_knowledge_base(kb_name=__key, metadata=__value.metadata)

    def __delitem__(self, __key: str) -> None:
        self._delete_knowledge_base(kb_name=__key, delete_articles=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} table_name={self.table_name}>"

    def create_table(self,
        kwargs: Dict[str, Any] = { "BillingMode": "PAY_PER_REQUEST" },
        gs_kwargs: Dict[str, Any] = {}
    ) -> None:
        """Creates a DynamoDB table that can be used to store multiple knowledge bases by this
        class.

        Args:
            kwargs (Dict[str, Any]): Additional keyword arguments to be passed to the create_table
                method. You can set for example provisioned capacity settings. Defaults to
                { "BillingMode": "PAY_PER_REQUEST" }.
            gs_kwargs (Dict[str, Any]): Additional keyword arguments to be passed to
                global secondary indexes configuration. You can set for example provisioned
                capacity settings. Defaults to {}.
        """
        self.dynamodb.create_table(
            TableName = self.table_name,
            KeySchema = [
                {
                    "AttributeName": self.table_pk,
                    "KeyType": "HASH"
                },
                {
                    "AttributeName": self.table_sk,
                    "KeyType": "RANGE"
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": self.index_name,
                    "KeySchema": [
                        {
                            "AttributeName": self.index_pk,
                            "KeyType": "HASH"
                        }
                    ],
                    "Projection": {
                        "ProjectionType": "ALL"
                    },
                    **gs_kwargs  # type: ignore
                }
            ],
            AttributeDefinitions = [
                {
                    "AttributeName": self.table_pk,
                    "AttributeType": "S"
                },
                {
                    "AttributeName": self.table_sk,
                    "AttributeType": "S"
                },
                {
                    "AttributeName": self.index_pk,
                    "AttributeType": "S"
                }
            ],
            **kwargs
        )

    def _get_knowledge_bases(self) -> Iterator[MutableKnowledgeBase]:
        kwargs = { "IndexName": self.index_name }
        for item in dynamodb_paginator(self.table.scan, kwargs):
            yield DynamoMultiKnowledgeBase(
                collection=self,
                name=item[self.index_pk],
                metadata=item.get(self.kb_metadata_attrib_name),
            )

    def _get_knowledge_base(self, kb_name: str) -> Optional[MutableKnowledgeBase]:
        kb_key = { self.table_pk: kb_name, self.table_sk: self.kb_sk_value }
        result = self.table.get_item(Key=kb_key)
        if "Item" not in result:
            return None
        item: Dict = result["Item"]
        return DynamoMultiKnowledgeBase(
            collection=self,
            name=kb_name,
            metadata=item.get(self.kb_metadata_attrib_name),
        )

    def put_knowledge_base(self, kb_name: str, metadata: Dict[str, Any] = {}) -> MutableKnowledgeBase:
        item: Dict = {
            self.table_pk: kb_name,
            self.table_sk: self.kb_sk_value,
            self.index_pk: kb_name,
            self.kb_metadata_attrib_name: metadata,
        }
        self.table.put_item(Item=item)
        return DynamoMultiKnowledgeBase(
            collection=self,
            name=kb_name,
            metadata=metadata,
        )

    def _delete_knowledge_base(self, kb_name: str, delete_articles: bool = False) -> None:
        if delete_articles:
            with self.table.batch_writer() as batch:
                query_kwargs = {
                    "KeyConditionExpression": Key(self.table_pk).eq(kb_name),
                    "ProjectionExpression": self.table_sk,
                }
                for item in dynamodb_paginator(self.table.query, query_kwargs):
                    if item[self.table_sk] == self.kb_sk_value:
                        continue
                    else:
                        batch.delete_item(
                            Key={
                                self.table_pk: kb_name,
                                self.table_sk: item[self.table_sk]
                            }
                        )
        key = { self.table_pk: kb_name, self.table_sk: self.kb_sk_value }
        print("delete key:", key)
        self.table.delete_item(Key=key)

    def _get_articles(self, kb_name: str) -> Iterator[Article]:
        kwargs = { "KeyConditionExpression": Key(self.table_pk).eq(kb_name) }
        for item in dynamodb_paginator(self.table.query, kwargs):
            if item[self.table_sk] == self.kb_sk_value:
                continue
            else:
                yield Article(
                    id=item[self.table_sk],
                    text=item["text"],
                    metadata=item.get(self.article_metadata_attrib_name, {})
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
                metadata=cast(dict, item.get(self.article_metadata_attrib_name, {})),
            )

    def _put_article(self, kb_name: str, article: Article, article_id: Optional[str] = None) -> None:
        item = article.model_dump(mode="json")
        a_id = item.pop("id")
        article_id = article_id or a_id
        item[self.table_pk] = kb_name
        item[self.table_sk] = article_id
        self.table.put_item(Item=item)

    def _delete_article(self, kb_name, article_id: str) -> None:
        self.table.delete_item(Key={ self.table_pk: kb_name, self.table_sk: article_id })
