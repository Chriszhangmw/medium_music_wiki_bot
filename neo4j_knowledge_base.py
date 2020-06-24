import json
from collections import defaultdict
from typing import Any, Dict, List, Text

from neo4j import GraphDatabase
from rasa_sdk.knowledge_base.storage import KnowledgeBase


class Neo4jKnowledgeBase(KnowledgeBase):
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

        self.representation_attribute = defaultdict(lambda: lambda obj: obj["name"])

        super().__init__(self)

    def close(self):
        self._driver.close()

    async def get_attributes_of_object(self, object_type: Text) -> List[Text]:
        # transformer for query
        object_type = object_type.capitalize()

        result = self.do_get_attributes_of_object(object_type)

    def do_get_atrributes_of_object(self, object_type) -> List[Text]:
        with self._driver.session() as session:
            result = session.write_transaction(
                self._do_get_atrributes_of_object, object_type
            )

        return result

    def _do_get_attributes_of_object(self, tx, object_type) -> List[Text]:
        query = "MATCH (o:{object_type}) RETURN o LIMIT 1".format(
            object_type=object_type
        )
        print(query)
        result = tx.run(query,)

        record = result.single()

        if record:
            return record[0].keys()

        return []

    async def get_representation_attribute_of_object(self, object_type: Text) -> Text:
        """
        Returns a lamdba function that takes the object and returns a string
        representation of it.
        Args:
            object_type: the object type
        Returns: lamdba function
        """
        return self.representation_attribute[object_type]

    def do_get_objects(
        self, object_type: Text, attributions: Dict[Text, Text], limit: int
    ):
        with self._driver.session() as session:
            result = session.write_transaction(
                self._do_get_objects, object_type, attributions, limit
            )

        return result

    @staticmethod
    def _do_get_objects(
        tx, object_type: Text, attributions: Dict[Text, Text], limit: int
    ):
        query = "MATCH (o:{object_type} {attrs}) RETURN o LIMIT {limit}".format(
            object_type=object_type, attrs=json.dumps(attributions), limit=limit
        )
        print(query)
        result = tx.run(query,)

        return [dict(record["o"].items()) for record in result]

    def do_get_object(
        self,
        object_type: Text,
        object_identifier: Text,
        key_attribute: Text,
        representation_attribute: Text,
    ):
        with self._driver.session() as session:
            result = session.write_transaction(
                self._do_get_object, object_type, object_identifier, key_attribute
            )

        return result

    @staticmethod
    def _do_get_object(
        tx,
        object_type: Text,
        object_identifier: Text,
        key_attribute: Text,
        representation_attribute: Text,
    ):
        # try match key first
        query = "MATCH (o:{object_type} {{{key}:{value}}}) RETURN o".format(
            object_type=object_type, key=key_attribute, value=object_identifier
        )
        print(query)
        result = tx.run(query,)
        record = result.single()
        if record:
            return dict(record[0].items())

        # try to match representation attribute
        query = "MATCH (o:{object_type} {{{key}:{value}}}) RETURN o".format(
            object_type=object_type,
            key=representation_attribute,
            value=object_identifier,
        )
        print(query)
        result = tx.run(query,)
        record = result.single()
        if record:
            return dict(record[0].items())

        # finally, failed
        return None

    async def get_objects(
        self, object_type: Text, attributes: List[Dict[Text, Text]], limit: int = 5
    ) -> List[Dict[Text, Any]]:
        """
        Query the knowledge base for objects of the given type. Restrict the objects
        by the provided attributes, if any attributes are given.
        Args:
            object_type: the object type
            attributes: list of attributes
            limit: maximum number of objects to return
        Returns: list of objects
        """

        # convert attributes to dict
        attrs = {}
        for a in attributes:
            attrs[a["name"]] = a["value"]

        # transformer for query
        object_type = object_type.capitalize()

        result = self.do_get_objects(object_type, attrs, limit)

        return result

    async def get_object(
        self, object_type: Text, object_identifier: Text
    ) -> Dict[Text, Any]:
        """
        Returns the object of the given type that matches the given object identifier.
        Args:
            object_type: the object type
            object_identifier: value of the key attribute or the string
            representation of the object
        Returns: the object of interest
        """
        # transformer for query
        object_type = object_type.capitalize()

        result = self.do_get_object(
            object_type,
            object_identifier,
            self.get_key_attribute_of_object(object_type),
            self.get_representation_attribute_of_object(object_type),
        )

        return result

if __name__ == "__main__":
    import asyncio

    kb = Neo4jKnowledgeBase("bolt://localhost:7687", "neo4j", "43215678")
    loop = asyncio.get_event_loop()

    result = loop.run_until_complete(kb.get_objects("singer", [], 5))
    print(result)

    result = loop.run_until_complete(kb.get_object("singer", "0"))
    print(result)

    loop.close()
