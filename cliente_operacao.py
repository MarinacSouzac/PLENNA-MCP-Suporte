
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    print("=== PLENNA - FECHAMENTO DE CHAMADOS ===")

    entrada = input("Informe o ID do chamado: ").strip()

    try:
        id_chamado = int(entrada)
        if id_chamado <= 0:
            raise ValueError()
    except ValueError:
        print("Erro: informe um ID inteiro positivo.")
        return

    confirmacao = input(
        f"Deseja realmente fechar o chamado {id_chamado}? "
        "(sim/nao): "
    ).strip().lower()

    if confirmacao != "sim":
        print("Operacao cancelada.")
        print("Nenhuma ferramenta de escrita foi chamada.")
        return

    servidor = Path(__file__).with_name("servidor.py")

    parametros = StdioServerParameters(
        command=sys.executable,
        args=[str(servidor)]
    )

    async with stdio_client(parametros) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            resultado = await session.call_tool(
                "fechar_chamado",
                arguments={"id": id_chamado}
            )

            print("\n=== RESULTADO ===")

            for conteudo in resultado.content:
                if conteudo.type == "text":
                    print(conteudo.text)

            if resultado.isError:
                print("A operacao apresentou um erro.")
            else:
                print("Operacao concluida.")


if __name__ == "__main__":
    asyncio.run(main())
