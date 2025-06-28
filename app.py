import streamlit as st
import pandas as pd

st.title("Comparador de Excel – Apenas Valores em Comum")

file1 = st.file_uploader("Primeiro arquivo (.xlsx)", type=["xlsx"])
file2 = st.file_uploader("Segundo arquivo (.xlsx)", type=["xlsx"])

def read_sheets_with_selection(file, selected_sheets=None):
    xls = pd.ExcelFile(file)
    all_sheets = xls.sheet_names
    if selected_sheets is None or selected_sheets == []:
        dfs = pd.read_excel(file, sheet_name=None, dtype=str)
        df_all = pd.concat(dfs.values(), ignore_index=True)
    else:
        dfs = []
        for sheet in selected_sheets:
            dfs.append(pd.read_excel(file, sheet_name=sheet, dtype=str))
        df_all = pd.concat(dfs, ignore_index=True)
    df_all = df_all.dropna(axis=1, how='all')
    return df_all

if file1 and file2:
    st.sidebar.header("Configuração do arquivo 1")
    all_sheets_1 = pd.ExcelFile(file1).sheet_names
    use_all_1 = st.sidebar.checkbox("Usar todas as abas do arquivo 1?", value=True)
    selected_sheets_1 = all_sheets_1
    if not use_all_1:
        selected_sheets_1 = st.sidebar.multiselect("Selecione as abas do arquivo 1", all_sheets_1, default=all_sheets_1)

    st.sidebar.header("Configuração do arquivo 2")
    all_sheets_2 = pd.ExcelFile(file2).sheet_names
    use_all_2 = st.sidebar.checkbox("Usar todas as abas do arquivo 2?", value=True)
    selected_sheets_2 = all_sheets_2
    if not use_all_2:
        selected_sheets_2 = st.sidebar.multiselect("Selecione as abas do arquivo 2", all_sheets_2, default=all_sheets_2)

    df1 = read_sheets_with_selection(file1, selected_sheets_1)
    df2 = read_sheets_with_selection(file2, selected_sheets_2)

    st.sidebar.header("Chaves para comparação")
    key1 = st.sidebar.selectbox("Chave no arquivo 1", df1.columns, key="key1")
    key2 = st.sidebar.selectbox("Chave no arquivo 2", df2.columns, key="key2")

    if "filters1" not in st.session_state:
        st.session_state.filters1 = []
    if "filters2" not in st.session_state:
        st.session_state.filters2 = []
    if "result_keys" not in st.session_state:
        st.session_state.result_keys = []
    if "df1_filtered" not in st.session_state:
        st.session_state.df1_filtered = pd.DataFrame()
    if "df2_filtered" not in st.session_state:
        st.session_state.df2_filtered = pd.DataFrame()

    with st.sidebar.form(key="filters_form"):
        if st.form_submit_button("➕ Adicionar filtro no arquivo 1"):
            st.session_state.filters1.append({"col": None, "val": None})
        if st.form_submit_button("➕ Adicionar filtro no arquivo 2"):
            st.session_state.filters2.append({"col": None, "val": None})

    st.sidebar.subheader("Filtros Arquivo 1")
    for i, filt in enumerate(st.session_state.filters1):
        col = st.sidebar.selectbox(
            f"Filtro {i+1}: coluna",
            [None] + list(df1.columns),
            index=([None] + list(df1.columns)).index(filt["col"]) if filt["col"] in df1.columns else 0,
            key=f"f1_col_{i}"
        )
        val = None
        if col:
            opts = df1[col].dropna().unique().tolist()
            val = st.sidebar.selectbox(
                f"Filtro {i+1}: valor",
                ["(todos)"] + opts,
                key=f"f1_val_{i}"
            )
            if val == "(todos)":
                val = None
        st.session_state.filters1[i] = {"col": col, "val": val}

    st.sidebar.subheader("Filtros Arquivo 2")
    for i, filt in enumerate(st.session_state.filters2):
        col = st.sidebar.selectbox(
            f"Filtro {i+1}: coluna",
            [None] + list(df2.columns),
            index=([None] + list(df2.columns)).index(filt["col"]) if filt["col"] in df2.columns else 0,
            key=f"f2_col_{i}"
        )
        val = None
        if col:
            opts = df2[col].dropna().unique().tolist()
            val = st.sidebar.selectbox(
                f"Filtro {i+1}: valor",
                ["(todos)"] + opts,
                key=f"f2_val_{i}"
            )
            if val == "(todos)":
                val = None
        st.session_state.filters2[i] = {"col": col, "val": val}

    with st.sidebar.form(key="compare_form"):
        submitted = st.form_submit_button("🔍 Comparar")

    if submitted:
        df1_f = df1.copy()
        df2_f = df2.copy()
        for filt in st.session_state.filters1:
            if filt["col"] and filt["val"] is not None:
                df1_f = df1_f[df1_f[filt["col"]] == filt["val"]]
        for filt in st.session_state.filters2:
            if filt["col"] and filt["val"] is not None:
                df2_f = df2_f[df2_f[filt["col"]] == filt["val"]]

        df1_f["__chave__"] = df1_f[key1].str.strip()
        df2_f["__chave__"] = df2_f[key2].str.strip()
        df1_f = df1_f[df1_f["__chave__"].notna() & (df1_f["__chave__"] != "")]
        df2_f = df2_f[df2_f["__chave__"].notna() & (df2_f["__chave__"] != "")]

        keys_1 = set(df1_f["__chave__"])
        keys_2 = set(df2_f["__chave__"])

        common_keys = sorted(keys_1.intersection(keys_2))
        only_in_1_keys = sorted(keys_1.difference(keys_2))
        only_in_2_keys = sorted(keys_2.difference(keys_1))

        st.session_state.result_keys = common_keys
        st.session_state.df1_filtered = df1_f[df1_f["__chave__"].isin(common_keys)]
        st.session_state.df2_filtered = df2_f[df2_f["__chave__"].isin(common_keys)]

        st.session_state.only_in_1 = df1_f[df1_f["__chave__"].isin(only_in_1_keys)]
        st.session_state.only_in_2 = df2_f[df2_f["__chave__"].isin(only_in_2_keys)]

    if st.session_state.result_keys:
        st.subheader("✅ Valores em Comum nos dois arquivos")
        st.success(f"✔ Foram encontrados {len(st.session_state.result_keys)} registros em comum.")

        extra1 = st.multiselect("➕ Colunas extras do arquivo 1", st.session_state.df1_filtered.columns.drop("__chave__"))
        extra2 = st.multiselect("➕ Colunas extras do arquivo 2", st.session_state.df2_filtered.columns.drop("__chave__"))

        df1_display = (
            st.session_state.df1_filtered
            .drop_duplicates(subset="__chave__")
            .set_index("__chave__")[extra1]
            if extra1 else pd.DataFrame(index=st.session_state.result_keys)
        )
        df2_display = (
            st.session_state.df2_filtered
            .drop_duplicates(subset="__chave__")
            .set_index("__chave__")[extra2]
            if extra2 else pd.DataFrame(index=st.session_state.result_keys)
        )

        final = pd.concat([df1_display, df2_display], axis=1).reset_index().rename(columns={"__chave__": "Valor Comparado"})

        def color_cells(val, col_name):
            if col_name in extra1:
                return 'background-color: #D0E4FF; color: black;'
            elif col_name in extra2:
                return 'background-color: #FFF9C4; color: black;'
            else:
                return ''

        styled_final = final.style.applymap(lambda v: '', subset=final.columns)
        for col in extra1:
            styled_final = styled_final.applymap(lambda v: 'background-color: #D0E4FF; color: black;', subset=[col])
        for col in extra2:
            styled_final = styled_final.applymap(lambda v: 'background-color: #FFF9C4; color: black;', subset=[col])

        st.dataframe(styled_final)

        # Mostrar diferenças

        st.subheader("❌ Valores só no arquivo 1")
        if not st.session_state.only_in_1.empty:
            st.dataframe(st.session_state.only_in_1.drop(columns="__chave__").reset_index(drop=True))
        else:
            st.write("Nenhum registro exclusivo encontrado no arquivo 1.")

        st.subheader("❌ Valores só no arquivo 2")
        if not st.session_state.only_in_2.empty:
            st.dataframe(st.session_state.only_in_2.drop(columns="__chave__").reset_index(drop=True))
        else:
            st.write("Nenhum registro exclusivo encontrado no arquivo 2.")
