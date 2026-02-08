"""Async pipelined Ollama runner with concurrent requests."""
import asyncio
import aiohttp
import json
from collections import deque


class AsyncOllamaRunner:
    """Pipelined interface to Ollama with concurrent requests."""
    
    def __init__(self, model_name, max_concurrent=10):
        """Initialize with Ollama model name and concurrency limit.
        
        Args:
            model_name: str - Ollama model identifier
            max_concurrent: int - max parallel requests
        """
        self.model_name = model_name
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.prompt_template = "Pick exactly two characters that most strongly suggest a specific action or logical operation. Output nothing else.\n\nSet: {slate}"
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def infer_one(self, slate_chars, temperature=0.8, top_p=0.95, 
                        top_k=50, repeat_penalty=1.05, num_predict=8):
        """Single async inference call.
        
        Args:
            slate_chars: str - formatted slate characters
            temperature: float - sampling temperature
            
        Returns:
            str - raw model output
        """
        prompt = self.prompt_template.format(slate=slate_chars)
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "repeat_penalty": repeat_penalty,
                "num_predict": num_predict
            }
        }
        
        async with self.semaphore:  # Limit concurrent requests
            try:
                async with self.session.post(
                    'http://localhost:11434/api/generate',
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    result = await response.json()
                    return result.get('response', '')
            except Exception as e:
                return None
    
    def parse_output(self, output, slate_set):
        """Parse model output to extract exactly 2 glyphs from slate."""
        if output is None:
            return None
        
        chars = [ord(c) for c in output if ord(c) in slate_set]
        
        if len(chars) != 2:
            return None
        
        return tuple(chars)
    
    async def infer_batch(self, batch_data):
        """Process batch of slates concurrently.
        
        Args:
            batch_data: list of (slate_chars, slate_set) tuples
            
        Returns:
            list of (cp1, cp2) tuples or None
        """
        # Launch all requests concurrently
        tasks = []
        for slate_chars, slate_set in batch_data:
            task = self.infer_one(slate_chars, temperature=0.7)
            tasks.append((task, slate_set))
        
        # Wait for all to complete
        results = []
        for task, slate_set in tasks:
            output = await task
            result = self.parse_output(output, slate_set)
            results.append(result)
        
        return results


async def test_runner():
    """Test async runner."""
    async with AsyncOllamaRunner('qwen2.5-coder:14b', max_concurrent=10) as runner:
        # Test with batch
        test_slates = [
            ('一丁七万丈', {ord(c) for c in '一丁七万丈'}),
            ('之乎者也', {ord(c) for c in '之乎者也'}),
            ('東西南北', {ord(c) for c in '東西南北'}),
        ]
        
        import time
        start = time.time()
        results = await runner.infer_batch(test_slates)
        elapsed = time.time() - start
        
        print(f"Batch of {len(test_slates)} completed in {elapsed:.2f}s")
        for i, result in enumerate(results):
            if result:
                print(f"  {i+1}: {chr(result[0])}, {chr(result[1])}")
            else:
                print(f"  {i+1}: Failed")


if __name__ == "__main__":
    asyncio.run(test_runner())
