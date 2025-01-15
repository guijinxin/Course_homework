# RAG_arxiv
基于arxiv网站论文数据库的知识问答系统

### load arxiv dataset

1. 连接数据库

   + ```python
     connections.connect(host="10.58.0.2", port="19530")
     ```

2. 定义向量数据库架构

   + ```python
    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=50, is_primary=True),  # 论文的唯一标识符
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384),  # 向量维度（与嵌入模型匹配）
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=5000),  # 论文摘要（必须命名为 text）
    ]
     schema = CollectionSchema(fields, "arXiv 数据集")
     ```

3. 创建集合

   + ```python
    collection_name = "arXiv"
    if collection_name not in utility.list_collections():
        collection = Collection(name=collection_name, schema=schema)
        print(f"集合 {collection_name} 创建成功！")
    else:
        # Drop the existing collection
        collection = Collection(name=collection_name)
        collection.drop()
        print(f"集合 {collection_name} 已删除！")
        collection = Collection(name=collection_name, schema=schema)
        print(f"集合 {collection_name} 创建成功！")
     ```

4. 加载嵌入模型

   + ```python
     embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")
     ```

5. 加载arxiv数据集并处理

   + ```python
     with open("/home/gjx/.cache/kagglehub/datasets/Cornell-University/arxiv/versions/210/arxiv-metadata-oai-snapshot.json", "r") as read_file:
    data = [json.loads(line) for line in read_file]
    #data = json.load(read_file)
    batch_size = 10000
    records = []
    for item in data:
        abstract = item.get("abstract", "unknown")  # 论文摘要
        if abstract is None:
            abstract = "unknown"
        elif len(abstract) > 5000:
            print(f"Abstract length exceeds 5000 characters: {len(abstract)}")
            abstract = abstract[:5000] 
        vector = embedding_model.encode(abstract).tolist()  # 生成向量
        record = {
            "id": item.get("id", "unknown"),
            "vector": vector,
            "text": abstract,
        }
        records.append(record)

        #批量插入数据
        if len(records) == batch_size:
            collection.insert(records)
            print(f"数据已成功插入到集合 {collection_name} 中！")
            records = []

    if len(records) > 0:
        collection.insert(records)      
     ```

6. 数据插入milvus、创建索引后将数据加载到内存中

   + ```python
    index_params = {
    "index_type": "IVF_FLAT",
    "metric_type": "L2",
    "params": {"nlist": 128},
    }
    collection.create_index("vector", index_params)
    print("索引创建成功！")

    collection.load()
    print("集合已加载到内存中！")
     ```

### 基于arxiv数据集的RAG问答系统

#### 用户查询优化

```python
# 提示优化函数
def refine_query(user_input):
    prompt = f"""
        Please refine the question description to better align with the data in the vector database by incorporating more keywords relevant to the question's topic, facilitating the identification of the most relevant academic papers:        
        user question: {user_input}
        refined question:
        Note: Only return the refined question without any additional explanation.
        """
    refined_query = llm_completion.invoke([HumanMessage(content=prompt)])
    return refined_query
```

#### 迭代式查询

```python
# 查询迭代函数
def query_iteration(user_input, max_iter=3):
    refined_query = user_input
    print(refined_query)
    for i in range(max_iter):
        # 检索最相关的摘要
        results = db.similarity_search(refined_query, k=5)
        print(results)
        if results:
            # 生成回答
            answer = llm_completion.invoke([HumanMessage(content=f"Based on the following paper abstract, answer the question: {user_input}\nabstract:{results[0].page_content}.\n")])
            return answer, results[0]
        else:
            refined_query = refine_query(user_input)  # 重新润色
    return "未找到相关答案", None
```
