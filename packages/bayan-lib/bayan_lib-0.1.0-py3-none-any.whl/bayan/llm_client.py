"""
Optional LLM integration for summarization and paper classification.
"""

from typing import Dict, Optional, List
import warnings


class LLMClient:
    """
    Interface for LLM-powered features like summarization and classification.
    Supports multiple providers: OpenAI, HuggingFace, and local models.
    """

    def __init__(self, provider: str = "openai", **kwargs):
        """
        Initialize LLM client.

        Args:
            provider: LLM provider ('openai', 'huggingface', 'local', 'anthropic')
            **kwargs: Provider-specific configuration
                - api_key: API key for the provider
                - model_name: Model name to use
                - base_url: Custom API base URL (for local/compatible APIs)
                - temperature: Sampling temperature
                - max_tokens: Maximum tokens for completion

        Raises:
            ValueError: If provider is not supported
            ImportError: If required library is not installed
        """
        self.provider = provider.lower()
        self.config = kwargs

        # Initialize provider-specific client
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "anthropic":
            self._init_anthropic()
        elif self.provider == "huggingface":
            self._init_huggingface()
        elif self.provider == "local":
            self._init_local()
        else:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported: openai, anthropic, huggingface, local"
            )

    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI library not installed. Install with: pip install openai"
            )

        api_key = self.config.get("api_key")
        if not api_key:
            raise ValueError("OpenAI requires 'api_key' parameter")

        base_url = self.config.get("base_url")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = self.config.get("model_name", "gpt-3.5-turbo")

    def _init_anthropic(self):
        """Initialize Anthropic Claude client."""
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError(
                "Anthropic library not installed. Install with: pip install anthropic"
            )

        api_key = self.config.get("api_key")
        if not api_key:
            raise ValueError("Anthropic requires 'api_key' parameter")

        self.client = Anthropic(api_key=api_key)
        self.model = self.config.get("model_name", "claude-3-5-sonnet-20241022")

    def _init_huggingface(self):
        """Initialize HuggingFace client."""
        try:
            from transformers import pipeline
        except ImportError:
            raise ImportError(
                "Transformers library not installed. "
                "Install with: pip install transformers torch"
            )

        model_name = self.config.get("model_name", "facebook/bart-large-cnn")
        self.client = pipeline("summarization", model=model_name)
        self.model = model_name

    def _init_local(self):
        """Initialize local model (Ollama or similar)."""
        try:
            import requests
        except ImportError:
            raise ImportError(
                "Requests library required for local models. "
                "Install with: pip install requests"
            )

        self.base_url = self.config.get("base_url", "http://localhost:11434")
        self.model = self.config.get("model_name", "llama2")
        self.client = requests.Session()

    def summarize(self, text: str, max_length: int = 200) -> str:
        """
        Generate a summary of the text.

        Args:
            text: Text to summarize
            max_length: Maximum length in words

        Returns:
            Summary text
        """
        if self.provider == "openai":
            return self._summarize_openai(text, max_length)
        elif self.provider == "anthropic":
            return self._summarize_anthropic(text, max_length)
        elif self.provider == "huggingface":
            return self._summarize_huggingface(text, max_length)
        elif self.provider == "local":
            return self._summarize_local(text, max_length)

    def _summarize_openai(self, text: str, max_length: int) -> str:
        """Summarize using OpenAI."""
        prompt = f"""Summarize the following academic text in approximately {max_length} words.
Focus on the main contributions and findings.

Text:
{text[:4000]}  # Limit input length
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at summarizing academic papers."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.config.get("temperature", 0.3),
            max_tokens=self.config.get("max_tokens", 500)
        )

        return response.choices[0].message.content.strip()

    def _summarize_anthropic(self, text: str, max_length: int) -> str:
        """Summarize using Anthropic Claude."""
        prompt = f"""Summarize the following academic text in approximately {max_length} words.
Focus on the main contributions and findings.

