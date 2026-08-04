import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from main import convert, json_records, valid_date


class ConversionTests(unittest.TestCase):
    def test_valid_date_rejects_invalid_or_wrongly_formatted_values(self):
        self.assertEqual(valid_date("2024-02-29"), "2024-02-29")
        self.assertEqual(valid_date("2023-02-29"), "")
        self.assertEqual(valid_date("01/02/2024"), "")
        self.assertEqual(valid_date(None), "")

    def test_json_records_skips_malformed_lines_and_non_objects(self):
        source = io.StringIO('{"club_id": "A"}\ninvalid\n[]\n')
        warnings = io.StringIO()

        with redirect_stderr(warnings):
            records = list(json_records(source))

        self.assertEqual(records, [{"club_id": "A"}])
        self.assertEqual(warnings.getvalue().count("registro ignorado"), 2)

    def test_conversion_filters_and_flattens_without_stopping_on_bad_data(self):
        records = [
            {
                "club_id": "A",
                "name": "Clube, com vírgula",
                "championship": "SERIE A",
                "founding_date": "2024-02-30",
                "nickname": None,
                "colors": ["azul", "branco"],
                "players": [
                    {
                        "player_id": "A-1",
                        "name": 'Nome "Teste"',
                        "age": 0,
                        "goals": 0,
                        "debut_date": "2024-01-01",
                    },
                    "jogador inválido",
                ],
            },
            {"club_id": "B", "championship": "SERIE C", "players": [{}]},
            {"club_id": "C", "championship": "SERIE B"},
        ]

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input.jsonl"
            input_path.write_text(
                "\n".join(json.dumps(record, ensure_ascii=False) for record in records)
                + "\n{inválido\n",
                encoding="utf-8",
            )

            with redirect_stderr(io.StringIO()):
                self.assertEqual(convert(input_path, root), (2, 1))

            with (root / "clubs.csv").open(encoding="utf-8", newline="") as file:
                clubs = list(csv.DictReader(file))
            with (root / "players.csv").open(encoding="utf-8", newline="") as file:
                players = list(csv.DictReader(file))

        self.assertEqual([club["Id do Clube"] for club in clubs], ["A", "C"])
        self.assertEqual(clubs[0]["Nome"], "Clube, com vírgula")
        self.assertEqual(clubs[0]["Data de Fundação"], "")
        self.assertEqual(clubs[0]["Apelido"], "")
        self.assertEqual(clubs[0]["Cores"], "azul|branco")
        self.assertEqual(players[0]["Id do Clube"], "A")
        self.assertEqual(players[0]["Nome"], 'Nome "Teste"')
        self.assertEqual(players[0]["Idade"], "0")


if __name__ == "__main__":
    unittest.main()
