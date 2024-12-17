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
         FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),  # 论文标题
         FieldSchema(name="authors", dtype=DataType.VARCHAR, max_length=500),  # 论文作者
         FieldSchema(name="categories", dtype=DataType.VARCHAR, max_length=200),  # 论文分类
         FieldSchema(name="doi", dtype=DataType.VARCHAR, max_length=200),  # 论文 DOI
         FieldSchema(name="journal_ref", dtype=DataType.VARCHAR, max_length=500),  # 期刊引用
         FieldSchema(name="comments", dtype=DataType.VARCHAR, max_length=500),  # 论文评论
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
         collection = Collection(name=collection_name)
         print(f"集合 {collection_name} 已存在！")
     ```

4. 加载嵌入模型

   + ```python
     embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")
     ```

5. 加载arxiv数据集并处理

   + ```python
     with open("arxiv-metadata-oai-snapshot.json", "r") as read_file:
         data = [json.loads(line) for line in read_file]
     
     vectors = []
     ids = []
     titles = []
     authors = []
     categories = []
     dois = []
     journal_refs = []
     comments = []
     texts = []
     
     for item in data:
         abstract = item.get("abstract", "")  # 论文摘要
         vector = embedding_model.encode(abstract).tolist()  # 生成向量
         vectors.append(vector)
         ids.append(item.get("id", ""))
         titles.append(item.get("title", ""))
         authors.append(", ".join([", ".join(author) for author in item.get("authors_parsed", [])]))  # 合并作者
         categories.append(item.get("categories", ""))
         dois.append(item.get("doi", ""))
         journal_refs.append(item.get("journal-ref", ""))
         comments.append(item.get("comments", ""))
         texts.append(abstract)
         print(item.get("id", "")+"已读取")
     ```

6. 数据插入milvus、创建索引后将数据持久化

   + ```python
     entities = [
         ids,  # 论文 ID
         vectors,  # 向量
         titles,  # 论文标题
         authors,  # 论文作者
         categories,  # 论文分类
         dois,  # 论文 DOI
         journal_refs,  # 期刊引用
         comments,  # 论文评论
         texts,  # 论文摘要
     ]
     
     collection.insert(entities)
     print(f"数据已成功插入到集合 {collection_name} 中！")
     
     创建索引（加速查询）
     index_params = {
         "index_type": "IVF_FLAT",
         "metric_type": "L2",
         "params": {"nlist": 128},
     }
     collection.create_index("vector", index_params)
     print("索引创建成功！")
     
     9. 持久化数据
     collection.load()
     print("集合已加载到内存中！")
     ```

### 基于arxiv数据集的RAG问答系统

#### 用户查询优化

```python
# 提示优化函数
def refine_query(user_input):
    prompt = f"""
    Please polishing the following query to better find relevant academic paper abstracts:
    user question：{user_input}
    polished question：
    """
    refined_query = llm_completion(prompt)
    return refined_query
```

#### 迭代式查询

```python
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
```
