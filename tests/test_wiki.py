"""Vérifier la navigation et la reproductibilité du wiki généré."""
from pathlib import Path
import tempfile
import unittest
from scripts.build_wiki import PAGES, REPOSITORY, WIKI, build, render, rewrite_link


class WikiTests(unittest.TestCase):
    def test_course_link_targets_wiki(self):
        self.assertEqual(rewrite_link('cours/01-concurrence.md', '00-fondations.md'),
                         WIKI + '/00-Fondations')

    def test_code_link_targets_repository(self):
        self.assertEqual(rewrite_link('cours/01-concurrence.md', '../pocs/p01a_ticket.py'),
                         REPOSITORY + '/blob/main/pocs/p01a_ticket.py')

    def test_fragment_and_external_url_unchanged(self):
        self.assertEqual(rewrite_link('cours/01-concurrence.md', '#exercice'), '#exercice')
        target = 'https://www.postgresql.org/docs/current/explicit-locking.html'
        self.assertEqual(rewrite_link('cours/01-concurrence.md', target), target)
        self.assertEqual(rewrite_link('cours/01-concurrence.md', '00-fondations.md#objectifs'),
                         WIKI + '/00-Fondations#objectifs')

    def test_code_block_is_not_rewritten(self):
        content = '[Cours](00-fondations.md)\n```text\n[Cours](00-fondations.md)\n```\n'
        result = render('cours/01-concurrence.md', content)
        self.assertIn(f'[Cours]({WIKI}/00-Fondations)', result)
        self.assertIn('```text\n[Cours](00-fondations.md)\n```', result)

    def test_missing_source_fails_build(self):
        with self.assertRaises(ValueError):
            rewrite_link('cours/01-concurrence.md', 'cours-absent.md')

    def test_generation_is_reproducible_and_complete(self):
        with tempfile.TemporaryDirectory() as folder:
            count = build(folder)
            first = {p.name: p.read_bytes() for p in Path(folder).glob('*.md')}
            self.assertEqual(count, len(PAGES) + 2)
            self.assertEqual(set(first), {name + '.md' for name in PAGES.values()} | {'_Sidebar.md', '_Footer.md'})
            build(folder)
            second = {p.name: p.read_bytes() for p in Path(folder).glob('*.md')}
            self.assertEqual(first, second)
            sidebar = first['_Sidebar.md'].decode()
            self.assertIn(WIKI + '/09-Fiabilite-IA', sidebar)
            self.assertIn(WIKI + '/Atelier-PostgreSQL', sidebar)


if __name__ == '__main__':
    unittest.main()
