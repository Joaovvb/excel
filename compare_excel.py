import pandas as pd
import sys

def compare_excels(path1, path2, cols):
    # lê só as colunas que o usuário pediu
    df1 = pd.read_excel(path1, usecols=cols)
    df2 = pd.read_excel(path2, usecols=cols)

    # marca a origem
    df1["_source"] = "arquivo1"
    df2["_source"] = "arquivo2"

    # junta tudo e identifica duplicados
    all_df = pd.concat([df1, df2], ignore_index=True)
    mask_dup = all_df.duplicated(subset=cols, keep=False)

    iguais = all_df[mask_dup].drop_duplicates(subset=cols)
    diferentes = all_df[~mask_dup]

    return iguais, diferentes

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python compare_excel.py arquivo1.xlsx arquivo2.xlsx Col1 Col2 ...")
        sys.exit(1)

    path1, path2, *cols = sys.argv[1:]
    iguais, diffs = compare_excels(path1, path2, cols)

    print("\n=== Valores Iguais ===")
    print(iguais.to_string(index=False))
    print("\n=== Valores Diferentes (com origem) ===")
    print(diffs.to_string(index=False))
