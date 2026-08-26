import unittest
from pathlib import Path


class MainMenuCatalogStructureTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.source = Path(
            "presentation/desktop/main_menu.py"
        ).read_text(
            encoding="utf-8"
        )

    def test_catalog_uses_providers_as_primary_entry(self):
        self.assertIn(
            'text="1 - Prestadores"',
            self.source,
        )
        self.assertIn(
            'text="2 - Veículos"',
            self.source,
        )

    def test_standalone_driver_entry_is_removed(self):
        self.assertNotIn(
            'text="1 - Motoristas"',
            self.source,
        )
        self.assertNotIn(
            "command=self.show_drivers",
            self.source,
        )

    def test_driver_list_view_is_not_routed_from_main_menu(self):
        self.assertNotIn(
            "from presentation.desktop.driver_list_view import",
            self.source,
        )
        self.assertNotIn(
            "def show_drivers(self):",
            self.source,
        )


if __name__ == "__main__":
    unittest.main()
