# joycaption_gguf_mlv.py
# Node: JoyCaption GGUF MLV — Inferência customizada para LoRA Training (LOCKED/UNLOCKED)
# Importa JC_GGUF_Models do original (zero duplicação de código de inferência)
# Customiza: prompt positioning, post-processing, defaults otimizados

import re
import gc
import torch
from torchvision.transforms import ToPILImage

# Importar classes e dados do JoyCaption original (sem duplicar)
import sys
from pathlib import Path

_JC_PATH = str(Path(__file__).resolve().parent.parent / "ComfyUI-JoyCaption")
if _JC_PATH not in sys.path:
    sys.path.insert(0, _JC_PATH)

from JC_GGUF import (
    JC_GGUF_Models,
    GGUF_MODELS,
    MODEL_SETTINGS,
    _MODEL_CACHE,
)


def _clean_caption(text: str) -> str:
    """Post-processing: remove meta-conversation, LOCKED attributes, degeneration."""
    original_text = text  # B7: preserve for fallback if cleaning empties result
    # Remove ASSISTANT: markers
    text = re.sub(r'(?i)\bASSISTANT\s*:\s*', '', text)
    # Remove meta-conversation phrases
    text = re.sub(r'(?i)\b(Now I\'ll|Let me|Here is|Here\'s|I will|I\'ll|Note:|Disclaimer:)\b.*?[.!]\s*', '', text)
    # Truncate at revision separators (model tries to rewrite)
    text = re.sub(r'\s*--+\s*(Here|Now|Let|I\'ll|Revised|Rewritten|Updated|Caption:).*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\s*---+.*$', '', text, flags=re.DOTALL)
    # Remove [bracketed content] — keep inner text
    text = re.sub(r'\[([^\]]*)\]', r'\1', text)
    # Remove verbalized instructions
    text = re.sub(r'(?i)(The person is the subject with trigger word\.?\s*)', '', text)
    text = re.sub(r'(?i)(Periods separate each descriptive element\.?\s*)', '', text)

    # === LOCKED ATTRIBUTE REMOVAL (post-process fallback) ===
    # Remove sentences containing hair references
    sentences = re.split(r'(?<=[.!?])\s+', text)
    clean_sentences = []
    hair_pattern = re.compile(
        r'\b(hair|hairs|hairstyle|hair\s*style|haircut|bald|balding|'
        r'curly|wavy|straight\s+hair|braids?|ponytail|bun|bangs|fringe|'
        r'blonde|brunette|redhead|auburn|gray\s*hair|grey\s*hair|'
        r'short\s*hair|long\s*hair|dark\s*hair|light\s*hair|'
        r'shoulder.length|bob\s*cut|pixie\s*cut|afro|dreadlocks?|'
        r'tied\s*(back|up)|pulled\s*back|loose\s*hair)\b',
        re.IGNORECASE
    )
    for sent in sentences:
        if not hair_pattern.search(sent):
            clean_sentences.append(sent)
    text = ' '.join(clean_sentences)

    # Remove token degeneration (repeated periods)
    text = re.sub(r'(\.\s*){3,}', '. ', text)
    text = re.sub(r'\.(\s*\.)+', '.', text)
    # Remove trailing incomplete sentences
    text = re.sub(r'[^.!?]*$', '', text).strip()
    if not text.endswith(('.', '!', '?')):
        text = re.sub(r'(\.\s*){3,}', '. ', text).strip()
    # Remove meta lines
    lines = text.split('\n')
    clean_lines = [l for l in lines if l.strip() and not re.match(r'(?i)^(note:|please |if you|warning:)', l.strip())]
    text = ' '.join(clean_lines)
    # Collapse multiple spaces
    text = re.sub(r'  +', ' ', text)
    # B7 + Devil R4: fallback with mini-validation (not blind)
    result = text.strip()
    if not result:
        if not re.match(r'(?i)^(ASSISTANT|Here is|Note:|Let me)', original_text.strip()):
            return original_text.strip()  # raw text > empty
        return "[CAPTION_EMPTY]"  # pure meta-text → explicit marker
    return result


