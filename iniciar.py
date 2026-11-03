"""Inicia o ParkControl na porta 8080 ou reutiliza uma instância já ativa."""

import argparse
import json
from urllib.error import URLError
from urllib.request import urlopen

import uvicorn


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    endereco = f"http://127.0.0.1:{args.port}"
    try:
        with urlopen(f"{endereco}/openapi.json", timeout=2) as resposta:
            dados = json.load(resposta)
        if dados.get("info", {}).get("title") == "Sistema de Estacionamento":
            print(f"ParkControl pronto em {endereco}", flush=True)
            return
    except (URLError, TimeoutError, ValueError):
        pass

    uvicorn.run("main:app", host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
