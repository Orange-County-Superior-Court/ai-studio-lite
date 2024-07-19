class DocumentTypeRouter:
    def __init__(self, metadata):
        self.metadata = metadata
        self.content_type = metadata.get('content_type', None)
        self.file_extension = metadata.get('file_extension', None)

        self.content_types = {
            "application/pdf": {"file_extension": ".pdf", "document_type": ".pdf", "document_loader": "PyPDFLoader", "file_path": "files/PDFS_F"},
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {"file_extension": ".docx", "document_type": ".docx", "document_loader": "Docx2txtLoader", "file_path": "files/DOCX_F"},
            "application/msword": {"file_extension": ".doc", "document_type": ".doc", "document_loader": "Docx2txtLoader", "file_path": "files/DOC_F"},
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": {"file_extension": ".pptx", "document_type": ".pptx", "document_loader": "UnstructuredPowerPointLoader", "file_path": "files/PPTX_F"},
            "text/csv": {"file_extension": ".csv", "document_type": ".csv", "document_loader": "DataFrameLoader", "file_path": "files/CSV_F"},
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {"file_extension": ".xlsx", "document_type": ".xlsx", "document_loader": "DataFrameLoader", "file_path": "files/XLSX_F"},
            "text/xml": {"file_extension": ".xml", "document_type": ".xml", "document_loader": "DataFrameLoader", "file_path": "files/XML_F"}
        }

        self.doc_extensions = {
            '.pdf':{'content_type':"application/pdf","document_type": ".pdf", "document_loader": "PyPDFLoader", "file_path": "files/PDFS_F"},
            '.docx':{'content_type':"application/vnd.openxmlformats-officedocument.wordprocessingml.document","file_extension": ".docx", "document_type": ".docx", "document_loader": "Docx2txtLoader", "file_path": "files/DOCX_F"},
            '.doc':{'content_type':"application/msword","file_extension": ".doc", "document_type": ".doc", "document_loader": "Docx2txtLoader", "file_path": "files/DOC_F"},
            '.pptx':{'content_type':"application/vnd.openxmlformats-officedocument.presentationml.presentation","file_extension": ".pptx", "document_type": ".pptx", "document_loader": "UnstructuredPowerPointLoader", "file_path": "files/PPTX_F"},
            '.csv':{'content_type':"text/csv","file_extension": ".csv", "document_type": ".csv", "document_loader": "DataFrameLoader", "file_path": "files/CSV_F"},
            '.xlsx':{'content_type':"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","file_extension": ".xlsx", "document_type": ".xlsx", "document_loader": "DataFrameLoader", "file_path": "files/XLSX_F"},
            '.xml':{'content_type':"text/xml","file_extension": ".xml", "document_type": ".xml", "document_loader": "DataFrameLoader", "file_path": "files/XML_F"}
        }

    def get_loader_type(self):
        content_type = self.content_type
        content_types = self.content_types

        self.metadata = {**self.metadata,**content_types.get(content_type,None)}
    
        return self.metadata
    def get_content_type(self):
        doc_extensions = self.doc_extensions
        self.metadata = {**self.metadata,**doc_extensions.get(self.file_extension,None)}

        return self.metadata