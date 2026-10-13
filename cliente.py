
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    servidor = Path(__file__).with_name("servidor.py")

    parametros = StdioServerParameters(
        command=sys.executable,
        args=[str(servidor)]
    )

    async with stdio_client(parametros) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()
            print("\n=== CONEXAO MCP ESTABELECIDA ===")

            # Descoberta das ferramentas
            ferramentas = await session.list_tools()
            print("\nFERRAMENTAS DISPONIVEIS:")
            for ferramenta in ferramentas.tools:
                print("-", ferramenta.name)

            # Descoberta da Resource
            recursos = await session.list_resources()
            print("\nRESOURCES:")
            for recurso in recursos.resources:
                print("-", recurso.uri)

            # Descoberta do Prompt
            prompts = await session.list_prompts()
            print("\nPROMPTS:")
            for prompt in prompts.prompts:
                print("-", prompt.name)

            # Leitura da Resource
            politica = await session.read_resource(
                "plenna://politica"
            )
            print("\nPOLITICA:")
            print(politica.model_dump_json(indent=2))

            # Obtencao do Prompt
            prompt = await session.get_prompt(
                "analisar_chamado",
                arguments={"id": "101"}
            )
            print("\nPROMPT:")
            print(prompt.model_dump_json(indent=2))

            async def testar(nome, argumentos):
                print(f"\n=== {nome}: {argumentos} ===")
                resultado = await session.call_tool(
                    nome, arguments=argumentos
                )
                print(resultado.model_dump_json(indent=2))
                return resultado

            # Testes das ferramentas
            await testar("listar_chamados", {})
            await testar("consultar_chamado", {"id": 101})
            await testar("consultar_chamado", {"id": 999})
            await testar("consultar_chamado", {"id": -1})
            await testar("consultar_chamado", {"id": "abc"})
            await testar("filtrar_chamados", {"prioridade": "alta"})
            await testar("filtrar_chamados", {"prioridade": "urgente"})

            print("\n=== TESTES DE CONSULTA FINALIZADOS ===")


if __name__ == "__main__":
    asyncio.run(main())
