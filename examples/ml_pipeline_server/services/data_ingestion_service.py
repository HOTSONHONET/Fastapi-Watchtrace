from ..core.decorators import traced_step
from ..utils.transformers import summarize_rows
from ..utils.validators import validate_non_empty_rows


class DataIngestionService:
    @traced_step("ingest_dataset")
    def ingest(self, payload: dict) -> dict:
        rows = payload["rows"]
        validate_non_empty_rows(rows)
        stats = summarize_rows(rows)
        return {
            **payload,
            "row_count": len(rows),
            "stats": stats,
        }


data_ingestion_service = DataIngestionService()
