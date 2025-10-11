from ..config import PROMPTS_DIR
    
def prompt_path(code_version, lang, basepath):
    return PROMPTS_DIR / code_version / lang / f'{basepath}.txt'

def load_prompt(code_version, lang, basepath):
    filepath = prompt_path(code_version, lang, basepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()