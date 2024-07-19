from llm_guard import scan_output, scan_prompt
from llm_guard.input_scanners import Anonymize, PromptInjection, TokenLimit, Toxicity
from llm_guard.output_scanners import Deanonymize, NoRefusal, Relevance, Sensitive
class Security:
    
    # constructor to take in input and output scanners
    # TODO Add thresholds
    def __init__(self, 
                 threshold: float = 0.5, 
                 ):
        # hard-coded input scanners
        self.input_scanners = [PromptInjection(), Toxicity()]



    # evaluate the results of the scan. Takes in the scan results and returns a dictionary indicating if any scanners were triggered and a list of said scanners
    def eval_scan(self, results_valid_dict):
        eval_dict = {
            'was_flagged': False,
            'flagged_scanners': []
        }
        # if one or more of the flags has been triggered then return the flag(s) information
        if all(results_valid_dict.values()) is False:
            # fetch the flags that caused the error and set triggered flag to True
            eval_dict['was_flagged'] = True
            eval_dict['flagged_scanners'] = [flag for flag, value in results_valid_dict.items() if value is False]

        return eval_dict

    # take the input scanners from metadata and run them on the prompt . Returns dict of scan results.
    def scan_input(self, user_message):
        '''
        Returns a dictionary with fields: {sanitized_prompt, was_flagged, 'results_score, flagged_scanners, eval_metrics}
        '''
        # user message
        self.user_message = user_message

        sanitized_prompt, results_valid, results_score = scan_prompt(scanners=self.input_scanners, prompt=self.user_message)
        output = self.eval_scan(results_valid)

        # metrics dictionary
        eval_metrics = [{"metric": key, "score": value} for key, value in results_score.items()]

        # dictionary containing results of the scan
        scan_results_dict = {
                'sanitized_prompt':sanitized_prompt,
                'was_flagged':output['was_flagged'],
                'results_score':results_score,
                'flagged_scanners':output['flagged_scanners'],
                'eval_metrics':eval_metrics
                }
        
        return scan_results_dict