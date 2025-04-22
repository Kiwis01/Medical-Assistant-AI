medical_rag_assistant/
│
├── agents/                     # All specialized medical agents
│   ├── base_agent.py
│   ├── cardiology_agent.py
│   ├── neurology_agent.py
│   └── dermatology_agent.py
│
├── retrieval/                  # RAPTOR & Vector Search logic
│   ├── base_retriever.py
│   ├── qdrant_client.py
│   ├── raptor_tree.py
│   └── reranker.py
│
├── llm/                        # LLM wrapper and generation logic
│   ├── base_llm.py
│   ├── gemini.py
│   └── prompt_builder.py
│
├── data/                       # Source documents / embeddings
│   ├── loader.py
│   ├── chunker.py
│   └── preprocessor.py
│
├── api/                        # If building RESTful endpoints
│   └── main.py                 # FastAPI / Flask entry point
│
├── config/                     
│   ├── config.json             # Contains prompts, agent names, system params
│   └── config.py               # Loads config.json, exposes API keys and parameters
│
├── utils/
│   └── logger.py               # Standard logger utility
│
├── main.py                     # Core pipeline runner (e.g. console interface)
└── README.md
