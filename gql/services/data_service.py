# gql/services/data_service.py

from typing import Dict, List, Optional, Type, TypeVar, Generic, Any, Callable
import polars as pl
import time
from gql.utils.reader import read_csv_files_to_polars_df
from gql.utils.logger import get_logger
from gql.utils.utility import check_file_path, normalize_path_for_spark
from strawberry.types import Info  # Import Info for type hinting

logger = get_logger(__name__)

T = TypeVar('T')

class DataService(Generic[T]):
    """Service for loading and caching data from CSV files."""
    
    def __init__(
        self, 
        path: str, 
        entity_type: Type[T],
        transform_func: Callable[[Dict[str, Any], Any], T], # CHANGED: Transform func signature
        cache_ttl_seconds: int = 300
    ):
        self.path = normalize_path_for_spark(path)
        self.entity_type = entity_type
        self.transform_func = transform_func
        self.cache_ttl_seconds = cache_ttl_seconds
        # CHANGED: We now cache the raw DataFrame, not the transformed objects
        self._df_cache: Optional[pl.DataFrame] = None
        self._last_refresh: Optional[float] = None
    
    # CHANGED: get_data now accepts the GraphQL info object
    def get_data(self, info: Info) -> List[T]:
        """Get data, transform it based on user context, using a cached DataFrame."""
        current_time = time.time()
        
        # If DataFrame cache is empty or expired, refresh it
        if (self._df_cache is None or 
            self._last_refresh is None or 
            current_time - self._last_refresh > self.cache_ttl_seconds):
            self._refresh_cache()
            
        if self._df_cache is None or self._df_cache.is_empty():
            return []
            
        # ADDED: Get the user from the context provided by FastAPI/Strawberry
        user = info.context.get("user")

        # ADDED: Perform the user-specific transformation on each request
        # This is fast because the expensive file I/O is already cached.
        return [
            self.transform_func(row, user) for row in self._df_cache.iter_rows(named=True)
        ]
    
    def _refresh_cache(self) -> None:
        """Refresh the raw DataFrame cache."""
        try:
            if not check_file_path(self.path):
                logger.error(f"Path not found: {self.path}")
                self._df_cache = pl.DataFrame() # Use empty DataFrame
                self._last_refresh = time.time()
                return
                
            logger.info(f"Reading CSV files from path: {self.path}")
            # CHANGED: Store the raw DataFrame in the cache
            self._df_cache = read_csv_files_to_polars_df(self.path)
            self._last_refresh = time.time()
            logger.info(f"Successfully cached {len(self._df_cache)} raw records for {self.entity_type.__name__}")
            
        except Exception as e:
            logger.error(f"Error refreshing {self.entity_type.__name__} data: {str(e)}")
            if self._df_cache is None:
                self._df_cache = pl.DataFrame()
            self._last_refresh = time.time()

    def clear_cache(self) -> None:
        """Force clear the cache."""
        self._df_cache = None
        self._last_refresh = None