from pathlib import Path
from unittest import TestCase

from fm_to_estry.parsers.units.sluice import Sluice


class TestSluice(TestCase):

    def test_load_radial(self):
        p = './tests/data/River_Sections_Radial.dat'
        rivers = []
        with Path(p).open() as f:
            i = -1
            for line in f:
                i += 1
                if line == 'SLUICE\n':
                    r = Sluice(p)
                    r.load(line, f, fixed_field_len=12, line_no=i)
                    rivers.append(r)
                    i = r.line_no
        self.assertEqual(1, len(rivers))

    def test_load_vertical(self):
        p = './tests/data/River_Sections_Vertical.dat'
        rivers = []
        with Path(p).open() as f:
            i = -1
            for line in f:
                i += 1
                if line == 'SLUICE\n':
                    r = Sluice(p)
                    r.load(line, f, fixed_field_len=12, line_no=i)
                    rivers.append(r)
                    i = r.line_no
        self.assertEqual(1, len(rivers))
