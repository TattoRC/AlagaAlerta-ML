"""
Baixa os dados horarios das estacoes automaticas do INMET na capital e arredores:
    A701 - Sao Paulo / Mirante de Santana (zona norte)
    A771 - Sao Paulo / Interlagos (zona sul)
    A755 - Barueri (oeste da capital)

O INMET publica um zip por ano com todas as estacoes do Brasil:
https://portal.inmet.gov.br/uploads/dadoshistoricos/AAAA.zip

Cada zip tem uns 100 MB, mas so precisamos de 3 arquivos dele. O script baixa
o zip numa pasta temporaria, extrai os CSVs dessas estacoes para
dados/brutos/inmet/ e apaga o zip.

Uso:
    python coleta/baixar_inmet.py 2019 2025
"""
import sys
import tempfile
import zipfile
from pathlib import Path

import requests

URL = "https://portal.inmet.gov.br/uploads/dadoshistoricos/{ano}.zip"
ESTACOES = ["A701", "A771", "A755"]
PASTA_SAIDA = Path(__file__).resolve().parents[1] / "dados" / "brutos" / "inmet"


def baixar_ano(ano):
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        arq_zip = Path(tmp) / f"{ano}.zip"
        print(f"baixando {ano}...", flush=True)
        with requests.get(URL.format(ano=ano), stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(arq_zip, "wb") as f:
                for pedaco in r.iter_content(chunk_size=1 << 20):
                    f.write(pedaco)

        with zipfile.ZipFile(arq_zip) as z:
            for nome in z.namelist():
                arquivo = Path(nome).name
                if any(f"_{cod}_" in arquivo for cod in ESTACOES):
                    (PASTA_SAIDA / arquivo).write_bytes(z.read(nome))
                    print(f"  {arquivo}")


def main():
    ano_ini = int(sys.argv[1]) if len(sys.argv) > 1 else 2019
    ano_fim = int(sys.argv[2]) if len(sys.argv) > 2 else 2025
    for ano in range(ano_ini, ano_fim + 1):
        baixar_ano(ano)


if __name__ == "__main__":
    main()
