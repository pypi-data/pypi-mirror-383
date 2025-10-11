import os
import json
import pandas as pd
from typing import Dict

def save(data: Dict[str, pd.DataFrame],
         output_dir: str = "exports",
         prefix: str = "ALL",
         period: str = "",
         format: str = "csv") -> None:
    """
    Salva os DataFrames do beta-Cynosure em CSV ou JSON.

    Parâmetros:
        data: dicionário retornado por get_all() (chaves: 'dfp', 'itr', 'fre')
        output_dir: diretório onde os arquivos serão salvos (default: 'exports')
        prefix: ticker ou nome da empresa/grupo (usado nos nomes dos arquivos)
        period: string do período (ex: '2023-2024')
        format: 'csv' ou 'json'

    Exemplo:
        data = get_all("2023-2024", ["PETR"])
        save(data, prefix="PETR", period="2023-2024", format="json")
    """
    os.makedirs(output_dir, exist_ok=True)
    fmt = format.lower()

    for key, df in data.items():
        if df is None or df.empty:
            continue

        filename = f"{key}_{prefix}_{period}.{fmt}".replace(" ", "_")
        path = os.path.join(output_dir, filename)

        if fmt == "csv":
            df.to_csv(path, index=False, encoding="utf-8-sig")
        elif fmt == "json":
            with open(path, "w", encoding="utf-8") as f:
                json.dump(json.loads(df.to_json(orient="records", force_ascii=False)), f, indent=2, ensure_ascii=False)
        else:
            raise ValueError("Formato inválido. Use 'csv' ou 'json'.")

    print(f"Arquivos exportados para: {os.path.abspath(output_dir)}")
