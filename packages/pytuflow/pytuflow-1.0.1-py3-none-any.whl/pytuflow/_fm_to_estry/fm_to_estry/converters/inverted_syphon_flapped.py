from fm_to_estry.converters.orifice import Orifice


class InvertedSyphonFlapped(Orifice):

    @staticmethod
    def complete_unit_type_name() -> str:
        return 'INVERTED SYPHON_FLAPPED'
