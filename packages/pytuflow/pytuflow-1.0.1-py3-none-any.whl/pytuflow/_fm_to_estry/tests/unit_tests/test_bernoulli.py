from pathlib import Path
from unittest import TestCase

from fm_to_estry.parsers.units.bernoulli import Bernoulli


class TestBernoulli(TestCase):

    def test_load(self):
        p = './tests/data/River_Sections_Bernoulli.dat'
        rivers = []
        with Path(p).open() as f:
            i = -1
            for line in f:
                i += 1
                if line == 'BERNOULLI\n':
                    r = Bernoulli(p)
                    r.load(line, f, fixed_field_len=12, line_no=i)
                    rivers.append(r)
                    i = r.line_no
        self.assertEqual(1, len(rivers))
