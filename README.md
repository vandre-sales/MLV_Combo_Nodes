# 🧬 MLV_Combo_Nodes

> **Custom nodes for ComfyUI** — Dynamic prompt builder for image generation + LoRA training caption pipeline with LOCKED/UNLOCKED protocol.

[![ComfyUI](https://img.shields.io/badge/ComfyUI-custom%20node-blue)](https://github.com/comfyanonymous/ComfyUI)
[![Category](https://img.shields.io/badge/category-MLV%20Combo%20Nodes-purple)](https://github.com/vandre-sales/MLV_Combo_Nodes)

---

## 📦 Nodes Included

| Node | Class | Category | Description |
|---|---|---|---|
| **MLV Combo (Ação Corporal)** | `MLV_Combo_acao_corporal` | `MLV Combo Nodes` | Body position, view, arms, legs |
| **MLV Combo (Ação Da Cabeça)** | `MLV_Combo_acao_da_cabeca` | `MLV Combo Nodes` | Head position, facial emotion |
| **MLV Combo (Cenario)** | `MLV_Combo_cenario` | `MLV Combo Nodes` | Location / background |
| **MLV Combo (Fotografia)** | `MLV_Combo_fotografia` | `MLV Combo Nodes` | Photography style, framing |
| **MLV Combo (Iluminacao)** | `MLV_Combo_iluminacao` | `MLV Combo Nodes` | Light color, direction |
| **MLV Combo (Kontext Edit)** | `MLV_Combo_kontext_edit` | `MLV Combo Nodes` | Flux Kontext edit commands (EN) |
| **MLV Combo (Persona)** | `MLV_Combo_persona` | `MLV Combo Nodes` | Archetype, ethnicity, eyes, hair, body, height |
| **MLV Combo (Vestuario)** | `MLV_Combo_vestuario` | `MLV Combo Nodes` | Clothing top/bottom/footwear + colors |
| **JoyCaption Extra MLV** | `JC_ExtraOptions_MLV` | `🧬MLV/📝Captioning` | LOCKED/UNLOCKED extra options for LoRA training captions |
| **JoyCaption GGUF MLV** | `JC_GGUF_MLV` | `🧬MLV/📝Captioning` | Custom GGUF inference with LOCKED-first prompt ordering |

---

## 🔌 Dependencies

### For MLV Combo nodes
- `toml` (Python) — installed automatically via `requirements.txt`

### For JoyCaption nodes (optional)
- [1038lab/ComfyUI-JoyCaption](https://github.com/1038lab/ComfyUI-JoyCaption) — **required** as sibling node pack
  - Provides: `JC_GGUF_Models`, `GGUF_MODELS`, `MODEL_SETTINGS`, `_MODEL_CACHE`
- `llama-cpp-python` compiled with CUDA:
  ```bash
  CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python
  ```
- JoyCaption GGUF model in `ComfyUI/models/LLM/joycaption-gguf/`:
  ```bash
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

# 2. Install Python dependency
pip install toml

# 3. (Optional) Install JoyCaption nodes + llama-cpp-python for JC nodes
git clone https://github.com/1038lab/ComfyUI-JoyCaption.git
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python

# 4. Restart ComfyUI
sudo systemctl restart comfyui
```

---

## 🧬 Node Reference — MLV Combo (*)

### Architecture

The `MLV_Combo_*` nodes are **dynamically generated** at ComfyUI startup. Each subdirectory under `configs/` becomes one node. Each `.txt` file inside a subdirectory becomes one COMBO dropdown input within that node.

```
configs/
├── acao_corporal/        → MLV Combo (Ação Corporal)    [4 inputs]
│   ├── 01_posicao_do_corpo.txt
│   ├── 02_visao_do_corpo.txt
│   ├── 03_posicao_dos_bracos.txt
│   └── 04_posicao_das_pernas.txt
├── acao_da_cabeca/       → MLV Combo (Ação Da Cabeça)   [2 inputs]
│   ├── 01_posicao_da_cabeca.txt
│   └── 02_emocao_do_rosto.txt
├── cenario/              → MLV Combo (Cenario)           [2 inputs]
├── fotografia/           → MLV Combo (Fotografia)        [2 inputs]
├── iluminacao/           → MLV Combo (Iluminacao)        [2 inputs]
├── kontext_edit/         → MLV Combo (Kontext Edit)      [7 inputs — EN]
│   ├── 01_command.txt        (Make, Change, Alter...)
│   ├── 02_target.txt         (the person, the subject...)
│   ├── 03_body_position.txt  (standing, kneeling...)
│   ├── 04_arm_position.txt   (arms relaxed, hands on hips...)
│   ├── 05_leg_position.txt   (legs straight, legs bent...)
│   ├── 06_view.txt           (facing camera, profile view...)
│   └── 07_constraints.txt    (without modifying camera angle...)
├── persona/              → MLV Combo (Persona)           [8 inputs]
│   ├── 01_arquetipos.txt     (baby, child, teen, adult...)
│   ├── 02_etnia.txt          (multiracial, native, asian...)
│   ├── 03_cor_dos_olhos.txt  (blue, green, brown, black...)
│   ├── 04_comprimento_dos_cabelos.txt
│   ├── 05_penteado.txt
│   ├── 06_cor_dos_cabelos.txt
│   ├── 07_estilo_de_corpo.txt
│   └── 08_estatura.txt       (short, medium, tall)
└── vestuario/            → MLV Combo (Vestuario)         [6 inputs]
    ├── 03_parte_de_cima.txt  (top, shirt, blouse...)
    ├── 04_cor_de_cima.txt
    ├── 05_parte_de_baixo.txt (pants, skirt, shorts...)
    ├── 06_cor_de_baixo.txt
    ├── 07_calcado.txt        (sneakers, sandals, boots...)
    └── 08_cor_do_calcado.txt
```

> **Note:** `kontext_edit` attributes are in **English** — designed for Flux Kontext image editing commands. All other categories are in **Portuguese**.

### Inputs (all Combo nodes)

| Input | Type | Description |
|---|---|---|
| `seed` | INT (0–18446744073709551615) | Controls randomness. Changes each run unless fixed. |
| `<attribute_name>` | COMBO | One dropdown per `.txt` file. First option is always `RANDOM`. |
| `previous_prompt` *(optional)* | STRING | Prepend text from another node or previous combo output. Enables chaining. |

### Output

| Output | Type | Description |
|---|---|---|
| `prompt` | STRING | All selected values assembled with `before_value + value + after_value` and joined by `separator`. |

### RANDOM Option

Every dropdown has `RANDOM` as the first option. When selected, the node randomly picks one value from the list using a **local seeded RNG** (`random.Random(seed)`). This ensures:
- Reproducible results when the same seed is reused
- No interference with other nodes' randomness

### Frontend — "Aleatorizar Tudo" Button

Each combo node has an **"Aleatorizar Tudo"** (Randomize All) button added via `web/js/script.js`. Clicking it sets **all COMBO dropdowns** to a random concrete value (excluding the `RANDOM` pseudo-option). The seed input is not affected — use it to lock reproducible batches.

### TOML Config Format

Each `.txt` file is a TOML document with this schema:

```toml
attribute_name = "Posição do corpo"        # Dropdown label in the node UI
before_value = "O seu corpo está em uma posição "  # Prefix added before selected value
after_value = ""                            # Suffix added after selected value
separator = " "                             # Separator between this and next attribute
list_value = [                             # List of options (RANDOM added automatically)
    "suspenso",
    "em pé",
    "inclinado",
    "agachado",
    "ajoelhado",
    "sentado",
    "deitado",
    "fetal"
]
```

**File ordering:** Files are sorted numerically by the prefix `N_` (e.g., `01_`, `02_`). This controls the assembly order in the output string.

### Adding Custom Categories

1. Create a new subdirectory under `configs/`: `configs/minha_categoria/`
2. Add `.txt` files with TOML schema above
3. Restart ComfyUI — `MLV Combo (Minha Categoria)` appears automatically

---

## 🎨 Typical Combo Workflow — Prompt Builder

```
[MLV Combo (Persona)]  ──────────────────────────────┐
     │ prompt (previous)                               │
     ▼                                                 │
[MLV Combo (Vestuario)] ← previous_prompt ───────────┤
     │ prompt                                          │ chaining
     ▼                                                 │
[MLV Combo (Ação Corporal)] ← previous_prompt ───────┤
     │ prompt                                          │
     ▼                                                 │
[MLV Combo (Cenario)] ← previous_prompt ─────────────┘
     │ prompt (final assembled string)
     ▼
[CLIPTextEncode] → [KSampler]
```

---

## 🎨 Typical Combo Workflow — Kontext Edit

```
[MLV Combo (Kontext Edit)]
  Command:       "Make"
  Target:        "the person"
  Body Position: "standing up straight"
  Arm Position:  "with arms relaxed downwards"
  Leg Position:  "with legs straight"
  View/Angle:    "facing the camera directly"
  Constraints:   "without modifying the camera angle"
        │ prompt → "Make the person standing up straight with arms relaxed downwards..."
        ▼
[Flux Kontext Node] ← input_image
```

---

## 📝 Node Reference — JoyCaption Nodes

### `JC_ExtraOptions_MLV` — JoyCaption Extra MLV

Generates a `JOYCAPTION_EXTRA_OPTIONS` output for `JC_GGUF_MLV`. Controls which visual elements to include or exclude in captions, following the LOCKED/UNLOCKED protocol for LoRA training.

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
| `flux_structure` | BOOLEAN | `True` | ⚡ Flux order: subject → expression → clothing → pose → scenery → lighting |
| `include_camera_angle` | BOOLEAN | `False` | 📷 Include camera angle (optional) |
| `include_depth_of_field` | BOOLEAN | `False` | 📷 Include depth of field (optional) |
| `exclude_text_in_image` | BOOLEAN | `False` | 🚫 Do not mention text/logos (optional) |
| `pronoun` | STRING | `Person (neutral)` | Accepts: `She/Her`, `He/Him`, `They/Them`, `Person (neutral)` — **STRING link supported** |
| `character_name` | STRING | `""` | Trigger word + class word (e.g., `rdpsnaiol woman`) |

**Pronoun automation:** `pronoun` is a STRING input with `forceInput: True` — accepts direct connections from other nodes. Use `StringContains` → `ComfySwitchNode` → `pronoun` for batch workflows with automatic pronoun selection.

#### Output

| Output | Type |
|---|---|
| `extra_options` | `JOYCAPTION_EXTRA_OPTIONS` |

---

### `JC_GGUF_MLV` — JoyCaption GGUF MLV

Custom GGUF inference node optimized for LoRA training caption generation.

**Key differences from `JC_GGUF` (original):**
- LOCKED rules positioned at the **beginning** of the prompt (higher attention weight)
- Post-processing removes ASSISTANT markers, meta-conversation, brackets, and hair references
- `image` is **optional** with `lazy: True` — no model loaded if no image connected
- Optimized defaults for training: `temperature=0.3`, `top_p=0.8`, `top_k=40`, `max_new_tokens=200`
- Token budget guard: prompt capped at ~800 chars (~200 tokens)

#### Inputs

| Input | Type | Default | Description |
|---|---|---|---|
| `model` | COMBO | first available | GGUF model (list from ComfyUI-JoyCaption) |
| `processing_mode` | COMBO | `Auto` | `Auto` / `GPU` / `CPU` |
| `caption_style` | COMBO | `Descriptive` | `Descriptive` / `Straightforward` / `Booru tag-like` |
| `system_prompt` | STRING | see below | System prompt |
| `max_new_tokens` | INT | `200` | Token output limit (50–512) |
| `temperature` | FLOAT | `0.3` | Lower = more factual (0.3 recommended) |
| `top_p` | FLOAT | `0.8` | Nucleus sampling |
| `top_k` | INT | `40` | Top-K filtering |
| `memory_management` | COMBO | `Global Cache` | `Keep in Memory` / `Clear After Run` / `Global Cache` |
| `post_process` | BOOLEAN | `True` | Clean ASSISTANT markers, brackets, meta-text |
| `image` *(optional, lazy)* | IMAGE | — | If absent: returns `("", "")` without loading model |
| `extra_options` *(optional)* | JOYCAPTION_EXTRA_OPTIONS | — | From `JC_ExtraOptions_MLV` |

Default system prompt:
```
You are a precise image captioner for AI training datasets. Output ONLY the caption — no explanations, no meta-text, no assistant markers.
```

#### Outputs

| Output | Type | Description |
|---|---|---|
| `caption` | STRING | Post-processed caption |
| `prompt_used` | STRING | Exact prompt sent to model (for debugging) |

#### Prompt Construction Order

```
1. LOCKED restrictions  → highest attention (first in context)
2. Pronoun instruction  → second position (B2 fix)
3. Core task            → "Describe this image in natural prose."
4. Subject context      → "The subject is called <trigger_word>." (only if provided)
5. Scope instructions   → optional visual elements to include
[Token budget: truncates scope if > 800 chars, preserving 1-4]
```

#### Post-Processing (`_clean_caption`)

7 cleaning passes applied when `post_process=True`:
1. Remove `ASSISTANT:` prefixes
2. Remove meta-conversation openers (`Now I'll`, `Let me`, `Here is`...)
3. Truncate at revision markers (`---`, `Revised:`, `Rewritten:`...)
4. Remove `[bracketed content]` — keeps inner text
5. Remove verbalized instructions that leaked into output
6. **Hair reference removal** — regex strips sentences mentioning hair (LOCKED attribute)
7. Degeneration cleanup (repeated `.`, trailing incomplete sentences)

#### Fallback behavior
- If `_clean_caption` produces empty string AND original text doesn't start with meta-phrases: returns raw text
- If original is pure meta-text: returns `[CAPTION_EMPTY]` as explicit marker
- On exception: returns `[CAPTION_ERROR] <message>` + empty `prompt_used`

---

## 🔄 JoyCaption Workflow

```
[Load Image]
     │
     ▼
[JC_ExtraOptions_MLV] ←── [String Contains] ──→ [pronoun STRING]
  character_name: "rdpsnaiol woman"
     │ extra_options (JOYCAPTION_EXTRA_OPTIONS)
     ▼
[JC_GGUF_MLV]
  model: llama-joycaption-beta-one.IQ4_XS.gguf
  temperature: 0.3 | top_p: 0.8 | max_new_tokens: 200
     │ caption (STRING)    │ prompt_used (STRING)
     ▼                     ▼
[Text File Writer]    [Preview Text]
```

---

## 📝 LOCKED/UNLOCKED Protocol

This node pack implements the **LOCKED/UNLOCKED captioning protocol** for LoRA training:

- **LOCKED** (never describe): physical identity, hair, eye color, body shape, permanent accessories
  → The LoRA learns these — mentioning them in captions creates contradictions during training
- **UNLOCKED** (always describe): clothing, pose, expression, lighting, scenery, composition
  → These define context the model must generalize across training images

> **Rule:** If you want the LoRA to reproduce it, LOCK it. If you want flexibility, UNLOCK it.

---

## 🔧 Compatibility

| Requirement | Notes |
|---|---|
| ComfyUI | Latest recommended — needs `lazy: True` V1 node support |
| ComfyUI-JoyCaption (1038lab) | Required for `JC_GGUF_MLV` — provides model loading infrastructure |
| Python | 3.10+ |
| CUDA | 12.x recommended for GPU inference |
| `llama-cpp-python` | Must be compiled with `GGML_CUDA=on` for GPU offload |
| `toml` | Required for MLV_Combo_* — installed via `requirements.txt` |

> ⚠️ `joycaption_gguf_mlv.py` imports directly from `ComfyUI-JoyCaption/JC_GGUF.py`. If the upstream API changes (`JC_GGUF_Models`, `GGUF_MODELS`, `_MODEL_CACHE`), this node needs an update.

---

## 📋 Changelog

| Version | Date | Changes |
|---|---|---|
| **v0.25.0** | 2026-04-06 | Audit Deep: pronoun position B2, anti-hallucination B3, lazy image B4, token budget B5, error marker B6, clean fallback B7 |
| **v0.24.0** | 2026-04-01 | `pronoun` COMBO → STRING + `forceInput: True` for DCE pipeline automation |
| **v0.11.0** | 2026-03-28 | Initial release: MLV_Combo_* (8 categories) + JC_ExtraOptions_MLV + JC_GGUF_MLV |

---

## 🔗 Related

- [1038lab/ComfyUI-JoyCaption](https://github.com/1038lab/ComfyUI-JoyCaption) — upstream JoyCaption nodes
- [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI) — ComfyUI engine
- [fancyfeast/llama-joycaption-beta-one-hf-llava](https://huggingface.co/fancyfeast/llama-joycaption-beta-one-hf-llava) — GGUF model
