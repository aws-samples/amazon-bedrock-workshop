# Lab 0 - Introduction to Bedrock

This lab will walk you through the basics of connecting to the Amazon Bedrock service from Python.

First, ensure you've completed the setup in the ['Getting Started' section of the root README](../README.md#Getting-started)

Then, you'll be ready to walk through the notebook [bedrock_boto3_setup.ipynb](bedrock_boto3_setup.ipynb), which shows how to install the required packages, connect to Bedrock, and invoke models. Before running any of the labs ensure you've run the [Bedrock boto3 setup notebook](../00_Intro/bedrock_boto3_setup.ipynb#Prerequisites).

## Python virtual environment setup

Following steps guides you through creation of a python virtual environment. 
This helps isolate all libraries used in the Amazon Bedrock workshop to:

- provide a better experience, and
- keep you python environment cleaner.

### Setup on your local machine

Open a new terminal on your machine, in which you will execute the next steps.

#### Linux or MacOS
First you'll create a new virtual environment. Run the following commands to create and activate the new bedrock python virtal environment.

```shell
python3 -m venv ~/.venv/bedrock
source ~/.venv/bedrock/bin/activate
```

Verify that you're using the new virtual environment. Run the command below.

```shell
which python
```

Your output should look similar to the below one.

    /Users/USER_NAME/.venv/bedrock/bin/python


Next, start your jupyter notebook. Run to command below to start jupyter notebook 
(or use any other ways you're used to doing it). If you're already running jupyter notebook server,
please stop the server and start it again in the terminal you just created the new python virtual environment.

```shell
jupyter notebook
```

### Clean up
Run the command below to delete the created python virtual environment.

```shell
rm -rf ~/.venv/bedrock 
```
