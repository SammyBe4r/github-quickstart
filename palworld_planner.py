"""Small, dependency-free planning algorithms for a Palworld-inspired base."""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass


def _require_positive_integer(value: int, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{label} deve ser um inteiro positivo.")


@dataclass(frozen=True)
class Recipe:
    name: str
    materials: dict[str, int]
    output_per_batch: int = 1

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("A receita precisa ter um nome.")
        _require_positive_integer(self.output_per_batch, "A produção por lote")
        if not self.materials:
            raise ValueError("A receita precisa conter ao menos um material.")
        for material, quantity in self.materials.items():
            if not material.strip():
                raise ValueError("O nome do material não pode ficar vazio.")
            _require_positive_integer(quantity, f"A quantidade de {material}")


@dataclass(frozen=True)
class Pal:
    name: str
    work_suitabilities: dict[str, int]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("O Pal precisa ter um nome.")
        for task, level in self.work_suitabilities.items():
            if not task.strip():
                raise ValueError("O nome da tarefa não pode ficar vazio.")
            if isinstance(level, bool) or not isinstance(level, int) or level < 0:
                raise ValueError(f"A aptidão de {task} deve ser um inteiro não negativo.")


def calculate_required_materials(
    recipe: Recipe, output_quantity: int
) -> dict[str, int]:
    """Return the materials needed, accounting for whole production batches."""
    _require_positive_integer(output_quantity, "A quantidade desejada")
    batches = math.ceil(output_quantity / recipe.output_per_batch)
    return {
        material: quantity * batches
        for material, quantity in recipe.materials.items()
    }


def calculate_shortages(
    required: dict[str, int], inventory: dict[str, int]
) -> dict[str, int]:
    """Return only positive material deficits."""
    for material, quantity in inventory.items():
        if not material.strip():
            raise ValueError("O nome do material no inventário não pode ficar vazio.")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 0:
            raise ValueError(
                f"A quantidade de {material} no inventário deve ser "
                "um inteiro não negativo."
            )
    return {
        material: max(0, quantity - inventory.get(material, 0))
        for material, quantity in required.items()
    }


def recommend_pals(
    pals: tuple[Pal, ...] | list[Pal], task: str, limit: int | None = None
) -> list[tuple[Pal, int]]:
    """Rank Pals with a positive suitability for a task."""
    task_key = task.strip().casefold()
    if not task_key:
        raise ValueError("Informe uma tarefa para buscar.")
    if limit is not None:
        _require_positive_integer(limit, "O limite")

    candidates = []
    for pal in pals:
        level = next(
            (
                value
                for suitability, value in pal.work_suitabilities.items()
                if suitability.casefold() == task_key
            ),
            0,
        )
        if level > 0:
            candidates.append((pal, level))

    candidates.sort(key=lambda candidate: (-candidate[1], candidate[0].name.casefold()))
    return candidates if limit is None else candidates[:limit]


SAMPLE_RECIPE = Recipe(
    name="kit de construção",
    materials={"madeira": 3, "pedra": 2},
    output_per_batch=2,
)

SAMPLE_PALS = (
    Pal("Pal de Plantio", {"plantio": 3, "coleta": 1}),
    Pal("Pal de Transporte", {"transporte": 3, "artesanato": 1}),
    Pal("Pal Artesão", {"artesanato": 3, "plantio": 1}),
    Pal("Pal de Apoio", {"transporte": 1}),
)


def _parse_inventory_item(value: str) -> tuple[str, int]:
    material, separator, raw_quantity = value.partition("=")
    if not separator or not material.strip():
        raise argparse.ArgumentTypeError(
            "use o formato recurso=quantidade, por exemplo madeira=10"
        )
    try:
        quantity = int(raw_quantity)
    except ValueError as error:
        raise argparse.ArgumentTypeError("a quantidade deve ser um inteiro") from error
    if quantity < 0:
        raise argparse.ArgumentTypeError("a quantidade não pode ser negativa")
    return material.strip(), quantity


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Planeja materiais e trabalhadores para uma base inspirada em Palworld."
    )
    parser.add_argument(
        "--quantity",
        type=int,
        default=3,
        help="quantidade desejada da receita (padrão: 3)",
    )
    parser.add_argument(
        "--inventory",
        action="append",
        type=_parse_inventory_item,
        default=[],
        metavar="RECURSO=QUANTIDADE",
        help="material disponível; pode ser informado mais de uma vez",
    )
    args = parser.parse_args()

    try:
        required = calculate_required_materials(SAMPLE_RECIPE, args.quantity)
        inventory = dict(args.inventory)
        shortages = calculate_shortages(required, inventory)
    except ValueError as error:
        parser.error(str(error))

    print("=== Planejador de base Palworld ===")
    print(f"Receita: {SAMPLE_RECIPE.name}")
    print(f"Unidades desejadas: {args.quantity}\n")
    print("Materiais:")
    for material, quantity in required.items():
        available = inventory.get(material, 0)
        print(
            f"- {material}: precisa de {quantity}, tem {available}, "
            f"faltam {shortages[material]}"
        )

    print("\nPals recomendados para artesanato:")
    recommendations = recommend_pals(SAMPLE_PALS, "artesanato")
    if not recommendations:
        print("- Nenhum Pal tem aptidão para essa tarefa.")
    else:
        for pal, level in recommendations:
            print(f"- {pal.name} (aptidão {level})")


if __name__ == "__main__":
    main()
