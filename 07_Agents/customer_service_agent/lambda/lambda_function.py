import json
import boto3
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
bucket = '<S3_BUCKET_NAME>'  # Name of bucket with data file and OpenAPI file
db_name = 'customer_service_agent_sqlite_db'  # Location of data file in S3
local_db = '/tmp/csbot.db'  # Location in Lambda /tmp folder where data file will be copied

# Download data file from S3 to your local lambda storage
print(bucket, db_name, local_db)
s3.download_file(bucket, db_name, local_db)

cursor = None
conn = None


def load_data():
    """
    Initial data load and SQLite3 cursor creation
    Returns:
        a cursor for the connection
    """
    # load SQL Lite database from S3
    # create the db
    global conn
    conn = sqlite3.connect(local_db)
    c = conn.cursor()
    logger.info('Completed initial data load ')
    return c


def return_customer_info(cust_name, c):
    """
    Function returns all customer info for a particular cust_name
    Args:
        cust_name (str): customer name to query database
        c: a cursor for the connection
    Returns:
        customer information
    """
    query = 'SELECT customerId, customerName, Addr1, Addr2, City, State, Zipcode, PreferredActivity, ShoeSize, OtherInfo FROM CustomerInfo WHERE customerName LIKE "%' + cust_name + '%"'
    c.execute(query)
    resp = c.fetchall()
    # adding column names to response values
    names = [description[0] for description in c.description]
    val_dict = {}
    index = 0
    for name in names:
        val_dict[name] = resp[0][index]
        index = index + 1
    logger.info('Customer Info retrieved')
    return val_dict


#
def return_shoe_inventory(c):
    """
    Function returns shoes inventory
    Args:
        c: a cursor for the connection
    Returns:
        Shoes inventory
    """
    query = 'SELECT ShoeID, BestFitActivity, StyleDesc, ShoeColors, Price, InvCount FROM ShoeInventory'
    c.execute(query)
    resp = c.fetchall()

    # adding column names to response values
    names = [description[0] for description in c.description]
    val_dict = []
    index = 0
    for item in resp:
        interim_dict = {}
        for name in names:
            interim_dict[name] = item[index]
            index = index + 1
        index = 0
        val_dict.append(interim_dict)
    logger.info('Shoe info retrieved')
    return val_dict


def place_shoe_order(shoe_id, cust_id, c, db_conn):
    """
    function places order -- reduces shoe inventory, updates order_details table --> all actions resulting from a shoe purchase
    Args:
        shoe_id (int): shoe id
        cust_id (int): customer id
        c: a cursor for the connection
        db_conn: database connector
    Returns:
        c: a cursor for the connection
    """
    query = 'Update ShoeInventory set InvCount = InvCount - 1 where ShoeID = ' + str(shoe_id)
    c.execute(query)

    today = datetime.today().strftime('%Y-%m-%d')
    query = 'INSERT INTO OrderDetails (orderdate, shoeId, CustomerId) VALUES ("' + today + '",' + str(shoe_id) + ',' + str(cust_id) + ')'
    c.execute(query)
    db_conn.commit()

    # Writing updated db file to S3 and setting cursor to None to force reload of data
    s3.upload_file(local_db, bucket, db_name)
    c = None
    logger.info('Shoe order placed')
    return c


def lambda_handler(event, context):
    responses = []
    global cursor
    if cursor is None:
        cursor = load_data()
    shoe_id = ''
    api_path = event['apiPath']
    logger.info('API Path')
    logger.info(api_path)
    body = ""
    if api_path == '/customer/{CustomerName}':
        parameters = event['parameters']
        for parameter in parameters:
            if parameter["name"] == "CustomerName":
                c_name = parameter["value"]
                body = return_customer_info(c_name, cursor)
    elif api_path == '/place_order':
        parameters = event['parameters']
        for parameter in parameters:
            if parameter["name"] == "ShoeID":
                shoe_id = parameter["value"]
            if parameter["name"] == "CustomerID":
                cid = parameter["value"]
                body = place_shoe_order(shoe_id, cid, cursor, conn)
    elif api_path == '/check_inventory':
        body = return_shoe_inventory(cursor)
    else:
        body = {"{} is not a valid api, try another one.".format(api_path)}

    response_body = {
        'application/json': {
            'body': json.dumps(body)
        }
    }

    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': 200,
        'responseBody': response_body
    }

    responses.append(action_response)

    api_response = {
        'messageVersion': '1.0',
        'response': action_response}

    return api_response
