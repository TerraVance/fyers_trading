import os
import openai
from backend.app.core.config import settings

class StrategyGenerator:
    """
    Uses an LLM to generate Python code for a trading strategy based on a text prompt.
    """
    def __init__(self):
        self.api_key = settings.openai_api_key
        if not self.api_key or self.api_key == "sk-...":
            print("WARNING: OpenAI API key is not set. Generator will fail.")
            
    def generate_strategy_code(self, strategy_name: str, english_description: str) -> str:
        client = openai.OpenAI(api_key=self.api_key)
        
        system_prompt = """
        You are a quantitative trading developer. 
        You write pure Python code that implements the `AbstractStrategy` interface.
        
        The AbstractStrategy interface:
        ```python
        from abc import ABC, abstractmethod
        import pandas as pd

        class AbstractStrategy(ABC):
            @abstractmethod
            def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
                pass
        ```
        
        You must use the `ta` library for technical indicators.
        Your code must be completely vectorized. Do not use loops.
        Return the dataframe with a new column named 'signal' containing 'BUY', 'SELL', or None.
        Return ONLY the raw Python code. Do not include markdown formatting like ```python. 
        The class name should exactly match the strategy_name parameter.
        Make sure the returned python file can be imported and executed cleanly.
        """
        
        user_prompt = f"Write a strategy class named {strategy_name}. Logic: {english_description}"
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0
            )
            
            code = response.choices[0].message.content
            # Clean up markdown formatting if the LLM ignores the system prompt
            if code.startswith("```python"):
                code = code[9:]
            elif code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
            
            return code.strip()
            
        except Exception as e:
            print(f"Error generating strategy: {e}")
            raise e
        
    def save_strategy(self, strategy_name: str, code: str) -> str:
        # Convert CamelCase to snake_case for filename
        filename = ''.join(['_'+c.lower() if c.isupper() else c for c in strategy_name]).lstrip('_') + ".py"
        filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "strategies", filename)
        
        with open(filepath, "w") as f:
            f.write(code)
        return filepath
