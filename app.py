"""app.py: main module with GUI"""

from tkinter import filedialog as fd
import customtkinter  # type: ignore
import calculation as calc
import visualisation as graph
import data as data
import signal_analysation as analyzed

# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("System")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("blue")
customtkinter.set_widget_scaling(120 / 100)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.plot_open = False

        # configure window
        self.title("MaPaVi - Masking Pattern Visualizer")
        self.geometry(f"{1350}x{780}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_frame,
            text="MaPaVi",
            font=customtkinter.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.testdata_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Ergebnisse aus\n Hörversuchen:"
        )
        self.testdata_label.grid(row=1, column=0, padx=20, pady=(20, 0))
        self.testdata_var = customtkinter.StringVar(value="nicht anzeigen")
        self.testdata_selection = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=[
                "nicht anzeigen",
                "250 Hz 60 dB",
                "1 kHz 40 dB",
                "1 kHz 60 dB",
                "1 kHz 80 dB",
                "4 kHz 60 dB",
            ],
            command=self.testdata_callback,
            variable=self.testdata_var,
        )
        self.testdata_selection.grid(row=2, column=0, padx=20, pady=(5, 0))
        self.appearance_mode_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Appearance Mode:", anchor="w"
        )
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event,
        )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="UI Scaling:", anchor="w"
        )
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=["80%", "90%", "100%", "110%", "120%"],
            command=self.change_scaling_event,
        )
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=750, height=500)
        self.tabview.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.tabview.add("Breitbandiges Signal")
        self.tabview.add("Einzelne Terzbänder")
        self.tabview.add("Datei Laden")
        self.tabview.tab("Breitbandiges Signal").grid_columnconfigure(
            4, weight=1
        )  # configure grid of individual tabs
        self.tabview.tab("Einzelne Terzbänder").grid_columnconfigure(3, weight=1)
        self.tabview.tab("Datei Laden").grid_columnconfigure(0, weight=1)

        # Tab Breitbandiges Signal
        tab_1 = self.tabview.tab("Breitbandiges Signal")
        self.freqband_count = 0

        self.tab_1_header_label_1 = customtkinter.CTkLabel(tab_1, text="Frequenzband")
        self.tab_1_header_label_1.grid(row=0, column=0, padx=20, pady=(5, 20))
        self.tab_1_header_label_2 = customtkinter.CTkLabel(
            tab_1, text="Untere Grenzfrequenz\n (f1) in Hz"
        )
        self.tab_1_header_label_2.grid(row=0, column=1, padx=20, pady=(5, 20))
        self.tab_1_header_label_3 = customtkinter.CTkLabel(
            tab_1, text="Obere Grenzfrequenz\n (f2) in Hz"
        )
        self.tab_1_header_label_3.grid(row=0, column=2, padx=20, pady=(5, 20))
        self.tab_1_header_label_4 = customtkinter.CTkLabel(
            tab_1, text="Pegel(L)\n in dB"
        )
        self.tab_1_header_label_4.grid(row=0, column=3, padx=20, pady=(5, 20))
        # Rauschtyp Auswahl
        self.noise_selector = customtkinter.CTkOptionMenu(
            tab_1, values=["white", "GAR", "GVR"]
        )
        self.noise_selector.grid(row=0, column=5, padx=20, pady=(5, 0))
        # Berechnen Button
        self.thirdbands_submit_button = customtkinter.CTkButton(
            tab_1, text="Mithörschwelle\n Berechnen", command=self.calculate_from_signal
        )
        self.thirdbands_submit_button.grid(row=1, column=5, padx=20, pady=(5, 0))
        # Frequenzband hinzufügen Button
        self.add_freqband_button = customtkinter.CTkButton(
            tab_1,
            text="Band hinzufügen\n (+)",
            command=self.add_freqband,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
        )
        self.add_freqband_button.grid(row=9, column=0, padx=20, pady=(30, 0))
        # Frequenzband entfernen Button
        self.remove_freqband_button = customtkinter.CTkButton(
            tab_1,
            text="Band entfernen \n (-)",
            command=self.remove_freqband,
            state="disabled",
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
        )
        self.remove_freqband_button.grid(row=9, column=1, padx=20, pady=(30, 0))
        # Freqband label
        self.freqband_label_1 = customtkinter.CTkLabel(tab_1, text="Frequenzband 1")
        self.freqband_label_1.grid(row=1, column=0, padx=20, pady=(5, 0))
        self.freqband_label_2 = customtkinter.CTkLabel(tab_1, text="Frequenzband 2")
        self.freqband_label_2.grid(row=2, column=0, padx=20, pady=(5, 0))
        self.freqband_label_2.grid_remove()
        self.freqband_label_3 = customtkinter.CTkLabel(tab_1, text="Frequenzband 3")
        self.freqband_label_3.grid(row=3, column=0, padx=20, pady=(5, 0))
        self.freqband_label_3.grid_remove()
        self.freqband_label_4 = customtkinter.CTkLabel(tab_1, text="Frequenzband 4")
        self.freqband_label_4.grid(row=4, column=0, padx=20, pady=(5, 0))
        self.freqband_label_4.grid_remove()
        self.freqband_label_5 = customtkinter.CTkLabel(tab_1, text="Frequenzband 5")
        self.freqband_label_5.grid(row=5, column=0, padx=20, pady=(5, 0))
        self.freqband_label_5.grid_remove()
        self.freqband_label_6 = customtkinter.CTkLabel(tab_1, text="Frequenzband 6")
        self.freqband_label_6.grid(row=6, column=0, padx=20, pady=(5, 0))
        self.freqband_label_6.grid_remove()
        self.freqband_label_7 = customtkinter.CTkLabel(tab_1, text="Frequenzband 7")
        self.freqband_label_7.grid(row=7, column=0, padx=20, pady=(5, 0))
        self.freqband_label_7.grid_remove()
        # Untere Grenzfrequenz f1 Eingabefelder
        self.entry_f1_1 = customtkinter.CTkEntry(tab_1, placeholder_text="f1")
        self.entry_f1_1.grid(row=1, column=1, padx=20, pady=(5, 0))
        self.entry_f1_2 = customtkinter.CTkEntry(tab_1, placeholder_text="f1")
        self.entry_f1_2.grid(row=2, column=1, padx=20, pady=(5, 0))
        self.entry_f1_2.grid_remove()
        self.entry_f1_3 = customtkinter.CTkEntry(tab_1, placeholder_text="f1")
        self.entry_f1_3.grid(row=3, column=1, padx=20, pady=(5, 0))
        self.entry_f1_3.grid_remove()
        self.entry_f1_4 = customtkinter.CTkEntry(tab_1, placeholder_text="f1")
        self.entry_f1_4.grid(row=4, column=1, padx=20, pady=(5, 0))
        self.entry_f1_4.grid_remove()
        self.entry_f1_5 = customtkinter.CTkEntry(tab_1, placeholder_text="f1")
        self.entry_f1_5.grid(row=5, column=1, padx=20, pady=(5, 0))
        self.entry_f1_5.grid_remove()
        self.entry_f1_6 = customtkinter.CTkEntry(tab_1, placeholder_text="f1")
        self.entry_f1_6.grid(row=6, column=1, padx=20, pady=(5, 0))
        self.entry_f1_6.grid_remove()
        self.entry_f1_7 = customtkinter.CTkEntry(tab_1, placeholder_text="f1")
        self.entry_f1_7.grid(row=7, column=1, padx=20, pady=(5, 0))
        self.entry_f1_7.grid_remove()
        # Obere Grenzfrequenz f2 Eingabefelder
        self.entry_f2_1 = customtkinter.CTkEntry(tab_1, placeholder_text="f2")
        self.entry_f2_1.grid(row=1, column=2, padx=20, pady=(5, 0))
        self.entry_f2_2 = customtkinter.CTkEntry(tab_1, placeholder_text="f2")
        self.entry_f2_2.grid(row=2, column=2, padx=20, pady=(5, 0))
        self.entry_f2_2.grid_remove()
        self.entry_f2_3 = customtkinter.CTkEntry(tab_1, placeholder_text="f2")
        self.entry_f2_3.grid(row=3, column=2, padx=20, pady=(5, 0))
        self.entry_f2_3.grid_remove()
        self.entry_f2_4 = customtkinter.CTkEntry(tab_1, placeholder_text="f2")
        self.entry_f2_4.grid(row=4, column=2, padx=20, pady=(5, 0))
        self.entry_f2_4.grid_remove()
        self.entry_f2_5 = customtkinter.CTkEntry(tab_1, placeholder_text="f2")
        self.entry_f2_5.grid(row=5, column=2, padx=20, pady=(5, 0))
        self.entry_f2_5.grid_remove()
        self.entry_f2_6 = customtkinter.CTkEntry(tab_1, placeholder_text="f2")
        self.entry_f2_6.grid(row=6, column=2, padx=20, pady=(5, 0))
        self.entry_f2_6.grid_remove()
        self.entry_f2_7 = customtkinter.CTkEntry(tab_1, placeholder_text="f2")
        self.entry_f2_7.grid(row=7, column=2, padx=20, pady=(5, 0))
        self.entry_f2_7.grid_remove()
        # Pegel Eingabefelder
        self.tab_1_entry_level_1 = customtkinter.CTkEntry(
            tab_1, placeholder_text="Pegel"
        )
        self.tab_1_entry_level_1.grid(row=1, column=3, padx=20, pady=(5, 0))
        self.tab_1_entry_level_2 = customtkinter.CTkEntry(
            tab_1, placeholder_text="Pegel"
        )
        self.tab_1_entry_level_2.grid(row=2, column=3, padx=20, pady=(5, 0))
        self.tab_1_entry_level_2.grid_remove()
        self.tab_1_entry_level_3 = customtkinter.CTkEntry(
            tab_1, placeholder_text="Pegel"
        )
        self.tab_1_entry_level_3.grid(row=3, column=3, padx=20, pady=(5, 0))
        self.tab_1_entry_level_3.grid_remove()
        self.tab_1_entry_level_4 = customtkinter.CTkEntry(
            tab_1, placeholder_text="Pegel"
        )
        self.tab_1_entry_level_4.grid(row=4, column=3, padx=20, pady=(5, 0))
        self.tab_1_entry_level_4.grid_remove()
        self.tab_1_entry_level_5 = customtkinter.CTkEntry(
            tab_1, placeholder_text="Pegel"
        )
        self.tab_1_entry_level_5.grid(row=5, column=3, padx=20, pady=(5, 0))
        self.tab_1_entry_level_5.grid_remove()
        self.tab_1_entry_level_6 = customtkinter.CTkEntry(
            tab_1, placeholder_text="Pegel"
        )
        self.tab_1_entry_level_6.grid(row=6, column=3, padx=20, pady=(5, 0))
        self.tab_1_entry_level_6.grid_remove()
        self.tab_1_entry_level_7 = customtkinter.CTkEntry(
            tab_1, placeholder_text="Pegel"
        )
        self.tab_1_entry_level_7.grid(row=7, column=3, padx=20, pady=(5, 0))
        self.tab_1_entry_level_7.grid_remove()
        self.freqband_label_list = [
            self.freqband_label_1,
            self.freqband_label_2,
            self.freqband_label_3,
            self.freqband_label_4,
            self.freqband_label_5,
            self.freqband_label_6,
            self.freqband_label_7,
        ]
        self.f1_entry_list = [
            self.entry_f1_1,
            self.entry_f1_2,
            self.entry_f1_3,
            self.entry_f1_4,
            self.entry_f1_5,
            self.entry_f1_6,
            self.entry_f1_7,
        ]
        self.f2_entry_list = [
            self.entry_f2_1,
            self.entry_f2_2,
            self.entry_f2_3,
            self.entry_f2_4,
            self.entry_f2_5,
            self.entry_f2_6,
            self.entry_f2_7,
        ]
        self.tab_1_level_entry_list = [
            self.tab_1_entry_level_1,
            self.tab_1_entry_level_2,
            self.tab_1_entry_level_3,
            self.tab_1_entry_level_4,
            self.tab_1_entry_level_5,
            self.tab_1_entry_level_6,
            self.tab_1_entry_level_7,
        ]

        # Tab Einzelne Terzbänder

        tab_2 = self.tabview.tab("Einzelne Terzbänder")
        self.thirdband_count = 0

        self.tab_2_header_label_1 = customtkinter.CTkLabel(tab_2, text="Terzband")
        self.tab_2_header_label_1.grid(row=0, column=0, padx=20, pady=(5, 20))
        self.tab_2_header_label_2 = customtkinter.CTkLabel(
            tab_2, text="Mittenfrequenz (fc)\n in Hz"
        )
        self.tab_2_header_label_2.grid(row=0, column=1, padx=20, pady=(5, 20))
        self.tab_2_header_label_3 = customtkinter.CTkLabel(
            tab_2, text="Pegel (L)\n in dB"
        )
        self.tab_2_header_label_3.grid(row=0, column=2, padx=20, pady=(5, 20))
        # Berechnen Button
        self.thirdbands_submit_button = customtkinter.CTkButton(
            tab_2,
            text="Mithörschwelle Berechnen",
            command=self.calculate_from_thirdband,
        )
        self.thirdbands_submit_button.grid(row=0, column=4, padx=20, pady=(5, 0))
        # Terzband hinzufügen Button
        self.add_thirdband_button = customtkinter.CTkButton(
            tab_2,
            text="Band hinzufügen\n (+)",
            command=self.add_thirdband,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
        )
        self.add_thirdband_button.grid(row=9, column=0, padx=20, pady=(30, 0))
        # Terzband entfernen Button
        self.remove_thirdband_button = customtkinter.CTkButton(
            tab_2,
            text="Band entfernen\n (-)",
            command=self.remove_thirdband,
            state="disabled",
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
        )
        self.remove_thirdband_button.grid(row=9, column=1, padx=20, pady=(30, 0))
        # Terzband label
        self.thirdband_label_1 = customtkinter.CTkLabel(tab_2, text="Terzband 1")
        self.thirdband_label_1.grid(row=1, column=0, padx=20, pady=(5, 0))
        self.thirdband_label_2 = customtkinter.CTkLabel(tab_2, text="Terzband 2")
        self.thirdband_label_2.grid(row=2, column=0, padx=20, pady=(5, 0))
        self.thirdband_label_2.grid_remove()
        self.thirdband_label_3 = customtkinter.CTkLabel(tab_2, text="Terzband 3")
        self.thirdband_label_3.grid(row=3, column=0, padx=20, pady=(5, 0))
        self.thirdband_label_3.grid_remove()
        self.thirdband_label_4 = customtkinter.CTkLabel(tab_2, text="Terzband 4")
        self.thirdband_label_4.grid(row=4, column=0, padx=20, pady=(5, 0))
        self.thirdband_label_4.grid_remove()
        self.thirdband_label_5 = customtkinter.CTkLabel(tab_2, text="Terzband 5")
        self.thirdband_label_5.grid(row=5, column=0, padx=20, pady=(5, 0))
        self.thirdband_label_5.grid_remove()
        self.thirdband_label_6 = customtkinter.CTkLabel(tab_2, text="Terzband 6")
        self.thirdband_label_6.grid(row=6, column=0, padx=20, pady=(5, 0))
        self.thirdband_label_6.grid_remove()
        self.thirdband_label_7 = customtkinter.CTkLabel(tab_2, text="Terzband 7")
        self.thirdband_label_7.grid(row=7, column=0, padx=20, pady=(5, 0))
        self.thirdband_label_7.grid_remove()
        # Mittenfrequenz Eingabefelder
        self.entry_fc_1 = customtkinter.CTkEntry(
            tab_2, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_1.grid(row=1, column=1, padx=20, pady=(5, 0))
        self.entry_fc_2 = customtkinter.CTkEntry(
            tab_2, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_2.grid(row=2, column=1, padx=20, pady=(5, 0))
        self.entry_fc_2.grid_remove()
        self.entry_fc_3 = customtkinter.CTkEntry(
            tab_2, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_3.grid(row=3, column=1, padx=20, pady=(5, 0))
        self.entry_fc_3.grid_remove()
        self.entry_fc_4 = customtkinter.CTkEntry(
            tab_2, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_4.grid(row=4, column=1, padx=20, pady=(5, 0))
        self.entry_fc_4.grid_remove()
        self.entry_fc_5 = customtkinter.CTkEntry(
            tab_2, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_5.grid(row=5, column=1, padx=20, pady=(5, 0))
        self.entry_fc_5.grid_remove()
        self.entry_fc_6 = customtkinter.CTkEntry(
            tab_2, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_6.grid(row=6, column=1, padx=20, pady=(5, 0))
        self.entry_fc_6.grid_remove()
        self.entry_fc_7 = customtkinter.CTkEntry(
            tab_2, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_7.grid(row=7, column=1, padx=20, pady=(5, 0))
        self.entry_fc_7.grid_remove()
        # Pegel Eingabefelder
        self.tab_2_entry_level_1 = customtkinter.CTkEntry(
            tab_2, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_1.grid(row=1, column=2, padx=20, pady=(5, 0))
        self.tab_2_entry_level_2 = customtkinter.CTkEntry(
            tab_2, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_2.grid(row=2, column=2, padx=20, pady=(5, 0))
        self.tab_2_entry_level_2.grid_remove()
        self.tab_2_entry_level_3 = customtkinter.CTkEntry(
            tab_2, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_3.grid(row=3, column=2, padx=20, pady=(5, 0))
        self.tab_2_entry_level_3.grid_remove()
        self.tab_2_entry_level_4 = customtkinter.CTkEntry(
            tab_2, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_4.grid(row=4, column=2, padx=20, pady=(5, 0))
        self.tab_2_entry_level_4.grid_remove()
        self.tab_2_entry_level_5 = customtkinter.CTkEntry(
            tab_2, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_5.grid(row=5, column=2, padx=20, pady=(5, 0))
        self.tab_2_entry_level_5.grid_remove()
        self.tab_2_entry_level_6 = customtkinter.CTkEntry(
            tab_2, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_6.grid(row=6, column=2, padx=20, pady=(5, 0))
        self.tab_2_entry_level_6.grid_remove()
        self.tab_2_entry_level_7 = customtkinter.CTkEntry(
            tab_2, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_7.grid(row=7, column=2, padx=20, pady=(5, 0))
        self.tab_2_entry_level_7.grid_remove()
        self.thirdband_label_list = [
            self.thirdband_label_1,
            self.thirdband_label_2,
            self.thirdband_label_3,
            self.thirdband_label_4,
            self.thirdband_label_5,
            self.thirdband_label_6,
            self.thirdband_label_7,
        ]
        self.fc_entry_list = [
            self.entry_fc_1,
            self.entry_fc_2,
            self.entry_fc_3,
            self.entry_fc_4,
            self.entry_fc_5,
            self.entry_fc_6,
            self.entry_fc_7,
        ]
        self.tab_2_level_entry_list = [
            self.tab_2_entry_level_1,
            self.tab_2_entry_level_2,
            self.tab_2_entry_level_3,
            self.tab_2_entry_level_4,
            self.tab_2_entry_level_5,
            self.tab_2_entry_level_6,
            self.tab_2_entry_level_7,
        ]

        # Tab Datei Laden
        tab_3 = self.tabview.tab("Datei Laden")
        self.tab_3_header_label_1 = customtkinter.CTkLabel(
            tab_3,
            text="Datei zur Berechnung der Mithörschwelle auswählen\
                 (WAV- oder Excel-Datei)",
        )
        self.tab_3_header_label_1.grid(row=0, column=0, padx=20, pady=(5, 20))
        # Datei Laden button
        self.load_file_button = customtkinter.CTkButton(
            tab_3, text="Datei auswählen", command=self.select_file
        )
        self.load_file_button.grid(row=1, column=0, padx=20, pady=(50, 0))
        self.file_label = customtkinter.CTkLabel(tab_3, text="Datei ausgewählt:")
        self.file_label.grid(row=2, column=0, padx=20, pady=(10, 0))
        self.selected_file_label = customtkinter.CTkLabel(
            tab_3,
            text="keine",
            fg_color=["grey95", "grey10"],
            text_color=["grey40", "grey60"],
            corner_radius=8,
        )
        self.selected_file_label.grid(row=3, column=0, padx=20, pady=(5, 0))
        # Mithörschwelle berechnen button
        self.file_submit_button = customtkinter.CTkButton(
            tab_3, text="Mithörschwelle berechnen", command=self.calculate_from_file
        )
        self.file_submit_button.grid(row=4, column=0, padx=20, pady=(100, 0))

        # Fehlermeldung
        self.error_message = customtkinter.CTkLabel(self, text="", text_color="red")

        # set default values
        self.appearance_mode_optionemenu.set("System")
        self.scaling_optionemenu.set("120%")
        self.noise_selector.set("white")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    # Hinzufügen der Eingabefelder für ein weiteres Terzband
    def add_thirdband(self):
        if self.thirdband_count < 6:
            self.thirdband_count += 1
            self.thirdband_label_list[self.thirdband_count].grid()
            self.fc_entry_list[self.thirdband_count].grid()
            self.tab_2_level_entry_list[self.thirdband_count].grid()
            if self.thirdband_count > 5:
                self.add_thirdband_button.configure(state="disabled")
            if self.thirdband_count > 0:
                self.remove_thirdband_button.configure(state="normal")

    # Entfernen der Eingabefelder für das zuletzt hinzugefügte Terzband
    def remove_thirdband(self):
        if self.thirdband_count > 0:
            self.thirdband_label_list[self.thirdband_count].grid_remove()
            self.fc_entry_list[self.thirdband_count].grid_remove()
            self.tab_2_level_entry_list[self.thirdband_count].grid_remove()
            if self.thirdband_count < 2:
                self.remove_thirdband_button.configure(state="disabled")
            if self.thirdband_count <= 6:
                self.add_thirdband_button.configure(state="normal")
            self.thirdband_count -= 1

    # Hinzufügen der Eingabefelder für ein weiteres Frequenzband
    def add_freqband(self):
        if self.freqband_count < 6:
            self.freqband_count += 1
            self.freqband_label_list[self.freqband_count].grid()
            self.f1_entry_list[self.freqband_count].grid()
            self.f2_entry_list[self.freqband_count].grid()
            self.tab_1_level_entry_list[self.freqband_count].grid()
            if self.freqband_count > 5:
                self.add_freqband_button.configure(state="disabled")
            if self.freqband_count > 0:
                self.remove_freqband_button.configure(state="normal")

    # Entfernen der Eingabefelder für das zuletzt hinzugefügte Frequenzband
    def remove_freqband(self):
        if self.freqband_count > 0:
            self.freqband_label_list[self.freqband_count].grid_remove()
            self.f1_entry_list[self.freqband_count].grid_remove()
            self.f2_entry_list[self.freqband_count].grid_remove()
            self.tab_1_level_entry_list[self.freqband_count].grid_remove()
            if self.freqband_count < 2:
                self.remove_freqband_button.configure(state="disabled")
            if self.freqband_count <= 6:
                self.add_freqband_button.configure(state="normal")
            self.freqband_count -= 1

    def validate(self, string_list):
        error = False
        msg = ""
        for i in string_list:
            if i.isspace():
                error = True
                msg = "Ein oder mehrere Felder sind leer!\
                        Alle Felder müssen ausgefüllt sein!"
            elif i.lstrip("+-").isnumeric() is False:
                error = True
                msg = "Ein oder mehrere Felder enthalten ungültige Werte!\
                     Bitte nur Zahlen eingeben!"
        return error, msg

    def show_error(self, msg):
        self.error_message.configure(text=msg)
        self.error_message.grid(row=1, column=1, padx=20, pady=(5, 0))

    # Berechnen und Anzeigen der Mithörschwelle aus den eingegebenen Frequenzbändern
    def calculate_from_signal(self):
        graph.close_plots()
        print("Berechne Mithörschwelle")
        i = self.freqband_count
        signal = []
        noise_type = self.noise_selector.get()
        for n in range(i + 1):
            f1_entry = self.f1_entry_list[n].get()
            f2_entry = self.f2_entry_list[n].get()
            level_entry = self.tab_1_level_entry_list[n].get()
            error, msg = self.validate((f1_entry, f2_entry, level_entry))
            if error is False:
                f1 = float(f1_entry)
                f2 = float(f2_entry)
                level = float(level_entry)
                if f1 <= f2:
                    signal.append((f1, f2, level))
                else:
                    signal.append((f2, f1, level))
        if error is False:
            filled = calc.fill_signal(signal)
            thirds = []
            for i in filled:
                cutted = calc.cut_to_thirds(i)
                for z in cutted:
                    thirds.append(z)
            low_freqs, center_freqs, high_freqs = list(map(list, zip(*thirds)))
            volume = calc.get_volumes(filled, noise_type)
            self.error_message.grid_remove()
            graph.render_plots(data.samples(), center_freqs, volume)
        else:
            self.show_error(msg)

    # Berechnen und Anzeigen der Mithörschwelle aus den eingegebenen Terzbändern
    def calculate_from_thirdband(self):
        graph.close_plots()
        print("Berechne Mithörschwelle")
        i = self.thirdband_count
        freqs = []
        levels = []
        for n in range(i + 1):
            fc_entry = self.fc_entry_list[n].get()
            level_entry = self.tab_2_level_entry_list[n].get()
            error, msg = self.validate((fc_entry, level_entry))
            if error is False:
                fc = float(fc_entry)
                level = float(level_entry)
                freqs.append(fc)
                levels.append(level)
        if error is False:
            self.error_message.grid_remove()
            graph.render_plots(data.samples(), freqs, levels, smooth=False)
        else:
            self.show_error(msg)

    # Berechnen und Anzeigen der Mithörschwelle aus der geladenen Datei
    def calculate_from_file(self):
        graph.close_plots()
        freqs, levels = analyzed.load_file(self.filename)
        graph.render_plots(data.samples(), freqs, levels)

    # Auswahl einer Datei zum Berechnen
    def select_file(self):
        filetypes = (("audio files", "*.wav"), ("Excel files", "*.xl*"))

        self.filename = fd.askopenfilename(
            title="Datei auswählen", initialdir="/", filetypes=filetypes
        )

        self.selected_file_label.configure(text=self.filename)

    def testdata_callback(self, choice):
        graph.testdata(choice)


if __name__ == "__main__":
    app = App()
    app.mainloop()
