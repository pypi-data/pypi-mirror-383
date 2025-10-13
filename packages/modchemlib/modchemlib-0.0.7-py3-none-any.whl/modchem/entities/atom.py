from modchem.catalogs.elements import *
class Atom(BaseChemicalPartical):
    atom_name: str
    molar_mass: float
    bounds_hash = []
    info = {}
    def __init__(self, atom_name: str):
        self.atom_name = atom_name
        self.molar_mass = atom_name
        self.bounds_hash = []
        self.info = ELEMENTS[self.atom_name].__dict__

    def info(self):
        return ELEMENTS[self.atom_name].__dict__
    
    def __str__(self):
        return str(ELEMENTS[self.atom_name].__dict__)
    
    def __add__(self, partical):
        return super().__add__(partical)
    

class AtomList(BaseChemicalParticalList):
    """Класс взаимодействия ансабля молекул в рамках иона"""
    atom: Atom
    count: int

    def __init__(self, atom: Atom, count: int):
        self.atom = atom
        self.count = count
    
    def get_list(self):
        return {self.atom.atom_name: self.atom, "count": self.count}
    
    def set_band():
        super().set_band()
        