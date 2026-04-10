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
            "name": "duckduckgo_results_json",
            "description": " A wrapper around Duck Duck Go Search. Useful for when you need to answer questions about current events. Input should be a search query. Output is a JSON string array of the query results ",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "internet search query to look up",
                        },                                                
                    },
                    "required": ["query"],
                }
            },
        }
    }


def fetch_duckduckgo_results_json_data(input_data):
    """
    Runs query through Duck Duck Go Search.
    
    :param input_data: The input data containing the query.
    :return: Nothing.
    """

    return