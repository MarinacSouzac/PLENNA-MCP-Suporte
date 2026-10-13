
import json
import logging
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("PLENNA Suporte")

BASE_DIR = Path(__file__).resolve().parent
ARQUIVO = BASE_DIR / "dados" / "chamados.json"


logger = logging.getLogger("plenna.suporte")
logger.setLevel(logging.INFO)
logger.propagate = False

arquivo_log = logging.FileHandler(
    BASE_DIR / "operacoes.log",
    encoding="utf-8"
)

arquivo_log.setFormatter(
    logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
)

logger.addHandler(arquivo_log)



def carregar_chamados():
    with ARQUIVO.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_chamados(chamados):
    with ARQUIVO.open("w", encoding="utf-8") as arquivo:
        json.dump(chamados, arquivo, indent=2, ensure_ascii=False)


def validar_id(id):
    if type(id) is not int or id <= 0:
        raise ValueError("O ID deve ser um inteiro positivo.")


@mcp.resource("plenna://politica")
def politica() -> str:
    """Politica de atendimento ficticio do PLENNA."""
    return (
        "Utilize somente os chamados ficticios cadastrados. "
        "Nao invente informacoes. "
        "Para fechar chamados, exija confirmacao no cliente."
    )


@mcp.tool()
def listar_chamados() -> dict:
    """Lista todos os chamados ficticios do PLENNA."""
    return {"chamados": carregar_chamados()}


@mcp.tool()
def consultar_chamado(id: int) -> dict:
    """Consulta um chamado pelo ID inteiro positivo."""
    validar_id(id)
    chamados = carregar_chamados()

    if str(id) not in chamados:
        logger.info("consulta | ID=%s | nao encontrado", id)
        raise ValueError("Chamado nao encontrado.")

    logger.info("consulta | ID=%s | sucesso", id)
    return {"id": id, **chamados[str(id)]}


@mcp.tool()
def filtrar_chamados(prioridade: str) -> dict:
    """Filtra chamados por alta, media ou baixa."""
    if prioridade not in ("alta", "media", "baixa"):
        raise ValueError("Prioridade invalida. Use alta, media ou baixa.")

    chamados = carregar_chamados()

    filtrados = [
        {"id": int(id), **dados}
        for id, dados in chamados.items()
        if dados["prioridade"] == prioridade
    ]

    logger.info("filtro | prioridade=%s | total=%s",
                 prioridade, len(filtrados))
    return {"chamados": filtrados}


@mcp.tool()
def fechar_chamado(id: int) -> dict:
    """Fecha um chamado existente. Operacao de escrita."""
    validar_id(id)
    chamados = carregar_chamados()

    if str(id) not in chamados:
        logger.info("fechamento | ID=%s | nao encontrado", id)
        raise ValueError("Chamado nao encontrado.")

    chamado = chamados[str(id)]

    if chamado["status"] == "fechado":
        logger.info("fechamento | ID=%s | ja fechado", id)
        return {
            "id": id,
            "status": "fechado",
            "mensagem": "Chamado ja estava fechado."
        }

    chamado["status"] = "fechado"
    salvar_chamados(chamados)

    logger.info("fechamento | ID=%s | sucesso", id)

    return {
        "id": id,
        "status": "fechado",
        "mensagem": "Chamado fechado com sucesso."
    }


@mcp.prompt()
def analisar_chamado(id: str) -> str:
    """Orienta a analise de um chamado."""
    return (
        f"Consulte o chamado {id} utilizando a ferramenta MCP. "
        "Informe titulo, prioridade e status. "
        "Se nao existir, informe isso sem inventar dados."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")

