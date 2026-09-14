import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
from app.schemas import RecommendRequest, RecommendResponse, ProductRecommendation

load_dotenv()
logger = logging.getLogger(__name__)


class ProductRecommender:
    """
    Vector similarity-based product recommender.
    Pipeline: embed query → Pinecone ANN search → filter → rank → return
    """

    def __init__(self):
        self._openai = None
        self._index  = None
        self._ready  = False

    def load(self) -> bool:
        try:
            self._openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
            self._index = pc.Index('product-catalog')
            stats = self._index.describe_index_stats()
            if stats.total_vector_count == 0:
                logger.warning('Product index is empty — run scripts/index_products.py')
                return False
            self._ready = True
            logger.info(f'Recommender ready: {stats.total_vector_count} products indexed')
            return True
        except Exception as e:
            logger.error(f'Failed to load recommender: {e}')
            return False

    @property
    def is_ready(self) -> bool:
        return self._ready

    def recommend(self, request: RecommendRequest) -> RecommendResponse:
        """
        Find the most semantically similar products to the customer query.

        1. Embed the query text using text-embedding-3-small
        2. Query Pinecone for top-k nearest neighbours
        3. Apply optional category and price filters
        4. Return ranked recommendations
        """
        if not self._ready:
            raise RuntimeError('Recommender not loaded.')

        # ── Step 1: Embed the customer query ─────────────────────
        response = self._openai.embeddings.create(
            model='text-embedding-3-small',
            input=request.query,
        )
        query_embedding = response.data[0].embedding

        # ── Step 2: Build Pinecone metadata filter ────────────────
        # Pinecone supports filtering on metadata fields during search
        filter_dict = {}
        if request.category_filter:
            filter_dict['category'] = {'$eq': request.category_filter}
        if request.max_price_ghs:
            filter_dict['price_ghs'] = {'$lte': request.max_price_ghs}

        # ── Step 3: Query Pinecone ────────────────────────────────
        # Fetch more than needed so filters don't reduce results below top_k
        fetch_k = request.top_k * 3 if filter_dict else request.top_k

        query_result = self._index.query(
            vector=query_embedding,
            top_k=fetch_k,
            include_metadata=True,   # Return metadata stored during indexing
            filter=filter_dict if filter_dict else None,
        )

        # ── Step 4: Build recommendation objects ──────────────────
        recs = []
        for rank, match in enumerate(query_result.matches[:request.top_k], start=1):
            meta = match.metadata
            recs.append(ProductRecommendation(
                product_id=match.id,
                name=meta.get('name', 'Unknown'),
                description=meta.get('description', ''),
                category=meta.get('category', 'Unknown'),
                price_ghs=float(meta.get('price_ghs', 0)),
                similarity_score=round(float(match.score), 4),
                rank=rank,
            ))

        return RecommendResponse(
            recommendations=recs,
            query=request.query,
            total_returned=len(recs),
            model_used='text-embedding-3-small + pinecone-cosine',
        )
