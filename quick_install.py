import subprocess
import sys

# Instalar pacotes essenciais
packages = [
    'Flask',
    'werkzeug',
    'psycopg2-binary',
    'python-dotenv',
    'pytz'
]

print("Instalando dependencias essenciais...")
for pkg in packages:
    try:
        print(f"  Instalando {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"    OK {pkg}")
    except Exception as e:
        print(f"    ERRO {pkg}: {e}")

print("\nInstalacao concluida!")
