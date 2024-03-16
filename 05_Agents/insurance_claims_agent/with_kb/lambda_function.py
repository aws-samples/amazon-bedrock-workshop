#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import json


def get_named_parameter(event, name):
    return next(item for item in event['parameters'] if item['name'] == name)['value']


def get_named_property(event, name):
    return next(
        item for item in
        event['requestBody']['content']['application/json']['properties']
        if item['name'] == name)['value']


def claim_detail(claim_id):
    if claim_id == 'claim-857':
        return {
            "response": {
                "claimId": claim_id,
                "createdDate": "21-Jul-2023",
                "lastActivityDate": "25-Jul-2023",
                "status": "Open",
                "policyType": "Vehicle"
            }
        }
    elif claim_id == 'claim-006':
        return {
            "response": {
                "claimId": claim_id,
                "createdDate": "20-May-2023",
                "lastActivityDate": "23-Jul-2023",
                "status": "Open",
                "policyType": "Vehicle"
            }
        }
    elif claim_id == 'claim-999':
        return {
            "response": {
                "claimId": claim_id,
                "createdDate": "10-Jan-2023",
                "lastActivityDate": "31-Feb-2023",
                "status": "Completed",
                "policyType": "Disability"
            }
        }
    else:
        return {
            "response": {
                "claimId": claim_id,
                "createdDate": "18-Apr-2023",
                "lastActivityDate": "20-Apr-2023",
                "status": "Open",
                "policyType": "Vehicle"
            }
        }


def open_claims():
    return {
        "response": [
            {
                "claimId": "claim-006",
                "policyHolderId": "A945684",
                "claimStatus": "Open"
            },
            {
                "claimId": "claim-857",
                "policyHolderId": "A645987",
                "claimStatus": "Open"
            },
            {
                "claimId": "claim-334",
                "policyHolderId": "A987654",
                "claimStatus": "Open"
            }
        ]
    }


def outstanding_paperwork(claim_id):
    outstanding_documents = {
        "claim-857": {
            "response": {
                    "pendingDocuments": ["DriverLicense, VehicleRegistration"]
            }
        },
        "claim-006": {
            "response": {
                    "pendingDocuments": ["AccidentImages"]
            }
        }
    }
    if claim_id in outstanding_documents:
        return outstanding_documents[claim_id]["response"]
    else:
        return {
            "response": {
                "pendingDocuments": ""
            }
        }


def send_reminder(claim_id, pending_documents):
    return {
        "response": {
            "ClaimId": claim_id,
            "PendingDocuments": pending_documents,
            "TrackingId": "50e8400-e29b-41d4-a716-446655440000",
            "Status": "InProgress"
        }
    }


def lambda_handler(event, context):
    action = event['actionGroup']
    api_path = event['apiPath']
    if api_path == '/open-items':
        body = open_claims()
    elif api_path == '/open-items/{claimId}/outstanding-paperwork':
        claim_id = get_named_parameter(event, "claimId")
        body = outstanding_paperwork(claim_id)
    elif api_path == '/open-items/{claimId}/detail':
        claim_id = get_named_parameter(event, "claimId")
        body = claim_detail(claim_id)
    elif api_path == '/notify':
        claim_id = get_named_property(event, "claimId")
        pending_documents = get_named_property(event, "pendingDocuments")
        body = send_reminder(claim_id, pending_documents)
    else:
        body = {"{}::{} is not a valid api, try another one.".format(action, api_path)}

    response_body = {
        'application/json': {
            'body': str(body)
        }
    }

    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': 200,
        'responseBody': response_body
    }

    response = {'response': action_response}
    return response
