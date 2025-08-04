import json
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import os
import sys

from Modul import Modul
from DashboardControl import dashboard_control

from UserManager import user_manager
user_manager = user_manager()



class dashboard_ui:
    """
    Hauptklasse für die Benutzeroberfläche des Dashboards.

    Verwaltet die Initialisierung, Registrierung, Login, Start des Dashboards,
    das Hinzufügen/Bearbeiten von Modulen und die gesamte Darstellung im GUI.
    """
    def __init__(self):
        """
        Konstruktor – initialisiert wichtige Variablen und startet den Registrierungs-/Login-Screen.

        Attribute:
        - dashboard_control: Verweist auf die Logikschicht des Dashboards (z. B. Modulverwaltung)
        - user_data: Wörterbuch mit Benutzerdaten (z. B. Zielnote, Studiengang etc.)
        - tempbenutzername: Temporärer Speicher für den Benutzernamen nach erfolgreichem Login
        """
        self.dashboard_control = None    
        self.user_data: dict
        self.create_registerscreen()
        self.tempbenutzername = ""
        
    
    def create_registerscreen(self):
        """
        Erstellt das GUI für Registrierung und Login.

        Erlaubt dem Benutzer, sich zu registrieren oder anzumelden.
        Entsprechend der Auswahl (Radiobuttons) werden Eingabefelder (z. B. Zielnote, Studiengang) angezeigt.
        Nach Klick auf 'Bestätigen' wird entweder registriert oder eingeloggt.

        -> Erfolgreiche Eingabe führt zu `close_window()` und dann zu `start_main_window()`.
        """

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        self.window = ctk.CTk()
        self.window.title("Login Fenster")
        self.window.geometry("1300x750")
        self.window.configure(fg_color="#f0f0f0")

        self.mode_var = ctk.StringVar(value="Registrieren")

        ctk.CTkLabel(self.window, text="Bitte auswählen", font=("Arial", 16, "bold")).pack(pady=(20, 10))

        

        # Radiobuttons
        radio_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        radio_frame.pack(pady=(0, 10))
        ctk.CTkRadioButton(radio_frame, text="Registrieren", variable=self.mode_var, value="Registrieren").pack(side="left", padx=10)
        ctk.CTkRadioButton(radio_frame, text="Anmelden", variable=self.mode_var, value="Anmelden").pack(side="left", padx=10)

        # Container für Felder
        form_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        form_frame.pack(pady=10)

        # Eingabefelder
        benutzername_entry = ctk.CTkEntry(form_frame, placeholder_text="Benutzername z.B. MaxMustermann", width=400)
        passwort_entry = ctk.CTkEntry(form_frame, placeholder_text="Passwort z.B. 12mulm34!", show="*", width=400)
        zielnote_entry = ctk.CTkEntry(form_frame, placeholder_text="Zielnote z.B. 2.0", width=400)
        startdatum_entry = ctk.CTkEntry(form_frame, placeholder_text="Startdatum (JJJJ-MM-TT)", width=400)
        enddatum_entry = ctk.CTkEntry(form_frame, placeholder_text="Enddatum (JJJJ-MM-TT)", width=400)
        studiengang_entry = ctk.CTkEntry(form_frame, placeholder_text="Studiengang z.B. Medizinische Informatik", width=400)

        def update_fields():
            for widget in form_frame.winfo_children():
                widget.pack_forget()

            benutzername_entry.pack(pady=5, fill="x", padx=20)
            passwort_entry.pack(pady=5, fill="x", padx=20)

            if self.mode_var.get() == "Registrieren":
                zielnote_entry.pack(pady=5, fill="x", padx=20)
                startdatum_entry.pack(pady=5, fill="x", padx=20)
                enddatum_entry.pack(pady=5, fill="x", padx=20)
                studiengang_entry.pack(pady=5, fill="x", padx=20)

        # Trigger initial + on change
        update_fields()
        self.mode_var.trace_add("write", lambda *args: update_fields())
        
        close_button = ctk.CTkButton(self.window, text="Bestätigen", command=lambda: self.close_window(
            from_close_button=True,
            benutzername=str(benutzername_entry.get()),
            passwort=str(passwort_entry.get()),
            zielnote=str(zielnote_entry.get()),
            startdatum=str(startdatum_entry.get()),
            enddatum=str(enddatum_entry.get()),
            studiengang=str(studiengang_entry.get())
        ))
        close_button.pack(padx=20, pady=20)

        
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_x_close)  # sauberes Schließen
        self.window.mainloop()
        

    def close_window(self, from_close_button=False, benutzername=None, passwort=None, zielnote=None, startdatum=None, enddatum=None, studiengang=None):
        """
        Wird beim Klick auf 'Bestätigen' oder beim Schließen des Fensters ausgelöst.

        - Führt Registrierung oder Login durch.
        - Bei Erfolg werden Benutzerdaten geladen und das Haupt-Dashboard gestartet.
        - Wenn `from_close_button=False`, wird das Fenster nur geschlossen (z. B. bei X-Klick).
        """
        if from_close_button:
            if self.mode_var.get() == "Registrieren":
                result = user_manager.Registrieren(benutzername, passwort, zielnote, startdatum, enddatum, studiengang)
                if result == "Name bereits vergeben":
                    if hasattr(self, "error_label") and self.error_label:
                        self.error_label.destroy()
                    self.error_label = ctk.CTkLabel(self.window, text="Registrierung fehlgeschlagen! Benutzername bereits vergeben", text_color="red")
                    self.error_label.pack(pady=(0, 10))
                    
                    return
                login_success = user_manager.Login(benutzername, passwort)
                if not login_success:
                    if hasattr(self, "error_label") and self.error_label:
                        self.error_label.destroy()
                    self.error_label = ctk.CTkLabel(self.window, text="Login fehlgeschlagen", text_color="red")
                    self.error_label.pack(pady=(0, 10))
                    
                    return
            elif self.mode_var.get() == "Anmelden":
                login_success = user_manager.Login(benutzername, passwort)
                if not login_success:
                    if hasattr(self, "error_label") and self.error_label:
                        self.error_label.destroy()
                    self.error_label = ctk.CTkLabel(self.window, text="Login fehlgeschlagen", text_color="red")
                    self.error_label.pack(pady=(0, 10))
                    
                    return

            # Wenn wir hier ankommen, war alles erfolgreich
            
            self.user_data = user_manager.data_content
            self.dashboard_control = dashboard_control(benutzername)
            self.tempbenutzername = benutzername            
            


        self.window.withdraw()
        self.window.grab_release()
        self.window.quit()
        self.start_main_window(benutzername)
            
            
        
        # Fenster sicher schließen, unabhängig von Button oder X    
        
        
        

                    
            

    def on_window_x_close(self):
        
        """
        Wird ausgeführt, wenn das Fenster über das 'X' geschlossen wird.
        Ruft `close_window()` mit einem Sicherheits-Flag auf.
        """
        self.close_window(from_close_button=False)
    
        
    

    def start_main_window(self, benutzername):
        """
        Startet das Haupt-Dashboard nach erfolgreichem Login.

        Lädt Benutzerdaten aus Datei, erstellt GUI-Elemente für Semesterwahl, Fortschrittsanzeige,
        Modulübersicht und Buttons zum Hinzufügen von Modulen/Semestern.

        Parameter:
        - benutzername: Der eingeloggte Benutzername, dessen Daten geladen werden.
        """
        user_dir = os.path.join(os.getcwd(), benutzername)

        

        # Default values
        self.ziel_note = 1.0
        self.studiengang = "Unbekannt"
        self.startdatum = "Unbekannt"
        self.enddatum = "Unbekannt"

        if os.path.isdir(user_dir):
            data_file = os.path.join(user_dir, "Data")
            if os.path.isfile(data_file):
                
                try:
                    with open(data_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self.ziel_note = float(data.get("ziel_note", self.ziel_note))
                    self.studiengang = data.get("studiengang", self.studiengang)
                    self.startdatum = data.get("startdatum", self.startdatum)
                    self.enddatum = data.get("enddatum", self.enddatum)
                except Exception as e:
                    print(f"Fehler beim Lesen der Data-Datei: {e}")

        self.current_sem = "semester1"
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        
        
        self.root = ctk.CTk()
        self.root.title(f"Modulübersicht – {self.studiengang}")
        self.root.geometry("1300x750")
        self.root.configure(fg_color="#f0f0f0")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        # === Header Frame ===
        self.header_frame = ctk.CTkFrame(self.root, fg_color="#f0f0f0")
        self.header_frame.pack(pady=20, padx=30, fill="x")

        # === Hauptbereich ===
        main_frame = ctk.CTkFrame(self.root, fg_color="white", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        ctk.CTkLabel(main_frame, text=f"Modulübersicht - {self.studiengang}", font=("Arial", 18, "bold"), text_color="black").pack(anchor="w", pady=(20, 10), padx=20)
         
        self.table_frame = ctk.CTkFrame(main_frame, fg_color="white")
        self.table_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(self.table_frame, text=f"Modulübersicht – {self.studiengang}", font=("Helvetica", 16, "bold"), text_color="black").pack(pady=(0, 10))

        
        semester_frame = ctk.CTkFrame(main_frame, fg_color="white")
        semester_frame.pack(anchor="w", padx=20, pady=(0, 10))

        user_data = self.user_data
        add_semester_button = ctk.CTkButton(semester_frame, text="+ Semester hinzufügen", command= lambda: self.add_new_semester(user_data), width=160, height=30, fg_color="#cccccc", text_color="black")
        add_semester_button.pack(side="left", padx=10)
        
        ctk.CTkLabel(semester_frame, text="Semesterauswahl:", font=("Arial", 13), text_color="black").pack(side="left")
        
        if self.dashboard_control.semester_names == []:
            dropdown_values = ["Noch kein Semster erstellt"]
        else:
            dropdown_values = self.dashboard_control.semester_names
        self.semester_dropdown = ctk.CTkOptionMenu(
            semester_frame,
            values=dropdown_values,
            command=self.semester_change  # Ruft update_dashboard mit Auswahl auf
        )

        # Default setzen: letztes vorhandenes Semester
        if self.dashboard_control.semester_names:
            letzter_eintrag = self.dashboard_control.semester_names[-1]
            self.semester_dropdown.set(letzter_eintrag)
            self.semester_change(letzter_eintrag)  # Direkt beim Start ausführen

        self.semester_dropdown.pack(side="left", padx=10)


        add_module_button = ctk.CTkButton(
            main_frame,
            text="+ Modul",
            fg_color="#4CAF50",
            text_color="white",
            corner_radius=10,
            command=self.on_add_module_click  # <== HIER
        )
        add_module_button.pack(anchor="e", padx=20, pady=10)


        # Optionally, add some padding or margins to the overall frame
        self.table_frame.pack(pady=20)

        
        self.root.mainloop()
        
        
        
        # Funktion zur Aktualisierung bei Auswahl
    
    def semester_change(self, sem):
        """
        Wird ausgeführt, wenn ein anderes Semester im Dropdown-Menü ausgewählt wird. Führt zu update_dashoboard, was dass dashboard aktualisiert

        Parameter:
        - sem: Der Name des Semesters (z. B. '1. Semester'), das angezeigt werden soll.
        """
        global current_sem
        self.update_dashboard(sem)
        current_sem = sem    
        
    def on_closing(self):
        """
        Beendet die gesamte Anwendung, wenn das Dashboard-Fenster geschlossen wird.

        Verwendet `sys.exit()` (hartes Beenden aller Prozesse).
        """
        sys.exit()  
    
    # === Fortschrittskreis mit matplotlib ===
    def create_progress_circle(self, parent, percent):
        """
        Erstellt einen Fortschrittskreis mit matplotlib zur Anzeige des Fortschritts in Prozent.

        Parameter:
        - parent: Das tkinter-Parent-Widget, in dem der Kreis erscheinen soll.
        - percent: Wert zwischen 0.0 und 1.0 (z. B. 0.75 für 75%)
        """
        fig, ax = plt.subplots(figsize=(1.8, 1.8), dpi=100)
        wedges, _ = ax.pie([percent, 1 - percent],
                        startangle=90,
                        counterclock=False,
                        colors=["#4CAF50", "#e0e0e0"],
                        wedgeprops={'width': 0.3})
        ax.text(0, 0, f"{int(percent * 100)}%", ha="center", va="center", fontsize=16)
        ax.set(aspect="equal")
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=5)

    def create_info_box(self, parent, title, value, subtext, include_circle=False, percent=0, text_color1="black", text_color2="#4CAF50", text_color3="#4CAF50"):
        """
        Erstellt eine Infobox mit Titel, Wert, Untertitel und optionalem Fortschrittskreis.

        Parameter:
        - parent: Übergeordnetes Widget (meist das Header-Frame)
        - title: Titel der Box (z. B. "Notendurchschnitt")
        - value: Hauptwert (z. B. "2.3")
        - subtext: Unterzeile (z. B. "Zielnote: 2.0")
        - include_circle: Falls True, wird ein Fortschrittskreis eingebaut.
        - percent: Prozentwert für Fortschrittskreis
        - text_colorX: Farben für verschiedene Textelemente
        """
        box = ctk.CTkFrame(parent, fg_color="white", corner_radius=12)
        box.pack(side="left", expand=True, fill="both", padx=15)
        # Titel, Wert und Subtext (wie zuvor)
        title_label = ctk.CTkLabel(box, text=title, font=("Arial", 13, "bold"), text_color=text_color1)
        title_label.pack(anchor="nw", padx=15, pady=(15, 0))
        value_label = ctk.CTkLabel(box, text=value, font=("Arial", 28, "bold"), text_color=text_color2)
        value_label.pack(anchor="nw", padx=15, pady=(5, 0))
        subtext_label = ctk.CTkLabel(box, text=subtext, font=("Arial", 11), text_color=text_color3)
        subtext_label.pack(anchor="nw", padx=15, pady=(0, 10))
        # Fortschrittskreis in der rechten oberen Ecke der Box
        if include_circle:
            circle_frame = ctk.CTkFrame(box, fg_color="transparent")  # Transparenter Container für den Kreis
            circle_frame.place(relx=0.95, rely=-0.1, anchor="ne")     # Rechts oben (95% vom Rand, 15% von oben)
            self.create_progress_circle(circle_frame, percent)             # Kreis in den Container einfügen

    def update_dashboard(self, semester="-"):    
        """
        Aktualisiert das Dashboard basierend auf dem aktuell ausgewählten Semester.

        - Entfernt bestehende Widgets im Hauptbereich.
        - Zeigt die Module des Semesters als Karten mit Name, Note, Credits und Schaltflächen zum Bearbeiten/Löschen.
        - Aktualisiert zudem die Fortschrittsinformationen im Header (z. B. Ø-Note, ECTS, Fortschritt).

        Parameter:
        - semester: Name des gewählten Semesters (z. B. '1. Semester')
        """

        if semester == "-":
            print("error, kein semester ausgewählt")
            return
        semesternummer = int(semester[0])
        
        modules = self.dashboard_control.semesters[semesternummer-1].module
        
        # Berechnungen:
        
        gesamt_ects = 0
        erreichte_ects = 0
        noten = []
        alle_noten = []
        bestandene_module = 0
        gesamte_module = len(modules)
        insgesamt_erreichte_ects = self.dashboard_control.add_all_ects()
        
        for modul in modules:
            gesamt_ects += modul.ects
            if isinstance(modul.status, str) and modul.status.startswith("✓"):
                try:
                    note = float(modul.status.replace("✓", "").strip())                
                    noten.append(note)
                    if note <= 4.0:
                        erreichte_ects += modul.ects
                        bestandene_module += 1
                except ValueError:
                    pass  # Wenn keine gültige Note angegeben ist, überspringen
            if isinstance(modul.status, str) and modul.status.startswith("✗"):
                try:
                    note = float(modul.status.replace("✗", "").strip())                
                    noten.append(note)
                    if note <= 4.0:
                        erreichte_ects += modul.ects
                        bestandene_module += 1
                except ValueError:
                    pass  # Wenn keine gültige Note angegeben ist, überspringen   
   

        durchschnittsnote = round(sum(noten) / len(noten), 2) if noten else "-"  
        alle_noten = self.dashboard_control.append_all_notes()
        durchschnittsnote_insgesamt = round(sum(alle_noten) / len(alle_noten), 2) if alle_noten else "-"  
        # Infobox 
        for widget in self.header_frame.winfo_children():
            widget.destroy()
            
        semestername = f"semester{semester[0]}"
        timing = self.dashboard_control.get_timing_status(semestername)    
            
        self.create_info_box(self.header_frame, "GESAMTFORTSCHRITT", f"{insgesamt_erreichte_ects}/180 ECTS", "", include_circle=True, percent=insgesamt_erreichte_ects/180, text_color1="black", text_color2="#4CAF50", text_color3="#4CAF50")
        text_color = "green"     
        if durchschnittsnote_insgesamt != "-" and durchschnittsnote_insgesamt > self.ziel_note:
            text_color = "red"
        self.create_info_box(self.header_frame, "NOTENDURCHSCHNITT", durchschnittsnote_insgesamt, f"Zielnote: {self.ziel_note}", text_color2=text_color)
        text_color = "green"
        if timing == "✗ Nicht im Zeitplan":
            text_color = "red"       
        self.create_info_box(self.header_frame, "ZEITPLANUNG", f"Aktuell: {semester}", timing, text_color3=text_color)    
            
        # Tabelle 
        for widget in self.table_frame.winfo_children():
            widget.destroy()  

        # Tabelle neu aufbauen
        heading = ctk.CTkLabel(self.table_frame, text=f"Modulübersicht - {self.studiengang}", font=("Helvetica", 16, "bold"))
        heading.pack(pady=(0, 10))

        header_row = ctk.CTkFrame(self.table_frame, fg_color="#e0e0e0", height=40)
        header_row.pack(fill="x", padx=10, pady=1)
        ctk.CTkLabel(header_row, text="", width=15).pack(side="left")
        ctk.CTkLabel(header_row, text="Modul", font=("Courier New", 12, "bold"), width=90*7, anchor="w", text_color="black").pack(side="left")
        ctk.CTkLabel(header_row, text="ECTS", font=("Courier New", 12, "bold"), width=10*7, anchor="w", text_color="black").pack(side="left")
        ctk.CTkLabel(header_row, text="Prüfungsform", font=("Courier New", 12, "bold"), width=45*7, anchor="w", text_color="black").pack(side="left")
        ctk.CTkLabel(header_row, text="Status", font=("Courier New", 12, "bold"), width=10*7, anchor="w", text_color="black").pack(side="left")

        
        row_colors = ["#ffffff", "#f0f0f0"]
        for i, modul in enumerate(modules):
            textcolor = "black"
            try:
                note = modul.status[0]  # nimmt das Zeichen an Index 0
                if note == "✓":
                    textcolor = "green"
                elif note == "✗":
                    textcolor = "red"
                else:
                    textcolor = "black"
            except Exception as e:
                print("Fehler beim Parsen des Status:", e)
            row_frame = ctk.CTkFrame(self.table_frame, fg_color=row_colors[i % 2], height=50, corner_radius=5)
            row_frame.pack(fill="x", padx=10, pady=2)

            ctk.CTkLabel(row_frame, text="", width=15).pack(side="left")
            ctk.CTkLabel(row_frame, text=modul.name, font=("Courier New", 12), width=90*7, anchor="w", text_color=f"{textcolor}").pack(side="left")
            ctk.CTkLabel(row_frame, text=modul.ects, font=("Courier New", 12), width=10*7, anchor="w", text_color=f"{textcolor}").pack(side="left")
            ctk.CTkLabel(row_frame, text=modul.pruefung, font=("Courier New", 12), width=45*7, anchor="w", text_color=f"{textcolor}").pack(side="left")
            ctk.CTkLabel(row_frame, text=modul.status, font=("Courier New", 12), width=10*7, anchor="w", text_color=f"{textcolor}").pack(side="left")
            ctk.CTkButton(row_frame,text="⚙",width=40,height=28,fg_color="#cccccc",text_color="black",corner_radius=5,
            command=lambda m=modul: self.edit_module_popup(m)).pack(side="left", padx=(5, 0))
            
        # Zusammenfassungszeile hinzufügen (wie Header, aber unten)
        summary_row = ctk.CTkFrame(self.table_frame, fg_color="#e0e0e0", height=40)
        summary_row.pack(fill="x", padx=10, pady=(10, 0))

        

        # Anzeige
        ctk.CTkLabel(summary_row, text="", width=15).pack(side="left")
        ctk.CTkLabel(summary_row, text=f"Gesamt ECTS im Semester: {str(gesamt_ects)} | Davon erreicht: {erreichte_ects}", font=("Courier New", 12, "bold"), width=90*7, anchor="w", text_color="black").pack(side="left")
        ctk.CTkLabel(summary_row, text="", font=("Courier New", 12), width=7*10, anchor="w", text_color="black").pack(side="left")
        ctk.CTkLabel(summary_row, text=f"Ø {durchschnittsnote}", font=("Courier New", 12), width=45*7, anchor="w", text_color="black").pack(side="left")
        ctk.CTkLabel(summary_row, text=f"{bestandene_module}/{gesamte_module} bestanden", font=("Courier New", 12), width=7*10, anchor="w", text_color="black").pack(side="left")

    def add_new_semester(self, user_data: dict):        
        """
        Öffnet ein neues Fenster zur Eingabe eines neuen Semesters.

        - Prüft, ob der Semestername bereits existiert.
        - Wenn nicht, wird das Semester im Backend hinzugefügt und das Dashboard aktualisiert.
        """
        nummer = len(self.dashboard_control.get_alle_semester()) + 1
        semester_name = f"{nummer}. Semester"                
        self.dashboard_control.neues_semester(f"semester{nummer}", user_data)            
        self.dashboard_control.semester_names.append(semester_name)
        self.semester_dropdown.configure(values=self.dashboard_control.semester_names)
        self.semester_dropdown.set(semester_name)
        self.semester_change(semester_name)                
            

        

    def edit_module_popup(self, modul):
        """
        Öffnet ein Popup-Fenster zur Bearbeitung eines bestehenden Moduls.

        - Ermöglicht die Bearbeitung von Modulnamen, Note und Credits.
        - Speichert die Änderungen im Backend und aktualisiert das Dashboard.

        Parameter:
        - modul: Modul-Objekt, das bearbeitet werden soll.
        - parent_frame: Das GUI-Element, in dem das Modul aktuell dargestellt wird.
        - semester: Das zugehörige Semester des Moduls.
        """
        popup = ctk.CTkToplevel(self.root)
        popup.title(f"Modul bearbeiten: {modul.name}")
        popup.geometry("600x550")  # Fenster breiter, damit Platz für neue Eingaben
        popup.grab_set()

        ctk.CTkLabel(popup, text="Modul bearbeiten", font=("Arial", 16, "bold")).pack(pady=(20, 10))

        # Modulname
        ctk.CTkLabel(popup, text="Modulname:").pack(anchor="w", padx=30)
        name_entry = ctk.CTkEntry(popup, width=400)
        name_entry.insert(0, modul.name)
        name_entry.pack(pady=5)

        # ECTS
        ctk.CTkLabel(popup, text="ECTS:").pack(anchor="w", padx=30, pady=(10, 0))
        ects_entry = ctk.CTkEntry(popup, width=100)
        ects_entry.insert(0, str(modul.ects))
        ects_entry.pack(pady=5)

        # Prüfungsform mit Dauer (nebeneinander)
        ctk.CTkLabel(popup, text="Prüfungsform:").pack(anchor="w", padx=30, pady=(10, 0))

        pruefung_frame = ctk.CTkFrame(popup, fg_color="transparent")
        pruefung_frame.pack(anchor="w", padx=30)

        pruefungsform_var = ctk.StringVar(value="Klausur")
        klausur_dauer_var = ctk.StringVar(value="90min")

        # Neue Variablen und Entry für Advanced Workbook (Wochen) und Portfolio (Aufgaben)
        aw_wochen_var = ctk.StringVar(value="")
        portfolio_aufgaben_var = ctk.StringVar(value="")

        pruefung_dropdown = ctk.CTkOptionMenu(
            pruefung_frame,
            values=["Klausur", "Advanced Workbook", "Portfolio"],
            variable=pruefungsform_var,
            width=250
        )
        pruefung_dropdown.pack(side="left", pady=5)

        # Klausur Dauer Dropdown
        dauer_label = ctk.CTkLabel(pruefung_frame, text="Dauer:")
        dauer_dropdown = ctk.CTkOptionMenu(
            pruefung_frame,
            values=["30min", "60min", "90min", "120min"],
            variable=klausur_dauer_var,
            width=100
        )

        # Advanced Workbook Wochen Eingabe
        aw_wochen_label = ctk.CTkLabel(pruefung_frame, text="Wochen:")
        aw_wochen_entry = ctk.CTkEntry(pruefung_frame, width=80, textvariable=aw_wochen_var)

        # Portfolio Aufgaben Eingabe
        portfolio_aufgaben_label = ctk.CTkLabel(pruefung_frame, text="Wochen:")
        portfolio_aufgaben_entry = ctk.CTkEntry(pruefung_frame, width=80, textvariable=portfolio_aufgaben_var)

        # Prüfungsform aus modul.pruefung parsen für die Eingabefelder
        pruefung_text = modul.pruefung
        if pruefung_text.startswith("Klausur"):
            pruefungsform_var.set("Klausur")
            if "(" in pruefung_text:
                try:
                    dauer = pruefung_text.split("(")[1].split(")")[0].strip()
                    if dauer in ["30min", "60min", "90min", "120min"]:
                        klausur_dauer_var.set(dauer)
                except:
                    pass
        elif pruefung_text.startswith("Advanced Workbook"):
            pruefungsform_var.set("Advanced Workbook")
            try:
                wochen = pruefung_text.split("(")[1].split(")")[0].replace("Wochen", "").strip()
                aw_wochen_var.set(wochen)
            except:
                aw_wochen_var.set("")
        elif pruefung_text.startswith("Portfolio"):
            pruefungsform_var.set("Portfolio")
            try:
                aufgaben = pruefung_text.split("(")[1].split(")")[0].replace("Aufgaben", "").strip()
                portfolio_aufgaben_var.set(aufgaben)
            except:
                portfolio_aufgaben_var.set("")
        else:
            pruefungsform_var.set("Klausur")  # fallback

        def pruefungsform_gewaehlt(choice):
            # Alle Zusatzfelder zuerst ausblenden
            dauer_label.pack_forget()
            dauer_dropdown.pack_forget()
            aw_wochen_label.pack_forget()
            aw_wochen_entry.pack_forget()
            portfolio_aufgaben_label.pack_forget()
            portfolio_aufgaben_entry.pack_forget()

            if choice == "Klausur":
                dauer_label.pack(side="left", padx=(20, 5))
                dauer_dropdown.pack(side="left")
            elif choice == "Advanced Workbook":
                aw_wochen_label.pack(side="left", padx=(20, 5))
                aw_wochen_entry.pack(side="left")
            elif choice == "Portfolio":
                portfolio_aufgaben_label.pack(side="left", padx=(20, 5))
                portfolio_aufgaben_entry.pack(side="left")

        pruefung_dropdown.configure(command=pruefungsform_gewaehlt)
        pruefungsform_gewaehlt(pruefungsform_var.get())

        # Status
        ctk.CTkLabel(popup, text="Status:").pack(anchor="w", padx=30, pady=(10, 0))
        status_var = ctk.StringVar()

        erledigt_frame = ctk.CTkFrame(popup, fg_color="transparent")
        erledigt_frame.pack(anchor="w", padx=50)

        erledigt_rb = ctk.CTkRadioButton(erledigt_frame, text="Erledigt", variable=status_var, value="Erledigt")
        erledigt_rb.pack(side="left")

        note_entry = ctk.CTkEntry(erledigt_frame, width=100)
        note_entry.pack(side="left", padx=(10, 0))
        note_entry.pack_forget()

        inarbeit_rb = ctk.CTkRadioButton(popup, text="In Arbeit", variable=status_var, value="In Arbeit")
        inarbeit_rb.pack(anchor="w", padx=50)

        ausstehend_rb = ctk.CTkRadioButton(popup, text="Ausstehend", variable=status_var, value="Ausstehend")
        ausstehend_rb.pack(anchor="w", padx=50)

        original_status = modul.status
        if original_status.startswith("✓") or original_status.startswith("✗"):
            status_var.set("Erledigt")
            try:
                note = original_status.split(" ")[1]
                note_entry.insert(0, note)
                note_entry.pack(side="left", padx=(10, 0))
            except IndexError:
                pass
        elif original_status in ["In Arbeit", "Ausstehend"]:
            status_var.set(original_status)
        else:
            status_var.set("In Arbeit")

        def on_status_change():
            if status_var.get() == "Erledigt":
                note_entry.pack(side="left", padx=(10, 0))
            else:
                note_entry.pack_forget()

        trace_id = status_var.trace_add("write", lambda *args: on_status_change())

        def close_popup():
            try:
                status_var.trace_remove("write", trace_id)
            except Exception:
                pass
            popup.destroy()

        popup.protocol("WM_DELETE_WINDOW", close_popup)

        def save_changes():
            try:
                name = name_entry.get()
                ects = int(ects_entry.get())
                pruefung = pruefungsform_var.get()

                if pruefung == "Klausur":
                    pruefung += f" ({klausur_dauer_var.get()})"
                elif pruefung == "Advanced Workbook":
                    wochen = aw_wochen_var.get()
                    if not wochen.isdigit():
                        print("Bitte eine gültige Zahl für Wochen eingeben.")
                        return
                    pruefung += f" ({wochen} Wochen)"
                elif pruefung == "Portfolio":
                    aufgaben = portfolio_aufgaben_var.get()
                    if not aufgaben.isdigit():
                        print("Bitte eine gültige Zahl für Aufgaben eingeben.")
                        return
                    pruefung += f" ({aufgaben} Aufgaben)"

                new_status_choice = status_var.get()
                if new_status_choice == "Erledigt":
                    note = note_entry.get()
                    if not note:
                        print("Bitte Note eingeben.")
                        return
                    if float(note) <= 4.0:
                        status = f"✓ {note}"
                    else:
                        status = f"✗ {note}"
                else:
                    status = new_status_choice

                new_modul = Modul(
                    name=name,
                    ects=ects,
                    pruefung=pruefung,
                    status=status
                )

                self.dashboard_control.semesters[int(current_sem[0]) - 1].change_module(modul, new_modul)
                self.semester_change(current_sem)
                close_popup()

            except Exception as e:
                print("Fehler beim Bearbeiten:", e)

        ctk.CTkButton(popup, text="Speichern", command=save_changes).pack(pady=20)



    def on_add_module_click(self):
        """
        Öffnet ein Eingabefenster zum Hinzufügen eines neuen Moduls zum aktuellen Semester.

        - Nimmt Modulnamen, Note und Credits entgegen.
        - Fügt das Modul bei Bestätigung dem Backend hinzu und aktualisiert das Dashboard.

        Parameter:
        - semester: Das Semester, zu dem das Modul hinzugefügt werden soll.
        """
        popup = ctk.CTkToplevel(self.root)
        popup.title("Neues Modul hinzufügen")
        popup.geometry("600x550")  # Breiteres Fenster
        popup.grab_set()

        ctk.CTkLabel(popup, text="Neues Modul hinzufügen", font=("Arial", 16, "bold")).pack(pady=(20, 10))

        # Modulname
        ctk.CTkLabel(popup, text="Modulname:").pack(anchor="w", padx=30)
        name_entry = ctk.CTkEntry(popup, width=400)
        name_entry.pack(pady=5)

        # ECTS
        ctk.CTkLabel(popup, text="ECTS:").pack(anchor="w", padx=30, pady=(10, 0))
        ects_entry = ctk.CTkEntry(popup, width=100)
        ects_entry.insert(0, "5")
        ects_entry.pack(pady=5)

        # Prüfungsform + Dauer nebeneinander
        ctk.CTkLabel(popup, text="Prüfungsform:").pack(anchor="w", padx=30, pady=(10, 0))

        pruefung_frame = ctk.CTkFrame(popup, fg_color="transparent")
        pruefung_frame.pack(anchor="w", padx=30)

        pruefungsform_var = ctk.StringVar(value="Klausur")
        pruefung_dropdown = ctk.CTkOptionMenu(
            pruefung_frame,
            values=["Klausur", "Advanced Workbook", "Portfolio"],
            variable=pruefungsform_var,
            width=250
        )
        pruefung_dropdown.pack(side="left", pady=5)

        # Dauer Dropdown (für Klausur)
        dauer_label = ctk.CTkLabel(pruefung_frame, text="Dauer:")
        klausur_dauer_var = ctk.StringVar(value="90min")
        dauer_dropdown = ctk.CTkOptionMenu(
            pruefung_frame,
            values=["30min", "60min", "90min", "120min"],
            variable=klausur_dauer_var,
            width=100
        )

        # Eingabefelder für Advanced Workbook und Portfolio
        aw_frame = ctk.CTkFrame(pruefung_frame, fg_color="transparent")
        aw_label = ctk.CTkLabel(aw_frame, text="Wochen:")
        aw_entry = ctk.CTkEntry(aw_frame, width=60)

        portfolio_frame = ctk.CTkFrame(pruefung_frame, fg_color="transparent")
        portfolio_label = ctk.CTkLabel(portfolio_frame, text="Wochen:")
        portfolio_entry = ctk.CTkEntry(portfolio_frame, width=60)

        def pruefungsform_gewaehlt(choice):
            # Erst alle verstecken
            dauer_label.pack_forget()
            dauer_dropdown.pack_forget()
            aw_frame.pack_forget()
            portfolio_frame.pack_forget()

            if choice == "Klausur":
                dauer_label.pack(side="left", padx=(20, 5))
                dauer_dropdown.pack(side="left")
            elif choice == "Advanced Workbook":
                aw_label.pack(side="left")
                aw_entry.pack(side="left", padx=(5, 0))
                aw_frame.pack(side="left", padx=(20, 0))
            elif choice == "Portfolio":
                portfolio_label.pack(side="left")
                portfolio_entry.pack(side="left", padx=(5, 0))
                portfolio_frame.pack(side="left", padx=(20, 0))

        pruefung_dropdown.configure(command=pruefungsform_gewaehlt)
        pruefungsform_gewaehlt(pruefungsform_var.get())

        # Status Auswahl
        ctk.CTkLabel(popup, text="Status:").pack(anchor="w", padx=30, pady=(10, 0))
        status_var = ctk.StringVar(value="In Arbeit")

        erledigt_frame = ctk.CTkFrame(popup, fg_color="transparent")
        erledigt_frame.pack(anchor="w", padx=50)

        erledigt_rb = ctk.CTkRadioButton(erledigt_frame, text="Erledigt", variable=status_var, value="Erledigt")
        erledigt_rb.pack(side="left")

        note_entry = ctk.CTkEntry(erledigt_frame, width=100)
        note_entry.pack(side="left", padx=(10, 0))
        note_entry.pack_forget()

        inarbeit_rb = ctk.CTkRadioButton(popup, text="In Arbeit", variable=status_var, value="In Arbeit")
        inarbeit_rb.pack(anchor="w", padx=50)

        ausstehend_rb = ctk.CTkRadioButton(popup, text="Ausstehend", variable=status_var, value="Ausstehend")
        ausstehend_rb.pack(anchor="w", padx=50)

        def on_status_change():
            if status_var.get() == "Erledigt":
                note_entry.pack(side="left", padx=(10, 0))
            else:
                note_entry.pack_forget()

        trace_id = status_var.trace_add("write", lambda *args: on_status_change())

        def close_popup():
            try:
                status_var.trace_remove("write", trace_id)
            except Exception:
                pass
            popup.destroy()

        popup.protocol("WM_DELETE_WINDOW", close_popup)

        def save_module():
            try:
                name = name_entry.get()
                ects = int(ects_entry.get())
                pruefung = pruefungsform_var.get()
                status_choice = status_var.get()

                if pruefung == "Klausur":
                    pruefung += f" ({klausur_dauer_var.get()})"
                elif pruefung == "Advanced Workbook":
                    wochen = aw_entry.get()
                    if not wochen.isdigit() or int(wochen) <= 0:
                        print("Bitte gültige Anzahl Wochen eingeben.")
                        return
                    pruefung += f" ({wochen} Wochen)"
                elif pruefung == "Portfolio":
                    wochen = portfolio_entry.get()
                    if not wochen.isdigit() or int(wochen) <= 0:
                        print("Bitte gültige Anzahl Aufgaben eingeben.")
                        return
                    pruefung += f" ({wochen} Wochen)"

                if not name:
                    print("Alle Felder müssen ausgefüllt werden.")
                    return

                if status_choice == "Erledigt":
                    note = note_entry.get()
                    if not note:
                        print("Bitte Note eingeben.")
                        return
                    if float(note) <= 4.0:
                        status = f"✓ {note}"
                    else:
                        status = f"✗ {note}"
                else:
                    status = status_choice

                modul = Modul(name=name, ects=ects, pruefung=pruefung, status=status)
                semesternummer = int(current_sem[0])
                self.dashboard_control.semesters[semesternummer - 1].add_modul(modul)

                self.semester_change(current_sem)
                close_popup()

            except ValueError:
                print("ECTS und Note müssen gültige Zahlen sein.")
            except Exception as e:
                print("Fehler beim Speichern:", e)

        ctk.CTkButton(popup, text="OK", command=save_module).pack(pady=20)





dashboard_ui()
