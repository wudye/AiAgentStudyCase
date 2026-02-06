检索增强生成（Retrieval-Augmented Generation, RAG） 是一种通过整合外部知识库来优化大型语言模型（LLM）输出的技术。它让模型在生成回答之前，先像查阅“参考书”一样从可靠的数据源中检索相关信息，从而提供更准确、更及时的内容。 
IBM Research
IBM Research
 +2
以下是 RAG 的核心解析：
1. 核心工作原理
RAG 的过程可以形象地比作“开卷考试”： 
IBM Research
IBM Research
检索 (Retrieval)： 系统根据用户的提问，在外部文档、数据库或互联网中搜索最相关的片段。
增强 (Augmentation)： 将检索到的事实与原始问题结合，形成一个更丰富的“提示词”（Prompt）发送给大模型。
生成 (Generation)： 模型利用这些补充信息来撰写回答，确保答案基于事实而非仅凭记忆。 
IBM Research
IBM Research
 +2
2. 为什么需要 RAG？
它解决了传统大模型（如 GPT、Claude）的三个关键痛点：
消除“幻觉”： 模型不再一本正经地胡说八道，而是基于引用的真实来源回答。
提供实时信息： 模型不需要重新训练就能获取最新的新闻、研究或企业内部数据。
数据安全与隐私： 企业可以将私有文档存在自己的数据库中，让模型通过 RAG 调用而无需将敏感数据传给 AI 厂商进行微调。 
Amazon Web Services (AWS)
Amazon Web Services (AWS)
 +2