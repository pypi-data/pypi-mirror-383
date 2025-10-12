from typing import Dict, List, Optional

from rapidfuzz import fuzz

from schema_search.search.base import BaseSearchStrategy
from schema_search.types import TableSchema, SearchResultItem
from schema_search.chunkers import Chunk
from schema_search.graph_builder import GraphBuilder
from schema_search.rankers.base import BaseRanker


class FuzzySearchStrategy(BaseSearchStrategy):
    def __init__(
        self, initial_top_k: int, rerank_top_k: int, reranker: Optional[BaseRanker]
    ):
        super().__init__(reranker, initial_top_k, rerank_top_k)

    def _initial_ranking(
        self,
        query: str,
        schemas: Dict[str, TableSchema],
        chunks: List[Chunk],
        graph_builder: GraphBuilder,
        hops: int,
    ) -> List[SearchResultItem]:
        scored_tables: List[tuple[str, float]] = []

        for table_name, schema in schemas.items():
            searchable_text = self._build_searchable_text(table_name, schema)
            score = fuzz.ratio(query, searchable_text, score_cutoff=0) / 100.0
            scored_tables.append((table_name, score))

        scored_tables.sort(key=lambda x: x[1], reverse=True)

        results: List[SearchResultItem] = []
        for table_name, score in scored_tables[: self.initial_top_k]:
            result = self._build_result_item(
                table_name=table_name,
                score=score,
                schema=schemas[table_name],
                matched_chunks=[],
                graph_builder=graph_builder,
                hops=hops,
            )
            results.append(result)

        return results

    def _build_searchable_text(self, table_name: str, schema: TableSchema) -> str:
        parts = [table_name]

        if schema["indices"]:
            for idx in schema["indices"]:
                parts.append(idx["name"])

        return " ".join(parts)
