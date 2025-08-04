import os
import json
from datetime import date
from typing import Optional

class user_manager:
    """
    Eine Klasse zur Verwaltung von Benutzerkonten.
    
    Diese Klasse behandelt die Registrierung neuer Benutzer und die Anmeldung
    bestehender Benutzer. Benutzerdaten werden in Dateien gespeichert.
    
    Attribute:
        data_content (dict): Ein Dictionary, das die Benutzerdaten enthält
    """
    
    def __init__(self): #,name: str, startdatum: Optional[date] = None, enddatum: Optional[date] = None):
        """
        Initialisiert den Benutzer-Manager.
        """
        self.data_content: dict
    
    def Login(self, username: str, pw: str) -> bool:
        """
        Versucht, einen Benutzer anzumelden.
        
        Diese Methode überprüft, ob ein Benutzerordner mit dem angegebenen
        Benutzernamen existiert und ob das Passwort korrekt ist.
        
        Args:
            username (str): Der Benutzername
            pw (str): Das Passwort
            
        Returns:
            bool: True, wenn die Anmeldung erfolgreich war, sonst False
        """
        if os.path.exists(username) and os.path.isdir(username):
            data_path = os.path.join(username, "Data")
            if os.path.exists(data_path):
                with open(data_path, "r") as data_file:
                    self.data_content = json.load(data_file)
                    stored_pw = self.data_content.get("pw", "")
                    if stored_pw == pw:
                        return True
        return False

    def Registrieren(self, name: str, pw: str, ziel_note: str, startdatum: date, enddatum: date, studiengang: str) -> Optional[str]:
        """
        Registriert einen neuen Benutzer.
        
        Diese Methode erstellt einen neuen Ordner für den Benutzer und speichert
        die Benutzerdaten in einer Datei namens "Data" in diesem Ordner.
        
        Args:
            name (str): Der gewünschte Benutzername
            pw (str): Das Passwort des Benutzers
            ziel_note (str): Die angestrebte Zielnote
            startdatum (date): Das Startdatum des Studiums
            enddatum (date): Das geplante Enddatum des Studiums
            studiengang (str): Der Studiengang des Benutzers
            
        Returns:
            Optional[str]: "Name bereits vergeben", wenn der Name bereits existiert, sonst None
        """
        # Check if folder with the given name exists
        if os.path.exists(name) and os.path.isdir(name):
            return "Name bereits vergeben"
        else:
            # Create the folder
            os.makedirs(name)
            # Create a file named "Data" inside the folder and write the password, ziel_note, and enddatum as JSON
            data_path = os.path.join(name, "Data")
            self.data_content = {
                "pw": pw,
                "ziel_note": ziel_note,
                "startdatum": startdatum,                
                "enddatum": enddatum,
                "studiengang": studiengang
            }
            with open(data_path, "w") as data_file:
                json.dump(self.data_content, data_file)
            return None

