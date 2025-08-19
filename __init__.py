# MLV_Combo_Nodes/__init__.py

import os
from .nodes import create_combo_node_class

# Dicionários que serão preenchidos dinamicamente e exportados
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Caminho absoluto para o diretório de configurações
p = os.path.dirname(os.path.realpath(__file__))
configs_path = os.path.join(p, "configs")

if os.path.exists(configs_path) and os.path.isdir(configs_path):
    # Itera sobre cada subdiretório em 'configs' (ex: 'persona', 'clothes')
    for subdir_name in os.listdir(configs_path):
        subdir_path = os.path.join(configs_path, subdir_name)
        if os.path.isdir(subdir_path):
            # Gera nomes únicos para a classe e para a exibição na UI
            class_name = f"MLV_Combo_{subdir_name}"
            display_name = f"MLV Combo ({subdir_name.replace('_', ' ').title()})"
            
            # Cria a classe do nó usando a fábrica
            NodeClass = create_combo_node_class(class_name, display_name, subdir_path, subdir_name)
            
            # Adiciona a classe e o nome de exibição aos dicionários de mapeamento
            NODE_CLASS_MAPPINGS[class_name] = NodeClass
            NODE_DISPLAY_NAME_MAPPINGS[class_name] = display_name
else:
    print(f"AVISO [MLV Combo Nodes]: Diretório 'configs' não encontrado em '{configs_path}'. Nenhum nó será carregado.")

# Exporta o diretório de JavaScript para o frontend
WEB_DIRECTORY = "./web"

# Garante que o ComfyUI descubra tudo o que foi registrado
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
