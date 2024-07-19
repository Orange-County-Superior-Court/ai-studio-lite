import json

class FileStorage:

    def __init__(self,metadata={}):
        self.base_storage_location = metadata.get('base_storage_location','local_storage')

    def get_file_content(self,file_path):
        base_path = 'local_storage'

        full_path = f'{base_path}/{file_path}'
        
        with open(full_path, 'r') as file:
            file_contents = file.read()

        return file_contents