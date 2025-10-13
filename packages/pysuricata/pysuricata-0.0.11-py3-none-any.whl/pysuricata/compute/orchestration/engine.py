"""Streaming engine for data processing orchestration.

This module provides the main streaming engine that orchestrates data processing
operations, including adapter selection, chunking, and streaming coordination.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from ..adapters import PandasAdapter, PolarsAdapter
from ..core.protocols import DataAdapter
from ..core.types import ProcessingResult
from ..processing.chunking import AdaptiveChunker, ChunkingStrategy

# Import pandas and polars for type checking
try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import polars as pl
except ImportError:
    pl = None


class EngineManager:
    """Manages engine adapters and their selection.

    This class is responsible for discovering and registering available engine
    adapters (e.g., for pandas and polars) and selecting the most appropriate
    one for a given data source. This allows the rest of the system to be
    agnostic to the underlying data-handling library.

    Attributes:
        logger: A logger instance for logging messages related to adapter
            management and selection.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initializes the EngineManager.

        Args:
            logger: An optional logger instance. If not provided, a new logger
                will be created.
        """
        self.logger = logger or logging.getLogger(__name__)
        self._adapters: Dict[str, DataAdapter] = {}
        self._register_default_adapters()

    def _register_default_adapters(self) -> None:
        """Discovers and registers the default engine adapters.

        This method attempts to import pandas and polars and, if successful,
        registers the corresponding adapters. It logs a warning if a library
        is not found.
        """
        try:
            import pandas as pd

            self._adapters["pandas"] = PandasAdapter()
        except ImportError:
            self.logger.warning("pandas not available, skipping pandas adapter")

        try:
            import polars as pl

            self._adapters["polars"] = PolarsAdapter()
        except ImportError:
            self.logger.warning("polars not available, skipping polars adapter")

    def select_adapter(self, data: Any) -> ProcessingResult[DataAdapter]:
        """Selects the most appropriate adapter for the given data.

        This method inspects the type of the input data to determine which
        engine adapter to use. It supports pandas DataFrames, polars
        DataFrames, and iterables of DataFrames.

        Args:
            data: The input data to analyze.

        Returns:
            A `ProcessingResult` containing the selected `DataAdapter` on
            success, or an error message on failure.
        """
        start_time = time.time()

        try:
            # Check for pandas DataFrame
            if (
                "pandas" in self._adapters
                and pd is not None
                and isinstance(data, pd.DataFrame)
            ):
                adapter = self._adapters["pandas"]
                duration = time.time() - start_time
                return ProcessingResult.success_result(
                    data=adapter,
                    metrics={
                        "adapter_type": "pandas",
                        "selection_reason": "pandas_dataframe",
                    },
                    duration=duration,
                )

            # Check for polars DataFrame
            if (
                "polars" in self._adapters
                and pl is not None
                and isinstance(data, pl.DataFrame)
            ):
                adapter = self._adapters["polars"]
                duration = time.time() - start_time
                return ProcessingResult.success_result(
                    data=adapter,
                    metrics={
                        "adapter_type": "polars",
                        "selection_reason": "polars_dataframe",
                    },
                    duration=duration,
                )

            # Check for iterable of DataFrames
            if hasattr(data, "__iter__") and not isinstance(data, (str, bytes)):
                try:
                    first_item = next(iter(data))
                    return self.select_adapter(first_item)
                except StopIteration:
                    return ProcessingResult.error_result("Empty source")

            duration = time.time() - start_time
            return ProcessingResult.error_result(
                f"Unsupported input type: {type(data)}",
                duration=duration,
            )

        except Exception as e:
            duration = time.time() - start_time
            return ProcessingResult.error_result(
                f"Adapter selection failed: {str(e)}",
                duration=duration,
            )

    def get_adapter_tag(self, adapter: DataAdapter) -> str:
        """Returns a short string tag for the given adapter.

        This is useful for logging and debugging.

        Args:
            adapter: The adapter to get a tag for.

        Returns:
            A short string tag for the adapter (e.g., "pandas", "polars").
        """
        return adapter.__class__.__name__.lower().replace("adapter", "")

    def register_adapter(self, name: str, adapter: DataAdapter) -> None:
        """Registers a custom engine adapter.

        This allows users to extend the library with support for new data
        sources or data-handling libraries.

        Args:
            name: The name to register the adapter under.
            adapter: The adapter instance to register.
        """
        self._adapters[name] = adapter
        self.logger.info(f"Registered adapter: {name}")

    def get_available_adapters(self) -> Dict[str, str]:
        """Returns a dictionary of available engine adapters.

        Returns:
            A dictionary mapping adapter names to their class names.
        """
        return {
            name: adapter.__class__.__name__ for name, adapter in self._adapters.items()
        }


class StreamingEngine:
    """Orchestrates the data processing pipeline for streaming data.

    This class is the core of the data processing functionality. It coordinates
    the various components of the system, including the `EngineManager` for
    adapter selection and the `AdaptiveChunker` for data chunking. It is
    responsible for processing a data stream end-to-end and returning the
    results.

    Attributes:
        engine_manager: An `EngineManager` instance for managing adapters.
        chunker: An `AdaptiveChunker` instance for chunking data.
        logger: A logger instance for logging messages.
    """

    def __init__(
        self,
        engine_manager: Optional[EngineManager] = None,
        chunker: Optional[AdaptiveChunker] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """Initializes the StreamingEngine.

        Args:
            engine_manager: An optional `EngineManager` instance. If not
                provided, a new one will be created.
            chunker: An optional `AdaptiveChunker` instance. If not provided,
                a new one will be created.
            logger: An optional logger instance. If not provided, a new logger
                will be created.
        """
        self.engine_manager = engine_manager or EngineManager(logger)
        self.chunker = chunker or AdaptiveChunker(
            strategy=ChunkingStrategy.ADAPTIVE, logger=logger
        )
        self.logger = logger or logging.getLogger(__name__)

    def process_stream(
        self,
        source: Any,
        config: Any,
        row_kmv: Any,
    ) -> ProcessingResult[tuple]:
        """Processes a data stream from end to end.

        This method orchestrates the entire data processing pipeline for a given
        data source. It performs the following steps:

        1.  Selects the appropriate engine adapter for the data source.
        2.  Generates chunks of data from the source.
        3.  Initializes accumulators and other metrics based on the first chunk.
        4.  Processes the remaining chunks, updating the accumulators and
            metrics.
        5.  Returns a `ProcessingResult` containing a tuple of the computed
            statistics and metadata.

        Args:
            source: The data source to process. This can be a pandas DataFrame,
                a polars DataFrame, or an iterable of DataFrames.
            config: A configuration object with settings for the processing.
            row_kmv: A `RowKMV` instance for estimating the number of unique
                rows.

        Returns:
            A `ProcessingResult` containing a tuple with the following items:
            - `kinds`: A `ColumnKinds` object with the inferred types of the
              columns.
            - `accs`: A dictionary of accumulators for each column.
            - `n_rows`: The total number of rows processed.
            - `n_cols`: The total number of columns.
            - `total_missing_cells`: The total number of missing cells.
            - `approx_mem_bytes`: An estimate of the memory usage in bytes.
            - `first_columns`: A list of the column names from the first
              chunk.
            - `sample_section_html`: The HTML for the sample data section.
            - `corr_est`: A streaming correlation estimator.
        """
        start_time = time.time()

        try:
            # Select appropriate adapter
            adapter_result = self.engine_manager.select_adapter(source)
            if not adapter_result.success:
                return ProcessingResult.error_result(
                    f"Adapter selection failed: {adapter_result.error}"
                )

            adapter = adapter_result.data

            # Generate chunks
            chunk_result = self.chunker.chunks_from_source(
                source, config.chunk_size, config.force_chunk_in_memory
            )
            if not chunk_result.success:
                return ProcessingResult.error_result(
                    f"Chunking failed: {chunk_result.error}"
                )

            chunks = chunk_result.data

            # Process first chunk to initialize
            try:
                first_chunk = next(chunks)
            except StopIteration:
                return ProcessingResult.error_result("Empty source")

            kinds, accs = adapter.infer_and_build(first_chunk, config)
            corr_est = self.maybe_corr_estimator(kinds, config)

            # Process first chunk
            adapter.consume_chunk(first_chunk, accs, kinds, config, self.logger)
            if corr_est is not None:
                adapter.update_corr(first_chunk, corr_est, self.logger)
            adapter.update_row_kmv(first_chunk, row_kmv)

            # Initialize metrics
            n_rows = len(first_chunk) if hasattr(first_chunk, "__len__") else 0
            n_cols = len(first_chunk.columns) if hasattr(first_chunk, "columns") else 0
            total_missing_cells = adapter.missing_cells(first_chunk)
            approx_mem_bytes = adapter.estimate_mem(first_chunk)
            first_columns = list(getattr(first_chunk, "columns", []))
            sample_section_html = adapter.sample_section_html(first_chunk, config)

            # Initialize chunk metadata collection
            chunk_metadata = []
            current_row = 0

            # Process first chunk
            chunk_size = len(first_chunk) if hasattr(first_chunk, "__len__") else 0
            chunk_missing = adapter.missing_cells(first_chunk)
            chunk_metadata.append(
                (current_row, current_row + chunk_size - 1, chunk_missing)
            )
            current_row += chunk_size

            # Process remaining chunks
            for chunk in chunks:
                adapter.consume_chunk(chunk, accs, kinds, config, self.logger)
                if corr_est is not None:
                    adapter.update_corr(chunk, corr_est, self.logger)
                adapter.update_row_kmv(chunk, row_kmv)

                chunk_size = len(chunk) if hasattr(chunk, "__len__") else 0
                chunk_missing = adapter.missing_cells(chunk)
                chunk_metadata.append(
                    (current_row, current_row + chunk_size - 1, chunk_missing)
                )
                current_row += chunk_size

                n_rows += chunk_size
                total_missing_cells += chunk_missing
                approx_mem_bytes += adapter.estimate_mem(chunk)

            duration = time.time() - start_time

            return ProcessingResult.success_result(
                data=(
                    kinds,
                    accs,
                    n_rows,
                    n_cols,
                    total_missing_cells,
                    approx_mem_bytes,
                    first_columns,
                    sample_section_html,
                    corr_est,
                    chunk_metadata,
                ),
                metrics={
                    "processing_time": duration,
                    "chunks_processed": chunk_result.metrics.get("chunk_size", 0),
                    "adapter_type": adapter.__class__.__name__,
                },
                duration=duration,
            )

        except Exception as e:
            duration = time.time() - start_time
            return ProcessingResult.error_result(
                f"Stream processing failed: {str(e)}",
                duration=duration,
            )

    def maybe_corr_estimator(self, kinds, config) -> Optional[Any]:
        """Creates a streaming correlation estimator if conditions are met.

        A correlation estimator is created if the following conditions are met:

        - The `compute_correlations` option is enabled in the configuration.
        - There are at least two numeric columns in the dataset.

        Args:
            kinds: A `ColumnKinds` object with the inferred types of the
                columns.
            config: A configuration object with settings for the processing.

        Returns:
            A `StreamingCorr` instance if the conditions are met, otherwise
            `None`.
        """
        try:
            from ..analysis.correlation import StreamingCorr

            if len(kinds.numeric) < 2:
                return None

            if not config.compute_correlations:
                return None

            return StreamingCorr(kinds.numeric)

        except Exception as e:
            self.logger.warning(f"Failed to create correlation estimator: {e}")
            return None

    def get_engine_info(self) -> Dict[str, Any]:
        """Returns a dictionary with information about the engine.

        This information can be used for debugging and monitoring.

        Returns:
            A dictionary with the following keys:
            - `available_adapters`: A dictionary of available engine adapters.
            - `chunker_strategy`: The chunking strategy being used.
            - `chunker_metrics`: A dictionary of metrics from the chunker.
        """
        return {
            "available_adapters": self.engine_manager.get_available_adapters(),
            "chunker_strategy": self.chunker.strategy.value,
            "chunker_metrics": self.chunker.get_performance_metrics(),
        }
