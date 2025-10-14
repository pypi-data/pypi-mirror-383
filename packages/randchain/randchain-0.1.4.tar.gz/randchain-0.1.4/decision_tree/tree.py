# decision_tree/tree.py
import re
from pathlib import Path
from typing import List, Dict, Any, Callable


class LLM:
    def __init__(self, orchestration: str, model_id: str, prompt: str, api_key: str = None):
        self.orchestration = orchestration
        self.model_id = model_id
        self.prompt = prompt
        self.api_key = api_key

    def call(self, query: str) -> str:
        if self.orchestration == "Ollama":
            # implement logger here
            print(f"[LLM] => Querying LLM with prompt: {query}", flush=True)
            from randchain_core.chat import ollama_chat
            return ollama_chat(self.prompt, self.model_id, query)
        elif self.orchestration == "OpenAI":
            print(f"[LLM] => Querying LLM with prompt: {query}", flush=True)
            from randchain_core.chat import open_ai_chat
            return open_ai_chat(self.api_key, self.prompt, self.model_id, query)
        else:
            raise ValueError(f"Unsupported orchestration: {self.orchestration}")


class DTCliassifier:
    def __init__(self, name: str, llm: LLM, children: List[Dict[str, Any]] = None):
        self.name = name
        self.llm = llm
        self.children = children if children else []

    def decide(self, query):
        # Ask the LLM to evaluate condition
        decision = self.llm.call(query)
        print(f"[Node] => Node {self.name} made decision: {decision}", flush=True)

        # Based on decision, select child node
        for child in self.children:
            print(f"[Node] => Evaluating child node {child['node'].name} for decision: {decision}", flush=True)
            if child["condition"](decision):
                print(f"[Node] => Child node {child['node'].name} selected for decision: {decision}", flush=True)
                return child["node"].decide(query)
        
        return  decision



