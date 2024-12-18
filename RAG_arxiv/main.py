import json

from langchain.llms import OpenAI, OpenAIChat
import os

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Milvus
from pymilvus import connections, Collection, utility
# 打印所有集合的名称

connections.connect(host="10.58.0.2", port="19530")

collections = utility.list_collections()
print("Available collections:", collections)

# 获取特定集合的详细信息
collection_name = "arXiv"
if collection_name in collections:
    collection = Collection(collection_name)
    print("Collection details for", collection_name)
    print("Schema:", collection.schema)
    print("Fields:", collection.schema.fields)
    print("Num entities:", collection.num_entities)
else:
    print(f"Collection '{collection_name}' does not exist.")
## 初始化环境变量
os.environ["OPENAI_API_KEY"] = "None"
os.environ["OPENAI_API_BASE"] = "http://10.58.0.2:8000/v1"
os.environ["http_proxy"] = "http://127.0.0.1:7897"
os.environ["https_proxy"] = "http://127.0.0.1:7897"
## 初始化要用的模型
llm_completion = OpenAI(model_name="Qwen2.5-14B")
llm_chat = OpenAIChat(model_name="Qwen2.5-14B")

## 导入嵌入模型
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")
## 创建Milvus数据库
db = Milvus(embedding_function=embedding, collection_name="arXiv",connection_args={"host": "10.58.0.2", "port": "19530"})
# 提示优化函数
def refine_query(user_input):
    prompt = f"""
        Please polishing the following query to better find relevant academic paper abstracts:
        user question：{user_input}
        polished question：
        """
    refined_query = llm_completion(prompt)
    return refined_query

# 查询迭代函数
def query_iteration(user_input, max_iter=3):
    refined_query = refine_query(user_input)
    for i in range(max_iter):
        # 检索最相关的摘要
        results = db.similarity_search(refined_query, k=3)
        if results:
            # 生成回答
            answer = llm_chat(f"Based on the following paper abstract, answer the question: {refined_query}\n摘要：{results[0].page_content}")
            return answer, results[0]
        else:
            refined_query = refine_query(refined_query)  # 重新润色
    return "未找到相关答案", None

def answer_question(question_path, answer_path):
    with open(question_path, "r", encoding="utf-8") as f:
        question_list = json.load(f)

    for item in question_list:
        question = item.get("question")
        if question is None:
            continue
        answer, reference_orig = query_iteration(question)
        item['answer'] = answer
        item['reference_orig'] = reference_orig

    with open(answer_path, "w", encoding="utf-8") as f:
        json.dump(question_list, f, ensure_ascii=False)


def main():
    print("欢迎使用 arXiv 知识问答系统！输入问题以开始。")
    print(db)

    while True:
        user_input = input("用户：")
        if user_input.lower() in ["退出", "exit"]:
            break
        answer, source = query_iteration(user_input)
        print(f"系统：{answer}")
        if source:
            print(f"信息来源：{source.metadata['title']} (https://arxiv.org/abs/{source.metadata['access_id']})")
if __name__ == "__main__":
    main()
# if __name__ == "__main__":
#     question_path = "./questions.jsonl"
#     answer_path = "./answers.json"
#     answer_question(question_path, answer_path)