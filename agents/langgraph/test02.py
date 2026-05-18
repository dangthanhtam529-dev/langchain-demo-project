from typing import Annotated
from typing_extensions import TypedDict
from operator import add
from langgraph.graph import StateGraph, START, END

class OverallState(TypedDict):
   name: str
   log: Annotated[list[dict[str, str]], add]  

# 定义节点
def node_1(state: OverallState):
    print(f"node_1节点接收状态: {state}")
    return {"log": [{"role": "ai", "content": "hello world"}]}
   
def node_2(state: OverallState):  
    print(f"node_2节点接收状态: {state}")
    return {"log": [{"role": "user", "content": "hi!"}]}

def node_3(state: OverallState):
    print(f"node_3节点接收状态: {state}") 
    return {"log": [{"role": "ai", "content": "hi!"}]}

graph = StateGraph(OverallState)
graph.add_node(node_1)
graph.add_node(node_2)
graph.add_node(node_3)
graph.add_edge(START, "node_1")
graph.add_edge("node_1", "node_2")
graph.add_edge("node_2", "node_3")
graph.add_edge("node_3", END)
graph = graph.compile()

result = graph.invoke({"name": "test", "log": []})
print(result)