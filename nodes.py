# MLV_Combo_Nodes/nodes.py

import os
import toml
import re
import random

# Global cache to avoid repeated disk reads during the session.
CONFIG_CACHE = {}

def load_configs_from_directory(subdir_path, subdir_name):
    """
    Loads, validates, and caches TOML configurations from a specific directory.
    Returns an ordered list of configuration dictionaries.
    """
    if subdir_path in CONFIG_CACHE:
        return CONFIG_CACHE[subdir_path]

    if not os.path.isdir(subdir_path):
        print(f"WARNING [MLV Combo Nodes]: Configuration directory '{subdir_path}' not found.")
        return []

    def get_sort_key(filename):
        match = re.match(r"(\d+)_", filename)
        return int(match.group(1)) if match else float('inf')

    try:
        config_files = sorted(
            [f for f in os.listdir(subdir_path) if f.endswith('.txt')],
            key=get_sort_key
        )
    except Exception as e:
        print(f"ERROR [MLV Combo Nodes]: Failed to list or sort files in '{subdir_path}': {e}")
        return []

    configs = []
    for filename in config_files:
        try:
            file_path = os.path.join(subdir_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)

            if "attribute_name" not in data or "list_value" not in data:
                print(f"WARNING [MLV Combo Nodes]: File '{filename}' in '{subdir_name}' skipped. Missing 'attribute_name' or 'list_value'.")
                continue
            
            configs.append({
                "attribute_name": data["attribute_name"],
                "list_value": [str(item) for item in data["list_value"]],
                "before_value": data.get("before_value", ""),
                "after_value": data.get("after_value", ""),
                "separator": data.get("separator", " "),
            })
        except Exception as e:
            print(f"ERROR [MLV Combo Nodes]: Failed to process '{filename}' in '{subdir_name}': {e}. File ignored.")
            
    CONFIG_CACHE[subdir_path] = configs
    return configs

def create_combo_node_class(class_name, display_name, subdir_path, subdir_name):
    """
    Class factory: Dynamically generates a ComfyUI node class.
    """
    
    node_configs = load_configs_from_directory(subdir_path, subdir_name)

    class DynamicComboNode:
        CATEGORY = "MLV Combo Nodes"
        RETURN_TYPES = ("STRING", )
        RETURN_NAMES = ("prompt",)
        FUNCTION = "execute"

        @classmethodgit
        def INPUT_TYPES(cls):
            # --- INICIO DA MELHORIA: ADIÇÃO DA SEMENTE (SEED) ---
            # Adiciona uma entrada de semente. Isso força o ComfyUI a reexecutar o nó
            # a cada vez, pois a semente muda a cada execução (a menos que fixada).
            # Esta é a maneira padrão de lidar com operações aleatórias.
            required = {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
            # --- END OF IMPROVEMENT ---

            if not node_configs:
                required["error"] = ("STRING", {"default": f"No valid config files found in '{subdir_name}'. Check console for errors.", "multiline": True})
                return {"required": required}

            for config in node_configs:
                attr_name = config["attribute_name"]
                value_list_with_random = ["RANDOM"] + config["list_value"]
                required[attr_name] = (value_list_with_random,)
            
            optional = {
                "previous_prompt": ("STRING", {
                    "multiline": True,
                    "default": ""
                })
            }
            
            return {"required": required, "optional": optional}

        # --- INICIO DA MELHORIA: RECEBENDO A SEMENTE NA EXECUÇÃO ---
        # The seed is now an explicit parameter of the execute method.
        def execute(self, seed, **kwargs):
        # --- END OF IMPROVEMENT ---
            if not node_configs:
                return ("Error: No valid configuration files loaded.",)

            # --- INICIO DA MELHORIA: GERADOR ALEATÓRIO LOCAL ---
            # Creates a local instance of the random number generator based on the seed.
            # This ensures that the randomness of this node is contained and reproducible
            # if the same seed is used, without affecting other nodes.
            rng = random.Random(seed)
            # --- FIM DA MELHORIA ---
            
            previous_prompt = kwargs.get('previous_prompt', None)

            prompt_fragments = []
            for config in node_configs:
                attr_name = config["attribute_name"]
                selected_value = kwargs.get(attr_name, "")
                
                if selected_value == "RANDOM":
                    original_list = config["list_value"]
                    if original_list:
                        # --- START OF IMPROVEMENT: USING THE LOCAL GENERATOR ---
                        # Uses the local generator (rng) instead of the global one (random).
                        selected_value = rng.choice(original_list)
                        # --- FIM DA MELHORIA ---
                    else:
                        selected_value = ""
                
                if selected_value:
                    fragment = f"{config['before_value']}{selected_value}{config['after_value']}"
                    prompt_fragments.append({
                        "text": fragment,
                        "separator": config['separator']
                    })
            
            current_prompt_parts = []
            for i, p in enumerate(prompt_fragments):
                current_prompt_parts.append(p["text"])
                if i < len(prompt_fragments) - 1:
                    current_prompt_parts.append(p["separator"])
            
            current_prompt = "".join(current_prompt_parts)
            current_prompt = re.sub(r'\s+', ' ', current_prompt).strip()
            
            final_prompt_parts = []
            if previous_prompt and previous_prompt.strip():
                final_prompt_parts.append(previous_prompt.strip())
            
            if current_prompt:
                final_prompt_parts.append(current_prompt)
            
            final_prompt = " ".join(final_prompt_parts)
            
            return (final_prompt,)

    DynamicComboNode.__name__ = class_name
    DynamicComboNode.DISPLAY_NAME = display_name
    
    return DynamicComboNode