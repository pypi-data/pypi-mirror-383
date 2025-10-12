"""
Extraction Service Module

This module provides business logic for handling extracted data storage and relationships.
"""

import logging
import os
import json
from datetime import datetime, UTC
from typing import Any

from dana.api.core.models import Document
from dana.api.core.schemas import DocumentRead
from sqlalchemy.orm.attributes import flag_modified

logger = logging.getLogger(__name__)


class ExtractionService:
    """
    Service for handling extraction data operations and file management.
    """

    def __init__(self, base_upload_directory: str = "./uploads"):
        """
        Initialize the extraction service.

        Args:
            base_upload_directory: Base directory where uploaded files are stored
        """
        self.base_upload_directory = base_upload_directory
        self.extract_data_directory = os.path.join(base_upload_directory, "extract-data")
        os.makedirs(self.extract_data_directory, exist_ok=True)

    async def save_extraction_json(
        self,
        original_filename: str,
        extraction_results: dict[str, Any],
        source_document_id: int,
        db_session,
        remove_old_extraction_files: bool = True,
        metadata: dict[str, Any] | None = None,
        deep_extracted: bool | None = None,
    ) -> DocumentRead:
        """
        Save extraction results as JSON file and create database relationship.

        Args:
            original_filename: Original filename of the source document
            extraction_results: The extracted data
            source_document_id: ID of the source document (PDF)
            db_session: Database session

        Returns:
            DocumentRead object with the stored JSON file information
        """
        try:
            # Get the source document to verify it exists
            source_document = db_session.query(Document).filter(Document.id == source_document_id).first()

            if not source_document:
                raise ValueError(f"Source document with ID {source_document_id} not found")

            # NOTE : Remove old extraction files
            extraction_files = db_session.query(Document).filter(Document.source_document_id == source_document_id).all()

            if remove_old_extraction_files and extraction_files:
                logger.info("Found %d extraction files to delete for document %d", len(extraction_files), source_document_id)
                for extraction_file in extraction_files:
                    # Delete extraction file from disk
                    if extraction_file.file_path:
                        # Extraction files store relative paths, so always join with upload directory
                        file_path = os.path.join(self.base_upload_directory, extraction_file.file_path)

                        if os.path.exists(file_path):
                            try:
                                os.remove(file_path)
                                logger.info("Deleted extraction file: %s", file_path)
                            except Exception as file_error:
                                logger.warning("Could not delete extraction file %s: %s", file_path, file_error)
                        else:
                            logger.warning("Extraction file not found: %s", file_path)

                    # Delete extraction file database record
                    db_session.delete(extraction_file)

                logger.info("Deleted %d extraction files for document %d", len(extraction_files), source_document_id)

            # Create JSON filename based on original filename
            base_name = os.path.splitext(original_filename)[0]
            json_filename = f"{base_name}_extraction_results.json"

            # Handle file conflicts by adding timestamp if needed
            json_path = os.path.join(self.extract_data_directory, json_filename)
            if os.path.exists(json_path):
                timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
                json_filename = f"{base_name}_extraction_results_{timestamp}.json"
                json_path = os.path.join(self.extract_data_directory, json_filename)

            # Add metadata to extraction results
            enhanced_results = {
                "original_filename": original_filename,
                "source_document_id": source_document_id,
                "extraction_date": datetime.now(UTC).isoformat(),
                "total_pages": extraction_results.get("total_pages", 0),
                "documents": extraction_results.get("documents", []),
                **extraction_results,
            }

            # Save JSON file to disk
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(enhanced_results, f, indent=2, ensure_ascii=False)

            file_size = os.path.getsize(json_path)

            # UPDATE METADATA TO THE EXTRACTION DOCUMENT
            if not metadata:
                metadata = {}

            if deep_extracted is not None:
                metadata["deep_extracted"] = deep_extracted

            # Create document record in database
            document = Document(
                filename=json_filename,
                original_filename=json_filename,
                file_path=os.path.relpath(json_path, self.base_upload_directory),
                file_size=file_size,
                mime_type="application/json",
                source_document_id=source_document_id,
                topic_id=None,  # No topic association for extraction files
                agent_id=None,  # No agent association for extraction files,
                doc_metadata=metadata,
            )

            db_session.add(document)
            db_session.commit()
            db_session.refresh(document)

            # UPDATE METADATA TO THE ORIGINAL DOCUMENT
            metadata["extraction_file_id"] = document.id
            source_document.doc_metadata = metadata
            flag_modified(source_document, "doc_metadata")
            db_session.commit()
            db_session.refresh(source_document)

            logger.info("Saved extraction JSON file: %s for source document ID: %s", json_filename, source_document_id)

            return DocumentRead(
                id=document.id,
                filename=document.filename,
                original_filename=document.original_filename,
                file_size=document.file_size,
                mime_type=document.mime_type,
                source_document_id=document.source_document_id,
                topic_id=document.topic_id,
                agent_id=document.agent_id,
                created_at=document.created_at,
                updated_at=document.updated_at,
            )

        except Exception as e:
            logger.error("Error saving extraction JSON: %s", e)
            raise


def get_extraction_service() -> ExtractionService:
    """Dependency injection for ExtractionService."""
    return ExtractionService()
