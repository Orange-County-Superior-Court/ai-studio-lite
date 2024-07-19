
from components.file_storage.files import FileStorage
from database.local_storage import LocalStorage
class Templates:
    def __init__(self,metadata = {}):
        self.metadata = metadata

    def template_lookup(self):
        template_dict = {
            "basic":
            {
                "safe":"prompts\generic\generic_with_guardrails.txt",
                "unsafe":"prompts\generic\generic_without_guardrails.txt"
            },
            "qa":
            {
                "safe":"prompts\qa_with_context\qa_with_guardrails.txt",
                "unsafe":"prompts\qa_with_context\qa_without_guardrails.txt"
            }
        }
        return template_dict
    
    # def get_prompt_template(self,template_type='generic',template_subtype='safe'):
    #     template_dict = self.template_lookup()
    #     template_path = template_dict.get(template_type,'generic').get(template_subtype,'safe')
        
    #     return FileStorage().get_file_content(template_path)

    def get_prompt_template(self,template_type='generic',template_subtype='safe'):
        local_storage = LocalStorage()
        chatbot_data = local_storage.read_chatbot(1)
        template = chatbot_data['prompt_template']
        return template