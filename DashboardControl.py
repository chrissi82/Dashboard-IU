from Semester import Semester
from datetime import date, datetime, timedelta
from typing import List, Tuple
import os
import json
from Modul import Modul


 

class dashboard_control:
    """
    Eine Hauptsteuerungsklasse für das Dashboard.
    
    Diese Klasse verwaltet Semester, Module und Benutzerdaten. Sie ist für das
    Laden bestehender Semester, Erstellen neuer Semester und Berechnen von
    Statistiken verantwortlich.
    
    Attribute:
        user (str): Der Benutzername
        semesters (List[Semester]): Eine Liste aller Semester des Benutzers
        semester_names (List[str]): Eine Liste der Namen aller Semester
    """
    
    def __init__(self, user: str):
        """
        Initialisiert das Dashboard-Control-Objekt.
        
        Args:
            user (str): Der Benutzername
        """
        self.user = user
        self.semesters: List[Semester] = []
        self.semester_names: List[str] = []
        self.lade_existierende_semester()
        

        
    
    
    
    
    def lade_existierende_semester(self):         
        """
        Lädt alle existierenden Semester des Benutzers.
        
        Diese Methode durchsucht den Benutzerordner nach JSON-Dateien mit
        Semesterdaten und erstellt für jede gefundene Datei ein Semester-Objekt.
        """
        for i in range(1, 100):
                if os.path.exists(self.user) and os.path.isdir(self.user):
                    dateiname = os.path.join(self.user, f"semester{i}.json")                
                if os.path.isfile(dateiname):
                    self.semesters.append(Semester(f"semester{i}", self.user))
                    self.semester_names.append(f"{i}. Semester")


    
    def split_date_period_into_segments(self, start_date: date, end_date: date) -> List[Tuple[date, date]]:
        """
        Teilt einen Datumsbereich in Semesterabschnitte auf.
        
        Diese Methode unterteilt einen Zeitraum in Halbjahre (bis Juni und bis Dezember).
        Jeder Abschnitt beginnt entweder am 1. Januar oder 1. Juli und endet am
        30. Juni oder 31. Dezember.
        
        Args:
            start_date (date): Das Startdatum des Zeitraums
            end_date (date): Das Enddatum des Zeitraums
            
        Returns:
            List[Tuple[date, date]]: Eine Liste von Tupeln mit Start- und Enddaten der Abschnitte
        """
        
        
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        semesterdates = []
        current_start: date = start_date

        while current_start < end_date:
            
            year = current_start.year
            june_30 = date(year, 6, 30)
            dec_31 = date(year, 12, 31)

            if current_start <= june_30:
                segment_end = june_30
            else:
                segment_end = dec_31

            if segment_end > end_date:
                segment_end = end_date

            semesterdates.append((current_start, segment_end))

            if segment_end == end_date:
                break

            current_start = segment_end + timedelta(days=1)

        
        return semesterdates
    
    def neues_semester(self, name: str, user_data: dict) -> Semester:
        """
        Erstellt ein neues Semester oder lädt ein bestehendes Semester.
        
        Diese Methode prüft, ob eine JSON-Datei für das Semester bereits existiert.
        Wenn ja, wird das Semester geladen. Wenn nein, wird ein neues Semester
        mit Daten aus den Benutzerdaten erstellt.
        
        Args:
            name (str): Der Name des Semesters (z.B. "semester1")
            user_data (dict): Die Benutzerdaten mit Start- und Enddatum
            
        Returns:
            Semester: Das erstellte oder geladene Semester-Objekt
        """
        pfad = name + ".json"
        pfad = os.path.join(self.user, pfad) 
        if os.path.isfile(pfad):
            print("Datei existiert – Semester wird geladen.")
            with open(pfad, "r", encoding="utf-8") as f:
                daten = json.load(f)

            
            module_daten = daten.get("module", [])
            
            
            start = date.fromisoformat(daten["startdatum"])
            end = date.fromisoformat(daten["enddatum"])

            semester = Semester(name, self.user, start, end)

            for mod in module_daten:
                modul = Modul(
                    name=mod["name"],
                    ects=mod["ects"],
                    pruefung=mod["pruefung"],
                    status=mod["status"]
                )
                semester.add_modul(modul)

            self.semesters.append(semester)
            return semester

        else:
            
            print("Datei nicht vorhanden – neues Semester wird erstellt.")
            nummer = int(name[-1])
            
            startdatum = user_data.get("startdatum", "Unbekannt")
            enddatum = user_data.get("enddatum", "Unbekannt")
            datestouples = self.split_date_period_into_segments(startdatum,enddatum)
            try:
                
                
                start = datestouples[nummer-1][0]
                end = datestouples[nummer-1][1]
                
            except Exception as e:
                print("Fehler beim Bearbeiten:", e)
                start = date(2000,1,1)
                end = date(2000,1,1)
                

            nummer = name[-1]
            neues = Semester(name, self.user, start, end)
            self.semesters.append(neues)

            daten = {
                "nummer": nummer,
                "startdatum": start.isoformat(),
                "enddatum": end.isoformat(),
                "module": []
            }
            with open(pfad, "w", encoding="utf-8") as f:
                json.dump(daten, f, indent=4, ensure_ascii=False)

            return neues



    def get_alle_semester(self) -> List[Semester]:
        """
        Gibt alle Semester des Benutzers zurück.
        
        Returns:
            List[Semester]: Eine Liste aller Semester
        """
        return self.semesters



    def get_timing_status(self, name: str) -> str:
        """
        Ermittelt den Zeitplanstatus eines Semesters.
        
        Diese Methode prüft, ob das Semester noch nicht begonnen hat, aktuell läuft
        oder bereits abgeschlossen ist. Im abgeschlossenen Fall wird geprüft, ob
        alle Module bearbeitet wurden.
        
        Args:
            name (str): Der Name des Semesters (z.B. "semester1")
            
        Returns:
            str: Der Status des Semesters (z.B. "✓ Im Zeitplan")
        """
        pfad = os.path.join(self.user, name + ".json")
        
        with open(pfad, "r", encoding="utf-8") as file:
            daten = json.load(file)

        start_str = daten.get("startdatum")
        end_str = daten.get("enddatum")

        start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        today = date.today()
        module = daten.get("module", [])
        if not module:
            return "Noch keine Module hinzugefügt"
        if today < start_date:
            return "✓ Im Zeitplan, Semester noch nicht begonnen"
        elif start_date <= today <= end_date:
            return "✓ Im Zeitplan"
        else:
            # Semester ist vorbei → Module prüfen
            
            for mod in module:
                status = mod.get("status", "").lower()
                
                if "in arbeit" in status or "ausstehend" in status:
                    return "✗ Nicht im Zeitplan"

            return "✓ Semester abgeschlossen"
    
    
    def add_all_ects(self)-> int:
        """
        Berechnet die Gesamtzahl der erreichten ECTS-Punkte.
        
        Diese Methode durchsucht alle Semester des Benutzers und summiert die
        ECTS-Punkte aller Module mit einem positiven Status (✓).
        
        Returns:
            int: Die Gesamtzahl der erreichten ECTS-Punkte
        """
        ects = 0
        for i in range(1, 100):
                if os.path.exists(self.user) and os.path.isdir(self.user):
                    pfad = os.path.join(self.user, f"semester{i}.json")                
                if os.path.isfile(pfad):
                    with open(pfad, "r", encoding="utf-8") as file:
                        daten = json.load(file)
                        module = daten.get("module", [])
                        for mod in module:
                            status = mod.get("status", "")
                            
                            if status[0] == "✓":                                
                                ects += mod.get("ects", "")
        return ects
    
    def append_all_notes(self)-> list:
        """
        Sammelt alle Noten aus allen Semestern.
        
        Diese Methode durchsucht alle Semester des Benutzers und extrahiert
        die Noten aller Module mit einem positiven oder negativen Status (✓ oder ✗).
        
        Returns:
            list: Eine Liste aller Noten
        """
        notes = []
        for i in range(1, 100):
                if os.path.exists(self.user) and os.path.isdir(self.user):
                    pfad = os.path.join(self.user, f"semester{i}.json")                
                if os.path.isfile(pfad):
                    with open(pfad, "r", encoding="utf-8") as file:
                        daten = json.load(file)
                        module = daten.get("module", [])
                        for mod in module:
                            status = mod.get("status", "")
                            
                            if status[0] == "✓":
                                note = float(status.replace("✓", "").strip())
                                notes.append(note)
                                
                            if status[0] == "✗":
                                note = float(status.replace("✗", "").strip())
                                notes.append(note)
        return notes                        
