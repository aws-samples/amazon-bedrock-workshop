from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_community.llms import Bedrock
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.tools import BaseTool

from langchain.agents.format_scratchpad.tools import format_to_tool_messages
from langchain.agents.output_parsers.tools import ToolsAgentOutputParser

#["weather", "search_sagemaker_policy" ] #-"SageMaker"]
import traceback


from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate,HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from langchain.embeddings.bedrock import BedrockEmbeddings
from langchain_aws.chat_models.bedrock import ChatBedrock

from langchain import LLMMathChain
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate,HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import requests

from langchain.tools import tool
from langchain.tools import StructuredTool

from langchain.agents import AgentType
from langchain import LLMMathChain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.config import RunnableConfig

from langchain_core.runnables import Runnable
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_aws.chat_models.bedrock import ChatBedrock

from langchain.document_loaders import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import FAISS

from langchain.embeddings import BedrockEmbeddings
import operator
from typing import Annotated, Any, Dict, List, Optional, Sequence, TypedDict
import functools

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.chat_history import InMemoryChatMessageHistory


import json
import os
import sys

import boto3



import warnings

from io import StringIO
import sys
import textwrap
import os
from typing import Optional

# External Dependencies:
import boto3
from botocore.config import Config

import streamlit as st

warnings.filterwarnings('ignore')

def print_ww(*args, width: int = 100, **kwargs):
    """Like print(), but wraps output to `width` characters (default 100)"""
    buffer = StringIO()
    try:
        _stdout = sys.stdout
        sys.stdout = buffer
        print(*args, **kwargs)
        output = buffer.getvalue()
    finally:
        sys.stdout = _stdout
    for line in output.splitlines():
        print("\n".join(textwrap.wrap(line, width=width)))
        



def get_bedrock_client(
    assumed_role: Optional[str] = None,
    region: Optional[str] = None,
    runtime: Optional[bool] = True,
):
    """Create a boto3 client for Amazon Bedrock, with optional configuration overrides

    Parameters
    ----------
    assumed_role :
        Optional ARN of an AWS IAM role to assume for calling the Bedrock service. If not
        specified, the current active credentials will be used.
    region :
        Optional name of the AWS Region in which the service should be called (e.g. "us-east-1").
        If not specified, AWS_REGION or AWS_DEFAULT_REGION environment variable will be used.
    runtime :
        Optional choice of getting different client to perform operations with the Amazon Bedrock service.
    """
    if region is None:
        target_region = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION"))
    else:
        target_region = region

    print(f"Create new client\n  Using region: {target_region}")
    session_kwargs = {"region_name": target_region}
    client_kwargs = {**session_kwargs}

    profile_name = os.environ.get("AWS_PROFILE")
    if profile_name:
        print(f"  Using profile: {profile_name}")
        session_kwargs["profile_name"] = profile_name

    retry_config = Config(
        region_name=target_region,
        retries={
            "max_attempts": 10,
            "mode": "standard",
        },
    )
    session = boto3.Session(**session_kwargs)

    if assumed_role:
        print(f"  Using role: {assumed_role}", end='')
        sts = session.client("sts")
        response = sts.assume_role(
            RoleArn=str(assumed_role),
            RoleSessionName="langchain-llm-1"
        )
        print(" ... successful!")
        client_kwargs["aws_access_key_id"] = response["Credentials"]["AccessKeyId"]
        client_kwargs["aws_secret_access_key"] = response["Credentials"]["SecretAccessKey"]
        client_kwargs["aws_session_token"] = response["Credentials"]["SessionToken"]

    if runtime:
        service_name='bedrock-runtime'
    else:
        service_name='bedrock'

    bedrock_client = session.client(
        service_name=service_name,
        config=retry_config,
        **client_kwargs
    )

    print("boto3 Bedrock client successfully created!")
    print(bedrock_client._endpoint)
    return bedrock_client




# ---- ⚠️ Un-comment and edit the below lines as needed for your AWS setup ⚠️ ----

# os.environ["AWS_DEFAULT_REGION"] = "<REGION_NAME>"  # E.g. "us-east-1"
# os.environ["AWS_PROFILE"] = "<YOUR_PROFILE>"
# os.environ["BEDROCK_ASSUME_ROLE"] = "<YOUR_ROLE_ARN>"  # E.g. "arn:aws:..."


