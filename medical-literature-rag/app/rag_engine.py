# Core RAG logic: load index, build query engines, run queries

import os
import time
import logging
from dotenv import load_dotenv
from pinecone import Pinecone
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI as LlamaOpenAI
from .schemas import MedicalAnswer, SourceDocument

load_dotenv()
logger = logging.getLogger(__name__)

class MedicalRAGEngine:
    """
    Production-ready RAG engine for medical literature search.

    Provides two query modes:
      1. Direct query: single retrieval + generation (fast, simple questions)
      2. Sub-question decomposition: breaks complex questions into sub-questions,
         retrieves for each, synthesises (slower but more accurate for multi-hop)
    """

    def __init__(self):
        self._index = None
        self._vector_count = 0
        self._is_loaded = False

    def load(self) -> bool:
        """Load the Pinecone index and set up LlamaIndex. Called once at startup."""
        try:
            Settings.embed_model = OpenAIEmbedding(
                model='text-embedding-3-small',
                api_key=os.getenv('OPENAI_API_KEY'),
            )
            Settings.llm = LlamaOpenAI(
                model='gpt-4o-mini',
                api_key=os.getenv('OPENAI_API_KEY'),
                temperature=0.1,
            )

            pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
            pinecone_index = pc.Index(os.getenv('PINECONE_INDEX_NAME', 'medical-literature'))

            stats = pinecone_index.describe_index_stats()
            self._vector_count = stats.total_vector_count

            if self._vector_count == 0:
                logger.warning('Pinecone index is empty — run scripts/ingest.py first')
                return False

            vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
            self._index = VectorStoreIndex.from_vector_store(vector_store)

            self._is_loaded = True
            logger.info(f'RAG engine loaded: {self._vector_count} vectors')
            return True

        except Exception as e:
            logger.error(f'Failed to load RAG engine: {e}')
            return False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @property
    def vector_count(self) -> int:
        return self._vector_count

    def query(
        self,
        question: str,
        top_k: int = 3,
        use_sub_questions: bool = False,
        temperature: float = 0.1,
    ) -> MedicalAnswer:
        """
        Run a medical query against the knowledge base.

        Args:
            question: The clinical question to answer
            top_k: Number of source chunks to retrieve
            use_sub_questions: Use SubQuestionQueryEngine for complex multi-hop questions
            temperature: LLM temperature for response generation
        """
        if not self._is_loaded:
            raise RuntimeError('RAG engine not loaded. Call load() first.')

        start_time = time.time()

        Settings.llm = LlamaOpenAI(
            model='gpt-4o-mini',
            api_key=os.getenv('OPENAI_API_KEY'),
            temperature=temperature,
        )

        system_prompt = """You are a clinical decision support AI assistant.
Answer questions based ONLY on the provided context from medical guidelines.
Always cite the guideline section when possible.
If the context does not contain sufficient information to answer the question, say:
'I could not find relevant information in the available guidelines for this
question.'
Do not provide medical advice beyond what is stated in the guidelines.
Format your answer clearly with specific dosages, targets, and criteria where
relevant."""

        if use_sub_questions:
            response, source_nodes = self._sub_question_query(question, top_k, system_prompt)
        else:
            response, source_nodes = self._direct_query(question, top_k, system_prompt)

        latency_ms = (time.time() - start_time) * 1000

        sources = []
        for node in source_nodes:
            sources.append(SourceDocument(
                filename=node.metadata.get('file_name', 'unknown'),
                chunk_text=node.text[:300] + '...' if len(node.text) > 300 else node.text,
                relevance_score=round(float(node.score or 0), 4),
            ))

        return MedicalAnswer(
            answer=str(response),
            sources=sources,
            question=question,
            num_sources_used=len(sources),
            latency_ms=round(latency_ms, 1),
            model_used='gpt-4o-mini + text-embedding-3-small',
        )

    def _direct_query(self, question, top_k, system_prompt):
        """Simple retrieval → generation."""
        engine = self._index.as_query_engine(
            similarity_top_k=top_k,
            response_mode='compact',
            system_prompt=system_prompt,
        )
        response = engine.query(question)
        return response, response.source_nodes

    def _sub_question_query(self, question, top_k, system_prompt):
        """
        Multi-step query: decompose complex question into sub-questions,
        retrieve for each, synthesise into a final answer.

        Example: 'Compare malaria treatment to hypertension treatment targets'
        → Sub-question 1: 'What is malaria treatment?' → retrieve from malaria docs
        → Sub-question 2: 'What are hypertension treatment targets?' → retrieve from
HTN docs
        → Synthesise both answers into a comparative response
        """
        # Create a tool for each document type
        base_engine = self._index.as_query_engine(similarity_top_k=top_k)
        query_engine_tool = QueryEngineTool(
            query_engine=base_engine,
            metadata=ToolMetadata(
                name='medical_guidelines',
                description='Contains clinical guidelines for malaria, hypertension, and diabetes management',
            ),
        )

        sub_engine = SubQuestionQueryEngine.from_defaults(
            query_engine_tools=[query_engine_tool],
            verbose=True,  # Log the sub-questions generated
        )
        response = sub_engine.query(question)
        # Collect all source nodes from all sub-queries
        all_nodes = []
        for sr in getattr(response, 'source_nodes', []):
            all_nodes.append(sr)
        return response, all_nodes
