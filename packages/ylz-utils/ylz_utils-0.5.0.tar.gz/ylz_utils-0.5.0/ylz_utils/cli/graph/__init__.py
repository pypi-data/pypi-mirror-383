from ylz_utils.cli.graph.db_graph import DbGraph
from ylz_utils.cli.graph.engineer_graph import EngineerGraph
from ylz_utils.cli.graph.life_graph import LifeGraph
from ylz_utils.cli.graph.self_rag_graph import SelfRagGraph
from ylz_utils.cli.graph.stand_graph import StandGraph
from ylz_utils.cli.graph.test_graph import TestGraph

from ylz_utils.data import StringLib
from ylz_utils.langchain import LangchainLib
from langchain_core.messages import HumanMessage,ToolMessage

from rich.console import Console

def input_with_readline(prompt):
    try:
        return input(prompt)
    except UnicodeDecodeError:
        print("输入的内容存在编码问题，请确保使用 UTF-8 编码的字符，并不要使用回退键。")
        return input_with_readline(prompt)
    
async def start_graph(langchainLib:LangchainLib,args):
    # # 设置标准输入为 UTF-8 编码
    # sys.stdin = codecs.getreader('utf-8')(sys.stdin.detach())
    graph_key = args["graph"] or 'test'
    llm_key = args["llm_key"]
    llm_model = args["llm_model"]
    message = args["message"]
    chat_dbname = args["chat_dbname"]
    rag_indexname = args["rag_indexname"]
    query_dbname = args["query_dbname"]
    user_id = args["user_id"] or 'default'
    conversation_id = args["conversation_id"] or 'default'
    thread_id = f"{user_id}-{conversation_id}"
    websearch_key = args["websearch"]
    graphLib = None
    match graph_key:
        case "stand":
            graphLib = StandGraph(langchainLib)
        case "life":
            graphLib = LifeGraph(langchainLib)
        case "engineer":
            graphLib = EngineerGraph(langchainLib)
        case "db":
            graphLib = DbGraph(langchainLib)
        case "selfrag":
            graphLib = SelfRagGraph(langchainLib)
        case "test":
            graphLib = TestGraph(langchainLib)
        case _ :
            return
    if chat_dbname:                                  
        graphLib.set_chat_dbname(chat_dbname)
        print("!!!",f"使用对话数据库{chat_dbname}")
    if rag_indexname:
        retriever = langchainLib.vectorstoreLib.get_store_with_provider_and_indexname(rag_indexname).as_retriever()
        graphLib.set_ragsearch_tool(retriever)
        print("!!!",f"使用知识库{rag_indexname}")
    if query_dbname:
        if query_dbname=="Chinook.db":
            print(StringLib.color(
                "执行wget https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db,确保Chinook.db在当前目录。",
                ["lmagenta","underline"]))
        graphLib.set_query_dbname(query_dbname)
        print("!!!",f"使用查询数据库{query_dbname}")
    if websearch_key:
        graphLib.set_websearch_tool(websearch_key)
        print("!!!",f"使用搜索工具{websearch_key}")
    #graphLib.set_nodes_llm_config((llm_key,llm_model))
    #graphLib.set_thread(user_id,conversation_id)
    graphLib.init_graph()
    message = input("User Input: ")
    config={"configurable":{"thread_id":thread_id,
                            "user_id":user_id,
                            "llm_key":llm_key,"llm_model":llm_model}}
    await graphLib.test(message,config)
    #current_state = graphLib.get_state(config)
    #Console().print("\n本次对话的所有消息:\n",current_state.values["messages"])
    #Console().print("\n最终的状态:\n",current_state)
    #graphLib.export()
    