def _build_mlv_prompt(
    extra_options: list[str] | None,
    character_name: str,
    caption_style: str,
) -> str:
    """Build COMPACT prompt (~150 tokens max) with LOCKED rules first.
    
    Key design: instructions are SHORT and AFFIRMATIVE.
    The 512-token context must leave ~300 tokens for the caption itself.
    
    Prompt order (B2+B3 fix):
      1. LOCKED restrictions (highest attention)
      2. Pronoun instruction (B2: moved from end to position 2)
      3. Core task (B3: no name_ref in task — prevents hallucination)
      4. Subject context (B3: name_ref as optional context, not presupposition)
      5. Scope instructions (other)
    """
    name_ref = character_name.strip() if character_name.strip() else "a person"

    # Separate LOCKED, pronoun, and other instructions
    # COUPLING: pronoun detection keywords match pronoun_map strings in extra_mlv.py (Devil R1)
    locked = []
    pronoun_instr = []
    other = []
    if extra_options:
        for opt in extra_options:
            opt_lower = opt.lower()
            if 'never' in opt_lower or 'do not' in opt_lower:
                locked.append(opt)
            elif 'pronoun' in opt_lower or 'she/' in opt_lower or 'he/' in opt_lower or 'they/' in opt_lower or "'the person'" in opt_lower:
                pronoun_instr.append(opt)
            else:
                other.append(opt)

    # Build prompt: LOCKED → Pronoun → Core Task → Subject Context → Scope
    prompt = ""

    # 1. LOCKED restrictions (first position = highest attention)
    if locked:
        prompt += " ".join(locked) + " "

    # 2. Pronoun instruction (B2: position 2 for high attention in first sentence)
    if pronoun_instr:
        prompt += " ".join(pronoun_instr) + " "

    # 3. Core task — NO name_ref here (B3: prevents hallucination of absent subjects)
    if caption_style == "Booru tag-like":
        prompt += "Write booru-style tags for this image."
    else:
        prompt += "Describe this image in natural prose."

    # 4. Subject context (B3: only if character_name provided, as context not presupposition)
    if character_name.strip() and name_ref != "a person":
        prompt += f" The subject is called {name_ref}."

    # 5. Scope (compact — what to include)
    if other:
        prompt += " " + " ".join(other)

    # Token budget guard (B5 + Devil R3: explicit core_end_marker, not //3 heuristic)
    MAX_PROMPT_CHARS = 800  # ~200 tokens
    if len(prompt) > MAX_PROMPT_CHARS:
        # Find end of core task (deterministic markers)
        core_end = -1
        for marker in ["in natural prose.", "for this image.", f"called {name_ref}."]:
            idx = prompt.find(marker)
            if idx > 0:
                core_end = max(core_end, idx + len(marker))
        if core_end <= 0:
            core_end = len(prompt) // 2  # absolute fallback
        # Truncate other list items sentence-by-sentence until within budget
        truncated = prompt[:core_end]
        remaining_parts = prompt[core_end:].strip().split(". ")
        for part in remaining_parts:
            if not part.strip():
                continue
            candidate = truncated + " " + part.strip() + "."
            if len(candidate) <= MAX_PROMPT_CHARS:
                truncated = candidate
            else:
                break
        prompt = truncated.strip()

    return prompt.strip()


# ============================================================
# NODE: JoyCaption GGUF MLV
# ============================================================

