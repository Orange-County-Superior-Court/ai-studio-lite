import os
import pandas as pd
import json
from langchain_community.document_loaders import WebBaseLoader,PyPDFLoader,Docx2txtLoader,UnstructuredPowerPointLoader, DataFrameLoader

CEILING_FLOAT = 2147483647
class DocumentLoader:
    def __init__(self, metadata, bytes=None):
        self.court_id = metadata['court_id']
        self.data_exchange_id = metadata['data_exchange_id']
        self.document_id = metadata['document_id']
        self.document_tag = metadata['document_tag']
        self.document_source = metadata.get('source', metadata.get('document_url'))
        self.bytes = bytes
        self.document_type = metadata.get('document_type', None)
        self.document_loader = metadata.get('document_loader', None)
        self.file_extension = metadata.get('file_extension', None)
        self.amount_of_columns_each = 10
    
    def standard_metadata_initializer(self, metadata):
        standard_metadata = {
                'document_loader': self.document_loader,
                'document_type': self.document_type,
                'document_source': self.document_source,
                'label_01': int(self.court_id),
                'label_02': int(self.data_exchange_id),
                'label_03': int(self.document_id),
                'label_04': self.document_tag,
                'label_05': '',
                'label_06': '',
                'label_07': '',
                'label_08': '',
                'label_09': '',
                'label_10': ''
            }
        standard_metadata.update({f"col_string_{i+1}": '' for i in range(0, self.amount_of_columns_each)})
        standard_metadata.update({f"col_decimal_{i+1}": 0.0 for i in range(0, self.amount_of_columns_each)})
        standard_metadata.update({f"col_int_{i+1}": 0 for i in range(0, self.amount_of_columns_each)})
        standard_metadata.update({f"col_date_{i+1}": pd.NaT for i in range(0, self.amount_of_columns_each)})
        metadata.update(standard_metadata)

    def create_local_file(self):
        doc_bytes = self.bytes
        local_storage = './local_storage'
        if not os.path.exists(f'{local_storage}/temp_files'):
            os.makedirs(f'{local_storage}/temp_files')
        local_file_path = os.path.join(local_storage, f'temp_files/{self.document_id}{self.file_extension}')
        with open(local_file_path, 'wb') as file:
            file.write(doc_bytes)

        self.local_file_path = local_file_path
        return self
    
    def website(self):
        loader = WebBaseLoader(self.document_source)
        documents = loader.load()
        for page_number, doc in enumerate(documents):
            doc.metadata.clear()
            doc.metadata.update({
                'source': self.document_source,
                'page': page_number + 1
            })
            self.standard_metadata_initializer(doc.metadata)

        return documents

    def pdf(self):
        self.create_local_file()

        local_file_path =  self.local_file_path

        loader = PyPDFLoader(local_file_path)
        documents = loader.load()
        for page_number,doc in enumerate(documents):
            doc.metadata.clear()
            doc.metadata.update({
                'source': local_file_path,
                'page': page_number + 1})
            self.standard_metadata_initializer(doc.metadata)

        os.remove(local_file_path)
        return documents
    
    def docx(self):
        self.create_local_file()
        local_file_path =  self.local_file_path

        loader = Docx2txtLoader(local_file_path)
        documents = loader.load()
        for page_number, doc in enumerate(documents):
            doc.metadata.clear()
            doc.metadata.update({
                'source': local_file_path, 
                'page': page_number + 1})
            self.standard_metadata_initializer(doc.metadata)

        os.remove(local_file_path)
        return documents
    
    def pptx(self):
        self.create_local_file()
        local_file_path =  self.local_file_path

        loader = UnstructuredPowerPointLoader(local_file_path, mode="elements", strategy="fast")
        documents = loader.load()
        for page_number,doc in enumerate(documents):
            doc.metadata.clear()
            doc.metadata.update({
                'source': local_file_path, 
                'page': page_number + 1})
            self.standard_metadata_initializer(doc.metadata)

        os.remove(local_file_path)
        return documents

    @staticmethod
    def preprocess_dataframe_for_json(cell):
        if isinstance(cell, pd.Timestamp):
            return cell.strftime('%Y-%m-%d')
        if cell is pd.NaT:
            return "No Date Entered"
        if isinstance(cell, float) and cell > CEILING_FLOAT and cell % 1 == 0:
            return int(cell)
        return cell
        
    @staticmethod
    def update_column_metadata(column_metadata, document_metadata, dataframe):
        string_index, float_index, date_index, int_index = 0, 0, 0, 0

        for key, value in document_metadata.items():
            if dataframe[key].dtype == 'object':
                string_index += 1
                column_metadata[f"col_string_{string_index}"] = value
            elif dataframe[key].dtype == 'datetime64[ns]':
                date_index += 1
                column_metadata[f"col_date_{date_index}"] = value
            elif dataframe[key].dtype == 'int64':
                int_index += 1
                column_metadata[f"col_int_{int_index}"] = value
            elif dataframe[key].dtype == 'float64' and value > CEILING_FLOAT and value % 1 == 0:
                int_index += 1
                column_metadata[f"col_int_{int_index}"] = int(value)
            elif dataframe[key].dtype == 'float64':
                float_index += 1
                column_metadata[f"col_decimal_{float_index}"] = value
            
    def dataframes(self):
        self.create_local_file()
        local_file_path = self.local_file_path
        df = None

        if self.file_extension == '.csv':
            df = pd.read_csv(local_file_path)
        elif self.file_extension == '.xlsx':
            df = pd.read_excel(local_file_path)
        elif self.file_extension == '.xml':
            df = pd.read_xml(local_file_path)
        else:
            print("unsupported file extension")
            return
            
        embedded_json_content = [None] * df.shape[0]
        for i in range(0,df.shape[0]):
            embedded_json_content[i] = json.dumps(df.iloc[i].apply(DocumentLoader.preprocess_dataframe_for_json).to_dict())
        df['Content to Embed'] = embedded_json_content
        loader = DataFrameLoader(df, page_content_column='Content to Embed')
        documents = loader.load()

        for page_number, doc in enumerate(documents):
            column_keys_metadata = {}
            DocumentLoader.update_column_metadata(column_keys_metadata, doc.metadata, df)
            doc.metadata.clear()
            doc.metadata.update({
                'source': local_file_path, 
                'page': page_number + 1})
            self.standard_metadata_initializer(doc.metadata)
            doc.metadata.update(column_keys_metadata)

        os.remove(local_file_path)
        return documents

    def load(self):
        if self.file_extension == '.pdf':
            return self.pdf()
        elif self.file_extension == '.docx':
            return self.docx()
        elif self.file_extension == '.pptx':
            return self.pptx()
        elif self.file_extension == '.csv' or self.file_extension == '.xlsx' or self.file_extension == '.xml':
            return self.dataframes()
        else:
            return self.website()
