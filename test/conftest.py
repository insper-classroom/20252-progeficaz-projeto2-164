import sys
from pathlib import Path

proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
    sys.path.insert(0, str(proj_root))


# SO RESOLVI CRIAR ESSE ARQUIVO PARA O COMANDO DE PYTEST FUNCIONAR