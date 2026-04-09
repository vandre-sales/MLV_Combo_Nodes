# joycaption_extra_mlv.py
# Node: JoyCaption Extra MLV — Opções LOCKED/UNLOCKED para LoRA Training
# Baseado no protocolo 06-dataset-captioning.md (UAIGF)
# Output type: JOYCAPTION_EXTRA_OPTIONS (compatível com 1038lab/ComfyUI-JoyCaption)
# v2: Instruções compactadas para caber no contexto de 512 tokens

MLV_EXTRA_OPTIONS = {
    # === LOCKED ENFORCEMENT (Excluir atributos permanentes) ===
    "exclude_locked_identity": {
        "name": "🔒 Exclude LOCKED Identity",
        "description": "Skip all physical identity traits. Describe ONLY what the person is wearing, doing, and where they are.",
        "default": True,
    },
    "exclude_permanent_accessories": {
        "name": "🔒 Exclude Permanent Accessories",
        "description": "Skip glasses, piercings, birthmarks and tattoos.",
        "default": True,
    },
    # === UNLOCKED ENFORCEMENT (5 elementos obrigatórios — compacto) ===
    "include_facial_expression": {
        "name": "🔓 Include Facial Expression",
        "description": "Describe facial expression and emotion.",
        "default": True,
    },
    "include_pose_action": {
        "name": "🔓 Include Pose & Action",
        "description": "Describe pose, body language and action.",
        "default": True,
    },
    "include_composition": {
        "name": "🔓 Include Composition & Framing",
        "description": "Specify camera framing and composition.",
        "default": True,
    },
    "include_lighting": {
        "name": "🔓 Include Lighting",
        "description": "Describe lighting type, quality and direction.",
        "default": True,
    },
    "include_scenery": {
        "name": "🔓 Include Scenery & Environment",
        "description": "Describe background scenery and environment.",
        "default": True,
    },
    "include_clothing_detail": {
        "name": "🔓 Include Clothing & Temp Accessories",
        "description": "Describe all clothing layers and temporary accessories in detail.",
        "default": True,
    },
    # === STYLE ENFORCEMENT (compacto) ===
    "use_natural_prose": {
        "name": "✍️ Natural Prose (No Tags)",
        "description": "Write natural English prose with complete sentences, not tags.",
        "default": True,
    },
    "avoid_meta_phrases": {
        "name": "✍️ Avoid Meta Phrases",
        "description": "Output ONLY the caption. No conversational text, no 'This image shows', no brackets.",
        "default": True,
    },
    "flux_structure": {
        "name": "⚡ Flux-Optimized Structure",
        "description": "Order: subject, expression, clothing, pose, scenery and lighting.",
        "default": True,
    },
    # === OPCIONAIS (desligados por padrão) ===
    "include_camera_angle": {
        "name": "📷 Include Camera Angle",
        "description": "Include camera angle and vantage point.",
        "default": False,
    },
    "include_depth_of_field": {
        "name": "📷 Include Depth of Field",
        "description": "Specify depth of field and background blur.",
        "default": False,
    },
    "exclude_text_in_image": {
        "name": "🚫 Exclude Text in Image",
        "description": "Do not mention any text or logos in the image.",
        "default": False,
    },
    "exclude_mood_feeling": {
        "name": "🚫 Exclude Mood/Feeling",
        "description": "Stick to objective visual description only.",
        "default": False,
    },
}


class JC_ExtraOptions_MLV:
    """JoyCaption Extra MLV — LOCKED/UNLOCKED options for LoRA training captions.
    
    Outputs JOYCAPTION_EXTRA_OPTIONS type, compatible with 1038lab/ComfyUI-JoyCaption nodes.
    Based on the LOCKED/UNLOCKED protocol (06-dataset-captioning.md).
    v2: Compact instructions to fit within 512 token context window.
    """

    @classmethod
    def INPUT_TYPES(cls):
        inputs = {"required": {}}
        for key, value in MLV_EXTRA_OPTIONS.items():
            inputs["required"][key] = ("BOOLEAN", {"default": value["default"]})
        inputs["required"]["pronoun"] = ("STRING", {
            "default": "Person (neutral)",
            "forceInput": True,
            "tooltip": "Pronoun: She/Her, He/Him, They/Them or Person (neutral). Accepts STRING link for conditional automation.",
        })
        inputs["required"]["character_name"] = (
            "STRING",
            {
                "default": "",
                "multiline": True,
                "placeholder": "Trigger word + class word (e.g., rdpsnaiol woman)",
            },
        )
        return inputs

    RETURN_TYPES = ("JOYCAPTION_EXTRA_OPTIONS",)
    RETURN_NAMES = ("extra_options",)
    FUNCTION = "get_extra_options"
    CATEGORY = "🧬MLV/📝Captioning"

    def get_extra_options(self, character_name, pronoun, **kwargs):
        ret_list = []
        for key, value in MLV_EXTRA_OPTIONS.items():
            if kwargs.get(key, False):
                ret_list.append(value["description"])
        # Add pronoun instruction
        pronoun_map = {
            "She/Her": "Refer to the subject using she/her pronouns.",
            "He/Him": "Refer to the subject using he/him pronouns.",
            "They/Them": "Refer to the subject using they/them pronouns.",
            "Person (neutral)": "Refer to the subject as 'the person' without gendered pronouns.",
        }
        # Normalize pronoun: accept exact match or partial match (case-insensitive)
        pronoun_clean = pronoun.strip() if isinstance(pronoun, str) else "She/Her"
        matched = pronoun_map.get(pronoun_clean)
        if not matched:
            # Fallback: partial case-insensitive match
            pronoun_lower = pronoun_clean.lower()
            for key, val in pronoun_map.items():
                if key.lower() in pronoun_lower or pronoun_lower in key.lower():
                    matched = val
                    break
            if not matched:
                matched = pronoun_map["Person (neutral)"]  # Safe default
        ret_list.append(matched)
        return ([ret_list, character_name],)
