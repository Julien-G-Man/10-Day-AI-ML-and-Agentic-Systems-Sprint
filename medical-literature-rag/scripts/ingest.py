import os
import time
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from llama_index.core import (
    SimpleDirectoryReader, VectorStoreIndex,
    Settings, StorageContext
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.vector_stores import Pinecone as PineconeVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI as LlamaOpenAI

load_dotenv()

PINECONE_INDEX_NAME = 'medical-literature'

print("\n====================================================================================================")
print("Ingest script running...")
print("====================================================================================================")

def configure_llama_index():
    Settings.embed_model = OpenAIEmbedding(
        model='text-embedding-3-small',
        api_key=os.getenv('OPENAI_API_KEY'),
    )
    Settings.llm = LlamaOpenAI(
        model='gpt-4o-mini',
        api_key=os.getenv('OPENAI_API_KEY'),
        temperature=0.1,
    )
    Settings.node_parser = SentenceSplitter(
        chunk_size=256,
        chunk_overlap=50,
    )


def check_current_state(stats, index_name: str):
    print(f'Pinecone index: {index_name}')
    print(f'Current vectors: {stats.total_vector_count}')


def add_metadata(documents):
    """ Add metadata to each document for citation in responses """
    for doc in documents:
        source = doc.metadata.get('file_name', 'unknown')
        doc.metadata['source'] = source
        doc.metadata['document_type'] = 'clinical_guideline'
        doc.metadata['ingested_at'] = time.strftime('%Y-%m-%d')
        print(f'  Prepared: {source}')


def verify_ingestion(stats_after, documents):
    print(f'\nIngestion complete!')
    print(f'Vectors stored: {stats_after.total_vector_count}')
    print(f'Documents: {len(documents)}')


def save_reference(index_name: str, documents, stats_after):
    """Save a reference to the index for the API to load """
    import json
    Path('configs').mkdir(exist_ok=True)
    with open('configs/index_config.json', 'w') as f:
        json.dump({
            'pinecone_index': index_name,
            'embedding_model': 'text-embedding-3-small',
            'llm_model': 'gpt-4o-mini',
            'chunk_size': 256,
            'chunk_overlap': 50,
            'num_documents': len(documents),
            'total_vectors': stats_after.total_vector_count,
        }, f, indent=2)
    print('Config saved to configs/index_config.json')


def main():
    configure_llama_index()
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    index_name = os.getenv('PINECONE_INDEX_NAME', 'medical-literature')
    pinecone_env = os.getenv("PINECONE_ENVIRONMENT")

    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region=pinecone_env
        )
    )
    print(f"Index created: {index_name}")

    pinecone_index = pc.Index(index_name)

    stats = pinecone_index.describe_index_stats()
    check_current_state(stats, index_name)

    reader = SimpleDirectoryReader('data/medical')
    documents = reader.load_data()
    print(f'Loaded {len(documents)} documents')

    add_metadata(documents)

    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print('Ingesting documents into Pinecone...')
    print('(This embeds each chunk and upserts it to Pinecone — may take 30-60 seconds)')

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
    )

    stats_after = pinecone_index.describe_index_stats()
    verify_ingestion(stats_after, documents)

    save_reference(index_name, documents, stats_after)




if __name__ == "__main__":
    main()
