"""Ollama runner for glyph mining."""
import subprocess
import json
import re
import urllib.request
import urllib.error


class OllamaRunner:
    """Interface to Ollama for glyph selection."""
    
    def __init__(self, model_name):
        """Initialize with Ollama model name.
        
        Args:
            model_name: str - Ollama model identifier (e.g., 'llama2', 'mistral')
        """
        self.model_name = model_name
        self.prompt_template = "Pick exactly two characters that most strongly suggest a specific action or logical operation. Output nothing else.\n\nSet: {slate}"
    
    def infer(self, slate_chars, temperature=0.8, top_p=0.95, top_k=50, 
              repeat_penalty=1.05, num_predict=8):
        """Run inference with Ollama.
        
        Args:
            slate_chars: str - formatted slate characters
            temperature: float - sampling temperature
            top_p: float - nucleus sampling
            top_k: int - top-k sampling
            repeat_penalty: float - repetition penalty
            num_predict: int - max output tokens
        
        Returns:
            str - raw model output
        """
        prompt = self.prompt_template.format(slate=slate_chars)
        
        options = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "repeat_penalty": repeat_penalty,
            "num_predict": num_predict
        }
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": options
        }
        
        try:
            # Use Ollama HTTP API
            req = urllib.request.Request(
                'http://localhost:11434/api/generate',
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', '')
            
        except urllib.error.URLError as e:
            raise RuntimeError(f"Ollama API error: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON from Ollama: {e}")
    
    def parse_output(self, output, slate_set):
        """Parse model output to extract exactly 2 glyphs from slate.
        
        Args:
            output: str - raw model output
            slate_set: set - valid codepoints in slate
        
        Returns:
            tuple - (cp1, cp2) or None if invalid
        """
        # Extract all characters
        chars = [ord(c) for c in output if ord(c) in slate_set]
        
        # Must be exactly 2
        if len(chars) != 2:
            return None
        
        return tuple(chars)
    
    def sample_with_schedule(self, slate_chars, slate_set, temp_schedule=[0.8, 0.6, 0.4]):
        """Try inference with temperature schedule until valid parse.
        
        Args:
            slate_chars: str - formatted slate
            slate_set: set - valid codepoints
            temp_schedule: list - temperatures to try
        
        Returns:
            tuple - (cp1, cp2) or None if all attempts fail
        """
        for temp in temp_schedule:
            try:
                output = self.infer(slate_chars, temperature=temp)
                result = self.parse_output(output, slate_set)
                if result:
                    return result
            except Exception as e:
                print(f"Inference failed at T={temp}: {e}")
                continue
        
        return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python runner_ollama.py <model_name>")
        sys.exit(1)
    
    model = sys.argv[1]
    runner = OllamaRunner(model)
    
    # Test with small slate
    test_slate = [0x4E00, 0x4E01, 0x4E03, 0x4E07, 0x4E08]
    slate_chars = ''.join(chr(cp) for cp in test_slate)
    slate_set = set(test_slate)
    
    print(f"Test slate: {slate_chars}")
    print(f"Running inference with {model}...")
    
    result = runner.sample_with_schedule(slate_chars, slate_set)
    if result:
        print(f"✓ Selected: {chr(result[0])}, {chr(result[1])}")
        print(f"  Codepoints: {result}")
    else:
        print("✗ No valid selection")