Text:
{text[:8000]}  # Claude has larger context
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.config.get("max_tokens", 500),
            temperature=self.config.get("temperature", 0.3),
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.content[0].text.strip()

    def _summarize_huggingface(self, text: str, max_length: int) -> str:
        """Summarize using HuggingFace."""
        # Limit input length
        max_input_length = 1024
        text = text[:max_input_length * 4]  # Rough character estimate

        result = self.client(
            text,
            max_length=max_length,
            min_length=max_length // 3,
            do_sample=False
        )

        return result[0]["summary_text"]

    def _summarize_local(self, text: str, max_length: int) -> str:
        """Summarize using local model (Ollama)."""
        prompt = f"""Summarize the following text in approximately {max_length} words:

{text[:4000]}
"""

        response = self.client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.get("temperature", 0.3)
                }
            }
        )

        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise RuntimeError(f"Local model error: {response.text}")

    def classify_paper(self, metadata: Dict, sections: Dict) -> Dict:
        """
        Classify the paper type and domain.

        Args:
            metadata: Paper metadata
            sections: Paper sections

        Returns:
            Dictionary with classification results:
                - paper_type: Type of paper (e.g., "empirical", "theoretical", "survey")
                - domain: Research domain (e.g., "machine learning", "NLP")
                - methodology: Research methodology used
        """
        # Prepare classification prompt
        title = metadata.get("title", "")
        abstract = sections.get("abstract", "")

        prompt = f"""Classify the following academic paper:

Title: {title}
Abstract: {abstract[:1000]}

Provide:
1. Paper type (empirical/theoretical/survey/review/position)
2. Research domain
3. Primary methodology

Format your response as JSON.
"""

        if self.provider == "openai":
            return self._classify_openai(prompt)
        elif self.provider == "anthropic":
            return self._classify_anthropic(prompt)
        else:
            # Fallback to simple heuristics
            return self._classify_heuristic(metadata, sections)

    def _classify_openai(self, prompt: str) -> Dict:
        """Classify using OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at classifying academic papers. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        import json
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {"error": "Failed to parse classification"}

    def _classify_anthropic(self, prompt: str) -> Dict:
        """Classify using Anthropic."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt + "\n\nRespond only with valid JSON."}
            ]
        )

        import json
        try:
            return json.loads(response.content[0].text)
        except:
            return {"error": "Failed to parse classification"}

    def _classify_heuristic(self, metadata: Dict, sections: Dict) -> Dict:
        """Simple rule-based classification fallback."""
        title = metadata.get("title", "").lower()
        abstract = sections.get("abstract", "").lower()

        # Paper type detection
        paper_type = "empirical"
        if any(word in title for word in ["survey", "review", "overview"]):
            paper_type = "survey"
        elif any(word in abstract for word in ["theorem", "proof", "formally"]):
            paper_type = "theoretical"

        # Domain detection (basic)
        domain = "unknown"
        domain_keywords = {
            "machine learning": ["machine learning", "neural network", "deep learning"],
            "nlp": ["natural language", "nlp", "text processing"],
            "computer vision": ["computer vision", "image recognition", "object detection"],
            "security": ["security", "cryptography", "vulnerability"],
        }

        for dom, keywords in domain_keywords.items():
            if any(kw in title or kw in abstract for kw in keywords):
                domain = dom
                break

        return {
            "paper_type": paper_type,
            "domain": domain,
            "methodology": "not analyzed"
        }

    def extract_key_contributions(self, sections: Dict) -> List[str]:
        """
        Extract key contributions from the paper.

        Args:
            sections: Paper sections

        Returns:
            List of key contributions
        """
        # Focus on introduction and conclusion
        text = sections.get("introduction", "") + "\n" + sections.get("conclusion", "")

        prompt = f"""Extract the main contributions from this academic paper.
List 3-5 key contributions as bullet points.

Text:
{text[:3000]}
"""

        if self.provider in ["openai", "anthropic"]:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Extract key contributions as a bulleted list."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                result = response.choices[0].message.content
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.content[0].text

            # Parse bullet points
            lines = result.strip().split("\n")
            contributions = [line.strip("- •*") for line in lines if line.strip()]
            return contributions

        return ["LLM provider does not support contribution extraction"]
