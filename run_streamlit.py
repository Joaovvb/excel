import subprocess

# Caminho fixo para a sua instalação (ajuste se precisar)
streamlit_path = r"C:\excel\venv\Scripts\streamlit.exe"
app_path = r"C:\excel\app.py"

print("Iniciando Streamlit com:")
print(f"  - Streamlit: {streamlit_path}")
print(f"  - App:       {app_path}\n")

try:
    ret = subprocess.call([streamlit_path, "run", app_path])
    print(f"\nProcesso finalizado com código: {ret}")
except Exception as e:
    print(f"\nErro ao iniciar Streamlit: {e}")

input("\nPressione ENTER para fechar...")
