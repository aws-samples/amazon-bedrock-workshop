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
            "name": "pubmed_search",
            "description": "  A wrapper around PubMed. Useful for when you need to answer questions about medicine, health, and biomedical topics from biomedical literature, MEDLINE, life science journals, and online books. Input should be a search query.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "pubmed search query to look up",
                        },                                                
                    },
                    "required": ["query"],
                }
            },
        }
    }


def fetch_pubmed_search_data(input_data):
    """
    Runs query through pubmed search.
    
    :param input_data: The input data containing the query.
    :return: Nothing.
    """

    return