boto3_bedrock = get_bedrock_client(
    assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
    region='us-west-2' #os.environ.get("AWS_DEFAULT_REGION", None)
)

### This below LEVARAGES the In-memory with multiple sessions and session id
store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    #print(session_id)
    if not session_id:
        session_id = "NONE"
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

def create_retriever_pain():

    br_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=boto3_bedrock)

    # s3_path = "s3://jumpstart-cache-prod-us-east-2/training-datasets/Amazon_SageMaker_FAQs/Amazon_SageMaker_FAQs.csv"
    # !aws s3 cp $s3_path ./rag_data/Amazon_SageMaker_FAQs.csv

    loader = CSVLoader("./rag_data/medi_history.csv") # --- > 219 docs with 400 chars, each row consists in a question column and an answer column
    documents_aws = loader.load() #
    print(f"Number of documents={len(documents_aws)}")

    docs = CharacterTextSplitter(chunk_size=2000, chunk_overlap=400, separator=",").split_documents(documents_aws)

    print(f"Number of documents after split and chunking={len(docs)}")
    vectorstore_faiss_aws = None

        
    vectorstore_faiss_aws = FAISS.from_documents(
        documents=docs,
        embedding = br_embeddings
    )

    print(f"vectorstore_faiss_aws: number of elements in the index={vectorstore_faiss_aws.index.ntotal}::")

    model_parameter = {"temperature": 0.0, "top_p": .5, "max_tokens_to_sample": 2000}
    modelId = "meta.llama3-8b-instruct-v1:0" #"anthropic.claude-v2"
    chatbedrock_llm = ChatBedrock(
        model_id=modelId,
        client=boto3_bedrock,
        model_kwargs=model_parameter, 
        beta_use_converse_api=True
    )

    contextualized_question_system_template = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualized_question_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualized_question_system_template),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    #- we will not ue this below
    # history_aware_retriever = create_history_aware_retriever(
    #     chatbedrock_llm, vectorstore_faiss_aws.as_retriever(), contextualized_question_prompt
    # )


    qa_system_prompt = """You are an assistant for question-answering tasks. \
    Use the following pieces of retrieved context to answer the question. \
    If the answer is not present in the context, just say you do not have enough context to answer. \
    If the input is not present in the context, just say you do not have enough context to answer. \
    If the question is not present in the context, just say you do not have enough context to answer. \
    If you don't know the answer, just say that you don't know. \
    Use three sentences maximum and keep the answer concise.\

    {context}"""

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])
    question_answer_chain = create_stuff_documents_chain(chatbedrock_llm, qa_prompt)

    #rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain) # - this works but adds a call to the LLM for context 
    pain_rag_chain = create_retrieval_chain(vectorstore_faiss_aws.as_retriever(), question_answer_chain) # - this works but adds a call to the LLM for context 

    #- Wrap the rag_chain with RunnableWithMessageHistory to automatically handle chat history:

    pain_retriever_chain = RunnableWithMessageHistory(
        pain_rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    return pain_rag_chain
 

def create_book_cancel_agent():

    @tool ("book_appointment")
    def book_appointment(date: str, time:str) -> dict:
        """Use this function to book an appointment. This function needs date and time as a string to books the appointment with the doctor. This function returns the booking id back which you must send to the user"""

        print(date, time)
        return {"status" : True, "date": date, "booking_id": "id_123"}
        
    @tool ("cancel_appointment")
    def cancel_appointment(booking_id: str) -> dict:
        """Use this function to cancel the appointment. This function needs a booking id to cancel the appointment with the doctor. This function returns the status of the booking and the booking id which you must return back to the user """

        print(booking_id)
        return {"status" : True, "booking_id": booking_id}

    @tool ("need_more_info")
    def need_more_info() -> dict:
        """Use this function to get more information from the user.  This function returns the date and time needed for the booking of appointment """

        return {"date": "August 11, 2024", "time": "11:00 am"}

    # BOTH prompt templates work -- 

    prompt_template_sys = """

    Use the following format:
    Question: the input question you must answer
    Thought: you should always think about what to do, Also try to follow steps mentioned above
    Action: the action to take, should be one of [ "book_appointment", "cancel_appointment"]
    Action Input: the input to the action\nObservation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Question: {input}

    Assistant:
    {agent_scratchpad}'

    """
    messages=[
        SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['agent_scratchpad', 'input'], template=prompt_template_sys)), 
        HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template='{input}'))
    ]

    chat_prompt_template = ChatPromptTemplate(
        input_variables=['agent_scratchpad', 'input'], 
        messages=messages
    )
    #print_ww(f"\nCrafted::prompt:template:{chat_prompt_template}")


    prompt_template_sys = """

    Use the following format:
    Question: the input question you must answer. 
    Thought: you should always think about what to do, Also try to follow steps mentioned above. If you need information do not make it up but return with "need_more_info"
    Action: the action to take, should be one of [ "book_appointment", "cancel_appointment", "need_more_info"]
    Action Input: the input to the action\nObservation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    """

    chat_prompt_template = ChatPromptTemplate.from_messages(
            messages = [
                ("system", prompt_template_sys),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
    )

    #print_ww(f"\nCrafted::prompt:template:{chat_prompt_template}")

    modelId = "anthropic.claude-3-sonnet-20240229-v1:0" 

    model_parameter = {"temperature": 0.0, "top_p": .5, "max_tokens_to_sample": 200}
    chat_bedrock_appointment = ChatBedrock(
        model_id=modelId,
        client=boto3_bedrock,
        model_kwargs=model_parameter, 
        beta_use_converse_api=True
    )


    tools_list_book = [ book_appointment, cancel_appointment, need_more_info]

    # Construct the Tools agent
    book_cancel_agent_t = create_tool_calling_agent(chat_bedrock_appointment, tools_list_book,chat_prompt_template)
    
    #return book_cancel_agent_t
    agent_executor_t = AgentExecutor(agent=book_cancel_agent_t, tools=tools_list_book, verbose=False, max_iterations=5, return_intermediate_steps=False)
    return book_cancel_agent_t, agent_executor_t

    


def extract_chat_history(chat_history):
    user_map = {'human':'user', 'ai':'assistant'}
    if not chat_history:
        chat_history = [] #InMemoryChatMessageHistory()
    
    messages_list=[{'role':user_map.get(msg.type), 'content':[{'text':msg.content}]} for msg in chat_history]
    return messages_list

def ask_doctor_advice(prompt_str,boto3_bedrock, chat_history=None ): # this modifies this list
    modelId = "meta.llama3-8b-instruct-v1:0"

    if not chat_history:
        chat_history = [] #InMemoryChatMessageHistory()
    chat_history.append(HumanMessage(content=prompt_str))
  
    messages_list=extract_chat_history(chat_history)

  
    response = boto3_bedrock.converse(
        messages=messages_list,
        modelId=modelId,
        inferenceConfig={
            "temperature": 0.5,
            "maxTokens": 100,
            "topP": 0.9
        }
    )
    response_body = response['output']['message']['content'][0]['text']
    return response_body

def ask_doctor_advice(prompt_str,boto3_bedrock, chat_history ): # this modifies this list and prompt_str is ignored
    modelId = "meta.llama3-8b-instruct-v1:0"

    if not chat_history:
        chat_history = [] #InMemoryChatMessageHistory()

  
 
    response = boto3_bedrock.converse(
        messages=chat_history,
        modelId=modelId,
        inferenceConfig={
            "temperature": 0.5,
            "maxTokens": 100,
            "topP": 0.9
        }
    )
    response_body = response['output']['message']['content'][0]['text']
    return response_body


members = ["book_cancel_agent","pain_retriever_chain","ask_doctor_advice" ]
#members = ["book or cancel an appointment","ask a question about pain medication","Ask a medical advice" ]
#print(members)
options = ["FINISH"] + members

def create_supervisor_agent():


    prompt_finish_template_simple = """
    Given the conversation below who should act next?
    1. To book or cancel an appointment return 'book_cancel_agent'
    2. To answer questin about pain medications return 'pain_retriever_chain'
    3. To answer question about any medical issue return 'ask_doctor_advice'
    4. If you have the answer return 'FINISH'
    Or should we FINISH? ONLY return one of these {options}. Do not explain the process.Select one of: {options}
    
    {history_chat}
    
    Question: {input}

    """
    model_parameter = {"temperature": 0.0, "top_p": .5, "max_tokens_to_sample": 200}
    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
    supervisor_llm = ChatBedrock(
        model_id=modelId,
        client=boto3_bedrock,
        beta_use_converse_api=True
    )

    supervisor_chain_t = (
        #{"input": RunnablePassthrough()}
        RunnablePassthrough()
        | ChatPromptTemplate.from_template(prompt_finish_template_simple)
        | supervisor_llm
        | ToolsAgentOutputParser() #StrOutputParser()
    )
    return supervisor_chain_t




def extract_chat_history(chat_history):
    user_map = {'human':'user', 'ai':'assistant'}
    if not chat_history:
        chat_history = [] #InMemoryChatMessageHistory()
    
    messages_list=[{'role':user_map.get(msg.type), 'content':[{'text':msg.content}]} for msg in chat_history]
    return messages_list

# The agent state is the input to each node in the graph
class GraphState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next_node' field indicates where to route to next
    next_node: str
    #- initial user query
    user_query: str
    #- # instantiate memory
    convo_memory: InMemoryChatMessageHistory
    # - options for the supervisor agent to decide which node to follow
    options: list
    #- session id for the supervisor since that is another option for managing memory
    curr_session_id: str 

def input_first(state: GraphState) -> Dict[str, str]:
    print_ww(f"""start input_first()....::state={state}::""")
    init_input = state.get("user_query", "").strip()

    # store the input and output
    #- # instantiate memory since this is the first node
    #convo_memory = ConversationBufferMemory(human_prefix="\nHuman", ai_prefix="\nAssistant", return_messages=False) # - get it as a string
    convo_memory =  InMemoryChatMessageHistory()
    convo_memory.add_user_message(init_input)
    #convo_memory.chat_memory.add_ai_message(ai_output.strip())
    
    options = ['FINISH', 'book_cancel_agent', 'pain_retriever_chain', 'ask_doctor_advice'] 

    return {"user_query":init_input, "options": options, "convo_memory": convo_memory}

def agent_node(state, final_result, name):
    result = {"output": f"hardcoded::Agent:name={name}::"} #agent.invoke(state)
    #- agent.invoke(state)
    
    init_input = state.get("user_query", "").strip()
    #state.get("convo_memory").add_user_message(init_input)
    state.get("convo_memory").add_ai_message(final_result) #f"SageMaker clarify helps to detect bias in our ml programs. There is no further information needed.")#result.return_values["output"])

    print(f"\nAgentNode:state={state}::return:result={final_result}:::returning END now\n")
    return {"next_node": END, "answer": final_result}

def retriever_node(state: GraphState) -> Dict[str, str]:
    global pain_rag_chain
    print_ww(f"use this to go the retriever way to answer the question():: state::{state}")
    #agent_return = retriever_agent.invoke()
    
    init_input = state.get("user_query", "").strip()
    chat_history = extract_chat_history(state.get("convo_memory").messages)
    if pain_rag_chain == None:
        pain_rag_chain = create_retriever_pain()    
    #- Use this tool to get the context for any questions to be answered for pain or medical issues or aches or headache or any body pain"
    result = pain_rag_chain.invoke(
        {"input": init_input, "chat_history": chat_history},
    )
    return agent_node(state, result['answer'], 'pain_retriever_chain')


def doctor_advice_node(state: GraphState) -> Dict[str, str]:
    print_ww(f"use this to answer about the Doctors advice from FINE TUNED Model::{state}::")
    #agent_return = react_agent.invoke()
    chat_history = extract_chat_history(state.get("convo_memory").messages)
    init_input = state.get("user_query", "").strip()
    result = ask_doctor_advice(init_input, boto3_bedrock, chat_history) 
    return agent_node(state, result, name="ask_doctor_advice")

def book_cancel_node(state: GraphState) -> Dict[str, str]:
    global book_cancel_agent, agent_executor_book_cancel
    print_ww(f"use this to book or cancel an appointment::{state}::")
    #agent_return = react_agent.invoke()
    init_input = state.get("user_query", "").strip()
    if book_cancel_agent == None:
        book_cancel_agent, agent_executor_book_cancel = create_book_cancel_agent()
    
    result = agent_executor_book_cancel.invoke(
        {"input": init_input, "chat_history": state.get("convo_memory").messages}, return_only_outputs=True,
        config={"configurable": {"session_id": "session_1"}}
    ) # ['text']
    ret_val = result['output'][0]['text'] #- ['output'][0]['text']
    try:
        ret_val = ret_val[ret_val.index('Final Answer:'):]
    except:
        print(traceback.format_exc())
    return agent_node(state, ret_val, name="book_cancel_agent")


def error(state: GraphState) -> Dict[str, str]:
    print_ww(f"""start error()::state={state}::""")
    return {"final_result": "error", "first_word": "error", "second_word": "error"}

def supervisor_node(state: GraphState) -> Dict[str, str]:
    global supervisor_wrapped_chain
    print_ww(f"""supervisor_node()::state={state}::""") #agent.invoke(state)
    #-  
    init_input = state.get("user_query", "").strip()
    options = state.get("options", ['FINISH', 'book_cancel_agent', 'pain_retriever_chain', 'ask_doctor_advice']  )

    convo_memory = state.get("convo_memory")
    print(f"\nsupervisor_node():History of messages so far :::{convo_memory.messages}\n")

    curr_sess_id = state.get("curr_session_id", "tmp_session_1")
    
    if supervisor_wrapped_chain == None:
        supervisor_wrapped_chain = create_supervisor_agent()
    
    result = supervisor_wrapped_chain.invoke({
        "input": init_input, 
        "options": options, 
        "history_chat": extract_chat_history(convo_memory.messages)
    })

    print_ww(f"\n\nsupervisor_node():result={result}......\n\n")

    # state.get("convo_memory").chat_memory.add_user_message(init_input)
    #state.get("convo_memory").add_ai_message(result.return_values["output"])

    return {"next_node": result.return_values["output"]}

def create_graph():

    print("\n Creating the graph........\n")
    workflow = StateGraph(GraphState)
    workflow.add_node("pain_retriever_chain", retriever_node)
    workflow.add_node("ask_doctor_advice", doctor_advice_node)
    workflow.add_node("book_cancel_agent", book_cancel_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("init_input", input_first)
    print(workflow)

    members = ['pain_retriever_chain', 'ask_doctor_advice', 'book_cancel_agent', 'init_input'] 

    print_ww(f"members of the nodes={members}")


    # for member in members:
    #     # We want our workers to ALWAYS "report back" to the supervisor when done
    #     workflow.add_edge(member, "supervisor")
        
    #workflow.add_edge("supervisor", 'init_input')

    # The supervisor populates the "next" field in the graph state which routes to a node or finishes
    conditional_map = {k: k for k in members}
    conditional_map["FINISH"] = END
    workflow.add_conditional_edges("supervisor", lambda x: x["next_node"], conditional_map)

    #- add end just for all the nodes  --
    #workflow.add_edge("weather_search", END)
    for member in members[:-1]: # - EACH node --- > to END 
        workflow.add_edge(member, END)

    #- entry node to supervisor
    workflow.add_edge("init_input", "supervisor")

    # Finally, add entrypoint
    workflow.set_entry_point("init_input")# - supervisor")

    graph = workflow.compile()
    graph.get_graph().print_ascii()

    return graph

## - Create the graph
pain_rag_chain = None
supervisor_wrapped_chain =  None
book_cancel_agent, agent_executor_book_cancel = None, None
#graph = None

import traceback
def init_session():
    #print(st.session_state)
    if 'graph' not in st.session_state:
        st.session_state.graph = create_graph()
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if 'doctor_messages' not in st.session_state:
        st.session_state.doctor_messages = []

def generate_text(payload):
    graph = st.session_state.graph
    try:
        result = graph.invoke(
            {"user_query": payload, "recursion_limit": 2, "curr_session_id": "session_1"},
        )
    except:
        result = traceback.format_exc()

    result_debug = f"final result.....{result}....."
    return result

def recreate_graph():
    print("\nRECREATET -- GRAPH - drop down -- why !!\n")
    st.session_state.graph = create_graph()
    st.session_state.messages = []
    st.session_state.doctor_messages=[]
    #pass


init_session()



col1, mid, col2 = st.columns([1,1,1])
with col1:
    st.image('./images/ml_image.png', width=300)
with col2:
    st.write('What would you like help on today?')
#st.image('/Users/rsgrewal/conda/streamlit_py/ml_image.jpg', width=300)
st.header("Virtual Clinic")


length = 50  # max length variation

st.sidebar.button(label="Clear...", on_click=recreate_graph, type="primary")

# End Point names
endpoint_name_radio = st.sidebar.selectbox(
    "Select your request",
    (
        'OTHER',
        'VIRTUAL-DOCTOR'
    ),
    #on_change=recreate_graph(),
)

# Sidebar title
st.sidebar.title("Model Parameters")

# Length control
length_choice = st.sidebar.select_slider("Length",
                                         options=['very short', 'short', 'medium', 'long', 'very long'],
                                         value='medium',
                                         help="Length of the model response")

# early_stopping
early_stopping = st.sidebar.selectbox("Early Stopping", ('True', 'False'))

# Temperature control
temp = st.sidebar.slider("Creativity/Temperature", min_value=0.0, max_value=1.5, value=0.6,
                         help="The creativity of the model")

# Repetition penalty control
rep_penalty = st.sidebar.slider("Repetition penalty", min_value=0.9, max_value=2.0, value=1.1,
                                help="Penalises the model for repition")

#  Max length
# max_length = st.sidebar.text_input("Max length", value="50", max_chars=2)
max_length = {'very short': 10, 'short': 20, 'medium': 30, 'long': 40, 'very long': 50}

dict_endpoint = {
    "VIRTUAL-DOCTOR": "ask_doctor_advice",
    "OTHER": "OTHER",

}

st.markdown("""
**:blue[You can ask this chat-bot for any help with the Clinic , few examples below.]**\n\n
Text: what are the effecs of Asprin?\n
Text: what is the general function of a doctor, what do they do?\n
Text: Can you book an appointment for me?\n
Text: Can you book an appointment for Sept 02, 2024 10 am?\n
Text: How do pain killer work in medical terms\n
""")

t_out = st.container(height=500)

def run_virtual_doctor(prompt):
    #if st.button("Run"):

    print(f"\n RUN:run_virtual_doctor........endpoint_name_radio={endpoint_name_radio}::prompt={prompt}::{st.session_state.doctor_messages}\n")

    ai_response = ""
    try:
        user_map = {'user':'user', 'assistant':'assistant'}
        messages_list=[{'role':user_map.get(msg['role']), 'content':[{'text':msg['content']}]} for msg in st.session_state.doctor_messages]
        messages_list.append({'role':'user', 'content':[{'text':prompt}]})
        ai_response = ask_doctor_advice(prompt, boto3_bedrock, messages_list)
    except:
        print(ai_response)
        print(traceback.format_exc())
        ai_response = "Error from System"

    #st.write(generated_text)
    with t_out:
        # Display chat messages from history on app rerun
        for message in st.session_state.doctor_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            st.markdown(ai_response)

    st.session_state.doctor_messages.append({"role": "user", "content": prompt}) # move it here for question
    st.session_state.doctor_messages.append({"role": "assistant", "content": ai_response })


def run_prompt(prompt):
    #if st.button("Run"):

    print(f"\n RUN........endpoint_name_radio={endpoint_name_radio}::prompt={prompt}::\n")

    #if endpoint_name_radio == 'VIRTUAL-DOCTOR':

    generated_text = generate_text(prompt)
    #print(generated_text)

    try:
        ai_response = generated_text['convo_memory'].messages[-1].content
    except:
        print(generated_text)
        print(traceback.format_exc())
        ai_response = "Error from System"

    #st.write(generated_text)
    with t_out:
        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            st.markdown(ai_response)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": ai_response })



#prompt = st.text_area(label='Enter Prompt', key='mlprompt', placeholder="Enter your prompt here:", height=350)
if prompt := st.chat_input(key='mlprompt', placeholder="Enter your prompt here:"):
    print(endpoint_name_radio)
    if endpoint_name_radio == 'VIRTUAL-DOCTOR':
        run_virtual_doctor(prompt)
    else:
        run_prompt(prompt)






 