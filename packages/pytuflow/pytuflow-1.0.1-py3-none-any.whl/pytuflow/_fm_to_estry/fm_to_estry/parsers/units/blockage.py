import io
from typing import TextIO

import numpy as np
import pandas as pd

from .handler import Handler


class Blockage(Handler):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.TYPE = 'component'
        self.headers = ['Time', 'Blockage']
        self.ncol = len(self.headers)
        self.blockage_table = pd.DataFrame()
        self.ups_label = None
        self.dns_label = None
        self.ups_label_ref = None
        self.dns_label_ref = None
        self.constriction = None
        self.k1 = 0.
        self.k2 = 0.
        self.n1 = 0
        self.tlag = 0.
        self.tm = 'SECONDS'
        self.repeat = 'NOEXTEND'
        self.valid = True

    @staticmethod
    def unit_type_name() -> str:
        return 'BLOCKAGE'

    def load(self, line: str, fo: TextIO, fixed_field_len: int, line_no: int) -> None:
        super().load(line, fo, fixed_field_len, line_no)
        self._set_attrs_str(self.read_line(True),
                            ['ups_label', 'dns_label', 'ups_label_ref', 'dns_label_ref', 'constriction'],
                            log_errors=[0, 1])
        self.id = self.ups_label
        self.uid = self._get_uid()
        self._set_attrs_float(self.read_line(), ['k1', 'k2'])
        self._set_attrs(self.read_line(), ['n1', 'tlag', 'tm', 'repeat'], [int, float, str, str],
                        log_errors=[0])
        if self.n1:
            a = np.genfromtxt(self.fo, delimiter=(10, 10), max_rows=self.n1, dtype='f4')
            if a.shape != (self.n1, self.ncol):
                a = np.reshape(a, (self.n1, self.ncol))
            self.blockage_table = pd.DataFrame(a, columns=self.headers)
            self.line_no += self.n1
