#!/usr/bin/env python3
"""
Image analysis module for Cline Clone
Provides screenshot interpretation and visual debugging capabilities
"""

import os
import base64
from typing import Optional, Dict, Any
from pathlib import Path


class ImageAnalyzer:
    """Handles image analysis for multi-modal AI interactions"""

    SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']

    def __init__(self, ollama_config: Dict[str, Any]):
        self.config = ollama_config

    async def analyze_image(self, image_path: str, prompt: str = "") -> Optional[str]:
        """Analyze an image file using AI vision capabilities"""
        try:
            if not os.path.exists(image_path):
                return None

            # Check if vision model is available
            vision_model = self._get_vision_model()
            if not vision_model:
                return "[Error] No vision-capable model available. Try: ollama pull llava or ollama pull moondream"

            # Convert image to base64
            base64_image = self._encode_image(image_path)
            if not base64_image:
                return "[Error] Failed to encode image"

            # Create vision prompt
            vision_prompt = f"""
{prompt if prompt else "Analyze this image and describe what you see. Focus on code-related details if present."}

Please provide a detailed analysis of the image content:
- What is visible in the image?
- Are there any code snippets, error messages, or technical content?
- Describe the overall context and purpose
- Provide insights or suggestions based on what you observe
"""

            # Call vision model via Ollama
            response = await self._call_vision_model(base64_image, vision_prompt, vision_model)
            return response

        except Exception as e:
            return f"[Error] Image analysis failed: {e}"

    async def analyze_screenshot(self, image_path: str, context: str = "code") -> Optional[str]:
        """Specialized analysis for screenshots (code, errors, UI)"""
        try:
            context_prompts = {
                "code": "Analyze this code screenshot. Identify programming languages, algorithms, or patterns. Suggest improvements if you see issues.",
                "error": "Analyze this error/debugging screenshot. Identify error messages, stack traces, or debugging information.",
                "ui": "Analyze this UI/application screenshot. Describe the interface, functionality, and any visible issues.",
                "terminal": "Analyze this terminal/command line screenshot. Focus on commands, outputs, and any errors.",
            }

            prompt = context_prompts.get(context, f"Analyze this {context} screenshot and provide detailed insights.")

            return await self.analyze_image(image_path, prompt)

        except Exception as e:
            return f"[Error] Screenshot analysis failed: {e}"

    def _get_vision_model(self) -> Optional[str]:
        """Find an available vision-capable model"""
        vision_models = ['llava', 'moondream', 'llava-llama', 'bakllava', 'llavanext', 'llava-phi']

        # Check if any vision model is configured
        current_model = self.config.get('model', '').lower()
        for model in vision_models:
            if model in current_model:
                return self.config.get('model')

        # Return first available vision model name as fallback
        # In practice, you'd check if these models are actually pulled
        return 'llava'  # Most common vision model

    def _encode_image(self, image_path: str) -> Optional[str]:
        """Convert image to base64 string"""
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception:
            return None

    async def _call_vision_model(self, base64_image: str, prompt: str, model: str) -> Optional[str]:
        """Call Ollama vision model with base64 encoded image"""
        try:
            import aiohttp

            request_data = {
                "model": model,
                "prompt": prompt,
                "images": [base64_image],
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Lower temperature for analysis tasks
                    "num_predict": self.config.get('max_tokens', 1024)
                }
            }

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.get('timeout', 300))) as session:
                async with session.post(
                    f"{self.config['base_url']}/api/generate",
                    json=request_data
                ) as response:
                    if response.status != 200:
                        error_msg = await response.text()
                        raise Exception(f"Vision model API error: {response.status} - {error_msg}")

                    result = await response.json()
                    return result.get('response', '').strip()

        except Exception as e:
            raise Exception(f"Vision model call failed: {e}")

    def is_supported_format(self, file_path: str) -> bool:
        """Check if the image format is supported"""
        return Path(file_path).suffix.lower() in self.SUPPORTED_FORMATS

    async def batch_analyze(self, image_paths: list, analysis_type: str = "general") -> Dict[str, str]:
        """Analyze multiple images in batch"""
        results = {}
        for i, image_path in enumerate(image_paths, 1):
            print(f"Analyzing image {i}/{len(image_paths)}: {os.path.basename(image_path)}")
            result = await self.analyze_image(image_path, analysis_type)
            results[image_path] = result

        return results
