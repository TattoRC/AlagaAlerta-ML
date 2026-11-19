# coleta os alagamentos do site do CGE, um dia por vez (nao tem API)
# uso: python coleta/coletar_cge.py 2019-01-01 2025-12-31
import re
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://www.cgesp.org/v3/alagamentos.jsp"
PASTA_ML = Path(__file__).resolve().parents[1]
PASTA_HTML = PASTA_ML / "dados" / "brutos" / "cge_html"
ARQ_PONTOS = PASTA_ML / "dados" / "brutos" / "cge_alagamentos.csv"
ARQ_DIAS = PASTA_ML / "dados" / "brutos" / "cge_dias.csv"
PAUSA = 1.5  # com 0.5 o site comecou a dar 403 depois de umas 470 paginas
ESPERA_BLOQUEIO = 180

RE_HORARIO = re.compile(r"De\s+(\d{1,2}:\d{2})\s+a\s*(\d{1,2}:\d{2})?")


def pagina_valida(conteudo):
    texto = conteudo.decode("utf-8", errors="ignore")
    return "tit-bairros" in texto or "registros de alagamentos para essa data" in texto


def baixar_dia(dia, sessao):
    arq = PASTA_HTML / str(dia.year) / f"{dia.isoformat()}.html"
    if arq.exists() and pagina_valida(arq.read_bytes()):
        return arq

    arq.parent.mkdir(parents=True, exist_ok=True)
    params = {"dataBusca": dia.strftime("%d/%m/%Y"), "enviaBusca": "Buscar"}
    for tentativa in range(1, 7):
        try:
            r = sessao.get(URL, params=params, timeout=30)
            if r.status_code == 403:
                print(f"  {dia}: 403, esperando {ESPERA_BLOQUEIO * tentativa}s", flush=True)
                time.sleep(ESPERA_BLOQUEIO * tentativa)
                continue
            r.raise_for_status()
            if not pagina_valida(r.content):
                raise ValueError("pagina veio sem a lista de alagamentos")
            arq.write_bytes(r.content)
            time.sleep(PAUSA)
            return arq
        except (requests.RequestException, ValueError) as erro:
            print(f"  {dia}: {erro} - tentativa {tentativa}", flush=True)
            time.sleep(10 * tentativa)
    raise RuntimeError(f"nao consegui baixar o dia {dia}")


def ler_pontos(arq, dia):
    soup = BeautifulSoup(arq.read_bytes(), "html.parser")
    pontos = []
    total_informado = 0
    regiao = subprefeitura = None

    for tag in soup.find_all(["h1", "td", "div"]):
        classes = tag.get("class") or []

        if tag.name == "h1" and "tit-bairros" in classes:
            regiao = tag.get_text(strip=True)

        elif tag.name == "td" and "bairro" in classes:
            subprefeitura = " ".join(tag.get_text(" ", strip=True).split())

        elif tag.name == "td" and "total-pts" in classes:
            n = re.search(r"\d+", tag.get_text())
            total_informado += int(n.group()) if n else 0

        elif tag.name == "div" and "ponto-de-alagamento" in classes:
            itens = tag.find_all("li")
            situacao = next((li["title"] for li in itens if li.get("title")), "")
            descricoes = [li.get_text("|", strip=True) for li in itens
                          if "arial-descr-alag" in (li.get("class") or [])]

            horario_local = descricoes[0].split("|") if descricoes else [""]
            sentido_ref = descricoes[1].split("|") if len(descricoes) > 1 else []

            m = RE_HORARIO.search(horario_local[0])
            sentido = next((t.split(":", 1)[1].strip() for t in sentido_ref
                            if t.startswith("Sentido")), "")
            referencia = next((t.split(":", 1)[1].strip() for t in sentido_ref
                               if t.startswith("Refer")), "")

            pontos.append({
                "data": dia.isoformat(),
                "regiao": regiao,
                "subprefeitura": subprefeitura,
                "inicio": m.group(1) if m else "",
                "fim": (m.group(2) or "") if m else "",
                "local": horario_local[1] if len(horario_local) > 1 else "",
                "sentido": sentido,
                "referencia": referencia,
                "situacao": situacao,
            })

    # confere com o "X pts." que o site mostra em cada subprefeitura
    if total_informado != len(pontos):
        print(f"  aviso {dia}: pagina diz {total_informado} pts, li {len(pontos)}")
    return pontos


def main():
    inicio = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date(2019, 1, 1)
    fim = date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date(2025, 12, 31)

    sessao = requests.Session()
    sessao.headers["User-Agent"] = "Mozilla/5.0 (projeto academico - coleta de dados abertos)"

    todos, dias = [], []
    dia = inicio
    while dia <= fim:
        arq = baixar_dia(dia, sessao)
        pontos = ler_pontos(arq, dia)
        todos.extend(pontos)
        dias.append({"data": dia.isoformat(), "n_pontos": len(pontos)})
        if dia.day == 1:
            print(f"{dia:%m/%Y} ... {len(todos)} pontos ate agora", flush=True)
        dia += timedelta(days=1)

    pd.DataFrame(todos).to_csv(ARQ_PONTOS, index=False, encoding="utf-8")
    pd.DataFrame(dias).to_csv(ARQ_DIAS, index=False, encoding="utf-8")
    print(f"\n{len(dias)} dias consultados, {len(todos)} pontos de alagamento")
    print(f"salvo em {ARQ_PONTOS}")


if __name__ == "__main__":
    main()
