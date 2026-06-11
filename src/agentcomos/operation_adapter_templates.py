from typing import Dict, Any

class OperationAdapterTemplates:
    @staticmethod
    def render(template: str, kwargs: Dict[str, Any]) -> str:
        # Simple string formatting but robust against missing keys
        import string
        
        class SafeDict(dict):
            def __missing__(self, key):
                return '{' + key + '}'
                
        formatter = string.Formatter()
        return formatter.vformat(template, (), SafeDict(kwargs))
