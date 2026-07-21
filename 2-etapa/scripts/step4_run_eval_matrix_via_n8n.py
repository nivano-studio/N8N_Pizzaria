import json
import os
import datetime

out_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\2-etapa\output"
os.makedirs(out_dir, exist_ok=True)

test_cases = [
    {
        "class_id": 1,
        "class_name": "Nome Exato",
        "query": "CALABRESA - G (8 Fatias)",
        "expected_facts": ["Preço R$ 50", "Molho, mussarela, calabresa", "8 Fatias"],
        "expected_top_1_name": "CALABRESA - G (8 Fatias)"
    },
    {
        "class_id": 2,
        "class_name": "Abreviação Comum",
        "query": "coca 2l original",
        "expected_facts": ["Refrigerante Coca-Cola 2 litros", "Preço R$ 15"],
        "expected_top_1_name": "Coca-Cola 2 Litros - Original"
    },
    {
        "class_id": 3,
        "class_name": "Ingrediente",
        "query": "carne de sol banana frita requeijao",
        "expected_facts": ["Carne de Sol com Banana", "Mussarela, carne de sol, banana frita, requeijão"],
        "expected_top_1_name": "CARNE DE SOL COM BANANA"
    },
    {
        "class_id": 4,
        "class_name": "Categoria",
        "query": "Pasteis doces cardapio",
        "expected_facts": ["Pastel Doce", "Romeu e Julieta", "Doçura", "Chocolate com Queijo"],
        "expected_top_1_name": "Pastel"
    },
    {
        "class_id": 5,
        "class_name": "Tamanho + Preço",
        "query": "Pizza Extra 70x70cm 16 Fatias preco especial",
        "expected_facts": ["Preço (Especiais) R$ 160", "16 Fatias", "70x70cm"],
        "expected_top_1_name": "NORDESTINA - Extra 70x70cm (16 Fatias)"
    },
    {
        "class_id": 6,
        "class_name": "Limite de Sabores",
        "query": "qual o limite de sabores da pizza Brotinha",
        "expected_facts": ["Limite de sabores: 1 sabor"],
        "expected_top_1_name": "Brotinha"
    },
    {
        "class_id": 7,
        "class_name": "Bebida + Volume",
        "query": "refrigerante lata guarana jesus",
        "expected_facts": ["Refrigerante em lata", "Guaraná Jesus", "Preço R$ 5"],
        "expected_top_1_name": "Refrigerante Lata - Guaraná Jesus"
    },
    {
        "class_id": 8,
        "class_name": "Exigência de Casco",
        "query": "refrigerante retornavel 1 litro casco",
        "expected_facts": ["Obrigatório possuir o casco para troca", "Preço R$ 8"],
        "expected_top_1_name": "Refrigerante Retornável (1L) - Coca-Cola"
    },
    {
        "class_id": 9,
        "class_name": "Item Inexistente",
        "query": "Sushi de Salmão Temaki",
        "expected_facts": ["Não disponível no cardápio Dona Rosa"],
        "expected_top_1_name": "Nenhum resultado relevante"
    },
    {
        "class_id": 10,
        "class_name": "Consulta de Conteúdo Antigo (Sanitização)",
        "query": "o site informa Sabor da Terra",
        "expected_facts": ["Zero ocorrências de 'o site informa' ou 'Sabor da Terra'"],
        "expected_top_1_name": "Sem conteúdo legado"
    }
]

out_matrix = os.path.join(out_dir, "hybrid_search_matrix_definition.json")
with open(out_matrix, "w", encoding="utf-8") as f:
    json.dump(test_cases, f, indent=2, ensure_ascii=False)

print(f"Saved 10-class hybrid search matrix definition to {out_matrix}")
