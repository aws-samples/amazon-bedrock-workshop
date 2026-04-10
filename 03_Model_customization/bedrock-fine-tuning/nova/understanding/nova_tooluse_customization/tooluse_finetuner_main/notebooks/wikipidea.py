# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import requests
from requests.exceptions import RequestException



def get_tool_spec():
    """
    Returns the JSON Schema specification for the terminal  tool. The tool specification
    defines the input schema and describes the tool's functionality.
    For more information, see https://json-schema.org/understanding-json-schema/reference.

    :return: The tool specification for the terminal tool.
    """
  

    return {
        "toolSpec": {
            "name": "wikipedia",
            "description": " A wrapper around Wikipedia. Useful for when you need to answer general questions about people, places, companies, facts, historical events, or other subjects. Input should be a search query.  ",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "query to look up on wikipedia",
                        },                                                
                    },
                    "required": ["query"],
                }
            },
        }
    }


def fetch_wikipidea_data(input_data):
    """
    Runs query on Wikipidea through a wrapper.
    

    :param input_data: The input data containing the query.
    :return: Nothing.
    """

    return