"""Data source adapters for various data types."""

from pdf_generator.data_sources.base import DataSource
from pdf_generator.data_sources.json_source import JSONDataSource
from pdf_generator.data_sources.csv_source import CSVDataSource
from pdf_generator.data_sources.database import DatabaseDataSource
from pdf_generator.data_sources.api_source import APIDataSource

__all__ = [
    "DataSource",
    "JSONDataSource",
    "CSVDataSource",
    "DatabaseDataSource",
    "APIDataSource",
]

