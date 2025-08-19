import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "MLV.ComboNodes.RandomizeButton",
    async nodeCreated(node) {
        // O `comfyClass` corresponde ao nome da classe que geramos dinamicamente.
        // Usamos `startsWith` para aplicar a lógica a todos os nós do nosso pacote.
        if (node.comfyClass && node.comfyClass.startsWith("MLV_Combo_")) {
            
            // Adiciona um widget do tipo 'button' ao nó.
            const randomizeButton = node.addWidget("button", "Aleatorizar Tudo", null, () => {
                // Itera sobre todos os widgets do nó.
                for (const w of node.widgets) {
                    // Verifica se o widget é um COMBO e tem opções.
                    if (w.type === "combo" && w.options?.values?.length > 0) {
                        
                        // --- INICIO DA MELHORIA: AJUSTE NO BOTÃO ALEATORIZAR ---
                        // Filtra a lista de opções para remover o item "RANDOM".
                        // Isso garante que o botão sempre escolha um valor concreto e útil.
                        const concrete_options = w.options.values.filter(val => val !== "RANDOM");

                        if (concrete_options.length > 0) {
                            // Seleciona um índice aleatório da lista filtrada (sem o "RANDOM").
                            const randomIndex = Math.floor(Math.random() * concrete_options.length);
                            // Define o valor do widget para a opção aleatória,
                            // o que também atualizará a UI.
                            w.value = concrete_options[randomIndex];
                        }
                        // --- FIM DA MELHORIA ---
                    }
                }
            });

            // Opcional: Adiciona um pouco de margem para um visual mais limpo.
            if (randomizeButton.row_el) {
                randomizeButton.row_el.style.marginTop = "10px";
            }
        }
    }
});