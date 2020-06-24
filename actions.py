import json
from collections import defaultdict
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker, utils
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase
from rasa_sdk.knowledge_base.storage import InMemoryKnowledgeBase


class EnToZh:
    def __init__(self, data_file):
        with open(data_file) as fd:
            self.data = json.load(fd)

    def __call__(self, key):
        return self.data.get(key, key)


class MyKnowledgeBaseAction(ActionQueryKnowledgeBase):
    def name(self) -> Text:
        return "action_response_query"

    def __init__(self):
        knowledge_base = InMemoryKnowledgeBase("data.json")
        super().__init__(knowledge_base)

        self.en_to_zh = EnToZh("en_to_zh.json")

    async def utter_objects(
        self,
        dispatcher: CollectingDispatcher,
        object_type: Text,
        objects: List[Dict[Text, Any]],
    ) -> None:
        """
        Utters a response to the user that lists all found objects.
        Args:
            dispatcher: the dispatcher
            object_type: the object type
            objects: the list of objects
        """
        if objects:
            dispatcher.utter_message(text="找到下列{}:".format(self.en_to_zh(object_type)))

            if utils.is_coroutine_action(
                self.knowledge_base.get_representation_function_of_object
            ):
                repr_function = await self.knowledge_base.get_representation_function_of_object(
                    object_type
                )
            else:
                repr_function = self.knowledge_base.get_representation_function_of_object(
                    object_type
                )

            for i, obj in enumerate(objects, 1):
                dispatcher.utter_message(text=f"{i}: {repr_function(obj)}")
        else:
            dispatcher.utter_message(
                text="我没找到任何{}.".format(self.en_to_zh(object_type))
            )

    def utter_attribute_value(
        self,
        dispatcher: CollectingDispatcher,
        object_name: Text,
        attribute_name: Text,
        attribute_value: Text,
    ) -> None:
        """
        Utters a response that informs the user about the attribute value of the
        attribute of interest.
        Args:
            dispatcher: the dispatcher
            object_name: the name of the object
            attribute_name: the name of the attribute
            attribute_value: the value of the attribute
        """
        if attribute_value:
            dispatcher.utter_message(
                text="{}的{}是{}。".format(
                    self.en_to_zh(object_name),
                    self.en_to_zh(attribute_name),
                    self.en_to_zh(attribute_value),
                )
            )
        else:
            dispatcher.utter_message(
                text="没有找到{}的{}。".format(
                    self.en_to_zh(object_name), self.en_to_zh(attribute_name)
                )
            )


class PlaySong(Action):
    def name(self) -> Text:
        return "action_play_song"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        song = tracker.get_slot("song")

        dispatcher.utter_message(text="正在为您播放歌曲《{}》。".format(song))
        return []


class PlayAlbum(Action):
    def name(self) -> Text:
        return "action_play_album"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        song = tracker.get_slot("album")

        dispatcher.utter_message(text="正在为您播放专辑《{}》。".format(song))
        return []
