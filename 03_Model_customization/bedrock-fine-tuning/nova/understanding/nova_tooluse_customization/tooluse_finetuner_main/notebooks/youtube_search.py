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
            "name": "youtube_search",
            "description": " search for youtube videos associated with a person. the input to this tool should be a comma separated list, the first part contains a person name and the second a number that is the maximum number of video results to return aka num_results. the second part is optional",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "youtube search query to look up",
                        },                                                
                    },
                    "required": ["query"],
                }
            },
        }
    }


def fetch_youtube_search_data(input_data):
    """
    Runs query through youtube search.
    
    :param input_data: The input data containing the query.
    :return: Nothing.
    """

    return