class JC_GGUF_MLV:
    """JoyCaption GGUF MLV — Custom inference node for LoRA training captions.
    
    Key differences from original:
    - LOCKED rules positioned at BEGINNING of prompt (highest attention weight)
    - Post-processing removes meta-conversation, brackets, ASSISTANT markers
    - Optimized defaults: temperature=0.3, top_p=0.8, top_k=40, max_new_tokens=200
    - System prompt customizable
    """

    @classmethod
    def INPUT_TYPES(cls):
        model_list = list(GGUF_MODELS.keys())
        return {
            "required": {
                "model": (model_list, {
                    "default": model_list[0],
                    "tooltip": "Select the GGUF model to use",
                }),
                "processing_mode": (["Auto", "GPU", "CPU"], {
                    "default": "Auto",
                    "tooltip": "Auto: detect best mode. GPU: faster. CPU: saves VRAM",
                }),
                "caption_style": (["Descriptive", "Straightforward", "Booru tag-like"], {
                    "default": "Descriptive",
                    "tooltip": "Style of caption output",
                }),
                "system_prompt": ("STRING", {
                    "default": "You are a precise image captioner for AI training datasets. Output ONLY the caption — no explanations, no meta-text, no assistant markers.",
                    "multiline": True,
                    "tooltip": "System prompt — defines the model's behavior",
                }),
                "max_new_tokens": ("INT", {
                    "default": 200,
                    "min": 50,
                    "max": 512,
                    "tooltip": "Max tokens in output. 200 ideal for LoRA captions (50-200 tokens)",
                }),
                "temperature": ("FLOAT", {
                    "default": 0.3,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05,
                    "tooltip": "Lower = more factual, less hallucination. 0.3 recommended for LOCKED/UNLOCKED",
                }),
                "top_p": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Nucleus sampling. 0.8 restricts vocabulary, less chance of mentioning LOCKED attributes",
                }),
                "top_k": ("INT", {
                    "default": 40,
                    "min": 0,
                    "max": 100,
                    "tooltip": "Top-K filtering. 40 limits choices, reduces creative violations of LOCKED rules",
                }),
                "memory_management": (["Keep in Memory", "Clear After Run", "Global Cache"], {
                    "default": "Global Cache",
                    "tooltip": "Global Cache: fastest for batch processing",
                }),
                "post_process": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Clean output: remove ASSISTANT markers, brackets, meta-conversation",
                }),
            },
            "optional": {
                "image": ("IMAGE", {
                    "lazy": True,
                    "tooltip": "Optional reference image. If absent, returns empty caption without loading GGUF model.",
                }),
                "extra_options": ("JOYCAPTION_EXTRA_OPTIONS", {
                    "tooltip": "Connect JoyCaption Extra MLV node for LOCKED/UNLOCKED options",
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("caption", "prompt_used")
    FUNCTION = "generate"
    CATEGORY = "🧬MLV/📝Captioning"

    def check_lazy_status(self, image=None, **kwargs):
        """Lazy eval: request image evaluation only if not yet available."""
        if image is not None:
            return []  # image already evaluated — proceed to execute
        return ["image"]  # image not yet evaluated — request engine to evaluate it

    def __init__(self):
        self.predictor = None
        self.current_processing_mode = None
        self.current_model = None

    def generate(
        self,
        model,
        processing_mode,
        caption_style,
        system_prompt,
        max_new_tokens,
        temperature,
        top_p,
        top_k,
        memory_management,
        post_process,
        image=None,
        extra_options=None,
    ):
        try:
            # Guard: skip captioning if no reference image provided (Devil R1/R3)
            if image is None:
                return ("", "")

            cache_key = f"mlv_{model}_{processing_mode}"

            # Model loading (reuses original JC_GGUF_Models class)
            if memory_management == "Global Cache":
                if cache_key in _MODEL_CACHE:
                    self.predictor = _MODEL_CACHE[cache_key]
                else:
                    model_name = GGUF_MODELS[model]["name"]
                    self.predictor = JC_GGUF_Models(model_name, processing_mode)
                    _MODEL_CACHE[cache_key] = self.predictor
            elif self.predictor is None or self.current_processing_mode != processing_mode or self.current_model != model:
                if self.predictor is not None:
                    del self.predictor
                    self.predictor = None
                    torch.cuda.empty_cache()
                model_name = GGUF_MODELS[model]["name"]
                self.predictor = JC_GGUF_Models(model_name, processing_mode)
                self.current_processing_mode = processing_mode
                self.current_model = model

            # Build prompt with LOCKED rules at BEGINNING
            opts_list = extra_options[0] if extra_options else []
            char_name = extra_options[1] if extra_options else ""
            prompt_text = _build_mlv_prompt(opts_list, char_name, caption_style)

            # Inference
            with torch.inference_mode():
                pil_image = ToPILImage()(image[0].permute(2, 0, 1))
                response = self.predictor.generate(
                    image=pil_image,
                    system=system_prompt.strip(),
                    prompt=prompt_text,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                )

            # Post-processing
            if post_process:
                response = _clean_caption(response)

            # Memory management
            if memory_management == "Clear After Run":
                del self.predictor
                self.predictor = None
                torch.cuda.empty_cache()
                gc.collect()

            return (response, prompt_text)

        except Exception as e:
            if memory_management == "Clear After Run" and self.predictor is not None:
                del self.predictor
                self.predictor = None
                torch.cuda.empty_cache()
                gc.collect()
            return (f"[CAPTION_ERROR] {str(e)}", "")
