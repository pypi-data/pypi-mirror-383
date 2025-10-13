from liminal.base.str_enum import StrEnum


class BenchlingEntityType(StrEnum):
    """This enum represents the different entity types that can be created in Benchling."""

    CUSTOM_ENTITY = "custom_entity"
    DNA_SEQUENCE = "dna_sequence"
    DNA_OLIGO = "dna_oligo"
    RNA_OLIGO = "rna_oligo"
    RNA_SEQUENCE = "rna_sequence"
    AA_SEQUENCE = "aa_sequence"
    ENTRY = "entry"
    MIXTURE = "mixture"
    MOLECULE = "molecule"

    def is_nt_sequence(self) -> bool:
        return self in [
            self.DNA_SEQUENCE,
            self.RNA_SEQUENCE,
            self.DNA_OLIGO,
            self.RNA_OLIGO,
        ]

    def is_sequence(self) -> bool:
        return self in [
            self.DNA_SEQUENCE,
            self.RNA_SEQUENCE,
            self.DNA_OLIGO,
            self.RNA_OLIGO,
            self.AA_SEQUENCE,
        ]
