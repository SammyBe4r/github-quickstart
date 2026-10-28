import unittest

from palworld_planner import (
    Pal,
    Recipe,
    calculate_required_materials,
    calculate_shortages,
    recommend_pals,
)


class CalculateRequiredMaterialsTests(unittest.TestCase):
    def test_rounds_up_to_a_whole_batch(self):
        recipe = Recipe("kit", {"madeira": 3, "pedra": 2}, output_per_batch=2)

        self.assertEqual(
            calculate_required_materials(recipe, 3),
            {"madeira": 6, "pedra": 4},
        )

    def test_rejects_non_positive_output_quantity(self):
        recipe = Recipe("kit", {"madeira": 3})

        with self.assertRaises(ValueError):
            calculate_required_materials(recipe, 0)

    def test_recipe_rejects_invalid_material_quantity(self):
        with self.assertRaises(ValueError):
            Recipe("kit", {"madeira": 0})


class CalculateShortagesTests(unittest.TestCase):
    def test_returns_remaining_materials_and_zero_for_sufficient_stock(self):
        shortages = calculate_shortages(
            {"madeira": 6, "pedra": 4},
            {"madeira": 8, "pedra": 1},
        )

        self.assertEqual(shortages, {"madeira": 0, "pedra": 3})

    def test_rejects_negative_inventory(self):
        with self.assertRaises(ValueError):
            calculate_shortages({"madeira": 2}, {"madeira": -1})


class RecommendPalsTests(unittest.TestCase):
    def setUp(self):
        self.pals = [
            Pal("Pal Z", {"artesanato": 2}),
            Pal("Pal B", {"Artesanato": 3}),
            Pal("Pal A", {"artesanato": 3}),
            Pal("Pal sem aptidão", {"plantio": 2}),
        ]

    def test_ranks_by_level_then_name_and_matches_case_insensitively(self):
        recommendations = recommend_pals(self.pals, "ARTESANATO")

        self.assertEqual(
            [(pal.name, level) for pal, level in recommendations],
            [("Pal A", 3), ("Pal B", 3), ("Pal Z", 2)],
        )

    def test_applies_limit(self):
        recommendations = recommend_pals(self.pals, "artesanato", limit=1)

        self.assertEqual([pal.name for pal, _ in recommendations], ["Pal A"])

    def test_rejects_empty_task(self):
        with self.assertRaises(ValueError):
            recommend_pals(self.pals, " ")


if __name__ == "__main__":
    unittest.main()
