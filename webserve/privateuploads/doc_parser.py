from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import RawUpload, DocFormat, DocumentFile


class RawDocParser:
    def parse(
        self,
        local_file: InMemoryUploadedFile,
        raw_file_obj: RawUpload,
        doc_type: DocFormat,
    ):
        """Given a raw file, parse and upload."""
        doc_cluster = raw_file_obj.document
        if doc_type == "pdf" or doc_type == "docx":
            # simple doc - create doc pointing to same location
            doc_file = DocumentFile(
                document=doc_cluster,
                source=raw_file_obj,
                file_role="primary",
                doc_format=doc_type,
                doc_name=local_file.name,
                location_container=raw_file_obj.location_container,
                location_path=raw_file_obj.location_path,
                processing_status="notstarted",
                last_jobid="",
            )
        else:
            raise NotImplementedError(doc_type)

        doc_file.save()
        return [doc_file]
