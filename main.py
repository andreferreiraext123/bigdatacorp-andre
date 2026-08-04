"""Converte clubes em JSONL para os arquivos tabulares do desafio."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, TextIO


CLUB_COLUMNS = (
    "Id do Clube",
    "Nome",
    "Campeonato",
    "Data de Fundação",
    "Cidade",
    "Estado",
    "País",
    "Estádio",
    "Presidente",
    "Apelido",
    "Cores",
)

PLAYER_COLUMNS = (
    "Id do Clube",
    "Id do Jogador",
    "Nome",
    "Idade",
    "Gols",
    "Data de Estreia",
    "Posição",
    "Número da Camisa",
)

ALLOWED_CHAMPIONSHIPS = {"SERIE A", "SERIE B"}


def scalar(value: Any) -> str | int | float | bool:
    """Converte valor vazio/complexo em campo vazio, preservando escalares."""
    if value is None or isinstance(value, (dict, list)):
        return ""
    return value


def valid_date(value: Any) -> str:
    """Retorna somente datas reais escritas exatamente como yyyy-MM-dd."""
    if not isinstance(value, str):
        return ""

    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return ""
    return parsed.isoformat() if parsed.isoformat() == value else ""


def joined_colors(value: Any) -> str:
    if not isinstance(value, list):
        return ""
    return "|".join(
        str(color) for color in value if isinstance(color, (str, int, float, bool))
    )


def club_row(club: dict[str, Any]) -> dict[str, Any]:
    return {
        "Id do Clube": scalar(club.get("club_id")),
        "Nome": scalar(club.get("name")),
        "Campeonato": scalar(club.get("championship")),
        "Data de Fundação": valid_date(club.get("founding_date")),
        "Cidade": scalar(club.get("city")),
        "Estado": scalar(club.get("state")),
        "País": scalar(club.get("country")),
        "Estádio": scalar(club.get("stadium")),
        "Presidente": scalar(club.get("president")),
        "Apelido": scalar(club.get("nickname")),
        "Cores": joined_colors(club.get("colors")),
    }


def player_row(club_id: Any, player: dict[str, Any]) -> dict[str, Any]:
    return {
        "Id do Clube": scalar(club_id),
        "Id do Jogador": scalar(player.get("player_id")),
        "Nome": scalar(player.get("name")),
        "Idade": scalar(player.get("age")),
        "Gols": scalar(player.get("goals")),
        "Data de Estreia": valid_date(player.get("debut_date")),
        "Posição": scalar(player.get("position")),
        "Número da Camisa": scalar(player.get("shirt_number")),
    }


def json_records(source: TextIO) -> Iterable[dict[str, Any]]:
    """Lê registros independentemente e ignora linhas inválidas."""
    for line_number, line in enumerate(source, start=1):
        try:
            record = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            print(f"Aviso: linha {line_number} inválida; registro ignorado.", file=sys.stderr)
            continue

        if not isinstance(record, dict):
            print(
                f"Aviso: linha {line_number} não contém um objeto; registro ignorado.",
                file=sys.stderr,
            )
            continue
        yield record


def convert(input_path: Path, output_dir: Path) -> tuple[int, int]:
    """Converte o JSONL e devolve as quantidades de clubes e jogadores."""
    output_dir.mkdir(parents=True, exist_ok=True)
    clubs_path = output_dir / "clubs.csv"
    players_path = output_dir / "players.csv"
    club_count = 0
    player_count = 0

    with (
        input_path.open("r", encoding="utf-8", errors="replace") as source,
        clubs_path.open("w", encoding="utf-8", newline="") as clubs_file,
        players_path.open("w", encoding="utf-8", newline="") as players_file,
    ):
        clubs_writer = csv.DictWriter(clubs_file, fieldnames=CLUB_COLUMNS)
        players_writer = csv.DictWriter(players_file, fieldnames=PLAYER_COLUMNS)
        clubs_writer.writeheader()
        players_writer.writeheader()

        for club in json_records(source):
            if club.get("championship") not in ALLOWED_CHAMPIONSHIPS:
                continue

            clubs_writer.writerow(club_row(club))
            club_count += 1

            players = club.get("players", [])
            if not isinstance(players, list):
                continue
            for player in players:
                if not isinstance(player, dict):
                    continue
                players_writer.writerow(player_row(club.get("club_id"), player))
                player_count += 1

    return club_count, player_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera clubs.csv e players.csv a partir de um arquivo JSONL."
    )
    parser.add_argument("input", type=Path, help="caminho do arquivo JSONL de entrada")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="diretório de saída (padrão: diretório atual)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        clubs, players = convert(args.input, args.output_dir)
    except OSError as error:
        print(f"Erro ao acessar arquivo: {error}", file=sys.stderr)
        return 1

    print(f"Concluído: {clubs} clubes e {players} jogadores processados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
