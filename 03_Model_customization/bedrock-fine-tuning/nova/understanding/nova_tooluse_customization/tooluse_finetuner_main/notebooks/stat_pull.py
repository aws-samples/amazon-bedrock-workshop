# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import requests
from requests.exceptions import RequestException


def get_tool_spec():
    """
    Returns the JSON Schema specification for the stat pull tool. The tool specification
    defines the input schema and describes the tool's functionality.
    For more information, see https://json-schema.org/understanding-json-schema/reference.

    :return: The tool specification for stat pull tool.
    """

    return {
        "toolSpec": {
            "name": "stat_pull",
            "description": "Get the stats of a team",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "league": {
                            "type": "string",
                            "description": "The US sports league the stat is associated with, e.g. NFL, NBA, NHL, MLB",
                        },
                        "year": {
                            "type": "string",
                            "description": "The year the stats are associated with",
                        },
                        "team": {
                            "type": "string",
                            "description": "A specific team the stats are associated with, e.g. Cincinnati Bengals, if no team, specify None",
                        },                        
                    },
                    "required": ["league", "year", "team"],
                }
            },
        }
    }


def fetch_stat_pull(input_data):
    """
     Formatting call for getting sports stats

    :param input_data: The input data containing the league, year, team.
    :return: Nothing.
    """

    return