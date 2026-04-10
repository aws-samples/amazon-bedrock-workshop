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
            "name": "terminal",
            "description": "Run shell commands on this MacOS machine ",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "commands": {
                            "type": "string",
                            "description": "TList of shell commands to run. Deserialized using json.loads",
                        },                                                
                    },
                    "required": ["commands"],
                }
            },
        }
    }


def fetch_terminal_data(input_data):
    """
    Run shell commands on this MacOS machine.
    

    :param input_data: The input data containing the commands.
    :return: Nothing.
    """

    return