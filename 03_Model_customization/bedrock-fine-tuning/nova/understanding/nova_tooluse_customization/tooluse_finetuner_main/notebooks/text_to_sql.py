# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import requests
from requests.exceptions import RequestException


def get_tool_spec():
    """
    Returns the JSON Schema specification for the SQL query  tool. The tool specification
    defines the input schema and describes the tool's functionality.
    For more information, see https://json-schema.org/understanding-json-schema/reference.

    :return: The tool specification for the SQL query tool.
    """
  

    return {
        "toolSpec": {
            "name": "text_to_sql",
            "description": "Tool for creating a SQL query. Pull the relevant table and any conditions used ",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "table": {
                            "type": "string",
                            "description": "The relevant table to pull data from",
                        },
                        "condition": {
                            "type": "string",
                            "description": "a condition like: where salary > 200",
                        },
                        
                    },
                    "required": ["table", "condition"],
                }
            },
        }
    }


def fetch_sql_data(input_data):
    """
    Pull the relevant table and any conditions used.
    

    :param input_data: The input data containing the table, codition.
    :return: Nothing.
    """

    return