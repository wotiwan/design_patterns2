class osv_line:
    def __init__(self, nomenclature, incoming=0, outgoing=0):
        self.nomenclature = nomenclature
        self.incoming = incoming
        self.outgoing = outgoing

    @property
    def closing_balance(self):
        return self.incoming - self.outgoing