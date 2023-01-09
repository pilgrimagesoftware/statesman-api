__author__ = "Paul Schifferer <paul@schifferers.net>"
"""
collection.py
- Collection utilities
"""


import json
import os, logging
from statesman_api import constants
from statesman_api.common.exceptions import SignatureException
from statesman_api.models.state_collection import StateCollection
from statesman_api.models.state_item import StateItem
from statesman_api.models.user import User
from statesman_api.models import constants as model_constants
from statesman_api.db import db
from statesman_api.utils.user import create_or_fetch_user
from statesman_api.utils.access import check_collection_permission, check_item_permission


def get_collection_items(collection:StateCollection, user:User) -> list:
    logging.debug("collection: %s, user: %s", collection, user)

    items = StateItem.query.filter_by(collection_id=collection.id).all()
    if len(items) == 0:
        blocks = [
            {
                    "text": f"_Collection *{collection.name}* is empty_."
            }
        ]
        return blocks

    blocks = [
        {
                "text": f"Collection: *<{collection.name}|{collection.name}>*"
            # },
            # "accessory": {
            #     "type": "button",
            #     "text": {
            #         "type": "plain_text",
            #         "emoji": True,
            #         "text": "Use"
            #     },
            #     "value": f"use:{collection.name}"
            # }
        },
        {
            "type": "divider"
        },
        {
                "text": f"_Items_:"
        },
    ]

    # fields = []
    for item in items:
        if not check_item_permission(user, item, model_constants.PERMISSION_READ):
            logging.debug("User %s does not have permission to read item %s.", user, item)
            continue

        label = item.name
        if item.label is not None and len(item.label) > 0:
            label = f"{item.label} ({item.name})"

        item_info = f"*{label}*: {item.value}"

        if item.default_value is not None and len(item.default_value) > 0:
            item_info += f"\n_Default value_: *{item.default_value}*"

        field = {
                "text": item_info,
            # },
            # "accessory": {
            #     "type": "overflow",
            #     "options": [
            #         {
            #             "text": {
            #                 "type": "plain_text",
            #                 "emoji": True,
            #                 "text": "Increment"
            #             },
            #             "value": f"add:{item.name}"
            #         },
            #         {
            #             "text": {
            #                 "type": "plain_text",
            #                 "emoji": True,
            #                 "text": "Decrement"
            #             },
            #             "value": f"subtract:{item.name}"
            #         },
            #         {
            #             "text": {
            #                 "type": "plain_text",
            #                 "emoji": True,
            #                 "text": "Reset"
            #             },
            #             "value": f"reset:{item.name}"
            #         },
            #         {
            #             "text": {
            #                 "type": "plain_text",
            #                 "emoji": True,
            #                 "text": "Unset"
            #             },
            #             "value": f"unset:{item.name}"
            #         },
            #     ]
            # }
        }
        blocks.append(field)

    # blocks.append({
    #     "type": "section",
    #     "fields": fields,
    # })

    return blocks


def list_collections(user_id:str, team_id:str) -> list:
    logging.debug("user_id: %s, team_id: %s", user_id, team_id)

    user = create_or_fetch_user(user_id, team_id)
    collections = StateCollection.query.filter_by(team_id=team_id).all()

    blocks = [
        {
                "text": "_Here are the state collections you can use_:"
        },
        {
            "type": "divider"
        },
    ]

    for c in collections:
        if not check_collection_permission(user, c, model_constants.PERMISSION_READ):
            logging.debug("User %s does not have permission to read collection %s.", user, c)
            continue

        blocks.append({
                "text": f"*{c.name}*\nCreated by <@{c.creator_id}>"
            # },
            # "accessory": {
            #     "type": "button",
            #     "text": {
            #         "type": "plain_text",
            #         "emoji": True,
            #         "text": "Use"
            #     },
            #     "value": f"use:{c.name}"
            # }
        })

    return blocks
