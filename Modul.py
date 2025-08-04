class Modul:
    """
    Eine Klasse, die ein Studienmodul repräsentiert.
    
    Attribute:
        name (str): Der Name des Moduls
        ects (int): Die Anzahl der ECTS-Punkte für das Modul
        pruefung (str): Die Prüfungsform des Moduls (z.B. "Klausur (90min)")
        status (str): Der aktuelle Status des Moduls (z.B. "✓ 1.7", "✗ 5.0", "In Arbeit")
    """
    
    def __init__(self, name: str, ects: int, pruefung: str, status: str):
        """
        Initialisiert ein Modul-Objekt.
        
        Args:
            name (str): Der Name des Moduls
            ects (int): Die Anzahl der ECTS-Punkte für das Modul
            pruefung (str): Die Prüfungsform des Moduls (z.B. "Klausur (90min)")
            status (str): Der aktuelle Status des Moduls (z.B. "✓ 1.7", "✗ 5.0", "In Arbeit")
        """
        self.name = name
        self.ects = ects
        self.pruefung = pruefung
        self.status = status  # z.B. "✓ 1.7", "✗ 5.0", "In Arbeit"

