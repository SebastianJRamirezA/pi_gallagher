import unittest

from src.data.cards import CARDS
from src.data.dialogues import DIALOGUES
from src.localization import localize, set_language, toggle_language, tr
from src.story.StoryManager import StoryManager


class LocalizationTests(unittest.TestCase):
    def setUp(self) -> None:
        set_language("en")

    def test_language_toggle_switches_between_english_and_spanish(self) -> None:
        self.assertEqual(tr("Continuar"), "Resume")
        self.assertEqual(toggle_language(), "es")
        self.assertEqual(tr("Continuar"), "Continuar")
        self.assertEqual(toggle_language(), "en")
        self.assertEqual(tr("Continuar"), "Resume")

    def test_dialogue_and_card_data_are_translated_recursively(self) -> None:
        dialogue = localize(DIALOGUES["sofia_office_intro"])
        card = localize(CARDS["C01"])

        self.assertEqual(dialogue["speaker"], "Sofia Del Roscio")
        self.assertTrue(dialogue["pages"][0].startswith("Detective Gallagher... thank you"))
        self.assertEqual(card["titulo"], "Police Report")
        self.assertIn("inside", card["descripcion"])

    def test_spanish_mode_preserves_source_text(self) -> None:
        set_language("es")
        self.assertEqual(tr("Continuar"), "Continuar")
        self.assertEqual(
            localize(CARDS["C01"])["titulo"],
            "Informe policial",
        )

    def test_clue_notifications_follow_the_selected_language(self) -> None:
        story = StoryManager()
        story.add_card("C01")
        self.assertEqual(
            story.notifications[-1]["text"],
            "New Clue: [C01] Police Report",
        )

        set_language("es")
        story.add_card("C02")
        self.assertEqual(
            story.notifications[-1]["text"],
            "Nueva Pista: [C02] Informe del soplón",
        )


if __name__ == "__main__":
    unittest.main()
