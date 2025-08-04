from datetime import date
from typing import List, Optional
from Modul import Modul
import os
import json 

class Semester:
    """
    Eine Klasse, die ein Semester repräsentiert und Module verwaltet.
    
    Attribute:
        nummer (int): Die Nummer des Semesters
        name (str): Der Name des Semesters
        user: Der Benutzer, dem das Semester gehört
        startdatum (date): Das Startdatum des Semesters
        enddatum (date): Das Enddatum des Semesters
        module (List[Modul]): Eine Liste der Module im Semester
    """
    
    def __init__(self, name: str, user, startdatum: Optional[date] = None, enddatum: Optional[date] = None):
        """
        Initialisiert ein Semester-Objekt.
        
        Args:
            name (str): Der Name des Semesters
            user: Der Benutzer, dem das Semester gehört
            startdatum (Optional[date]): Das Startdatum des Semesters (optional)
            enddatum (Optional[date]): Das Enddatum des Semesters (optional)
        """
        self.nummer: int
        self.name: str = name
        self.user = user        
        self.startdatum: date = startdatum
        self.enddatum: date = enddatum
        self.module: List[Modul] = []
        self.load_semester(self.name)

    def load_semester(self, name: str):
        """
        Lädt die Semesterdaten aus einer JSON-Datei.
        
        Diese Methode sucht nach einer JSON-Datei mit dem Namen des Semesters und lädt
        die enthaltenen Moduldaten sowie Datumsinformationen. Wenn die Datei existiert,
        werden die Module erstellt und der Semesterdaten geladen.
        
        Args:
            name (str): Der Name des Semesters, das geladen werden soll
        """
        pfad = name + ".json"
        pfad = os.path.join(self.user, pfad)
        if os.path.isfile(pfad):
            print("Datei existiert – Semester wird geladen.")
            with open(pfad, "r", encoding="utf-8") as f:
                daten = json.load(f)

            self.nummer = name[-1]
            module_daten = daten.get("module", [])
            
            for mod in module_daten:
                modul = Modul(
                    name=mod["name"],
                    ects=mod["ects"],
                    pruefung=mod["pruefung"],
                    status=mod["status"]
                )
                self.module.append(modul)

            # Wenn kein Datum übergeben wurde, nimm Daten aus der Datei
            self.startdatum = date.fromisoformat(daten["startdatum"])
            self.enddatum = date.fromisoformat(daten["enddatum"])
    
    def add_modul(self, modul: Modul): 
        """
        Fügt ein Modul zum Semester hinzu und speichert es in der JSON-Datei.
        
        Diese Methode fügt ein Modul zur internen Liste hinzu und aktualisiert
        die zugehörige JSON-Datei, indem das Modul dort hinzugefügt wird.
        
        Args:
            modul (Modul): Das Modul, das hinzugefügt werden soll
        """
        self.module.append(modul)
        pfad = f"{self.name}.json"
        pfad = os.path.join(self.user, pfad)
        modul_dict = {
        "name": modul.name,
        "ects": modul.ects,
        "pruefung": modul.pruefung,
        "status": modul.status
        }
        if os.path.exists(pfad):
            with open(pfad, "r", encoding="utf-8") as f:
                try:
                    daten = json.load(f)
                except json.JSONDecodeError:
                    daten = {}
        else:
            daten = {}

        # Falls keine Module vorhanden sind, leere Liste einfügen
        if "module" not in daten:
            daten["module"] = []

        # Modul anhängen
        daten["module"].append(modul_dict)

        # Datei speichern
        with open(pfad, "w", encoding="utf-8") as f:
            json.dump(daten, f, indent=4, ensure_ascii=False)
            
    def change_module(self, old_module: Modul, new_module: Modul):
        """
        Ersetzt ein bestehendes Modul durch ein neues Modul.
        
        Diese Methode sucht ein bestehendes Modul in der internen Liste und ersetzt es
        durch ein neues Modul. Anschließend wird die JSON-Datei aktualisiert.
        
        Args:
            old_module (Modul): Das zu ersetzende Modul
            new_module (Modul): Das neue Modul, das das alte ersetzt
        """
        if old_module in self.module:
            index = self.module.index(old_module)
            self.module[index] = new_module
        pfad = f"{self.name}.json"
        pfad = os.path.join(self.user, pfad)
        with open(pfad, "r", encoding="utf-8") as f:
            daten = json.load(f)
        module_liste = daten.get("module", [])

        # Suche nach dem alten Modul anhand eindeutiger Eigenschaften (z.B. Name)
        for i, mod in enumerate(module_liste):
            if mod["name"] == old_module.name:
                # Ersetze es durch das neue Modul
                module_liste[i] = {
                    "name": new_module.name,
                    "ects": new_module.ects,
                    "pruefung": new_module.pruefung,
                    "status": new_module.status
                }
                break  # nur das erste passende ersetzen

        # Speichern
        daten["module"] = module_liste
        with open(pfad, "w", encoding="utf-8") as f:
            json.dump(daten, f, indent=4, ensure_ascii=False)

    