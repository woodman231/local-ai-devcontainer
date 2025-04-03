import os
import asyncio
from typing import List
from chromadb import chromadb, AsyncClientAPI
from nltk.tokenize import sent_tokenize
import pymupdf4llm
from uuid import uuid4
from base64 import b64encode
import nltk
nltk.download('punkt_tab')
from pdftitle import get_title_from_file, GetTitleParameters
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionUserMessageParam 

async def main():    
    chroma_client = await chromadb.AsyncHttpClient(host="chroma", port=8000)    
    ollama_openai_client: AsyncOpenAI = AsyncOpenAI(
        api_key="ollama",
        base_url="http://ollama:11434/v1",
    )
    
    await delete_all_collections(chroma_client)

    pdf_files = get_pdf_files_in_folder("/workspace/docs1")    
    collection = await chroma_client.create_collection(name="pdf_files")

    files_processed = 0

    for pdf_file_path in pdf_files:
        print(f"Processing file: {pdf_file_path}")
        pdf_file_name = os.path.basename(pdf_file_path)
        file_id = b64encode(pdf_file_path.encode("utf-8")).decode("utf-8")
        pdf_title = get_pdf_title(pdf_file_path)
        metadata = {"file_id": file_id, "file_name": pdf_file_name, "title": pdf_title}
        markdown = get_markdown_from_pdf(pdf_file_path)
        chunks = split_document(markdown)        
        
        for chunk in chunks:            
            response = await ollama_openai_client.embeddings.create(
                model="mxbai-embed-large",
                input=chunk,
            )
            print(f"Embedding Response: {response}")

            embeddings = response.data[0].embedding

            await collection.add(
                documents=[chunk],
                metadatas=[metadata],
                embeddings=embeddings,
                ids=[str(uuid4())],
            )
        files_processed += 1

    print(f"Processed {files_processed} files.")

    documents_count = await collection.count()
    print(f"Total documents in collection: {documents_count}")
    
    query_text = "What's the NASA earth book about?"    
    embedded_query_text = await ollama_openai_client.embeddings.create(
        model="mxbai-embed-large",
        input=query_text,
    )
    embedded_query_text = embedded_query_text.data[0].embedding

    results = await collection.query(
        query_texts=[query_text],
        query_embeddings=embedded_query_text,
        n_results=5,
    )
    print(f"Query results for '{query_text}':")
    print(results)

    GROUNDED_PROMPT="""
    You are an AI assistant that helps users learn from the information found in the source material.
    Answer the query using only the sources provided below.
    Use bullets if the answer has multiple points.
    If the answer is longer than 3 sentences, provide a summary.
    Answer ONLY with the facts listed in the list of sources below. Cite your source when you answer the question
    If there isn't enough information below, say you don't know.
    Do not generate answers that don't use the sources below.
    Query: {query}
    Sources:\n{sources}
    """

    source_title_contents = []
    for index, document in enumerate(results["documents"]):
        target_meta = results["metadatas"][0][index]
        title = target_meta["title"]
        content = document[0]

        source_title_contents.append({ "title": title, "content": content })

    sources_formatted = "=================\n".join(
        [f"Title: {source['title']}\nContent: {source['content']}" for source in source_title_contents]
    )    
    
    try:         
        response = await ollama_openai_client.chat.completions.create(
            model="llama3",
            messages=[ChatCompletionUserMessageParam(role="user", content=GROUNDED_PROMPT.format(
                query=query_text,
                sources=sources_formatted,
            ))],
            stream=True,
            temperature=0.7,            
        )
        async for chunk in response:            
            print(chunk.choices[0].delta.content, end='', flush=True)
        print("\n\n")

    except Exception as e:
        print(f"Error during Ollama API call: {e}")


async def delete_one_collection(client: AsyncClientAPI, collection_name: str):
    # Delete a collection
    await client.delete_collection(name=collection_name)
    print(f"Deleted collection: {collection_name}")

async def delete_all_collections(client: AsyncClientAPI):
    collection_names = await client.list_collections()
    for name in collection_names:
        await delete_one_collection(client, name)

def split_document(document, max_length=512):
    sentences = sent_tokenize(document)
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence.split())
        if current_length + sentence_length > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(sentence)
        current_length += sentence_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def get_markdown_from_pdf(pdf_path):
    return pymupdf4llm.to_markdown(pdf_path)

def get_pdf_title(pdf_path):
    return get_title_from_file(pdf_file=pdf_path, params=GetTitleParameters(                
    ))

def get_pdf_files_in_folder(folder_path):
    file_names: List[str] = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".pdf"):
                file_names.append(os.path.join(root, file))
    return file_names

asyncio.run(main())
