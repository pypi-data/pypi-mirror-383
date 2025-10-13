from __future__ import annotations

import textwrap
import re
from typing import List
import click
import subprocess
from rich.console import Console
from rich.panel import Panel
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, TextIteratorStreamer
from threading import Thread

from .utils import retrieve_context, build_or_load_index

console = Console()
_generator = None  # lazy-init model
_tokenizer = None

# Max prompt tokens for prompt context
MAX_PROMPT_TOKENS = 1024
RESERVED_NEW_TOKENS = 256  # space for generated text


def _get_generator():
    """Lazy-load the instruction-tuned causal LM (Qwen2.5-0.5B-Instruct, CPU)."""
    global _generator, _tokenizer
    if _generator is None or _tokenizer is None:
        console.print("[yellow]Loading Qwen/Qwen2.5-0.5B-Instruct on CPU. This may take a moment...[/yellow]")
        model_name = "Qwen/Qwen2.5-0.5B-Instruct"
        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        _generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=_tokenizer,
            device=-1,
        )
    return _generator, _tokenizer


def _truncate_prompt(prompt: str, tokenizer) -> str:
    """Truncate prompt to fit within the model token limit."""
    tokens = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_PROMPT_TOKENS - RESERVED_NEW_TOKENS).input_ids
    if tokens.size(1) > MAX_PROMPT_TOKENS - RESERVED_NEW_TOKENS:
        tokens = tokens[:, - (MAX_PROMPT_TOKENS - RESERVED_NEW_TOKENS) :]
        prompt = tokenizer.decode(tokens[0], skip_special_tokens=True)
    return prompt


def _format_context(docs: List[dict], max_chars: int = 300) -> str:
    """Concatenate retrieved docs into a compact string with truncation."""
    parts = []
    for d in docs:
        header = f"[Source: {d.get('path','unknown')}]"
        body = (d.get("text") or "").strip()
        if len(body) > max_chars:
            body = body[:max_chars] + " ..."
        parts.append(f"{header}\n{body}")
    return "\n\n".join(parts)


@click.command()
@click.argument("command", nargs=-1)
def main(command):
    """ShellSage — explain Linux commands with AI."""
    cmd = " ".join(command)

    # Build/load FAISS index
    build_or_load_index(force_rebuild=False)

    # Retrieve context
    docs = retrieve_context(cmd, top_k=1)
    context_str = _format_context(docs) if docs else ""
    if not context_str:
        console.print("[yellow]No docs found in ./docs. Proceeding without extra context.[/yellow]")

    # Prepare prompt for an instruction-following causal LM
    prompt = textwrap.dedent(f"""
        System: You are ShellSage. Explain a Linux command for a beginner. Be concise and organized. Include: what it does, option breakdown, a practical example, and caveats. If context is available, use it to improve accuracy.

        Context:
        {context_str}

        User: Explain and do not repeat the command verbatim: {cmd}
    """).strip()

    # Load model and tokenizer
    generator, tokenizer = _get_generator()
    prompt = _truncate_prompt(prompt, tokenizer)

    # Generation arguments
    eos_id = tokenizer.eos_token_id
    gen_kwargs = dict(
        max_new_tokens=120,
        do_sample=True,
        temperature=0.3,
        top_p=0.9,
        top_k=20,
        no_repeat_ngram_size=4,
        repetition_penalty=1.15,
        eos_token_id=eos_id,
        pad_token_id=eos_id,
        return_full_text=False,
    )

    console.print(Panel(f"Command: [bold cyan]{cmd}[/bold cyan]", title="ShellSage"))
    out = generator(prompt, **gen_kwargs)
    explanation = out[0]["generated_text"].strip()
    console.print(Panel(explanation, title="Explanation"))

