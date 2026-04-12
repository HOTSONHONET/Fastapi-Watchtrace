import time

from ..core.logging_util import get_logger
from ..utils.retry import retry

logger = get_logger(__name__)


class FeatureStoreClient:
    @retry(times=2, delay_s=0.01)
    def fetch_feature_metadata(self, feature_columns: list[str]) -> dict:
        time.sleep(0.005)
        logger.info("Fetched feature metadata for columns=%s", feature_columns)
        return {
            "feature_count": len(feature_columns),
            "features": [
                {"name": col, "type": "numeric", "freshness": "daily"} for col in feature_columns
            ],
        }


feature_store_client = FeatureStoreClient()
