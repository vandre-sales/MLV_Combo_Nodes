# 🧬 MLV_Combo_Nodes

> **Custom nodes for ComfyUI** — LoRA training caption pipeline with LOCKED/UNLOCKED protocol + dynamic combo selectors.

[![ComfyUI](https://img.shields.io/badge/ComfyUI-custom%20node-blue)](https://github.com/comfyanonymous/ComfyUI)
[![Category](https://img.shields.io/badge/category-Captioning-purple)](https://github.com/vandre-sales/MLV_Combo_Nodes)

---

## 📦 Nodes Included

| Node | Class | Category | Description |
|---|---|---|---|
| **JoyCaption Extra MLV** | `JC_ExtraOptions_MLV` | `🧬MLV/📝Captioning` | LOCKED/UNLOCKED extra options for LoRA training captions |
| **JoyCaption GGUF MLV** | `JC_GGUF_MLV` | `🧬MLV/📝Captioning` | Custom GGUF inference with LOCKED-first prompt ordering |
| **MLV Combo (*)** | `MLV_Combo_<name>` | `🧬MLV` | Dynamic combo selectors from YAML config files |

---

## 🔌 Dependencies

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) (recent version with `lazy: True` support in V1 nodes)
- [1038lab/ComfyUI-JoyCaption](https://github.com/1038lab/ComfyUI-JoyCaption) — **required** as sibling node pack
  - Provides: `JC_GGUF_Models`, `GGUF_MODELS`, `MODEL_SETTINGS`, `_MODEL_CACHE`
- `llama-cpp-python` compiled with CUDA support:
  ```bash
  CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python
  ```
- JoyCaption GGUF model in `ComfyUI/models/LLM/`:
  ```bash
  # Example: IQ4_XS (lightweight) or f16 (quality)
  huggingface-cli download fancyfeast/llama-joycaption-beta-one-hf-llava \
    --include "*.gguf" \
    --local-dir ComfyUI/models/LLM/joycaption-gguf/
  ```

---

## 📥 Installation

```bash
# 1. Clone into ComfyUI custom_nodes
cd ComfyUI/custom_nodes
git clone https://github.com/vandre-sales/MLV_Combo_Nodes.git

# 2. Install 1038lab/ComfyUI-JoyCaption (required dependency)
git clone https://github.com/1038lab/ComfyUI-JoyCaption.git

# 3. Install llama-cpp-python with CUDA (for JC_GGUF_MLV)
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python

# 4. Restart ComfyUI
sudo systemctl restart comfyui  # or your ComfyUI service command
```

---

## 🧬 Node Reference

### 1. `JC_ExtraOptions_MLV` — JoyCaption Extra MLV

Generates a `JOYCAPTION_EXTRA_OPTIONS` output for use with `JC_GGUF_MLV`. Controls which visual elements to include or exclude in captions, following the LOCKED/UNLOCKED protocol for LoRA training.

#### Inputs

| Input | Type | Default | Description |
|---|---|---|---|
| `exclude_locked_identity` | BOOLEAN | `True` | 🔒 Skip physical identity traits (face, body, hair) |
| `exclude_permanent_accessories` | BOOLEAN | `True` | 🔒 Skip glasses, piercings, birthmarks, tattoos |
| `include_facial_expression` | BOOLEAN | `True` | 🔓 Describe facial expression and emotion |
| `include_pose_action` | BOOLEAN | `True` | 🔓 Describe pose, body language and action |
| `include_composition` | BOOLEAN | `True` | 🔓 Specify camera framing and composition |
| `include_lighting` | BOOLEAN | `True` | 🔓 Describe lighting type, quality and direction |
| `include_scenery` | BOOLEAN | `True` | 🔓 Describe background scenery and environment |
| `include_clothing_detail` | BOOLEAN | `True` | 🔓 Describe all clothing layers and accessories |
| `use_natural_prose` | BOOLEAN | `True` | ✍️ Natural English prose (no tags) |
| `avoid_meta_phrases` | BOOLEAN | `True` | ✍️ Output ONLY the caption, no conversational text |
| `flux_structure` | BOOLEAN | `True` | ⚡ Flux-optimized order: subject → expression → clothing → pose → scenery → lighting |
| `include_camera_angle` | BOOLEAN | `False` | 📷 Include camera angle (optional) |
| `include_depth_of_field` | BOOLEAN | `False` | 📷 Include depth of field (optional) |
| `exclude_text_in_image` | BOOLEAN | `False` | 🚫 Do not mention text/logos (optional) |
| `pronoun` | STRING | `Person (neutral)` | Accepts: `She/Her`, `He/Him`, `They/Them`, `Person (neutral)` — **accepts STRING link for automation** |
| `character_name` | STRING | `""` | Trigger word + class word (e.g., `rdpsnaiol woman`) |

#### Output

| Output | Type | Description |
|---|---|---|
| `extra_options` | `JOYCAPTION_EXTRA_OPTIONS` | Connect to `JC_GGUF_MLV` extra_options input |

> **Pronoun automation:** `pronoun` accepts STRING connections (not COMBO). Use `StringContains` → `ComfySwitchNode` → `JC_ExtraOptions_MLV.pronoun` for conditional pronoun assignment in batch workflows.

---

### 2. `JC_GGUF_MLV` — JoyCaption GGUF MLV

Custom inference node for LoRA training caption generation. Key improvements over the original JoyCaption GGUF node:

- **LOCKED rules at prompt beginning** — highest attention weight, better constraint adherence
- **Post-processing pipeline** — removes ASSISTANT markers, meta-conversation, brackets, hair references
- **Optimized defaults** for training datasets: `temperature=0.3`, `top_p=0.8`, `top_k=40`, `max_new_tokens=200`
- **Lazy image evaluation** — skips model loading if no image connected
- **Token budget guard** — prompt capped at ~200 tokens, preserving context for caption

#### Inputs

| Input | Type | Default | Description |
|---|---|---|---|
| `model` | COMBO | first available | GGUF model selection (from ComfyUI-JoyCaption) |
| `processing_mode` | COMBO | `Auto` | `Auto`, `GPU`, `CPU` |
| `caption_style` | COMBO | `Descriptive` | `Descriptive`, `Straightforward`, `Booru tag-like` |
| `system_prompt` | STRING | (see below) | System prompt for model behavior |
| `max_new_tokens` | INT | `200` | Output token limit (50–512). 200 ideal for LoRA captions |
| `temperature` | FLOAT | `0.3` | Lower = more factual. 0.3 recommended for LOCKED rules |
| `top_p` | FLOAT | `0.8` | Nucleus sampling — limits vocabulary |
| `top_k` | INT | `40` | Top-K filtering — reduces creative violations |
| `memory_management` | COMBO | `Global Cache` | `Keep in Memory`, `Clear After Run`, `Global Cache` |
| `post_process` | BOOLEAN | `True` | Clean output (ASSISTANT markers, brackets, meta-text) |
| `image` *(optional)* | IMAGE | — | Reference image. If absent, returns empty string without loading model |
| `extra_options` *(optional)* | JOYCAPTION_EXTRA_OPTIONS | — | Connect from `JC_ExtraOptions_MLV` |

Default system prompt:
```
You are a precise image captioner for AI training datasets. Output ONLY the caption — no explanations, no meta-text, no assistant markers.
```

#### Outputs

| Output | Type | Description |
|---|---|---|
| `caption` | STRING | Generated and post-processed caption |
| `prompt_used` | STRING | Actual prompt sent to the model (for debugging) |

#### Prompt Construction Order

```
1. LOCKED restrictions    → "Skip all physical identity traits. ..."
2. Pronoun instruction    → "Refer to the subject using she/her pronouns."
3. Core task              → "Describe this image in natural prose."
4. Subject context        → "The subject is called rdpsnaiol woman."
5. Scope instructions     → "Describe facial expression and emotion. ..."
[Token budget guard: truncates scope if > 800 chars / ~200 tokens]
```

#### Post-Processing Pipeline

The `_clean_caption` function applies 7 cleaning passes:
1. Remove `ASSISTANT:` markers
2. Remove meta-conversation phrases (`Now I'll`, `Let me`, `Here is`, etc.)
3. Truncate at revision separators (`---`, `Revised:`, etc.)
4. Remove `[bracketed content]` (keeps inner text)
5. Remove verbalized instructions
6. **LOCKED attribute removal** — regex removes sentences containing hair references
7. Remove token degeneration (repeated periods, trailing incomplete sentences)

---

### 3. `MLV_Combo_*` — Dynamic Combo Nodes

Auto-generated combo selector nodes from YAML config files in `configs/`. Each subdirectory in `configs/` generates one node.

```
configs/
├── persona/     → MLV Combo (Persona) node
├── clothes/     → MLV Combo (Clothes) node
└── ...          → MLV Combo (<name>) node
```

---

## 🔄 Typical Workflow

```
[Image Batch]
     │
     ▼
[JC_ExtraOptions_MLV]  ←─── [String Contains] ──→ [pronoun: "She/Her"]
     │ extra_options
     ▼
[JC_GGUF_MLV] ←── image ──── [Load Image]
     │ caption
     ▼
[Save Caption / Text File Writer]
```

---

## 📝 LOCKED/UNLOCKED Protocol

This node pack implements the **LOCKED/UNLOCKED captioning protocol** for LoRA training datasets:

- **LOCKED attributes** (never describe): physical identity, hair, eye color, body shape, permanent accessories
  - These are the characteristics the LoRA is being trained to reproduce — describing them in captions confuses training
- **UNLOCKED attributes** (always describe): clothing, pose, expression, lighting, scenery, composition
  - These define what changes between images and teach the model about context

> **Rule of thumb:** If you want the LoRA to learn it, it must be LOCKED. If you want the LoRA to generalize it, it must be UNLOCKED.

---

## 🔧 Compatibility Notes

| Requirement | Version |
|---|---|
| ComfyUI | Latest (needs `lazy: True` support in V1 nodes) |
| ComfyUI-JoyCaption (1038lab) | Latest |
| Python | 3.10+ |
| CUDA | 12.x recommended |
| `llama-cpp-python` | CUDA build required |

> ⚠️ **Upstream coupling:** `joycaption_gguf_mlv.py` imports `JC_GGUF_Models`, `GGUF_MODELS`, `MODEL_SETTINGS`, `_MODEL_CACHE` from `ComfyUI-JoyCaption`. If the upstream API changes, this node requires an update.

---

## 📋 Changelog

| Version | Date | Changes |
|---|---|---|
| **v0.25.0** | 2026-04-06 | Audit Deep fixes: pronoun position (B2), anti-hallucination name_ref (B3), lazy image eval (B4), token budget guard (B5), error marker (B6), clean fallback (B7) |
| **v0.24.0** | 2026-04-01 | `pronoun` COMBO → STRING with `forceInput: True` for DCE automation |
| **v0.11.0** | 2026-03-28 | Initial release: JC_ExtraOptions_MLV + JC_GGUF_MLV (GGUF+llama-cpp backend, 7-layer post-processing) |

---

## 🔗 Related

- [1038lab/ComfyUI-JoyCaption](https://github.com/1038lab/ComfyUI-JoyCaption) — upstream JoyCaption node pack
- [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI) — ComfyUI engine
- [fancyfeast/llama-joycaption-beta-one-hf-llava](https://huggingface.co/fancyfeast/llama-joycaption-beta-one-hf-llava) — GGUF model on HuggingFace
