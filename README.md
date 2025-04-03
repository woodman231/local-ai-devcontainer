# Local AI Development Stack
This is just a sample library showing how to do AI applications locally.

This dev container uses the following images for the various services

- [Python:3.13.2-slim](https://hub.docker.com/layers/library/python/3.13.2-slim/images/sha256-cdd05847ea468adac731f07eebdd700920cdba58caca6ef25bf8fa8261eb26fc)
- [chromadb/chroma:latest](https://hub.docker.com/r/chromadb/chroma)
- [ollama/ollama:0.6.3](https://hub.docker.com/layers/ollama/ollama/0.6.3/images/sha256-3357d9dbb374fd82ee59e2fa47e3935e48bed3dd0bad8291374700cb66fe7232)
- [postgres:16.2-alpine3.19](https://hub.docker.com/layers/library/postgres/16.2-alpine3.19/images/sha256-8e50de55645e01728c523ab17dbf3c2f61f68bc3a8d73c86a6c55509a2bc4a22)

Python is the most popular AI development language
Chromadb is an up and coming vector database which is greate for RAG AI applications.
Ollama is by far the easiest way to run an LLM locally
PostgreSQL in case you need it for other non-vector data needs

Ollama provides exerimental compatibility with the OpenAI API, so some features might be limited. Also if you want to test out function calling you must use at least ollama3.2 for the llm runner

The computer that this was initially developd on has an NVIDIA GPU on windows and required WSL Installation with Docker integration and NVIDIA Container Toolkit installed in the WSL environment.

Link to Microsoft documentation on WSL installation: https://learn.microsoft.com/en-us/windows/wsl/install

Link to NVIDIA documentation on installing NVIDIA COntainer Toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installation

If only using a CPU that is ok. Comment out the "deploy" key from the ollama service in docker-compose.yml

I.E.
```yaml
  ollama:
    image: ollama/ollama:0.6.3
    container_name: ollama    
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: all
    #           capabilities: [gpu]
```

Out of the box this dev container will run chromadb on port 8001, ollama on port 11434 and postgres on 5432 and can be accessed by the service name in docker-compose

I.E.: ollama:11434, chroma:8000, postgres:5432

Examples of chunking, indexing, querying the index, and querying the LLM are included in this repository

The examples are mostly based on this tutorial from Microsoft: https://learn.microsoft.com/en-us/azure/search/tutorial-rag-build-solution

The key differences here is that instead of the index being in Azure Cognative Search, the index is in the ChromaDB. Instead of creating an Indexer, the logic in the application is used to chunk, and embed the documents, then save the embeddings to the ChromaDB index. These examples show getting the embeddings from an ollama embedding end point, but there is an embedding method available in the chromadb package so that could be used instead if you prefer. 

To get started with the examples you can download their sample PDFs from here https://github.com/Azure-Samples/azure-search-sample-data/tree/main/nasa-e-book/earth_book_2019_text_pages and copy them to the "docs1" folder in this repository on your computer. The samples should work right away.

Alternatively you can save other PDFs to the docs1 folder and change the query_text for a question relevant to the documents that you uploaded. You can also save the files to other folders and be sure to update the appropriate code to point to a folder name that is more friendly for you.
