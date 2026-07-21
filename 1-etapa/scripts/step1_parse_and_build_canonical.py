import json
import os
import csv

input_cardapio = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\.md\cardapio-dona-rosa.md"
input_rules = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\.md\informacoes-pizzaria-dona-rosa.md"
input_prod_csv = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\.csv\products.csv"

out_dir = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\1-etapa"
os.makedirs(os.path.join(out_dir, "scripts"), exist_ok=True)
os.makedirs(os.path.join(out_dir, "output"), exist_ok=True)

ref_rows = []
with open(input_prod_csv, mode="r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ref_rows.append(row)

ref_map_by_name = {r["name"].strip(): r for r in ref_rows}

print(f"Loaded {len(ref_rows)} rows from current products.csv state reference.")

# Definition of pizza sizes & prices
pizza_sizes = [
    {"size": "Brotinha", "slices": "-", "limits": "1 sabor", "price_trad": 15, "price_esp": 20},
    {"size": "P (4 Fatias)", "slices": "4 Fatias", "limits": "até 2 sabores", "price_trad": 30, "price_esp": 35},
    {"size": "M (6 Fatias)", "slices": "6 Fatias", "limits": "até 3 sabores", "price_trad": 40, "price_esp": 45},
    {"size": "G (8 Fatias)", "slices": "8 Fatias", "limits": "até 3 sabores", "price_trad": 50, "price_esp": 55},
    {"size": "F (10 Fatias)", "slices": "10 Fatias", "limits": "até 4 sabores", "price_trad": 60, "price_esp": 70},
    {"size": "XF (12 Fatias)", "slices": "12 Fatias", "limits": "até 4 sabores", "price_trad": 70, "price_esp": 80},
    {"size": "GG (14 Fatias)", "slices": "14 Fatias", "limits": "até 4 sabores", "price_trad": 90, "price_esp": 100},
    {"size": "Extra 70x70cm (16 Fatias)", "slices": "16 Fatias", "limits": "até 4 sabores", "price_trad": 150, "price_esp": 160},
]

# 14 Tradicionais
pizzas_tradicionais = [
    {"flavor": "Calabresa", "upper_name": "CALABRESA", "ingredients": "Molho, mussarela, calabresa, tomate, cebola e orégano.", "img": "/images/pizzas_cardapio/Calabresa.webp"},
    {"flavor": "A Moda da Casa", "upper_name": "A MODA DA CASA", "ingredients": "Molho, mussarela, presunto, frango, milho, ovo, azeitona e orégano.", "img": "/images/pizzas_cardapio/A Moda da Casa.webp"},
    {"flavor": "Frango com Catupiry", "upper_name": "FRANGO COM CATUPIRY", "ingredients": "Molho, mussarela, frango, catupiry e orégano.", "img": "/images/pizzas_cardapio/Frango com Catupiry.webp"},
    {"flavor": "Bacon com Milho", "upper_name": "BACON COM MILHO", "ingredients": "Molho, mussarela, bacon, milho, tomate, cebola e orégano.", "img": "/images/pizzas_cardapio/Bacon com Milho.webp"},
    {"flavor": "Mista", "upper_name": "MISTA", "ingredients": "Molho, mussarela, presunto, frango, calabresa, milho, azeitona e orégano.", "img": "/images/pizzas_cardapio/Mista.webp"},
    {"flavor": "Mexicana", "upper_name": "MEXICANA", "ingredients": "Molho, mussarela, pimentão, pimenta calabresa, tomate, cebola e orégano.", "img": "/images/pizzas_cardapio/Mexicana.webp"},
    {"flavor": "Portuguesa", "upper_name": "PORTUGUESA", "ingredients": "Molho, mussarela, presunto, tomate, cebola, milho, ovo, catupiry, azeitona e orégano.", "img": "/images/pizzas_cardapio/Portuguesa.webp"},
    {"flavor": "Frango", "upper_name": "FRANGO", "ingredients": "Molho, mussarela, frango, tomate, cebola e orégano.", "img": "/images/pizzas_cardapio/Frango.webp"},
    {"flavor": "Seis Cobertas", "upper_name": "SEIS COBERTAS", "ingredients": "Molho, mussarela, presunto, frango, milho, tomate e orégano.", "img": "/images/pizzas_cardapio/Seis Cobertas.webp"},
    {"flavor": "Pepperoni", "upper_name": "PEPPERONI", "ingredients": "Molho, mussarela, calabresa, bacon, milho, pimentão, tomate, cebola e azeitona.", "img": "/images/pizzas_cardapio/Pepperoni.webp"},
    {"flavor": "Mussarela", "upper_name": "MUSSARELA", "ingredients": "Molho, mussarela, tomate, azeitona e orégano.", "img": "/images/pizzas_cardapio/Mussarela.webp"},
    {"flavor": "Vegetariana", "upper_name": "VEGETARIANA", "ingredients": "Molho, mussarela, tomate, cebola, pimentão, milho, batata palha, azeitona e orégano.", "img": "/images/pizzas_cardapio/Vegetariana.webp"},
    {"flavor": "Balacubana", "upper_name": "BALACUBANA", "ingredients": "Molho, mussarela, presunto, frango, bacon, cebola e azeitona.", "img": "/images/pizzas_cardapio/Balacubana.webp"},
    {"flavor": "Baiana", "upper_name": "BAIANA", "ingredients": "Molho, mussarela, presunto, cebola, ovo, pimenta calabresa, azeitona e orégano.", "img": "/images/pizzas_cardapio/Baiana.webp"},
]

# 7 Especiais
pizzas_especiais = [
    {"flavor": "Nordestina", "upper_name": "NORDESTINA", "ingredients": "Molho, mussarela, carne de sol, cebola roxa, cheiro verde, pimenta calabresa e orégano.", "img": "/images/pizzas_cardapio/Nordestina.webp"},
    {"flavor": "Carne de Sol", "upper_name": "CARNE DE SOL", "ingredients": "Molho, mussarela, carne de sol, cebola, tomate e orégano.", "img": "/images/pizzas_cardapio/Carne de Sol.webp"},
    {"flavor": "4 Queijos", "upper_name": "4 QUEIJOS", "ingredients": "Molho, mussarela, catupiry, requeijão, parmesão, cebola, tomate e orégano.", "img": "/images/pizzas_cardapio/4 Queijos.webp"},
    {"flavor": "Carne de Sol com Banana", "upper_name": "CARNE DE SOL COM BANANA", "ingredients": "Molho, mussarela, carne de sol, banana frita, requeijão, cebola, tomate e orégano.", "img": "/images/pizzas_cardapio/Carne de Sol com Banana.webp"},
    {"flavor": "Nutella Premium", "upper_name": "NUTELLA PREMIUM", "ingredients": "Mussarela, creme de avelã, leite ninho e morangos.", "img": "/images/pizzas_cardapio/Nutella Premium.webp"},
    {"flavor": "Lombo Canadense", "upper_name": "LOMBO CANADENSE", "ingredients": "Molho, mussarela, lombo canadense, requeijão, bacon, abacaxi, cebola, tomate e orégano.", "img": "/images/pizzas_cardapio/Lombo Canadense.webp"},
    {"flavor": "Escondidinho", "upper_name": "ESCONDIDINHO", "ingredients": "Molho, mussarela, carne de sol, catupiry, batata palha, azeitona, cebola, tomate e orégano.", "img": "/images/pizzas_cardapio/Escondidinho.webp"},
]

# 4 Doces
pizzas_doces = [
    {"flavor": "Abacaxi", "upper_name": "ABACAXI", "ingredients": "Mussarela, abacaxi e leite condensado.", "img": "/images/pizzas_cardapio/Abacaxi.webp"},
    {"flavor": "Banana", "upper_name": "BANANA", "ingredients": "Mussarela, banana, canela e leite condensado.", "img": "/images/pizzas_cardapio/Banana.webp"},
    {"flavor": "Chocolate", "upper_name": "CHOCOLATE", "ingredients": "Mussarela, chocolate e leite condensado.", "img": "/images/pizzas_cardapio/Chocolate Granulado.webp"},
    {"flavor": "Pizza de Coco", "upper_name": "PIZZA DE COCO", "ingredients": "Mussarela, coco ralado e chocolate.", "img": "/images/pizzas_cardapio/Pizza de Coco.webp"},
]

# Pastéis (10 pastéis: 7 salgados, 3 doces)
pasteis = [
    {"name": "Pastel - FRANGO COM CATUPIRY", "type": "Pastel Salgado", "flavor": "FRANGO COM CATUPIRY", "price": 8, "img": "/images/pasteis/Frango com Catupiry.webp"},
    {"name": "Pastel - FRANGO", "type": "Pastel Salgado", "flavor": "FRANGO", "price": 8, "img": "/images/pasteis/Frango.webp"},
    {"name": "Pastel - QUEIJO", "type": "Pastel Salgado", "flavor": "QUEIJO", "price": 8, "img": "/images/pasteis/Queijo.webp"},
    {"name": "Pastel - QUEIJO E PRESUNTO", "type": "Pastel Salgado", "flavor": "QUEIJO E PRESUNTO", "price": 10, "img": "/images/pasteis/Queijo e Presunto.webp"},
    {"name": "Pastel - PIZZA", "type": "Pastel Salgado", "flavor": "PIZZA", "price": 10, "img": "/images/pasteis/Pizza.webp"},
    {"name": "Pastel - CARNE", "type": "Pastel Salgado", "flavor": "CARNE", "price": 10, "img": "/images/pasteis/Carne.webp"},
    {"name": "Pastel - CARNE E QUEIJO", "type": "Pastel Salgado", "flavor": "CARNE E QUEIJO", "price": 10, "img": "/images/pasteis/Carne e Queijo.webp"},
    {"name": "Pastel - ROMEU E JULIETA", "type": "Pastel Doce", "flavor": "ROMEU E JULIETA", "price": 10, "img": "/images/pasteis/Romeu e Julieta.webp"},
    {"name": "Pastel - DOÇURA", "type": "Pastel Doce", "flavor": "DOÇURA", "price": 10, "img": "/images/pasteis/Doçura.webp"},
    {"name": "Pastel - CHOCOLATE COM QUEIJO", "type": "Pastel Doce", "flavor": "CHOCOLATE COM QUEIJO", "price": 10, "img": "/images/pasteis/Chocolate com Queijo.webp"},
]

# Porções e Aperitivos (10 items)
porcoes = [
    {"name": "Macarronada - Frango", "description": "Deliciosa macarronada caseira preparada na hora. Opção: Frango.", "price": 20, "img": "/images/porcos/macarronada.webp"},
    {"name": "Macarronada - Carne", "description": "Deliciosa macarronada caseira preparada na hora. Opção: Carne.", "price": 20, "img": "/images/porcos/macarronada.webp"},
    {"name": "Batata Frita", "description": "Batata frita crocante acompanhada de molho.", "price": 16, "img": "/images/porcos/batata-frita.webp"},
    {"name": "Tábua de Frios", "description": "Salame com limão, cubos de queijo e azeitona.", "price": 30, "img": "/images/porcos/tabua-de-frios.webp"},
    {"name": "Calabresa Acebolada", "description": "Calabresa fatiada com cebola frita e farofa.", "price": 15, "img": "/images/porcos/calabresa-acebolada.webp"},
    {"name": "Ovo de Codorna", "description": "Ovos de codorna temperados com orégano.", "price": 10, "img": "/images/porcos/ovo-de-codorna.webp"},
    {"name": "Mix de Boteco", "description": "Porção de queijo temperado com orégano.", "price": 15, "img": "/images/porcos/mix-de-boteco.webp"},
    {"name": "Aperitivo de Queijo Temperado", "description": "Cubos de queijo temperados com orégano e azeitona.", "price": 20, "img": "/images/porcos/aperitivo-queijo-temperado.webp"},
    {"name": "Clássico com Fritas", "description": "Filé com batata frita, farofa, vinagrete e molho.", "price": 45, "img": "/images/porcos/classico-com-fritas.webp"},
    {"name": "Aperitivo Nordestino", "description": "Carne de sol com vinagrete e farofa.", "price": 45, "img": "/images/porcos/aperitivo-nordestino.webp"},
]

# Bebidas (22 items)
bebidas = [
    {"name": "Suco Natural - Laranja", "description": "Suco natural. Opção: Laranja. Sabores disponíveis: Laranja, Maracujá, Cajá, Acerola e Bacuri.", "price": 8, "img": "/images/bebidas/suco_natural.webp"},
    {"name": "Suco Natural - Maracujá", "description": "Suco natural. Opção: Maracujá. Sabores disponíveis: Laranja, Maracujá, Cajá, Acerola e Bacuri.", "price": 8, "img": "/images/bebidas/suco_natural.webp"},
    {"name": "Suco Natural - Cajá", "description": "Suco natural. Opção: Cajá. Sabores disponíveis: Laranja, Maracujá, Cajá, Acerola e Bacuri.", "price": 8, "img": "/images/bebidas/suco_natural.webp"},
    {"name": "Suco Natural - Acerola", "description": "Suco natural. Opção: Acerola. Sabores disponíveis: Laranja, Maracujá, Cajá, Acerola e Bacuri.", "price": 8, "img": "/images/bebidas/suco_natural.webp"},
    {"name": "Suco Natural - Bacuri", "description": "Suco natural. Opção: Bacuri. Sabores disponíveis: Laranja, Maracujá, Cajá, Acerola e Bacuri.", "price": 8, "img": "/images/bebidas/suco_natural.webp"},
    {"name": "Água - Sem Gás", "description": "Água mineral sem gás.", "price": 4, "img": "/images/bebidas/agua_v3.webp"},
    {"name": "Água - Com Gás", "description": "Água mineral com gás.", "price": 5, "img": "/images/bebidas/agua_v3.webp"},
    {"name": "Coca-Cola 2 Litros - Original", "description": "Refrigerante Coca-Cola 2 litros. Opção: Original.", "price": 15, "img": "/images/bebidas/coca_cola_2l.webp"},
    {"name": "Coca-Cola 2 Litros - Zero", "description": "Refrigerante Coca-Cola 2 litros. Opção: Zero.", "price": 15, "img": "/images/bebidas/coca_cola_2l.webp"},
    {"name": "Refrigerante 2 Litros - Guaraná Jesus", "description": "Refrigerante 2 litros. Opção: Guaraná Jesus.", "price": 15, "img": "/images/bebidas/refrigerante_2l.webp"},
    {"name": "Refrigerante 2 Litros - Guaraná", "description": "Refrigerante 2 litros. Opção: Guaraná.", "price": 15, "img": "/images/bebidas/refrigerante_2l.webp"},
    {"name": "Refrigerante Retornável (1L) - Coca-Cola", "description": "Refrigerante retornável 1 litro Coca-Cola. (Obrigatório possuir o casco para troca)", "price": 8, "img": "/images/bebidas/refrigerante_retornavel.webp"},
    {"name": "Refrigerante 1 Litro - Coca-Cola", "description": "Refrigerante 1 litro. Opção: Coca-Cola.", "price": 9, "img": "/images/bebidas/refrigerante_1l.webp"},
    {"name": "Refrigerante 1 Litro - Coca-Cola Zero", "description": "Refrigerante 1 litro. Opção: Coca-Cola Zero.", "price": 9, "img": "/images/bebidas/refrigerante_1l.webp"},
    {"name": "Refrigerante 1 Litro - Guaraná Jesus", "description": "Refrigerante 1 litro. Opção: Guaraná Jesus.", "price": 9, "img": "/images/bebidas/refrigerante_1l.webp"},
    {"name": "Refrigerante 1 Litro - Guaraná", "description": "Refrigerante 1 litro. Opção: Guaraná.", "price": 9, "img": "/images/bebidas/refrigerante_1l.webp"},
    {"name": "Refrigerante Lata - Coca-Cola", "description": "Refrigerante em lata. Opção: Coca-Cola.", "price": 5, "img": "/images/bebidas/refrigerante_lata.webp"},
    {"name": "Refrigerante Lata - Coca-Cola Zero", "description": "Refrigerante em lata. Opção: Coca-Cola Zero.", "price": 5, "img": "/images/bebidas/refrigerante_lata.webp"},
    {"name": "Refrigerante Lata - Guaraná Jesus", "description": "Refrigerante em lata. Opção: Guaraná Jesus.", "price": 5, "img": "/images/bebidas/refrigerante_lata.webp"},
    {"name": "Refrigerante Lata - Guaraná", "description": "Refrigerante em lata. Opção: Guaraná.", "price": 5, "img": "/images/bebidas/refrigerante_lata.webp"},
    {"name": "Refrigerante Lata - Laranja", "description": "Refrigerante em lata. Opção: Laranja.", "price": 5, "img": "/images/bebidas/refrigerante_lata.webp"},
    {"name": "Refrigerante KS (290ml) - Coca-Cola", "description": "Refrigerante KS 290ml Coca-Cola. (Obrigatório possuir o casco para troca)", "price": 4, "img": "/images/bebidas/ks.webp"},
]

old_bebida_map = {
    "Coca-Cola 2 Litros - Original": "Coca-Cola 2L - Original",
    "Coca-Cola 2 Litros - Zero": "Coca-Cola 2L - Zero",
    "Refrigerante 2 Litros - Guaraná Jesus": "Refrigerante 2L - Jesus",
    "Refrigerante 2 Litros - Guaraná": "Refrigerante 2L - Guaraná",
    "Refrigerante Retornável (1L) - Coca-Cola": "Refrigerante Retornável - Coca",
    "Refrigerante 1 Litro - Coca-Cola": "Refrigerante 1L - Coca",
    "Refrigerante 1 Litro - Coca-Cola Zero": "Refrigerante 1L - Coca Zero",
    "Refrigerante 1 Litro - Guaraná Jesus": "Refrigerante 1L - Jesus",
    "Refrigerante 1 Litro - Guaraná": "Refrigerante 1L - Guaraná",
    "Refrigerante Lata - Coca-Cola": "Refrigerante Lata - Coca",
    "Refrigerante Lata - Coca-Cola Zero": "Refrigerante Lata - Coca Zero",
    "Refrigerante Lata - Guaraná Jesus": "Refrigerante Lata - Jesus",
    "Refrigerante Lata - Guaraná": "Refrigerante Lata - Guaraná",
    "Refrigerante KS (290ml) - Coca-Cola": "KS - Coca"
}

all_canonical_products = []

# Build 112 Pizzas Tradicionais
for p in pizzas_tradicionais:
    for s in pizza_sizes:
        size_str = s["size"]
        prod_name = f"{p['upper_name']} - {size_str}"
        desc = f"Ingredientes: {p['ingredients']} | Tamanho: {size_str.split(' ')[0]} | Fatias: {s['slices']} | Limite de sabores: {s['limits']} | Tabela de preço: Tradicionais/Doces"
        price_val = str(s["price_trad"])
        
        ref_entry = ref_map_by_name.get(prod_name)
        img_url = ref_entry["image_url"] if ref_entry else p["img"]
        active_val = ref_entry["active"] if ref_entry else "true"
        
        all_canonical_products.append({
            "name": prod_name,
            "description": desc,
            "price": price_val,
            "category": "Pizza Tradicional",
            "image_url": img_url,
            "active": active_val
        })

# Build 56 Pizzas Especiais
for p in pizzas_especiais:
    for s in pizza_sizes:
        size_str = s["size"]
        prod_name = f"{p['upper_name']} - {size_str}"
        desc = f"Ingredientes: {p['ingredients']} | Tamanho: {size_str.split(' ')[0]} | Fatias: {s['slices']} | Limite de sabores: {s['limits']} | Tabela de preço: Especiais"
        price_val = str(s["price_esp"])
        
        ref_entry = ref_map_by_name.get(prod_name)
        img_url = ref_entry["image_url"] if ref_entry else p["img"]
        active_val = ref_entry["active"] if ref_entry else "true"
        
        all_canonical_products.append({
            "name": prod_name,
            "description": desc,
            "price": price_val,
            "category": "Pizza Especial",
            "image_url": img_url,
            "active": active_val
        })

# Build 32 Pizzas Doces
for p in pizzas_doces:
    for s in pizza_sizes:
        size_str = s["size"]
        prod_name = f"{p['upper_name']} - {size_str}"
        desc = f"Ingredientes: {p['ingredients']} | Tamanho: {size_str.split(' ')[0]} | Fatias: {s['slices']} | Limite de sabores: {s['limits']} | Tabela de preço: Tradicionais/Doces"
        price_val = str(s["price_trad"])
        
        ref_entry = ref_map_by_name.get(prod_name)
        img_url = ref_entry["image_url"] if ref_entry else p["img"]
        active_val = ref_entry["active"] if ref_entry else "true"
        
        all_canonical_products.append({
            "name": prod_name,
            "description": desc,
            "price": price_val,
            "category": "Pizza Doce",
            "image_url": img_url,
            "active": active_val
        })

# Build 10 Pastéis
for pas in pasteis:
    prod_name = pas["name"]
    desc = f"Tipo: {pas['type']} | Sabor: {pas['flavor']}"
    price_val = str(pas["price"])
    ref_entry = ref_map_by_name.get(prod_name)
    img_url = ref_entry["image_url"] if ref_entry else pas["img"]
    active_val = ref_entry["active"] if ref_entry else "true"
    
    all_canonical_products.append({
        "name": prod_name,
        "description": desc,
        "price": price_val,
        "category": "Pastel",
        "image_url": img_url,
        "active": active_val
    })

# Build 10 Porções e Aperitivos
for por in porcoes:
    prod_name = por["name"]
    desc = por["description"]
    price_val = str(por["price"])
    ref_entry = ref_map_by_name.get(prod_name)
    img_url = ref_entry["image_url"] if ref_entry else por["img"]
    active_val = ref_entry["active"] if ref_entry else "true"
    
    all_canonical_products.append({
        "name": prod_name,
        "description": desc,
        "price": price_val,
        "category": "Porções e Aperitivos",
        "image_url": img_url,
        "active": active_val
    })

# Build 22 Bebidas
for beb in bebidas:
    prod_name = beb["name"]
    desc = beb["description"]
    price_val = str(beb["price"])
    
    ref_entry = ref_map_by_name.get(prod_name)
    if not ref_entry and prod_name in old_bebida_map:
        ref_entry = ref_map_by_name.get(old_bebida_map[prod_name])
        
    img_url = ref_entry["image_url"] if ref_entry else beb["img"]
    active_val = ref_entry["active"] if ref_entry else "true"
    
    all_canonical_products.append({
        "name": prod_name,
        "description": desc,
        "price": price_val,
        "category": "Bebidas",
        "image_url": img_url,
        "active": active_val
    })

print(f"Generated {len(all_canonical_products)} canonical items in total.")

category_counts = {}
for p in all_canonical_products:
    cat = p["category"]
    category_counts[cat] = category_counts.get(cat, 0) + 1

print("\n--- CATEGORY BREAKDOWN ---")
for cat, count in category_counts.items():
    print(f" - {cat}: {count} items")

names_list = [p["name"] for p in all_canonical_products]
duplicate_names = set([n for n in names_list if names_list.count(n) > 1])
assert len(duplicate_names) == 0, f"Duplicate natural keys found: {duplicate_names}"
print("Natural key uniqueness check passed: 0 duplicates.")

json_out = os.path.join(out_dir, "output", "canonical_catalog.json")
with open(json_out, "w", encoding="utf-8") as f:
    json.dump(all_canonical_products, f, indent=2, ensure_ascii=False)

csv_out = os.path.join(out_dir, "output", "products.corrected.csv")
fieldnames = ["name", "description", "price", "category", "image_url", "active"]
with open(csv_out, mode="w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_canonical_products)

csv_root_out = r"c:\Users\Administrator\Desktop\N8N_Pizzaria\.csv\products.corrected.csv"
with open(csv_root_out, mode="w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_canonical_products)
