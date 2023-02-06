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
        self.geometry(f"{1500}x{920}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.sidebar_frame.grid_rowconfigure(7, weight=1)
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
        self.show_thirdbands = customtkinter.StringVar(value="on")
        self.show_thirdbands_switch = customtkinter.CTkSwitch(
            self.sidebar_frame,
            text="Terzbänder\nanzeigen",
            command=self.thirdband_switch,
            variable=self.show_thirdbands,
            onvalue="on",
            offvalue="off",
        )
        self.show_thirdbands_switch.grid(row=3, column=0, padx=20, pady=(30, 0))
        self.appearance_mode_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Darstellungsmodus:", anchor="w"
        )
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event,
        )
        self.appearance_mode_optionemenu.grid(row=9, column=0, padx=20, pady=(10, 20))

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=750, height=600)
        self.tabview.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.tabview.add("Breitbandiges Signal")
        self.tabview.add("Einzelne Terzbänder")
        self.tabview.add("Datei Laden")
        self.tabview.add("Terzbandrechner")
        self.tabview.tab("Breitbandiges Signal").grid_columnconfigure(
            1, weight=1
        )  # configure grid of individual tabs
        self.tabview.tab("Einzelne Terzbänder").grid_columnconfigure(1, weight=1)
        self.tabview.tab("Datei Laden").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Terzbandrechner").grid_columnconfigure(0, weight=1)

        # Tab Breitbandiges Signal
        tab_1 = self.tabview.tab("Breitbandiges Signal")
        self.freqband_count = 0
        self.tab_1_entry_frame = customtkinter.CTkFrame(tab_1, width=800, height=800)
        self.tab_1_entry_frame.grid(row=0, column=0, padx=5, pady=10)
        self.tab_1_control_frame = customtkinter.CTkFrame(tab_1, width=200, height=800)
        self.tab_1_control_frame.grid(row=0, column=2, padx=5, pady=10, sticky="N")

        self.tab_1_header_label_1 = customtkinter.CTkLabel(
            self.tab_1_entry_frame, text="Frequenzband"
        )
        self.tab_1_header_label_1.grid(row=0, column=0, padx=20, pady=(5, 20))
        self.tab_1_header_label_2 = customtkinter.CTkLabel(
            self.tab_1_entry_frame, text="Untere Grenzfrequenz\n (f1) in Hz"
        )
        self.tab_1_header_label_2.grid(row=0, column=1, padx=20, pady=(5, 20))
        self.tab_1_header_label_3 = customtkinter.CTkLabel(
            self.tab_1_entry_frame, text="Obere Grenzfrequenz\n (f2) in Hz"
        )
        self.tab_1_header_label_3.grid(row=0, column=2, padx=20, pady=(5, 20))
        self.tab_1_header_label_4 = customtkinter.CTkLabel(
            self.tab_1_entry_frame, text="Pegel(L)\n in dB"
        )
        self.tab_1_header_label_4.grid(row=0, column=3, padx=20, pady=(5, 20))
        # Rauschtyp Auswahl
        self.noise_selector_label = customtkinter.CTkLabel(
            self.tab_1_control_frame, text="Rauschtyp:"
        )
        self.noise_selector_label.grid(row=0, column=0, padx=20, pady=(0, 0))
        self.noise_selector = customtkinter.CTkOptionMenu(
            self.tab_1_control_frame,
            values=["blau", "weiß", "rosa", "rot", "GAR", "GVR"],
        )
        self.noise_selector.grid(row=1, column=0, padx=20, pady=(0, 0))
        # Berechnen Button
        self.thirdbands_submit_button = customtkinter.CTkButton(
            self.tab_1_control_frame,
            text="Mithörschwelle\n Berechnen",
            command=self.calculate_from_signal,
        )
        self.thirdbands_submit_button.grid(row=3, column=0, padx=20, pady=(65, 20))
        # Frequenzband hinzufügen Button
        self.add_freqband_button = customtkinter.CTkButton(
            self.tab_1_entry_frame,
            text="Band hinzufügen\n (+)",
            command=self.add_freqband,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
        )
        self.add_freqband_button.grid(row=9, column=0, padx=20, pady=(30, 20))
        # Frequenzband entfernen Button
        self.remove_freqband_button = customtkinter.CTkButton(
            self.tab_1_entry_frame,
            text="Band entfernen \n (-)",
            command=self.remove_freqband,
            state="disabled",
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
        )
        self.remove_freqband_button.grid(row=9, column=1, padx=20, pady=(30, 20))
        # Freqband label
        self.freqband_label_1 = customtkinter.CTkLabel(
            self.tab_1_entry_frame, text="Frequenzband 1"
        )
        self.freqband_label_1.grid(row=1, column=0, padx=20, pady=(5, 0))
        self.freqband_label_2 = customtkinter.CTkLabel(
            self.tab_1_entry_frame, text="Frequenzband 2"
        )
        self.freqband_label_2.grid(row=2, column=0, padx=20, pady=(5, 0))
        self.freqband_label_2.grid_remove()
        self.freqband_label_3 = customtkinter.CTkLabel(
            self.tab_1_entry_frame, text="Frequenzband 3"
        )
        self.freqband_label_3.grid(row=3, column=0, padx=20, pady=(5, 0))
        self.freqband_label_3.grid_remove()
        self.freqband_label_4 = customtkinter.CTkLabel(
            self.tab_1_entry_frame, text="Frequenzband 4"
        )
        self.freqband_label_4.grid(row=4, column=0, padx=20, pady=(5, 0))
        self.freqband_label_4.grid_remove()
        self.freqband_label_5 = customtkinter.CTkLabel(
            self.tab_1_entry_frame, text="Frequenzband 5"
        )
        self.freqband_label_5.grid(row=5, column=0, padx=20, pady=(5, 0))
        self.freqband_label_5.grid_remove()
        self.freqband_label_6 = customtkinter.CTkLabel(
            self.tab_1_entry_frame, text="Frequenzband 6"
        )
        self.freqband_label_6.grid(row=6, column=0, padx=20, pady=(5, 0))
        self.freqband_label_6.grid_remove()
        self.freqband_label_7 = customtkinter.CTkLabel(
            self.tab_1_entry_frame, text="Frequenzband 7"
        )
        self.freqband_label_7.grid(row=7, column=0, padx=20, pady=(5, 0))
        self.freqband_label_7.grid_remove()
        # Untere Grenzfrequenz f1 Eingabefelder
        self.entry_f1_1 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="f1"
        )
        self.entry_f1_1.grid(row=1, column=1, padx=20, pady=(5, 0))
        self.entry_f1_2 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="f1"
        )
        self.entry_f1_2.grid(row=2, column=1, padx=20, pady=(5, 0))
        self.entry_f1_2.grid_remove()
        self.entry_f1_3 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="f1"
        )
        self.entry_f1_3.grid(row=3, column=1, padx=20, pady=(5, 0))
        self.entry_f1_3.grid_remove()
        self.entry_f1_4 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="f1"
        )
        self.entry_f1_4.grid(row=4, column=1, padx=20, pady=(5, 0))
        self.entry_f1_4.grid_remove()
        self.entry_f1_5 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="f1"
        )
        self.entry_f1_5.grid(row=5, column=1, padx=20, pady=(5, 0))
        self.entry_f1_5.grid_remove()
        self.entry_f1_6 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="f1"
        )
        self.entry_f1_6.grid(row=6, column=1, padx=20, pady=(5, 0))
        self.entry_f1_6.grid_remove()
        self.entry_f1_7 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="f1"
        )
        self.entry_f1_7.grid(row=7, column=1, padx=20, pady=(5, 0))
        self.entry_f1_7.grid_remove()
        # Obere Grenzfrequenz f2 Eingabefelder
        self.entry_f2_1 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="f2"
        )
        self.entry_f2_1.grid(row=1, column=2, padx=20, pady=(5, 0))
        self.entry_f2_2 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="f2"
        )
        self.entry_f2_2.grid(row=2, column=2, padx=20, pady=(5, 0))
        self.entry_f2_2.grid_remove()
        self.entry_f2_3 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="f2"
        )
        self.entry_f2_3.grid(row=3, column=2, padx=20, pady=(5, 0))
        self.entry_f2_3.grid_remove()
        self.entry_f2_4 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="f2"
        )
        self.entry_f2_4.grid(row=4, column=2, padx=20, pady=(5, 0))
        self.entry_f2_4.grid_remove()
        self.entry_f2_5 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="f2"
        )
        self.entry_f2_5.grid(row=5, column=2, padx=20, pady=(5, 0))
        self.entry_f2_5.grid_remove()
        self.entry_f2_6 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="f2"
        )
        self.entry_f2_6.grid(row=6, column=2, padx=20, pady=(5, 0))
        self.entry_f2_6.grid_remove()
        self.entry_f2_7 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="f2"
        )
        self.entry_f2_7.grid(row=7, column=2, padx=20, pady=(5, 0))
        self.entry_f2_7.grid_remove()
        # Pegel Eingabefelder
        self.tab_1_entry_level_1 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="Pegel"
        )
        self.tab_1_entry_level_1.grid(row=1, column=3, padx=20, pady=(5, 0))
        self.tab_1_entry_level_2 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="Pegel"
        )
        self.tab_1_entry_level_2.grid(row=2, column=3, padx=20, pady=(5, 0))
        self.tab_1_entry_level_2.grid_remove()
        self.tab_1_entry_level_3 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="Pegel"
        )
        self.tab_1_entry_level_3.grid(row=3, column=3, padx=20, pady=(5, 0))
        self.tab_1_entry_level_3.grid_remove()
        self.tab_1_entry_level_4 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="Pegel"
        )
        self.tab_1_entry_level_4.grid(row=4, column=3, padx=20, pady=(5, 0))
        self.tab_1_entry_level_4.grid_remove()
        self.tab_1_entry_level_5 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="Pegel"
        )
        self.tab_1_entry_level_5.grid(row=5, column=3, padx=20, pady=(5, 0))
        self.tab_1_entry_level_5.grid_remove()
        self.tab_1_entry_level_6 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="Pegel"
        )
        self.tab_1_entry_level_6.grid(row=6, column=3, padx=20, pady=(5, 0))
        self.tab_1_entry_level_6.grid_remove()
        self.tab_1_entry_level_7 = customtkinter.CTkEntry(
            self.tab_1_entry_frame, placeholder_text="Pegel"
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
        self.tab_2_entry_frame = customtkinter.CTkFrame(tab_2, width=800, height=800)
        self.tab_2_entry_frame.grid(row=0, column=0, padx=5, pady=10)
        self.tab_2_control_frame = customtkinter.CTkFrame(tab_2, width=200, height=800)
        self.tab_2_control_frame.grid(row=0, column=2, padx=5, pady=10, sticky="N")

        self.tab_2_header_label_1 = customtkinter.CTkLabel(
            self.tab_2_entry_frame,
            text="Terzband",
        )
        self.tab_2_header_label_1.grid(row=0, column=0, padx=5, pady=(5, 20))
        self.tab_2_header_label_2 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Mittenfrequenz (fc)\n in Hz"
        )
        self.tab_2_header_label_2.grid(row=0, column=1, padx=10, pady=(5, 20))
        self.tab_2_header_label_3 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Pegel (L)\n in dB"
        )
        self.tab_2_header_label_3.grid(row=0, column=2, padx=10, pady=(5, 20))
        # Berechnen Button
        self.thirdbands_submit_button = customtkinter.CTkButton(
            self.tab_2_control_frame,
            text="Mithörschwelle Berechnen",
            command=self.calculate_from_thirdband,
        )
        self.thirdbands_submit_button.grid(row=0, column=0, padx=20, pady=(20, 20))
        # Terzband hinzufügen Button
        self.add_thirdband_button = customtkinter.CTkButton(
            self.tab_2_entry_frame,
            text="Band hinzufügen\n (+)",
            command=self.add_thirdband,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
        )
        self.add_thirdband_button.grid(row=17, column=1, padx=10, pady=(30, 20))
        # Terzband entfernen Button
        self.remove_thirdband_button = customtkinter.CTkButton(
            self.tab_2_entry_frame,
            text="Band entfernen\n (-)",
            command=self.remove_thirdband,
            state="disabled",
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
        )
        self.remove_thirdband_button.grid(row=17, column=2, padx=10, pady=(30, 20))
        # Terzband label
        self.thirdband_label_1 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 1", width=50
        )
        self.thirdband_label_1.grid(row=1, column=0, padx=5, pady=(5, 0))
        self.thirdband_label_2 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 2"
        )
        self.thirdband_label_2.grid(row=2, column=0, padx=5, pady=(5, 0))
        self.thirdband_label_2.grid_remove()
        self.thirdband_label_3 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 3"
        )
        self.thirdband_label_3.grid(row=3, column=0, padx=5, pady=(5, 0))
        self.thirdband_label_3.grid_remove()
        self.thirdband_label_4 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 4"
        )
        self.thirdband_label_4.grid(row=4, column=0, padx=5, pady=(5, 0))
        self.thirdband_label_4.grid_remove()
        self.thirdband_label_5 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 5"
        )
        self.thirdband_label_5.grid(row=5, column=0, padx=5, pady=(5, 0))
        self.thirdband_label_5.grid_remove()
        self.thirdband_label_6 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 6"
        )
        self.thirdband_label_6.grid(row=6, column=0, padx=5, pady=(5, 0))
        self.thirdband_label_6.grid_remove()
        self.thirdband_label_7 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 7"
        )
        self.thirdband_label_7.grid(row=7, column=0, padx=5, pady=(5, 0))
        self.thirdband_label_7.grid_remove()
        self.thirdband_label_8 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 8"
        )
        self.thirdband_label_8.grid(row=8, column=0, padx=5, pady=(5, 0))
        self.thirdband_label_8.grid_remove()
        self.thirdband_label_9 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 9"
        )
        self.thirdband_label_9.grid(row=9, column=0, padx=5, pady=(5, 0))
        self.thirdband_label_9.grid_remove()
        self.thirdband_label_10 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 10"
        )
        self.thirdband_label_10.grid(row=10, column=0, padx=5, pady=(5, 0))
        self.thirdband_label_10.grid_remove()
        self.thirdband_label_11 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 11"
        )
        self.thirdband_label_11.grid(row=11, column=0, padx=5, pady=(5, 0))
        self.thirdband_label_11.grid_remove()
        self.thirdband_label_12 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 12"
        )
        self.thirdband_label_12.grid(row=12, column=0, padx=5, pady=(5, 0))
        self.thirdband_label_12.grid_remove()
        self.thirdband_label_13 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 13"
        )
        self.thirdband_label_13.grid(row=13, column=0, padx=5, pady=(5, 0))
        self.thirdband_label_13.grid_remove()
        self.thirdband_label_14 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 14"
        )
        self.thirdband_label_14.grid(row=14, column=0, padx=5, pady=(5, 0))
        self.thirdband_label_14.grid_remove()
        self.thirdband_label_15 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 15"
        )
        self.thirdband_label_15.grid(row=15, column=0, padx=5, pady=(5, 0))
        self.thirdband_label_15.grid_remove()
        self.thirdband_label_16 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 16"
        )
        self.thirdband_label_16.grid(row=1, column=3, padx=5, pady=(5, 0))
        self.thirdband_label_16.grid_remove()
        self.thirdband_label_17 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 17"
        )
        self.thirdband_label_17.grid(row=2, column=3, padx=5, pady=(5, 0))
        self.thirdband_label_17.grid_remove()
        self.thirdband_label_18 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 18"
        )
        self.thirdband_label_18.grid(row=3, column=3, padx=5, pady=(5, 0))
        self.thirdband_label_18.grid_remove()
        self.thirdband_label_19 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 19"
        )
        self.thirdband_label_19.grid(row=4, column=3, padx=5, pady=(5, 0))
        self.thirdband_label_19.grid_remove()
        self.thirdband_label_20 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 20"
        )
        self.thirdband_label_20.grid(row=5, column=3, padx=5, pady=(5, 0))
        self.thirdband_label_20.grid_remove()
        self.thirdband_label_21 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 21"
        )
        self.thirdband_label_21.grid(row=6, column=3, padx=5, pady=(5, 0))
        self.thirdband_label_21.grid_remove()
        self.thirdband_label_22 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 22"
        )
        self.thirdband_label_22.grid(row=7, column=3, padx=5, pady=(5, 0))
        self.thirdband_label_22.grid_remove()
        self.thirdband_label_23 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 23"
        )
        self.thirdband_label_23.grid(row=8, column=3, padx=5, pady=(5, 0))
        self.thirdband_label_23.grid_remove()
        self.thirdband_label_24 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 24"
        )
        self.thirdband_label_24.grid(row=9, column=3, padx=5, pady=(5, 0))
        self.thirdband_label_24.grid_remove()
        self.thirdband_label_25 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 25"
        )
        self.thirdband_label_25.grid(row=10, column=3, padx=5, pady=(5, 0))
        self.thirdband_label_25.grid_remove()
        self.thirdband_label_26 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 26"
        )
        self.thirdband_label_26.grid(row=11, column=3, padx=5, pady=(5, 0))
        self.thirdband_label_26.grid_remove()
        self.thirdband_label_27 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 27"
        )
        self.thirdband_label_27.grid(row=12, column=3, padx=5, pady=(5, 0))
        self.thirdband_label_27.grid_remove()
        self.thirdband_label_28 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 28"
        )
        self.thirdband_label_28.grid(row=13, column=3, padx=5, pady=(5, 0))
        self.thirdband_label_28.grid_remove()
        self.thirdband_label_29 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 29"
        )
        self.thirdband_label_29.grid(row=14, column=3, padx=5, pady=(5, 0))
        self.thirdband_label_29.grid_remove()
        self.thirdband_label_30 = customtkinter.CTkLabel(
            self.tab_2_entry_frame, text="Terzband 30"
        )
        self.thirdband_label_30.grid(row=15, column=3, padx=5, pady=(5, 0))
        self.thirdband_label_30.grid_remove()
        # Mittenfrequenz Eingabefelder
        self.entry_fc_1 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_1.grid(row=1, column=1, padx=10, pady=(5, 0))
        self.entry_fc_2 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_2.grid(row=2, column=1, padx=10, pady=(5, 0))
        self.entry_fc_2.grid_remove()
        self.entry_fc_3 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_3.grid(row=3, column=1, padx=10, pady=(5, 0))
        self.entry_fc_3.grid_remove()
        self.entry_fc_4 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_4.grid(row=4, column=1, padx=10, pady=(5, 0))
        self.entry_fc_4.grid_remove()
        self.entry_fc_5 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_5.grid(row=5, column=1, padx=10, pady=(5, 0))
        self.entry_fc_5.grid_remove()
        self.entry_fc_6 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_6.grid(row=6, column=1, padx=10, pady=(5, 0))
        self.entry_fc_6.grid_remove()
        self.entry_fc_7 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_7.grid(row=7, column=1, padx=10, pady=(5, 0))
        self.entry_fc_7.grid_remove()
        self.entry_fc_8 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_8.grid(row=8, column=1, padx=10, pady=(5, 0))
        self.entry_fc_8.grid_remove()
        self.entry_fc_9 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_9.grid(row=9, column=1, padx=10, pady=(5, 0))
        self.entry_fc_9.grid_remove()
        self.entry_fc_10 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_10.grid(row=10, column=1, padx=10, pady=(5, 0))
        self.entry_fc_10.grid_remove()
        self.entry_fc_11 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_11.grid(row=11, column=1, padx=10, pady=(5, 0))
        self.entry_fc_11.grid_remove()
        self.entry_fc_12 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_12.grid(row=12, column=1, padx=10, pady=(5, 0))
        self.entry_fc_12.grid_remove()
        self.entry_fc_13 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_13.grid(row=13, column=1, padx=10, pady=(5, 0))
        self.entry_fc_13.grid_remove()
        self.entry_fc_14 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_14.grid(row=14, column=1, padx=10, pady=(5, 0))
        self.entry_fc_14.grid_remove()
        self.entry_fc_15 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_15.grid(row=15, column=1, padx=10, pady=(5, 0))
        self.entry_fc_15.grid_remove()
        self.entry_fc_16 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_16.grid(row=1, column=4, padx=10, pady=(5, 0))
        self.entry_fc_16.grid_remove()
        self.entry_fc_17 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_17.grid(row=2, column=4, padx=10, pady=(5, 0))
        self.entry_fc_17.grid_remove()
        self.entry_fc_18 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_18.grid(row=3, column=4, padx=10, pady=(5, 0))
        self.entry_fc_18.grid_remove()
        self.entry_fc_19 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_19.grid(row=4, column=4, padx=10, pady=(5, 0))
        self.entry_fc_19.grid_remove()
        self.entry_fc_20 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_20.grid(row=5, column=4, padx=10, pady=(5, 0))
        self.entry_fc_20.grid_remove()
        self.entry_fc_21 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_21.grid(row=6, column=4, padx=10, pady=(5, 0))
        self.entry_fc_21.grid_remove()
        self.entry_fc_22 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_22.grid(row=7, column=4, padx=10, pady=(5, 0))
        self.entry_fc_22.grid_remove()
        self.entry_fc_23 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_23.grid(row=8, column=4, padx=10, pady=(5, 0))
        self.entry_fc_23.grid_remove()
        self.entry_fc_24 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_24.grid(row=9, column=4, padx=10, pady=(5, 0))
        self.entry_fc_24.grid_remove()
        self.entry_fc_25 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_25.grid(row=10, column=4, padx=10, pady=(5, 0))
        self.entry_fc_25.grid_remove()
        self.entry_fc_26 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_26.grid(row=11, column=4, padx=10, pady=(5, 0))
        self.entry_fc_26.grid_remove()
        self.entry_fc_27 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_27.grid(row=12, column=4, padx=10, pady=(5, 0))
        self.entry_fc_27.grid_remove()
        self.entry_fc_28 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_28.grid(row=13, column=4, padx=10, pady=(5, 0))
        self.entry_fc_28.grid_remove()
        self.entry_fc_29 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_29.grid(row=14, column=4, padx=10, pady=(5, 0))
        self.entry_fc_29.grid_remove()
        self.entry_fc_30 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Mittenfrequenz"
        )
        self.entry_fc_30.grid(row=15, column=4, padx=10, pady=(5, 0))
        self.entry_fc_30.grid_remove()
        # Pegel Eingabefelder
        self.tab_2_entry_level_1 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_1.grid(row=1, column=2, padx=10, pady=(5, 0))
        self.tab_2_entry_level_2 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_2.grid(row=2, column=2, padx=10, pady=(5, 0))
        self.tab_2_entry_level_2.grid_remove()
        self.tab_2_entry_level_3 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_3.grid(row=3, column=2, padx=10, pady=(5, 0))
        self.tab_2_entry_level_3.grid_remove()
        self.tab_2_entry_level_4 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_4.grid(row=4, column=2, padx=10, pady=(5, 0))
        self.tab_2_entry_level_4.grid_remove()
        self.tab_2_entry_level_5 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_5.grid(row=5, column=2, padx=10, pady=(5, 0))
        self.tab_2_entry_level_5.grid_remove()
        self.tab_2_entry_level_6 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_6.grid(row=6, column=2, padx=10, pady=(5, 0))
        self.tab_2_entry_level_6.grid_remove()
        self.tab_2_entry_level_7 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_7.grid(row=7, column=2, padx=10, pady=(5, 0))
        self.tab_2_entry_level_7.grid_remove()
        self.tab_2_entry_level_8 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_8.grid(row=8, column=2, padx=10, pady=(5, 0))
        self.tab_2_entry_level_8.grid_remove()
        self.tab_2_entry_level_9 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_9.grid(row=9, column=2, padx=10, pady=(5, 0))
        self.tab_2_entry_level_9.grid_remove()
        self.tab_2_entry_level_10 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_10.grid(row=10, column=2, padx=10, pady=(5, 0))
        self.tab_2_entry_level_10.grid_remove()
        self.tab_2_entry_level_11 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_11.grid(row=11, column=2, padx=10, pady=(5, 0))
        self.tab_2_entry_level_11.grid_remove()
        self.tab_2_entry_level_12 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_12.grid(row=12, column=2, padx=10, pady=(5, 0))
        self.tab_2_entry_level_12.grid_remove()
        self.tab_2_entry_level_13 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_13.grid(row=13, column=2, padx=10, pady=(5, 0))
        self.tab_2_entry_level_13.grid_remove()
        self.tab_2_entry_level_14 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_14.grid(row=14, column=2, padx=10, pady=(5, 0))
        self.tab_2_entry_level_14.grid_remove()
        self.tab_2_entry_level_15 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_15.grid(row=15, column=2, padx=10, pady=(5, 0))
        self.tab_2_entry_level_15.grid_remove()
        self.tab_2_entry_level_16 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_16.grid(row=1, column=5, padx=10, pady=(5, 0))
        self.tab_2_entry_level_16.grid_remove()
        self.tab_2_entry_level_17 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_17.grid(row=2, column=5, padx=10, pady=(5, 0))
        self.tab_2_entry_level_17.grid_remove()
        self.tab_2_entry_level_18 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_18.grid(row=3, column=5, padx=10, pady=(5, 0))
        self.tab_2_entry_level_18.grid_remove()
        self.tab_2_entry_level_19 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_19.grid(row=4, column=5, padx=10, pady=(5, 0))
        self.tab_2_entry_level_19.grid_remove()
        self.tab_2_entry_level_20 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_20.grid(row=5, column=5, padx=10, pady=(5, 0))
        self.tab_2_entry_level_20.grid_remove()
        self.tab_2_entry_level_21 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_21.grid(row=6, column=5, padx=10, pady=(5, 0))
        self.tab_2_entry_level_21.grid_remove()
        self.tab_2_entry_level_22 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_22.grid(row=7, column=5, padx=10, pady=(5, 0))
        self.tab_2_entry_level_22.grid_remove()
        self.tab_2_entry_level_23 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_23.grid(row=8, column=5, padx=10, pady=(5, 0))
        self.tab_2_entry_level_23.grid_remove()
        self.tab_2_entry_level_24 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_24.grid(row=9, column=5, padx=10, pady=(5, 0))
        self.tab_2_entry_level_24.grid_remove()
        self.tab_2_entry_level_25 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_25.grid(row=10, column=5, padx=10, pady=(5, 0))
        self.tab_2_entry_level_25.grid_remove()
        self.tab_2_entry_level_26 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_26.grid(row=11, column=5, padx=10, pady=(5, 0))
        self.tab_2_entry_level_26.grid_remove()
        self.tab_2_entry_level_27 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_27.grid(row=12, column=5, padx=10, pady=(5, 0))
        self.tab_2_entry_level_27.grid_remove()
        self.tab_2_entry_level_28 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_28.grid(row=13, column=5, padx=10, pady=(5, 0))
        self.tab_2_entry_level_28.grid_remove()
        self.tab_2_entry_level_29 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_29.grid(row=14, column=5, padx=10, pady=(5, 0))
        self.tab_2_entry_level_29.grid_remove()
        self.tab_2_entry_level_30 = customtkinter.CTkEntry(
            self.tab_2_entry_frame, placeholder_text="Terzpegel"
        )
        self.tab_2_entry_level_30.grid(row=15, column=5, padx=10, pady=(5, 0))
        self.tab_2_entry_level_30.grid_remove()
        self.thirdband_label_list = [
            self.thirdband_label_1,
            self.thirdband_label_2,
            self.thirdband_label_3,
            self.thirdband_label_4,
            self.thirdband_label_5,
            self.thirdband_label_6,
            self.thirdband_label_7,
            self.thirdband_label_8,
            self.thirdband_label_9,
            self.thirdband_label_10,
            self.thirdband_label_11,
            self.thirdband_label_12,
            self.thirdband_label_13,
            self.thirdband_label_14,
            self.thirdband_label_15,
            self.thirdband_label_16,
            self.thirdband_label_17,
            self.thirdband_label_18,
            self.thirdband_label_19,
            self.thirdband_label_20,
            self.thirdband_label_21,
            self.thirdband_label_22,
            self.thirdband_label_23,
            self.thirdband_label_24,
            self.thirdband_label_25,
            self.thirdband_label_26,
            self.thirdband_label_27,
            self.thirdband_label_28,
            self.thirdband_label_29,
            self.thirdband_label_30,
        ]
        self.fc_entry_list = [
            self.entry_fc_1,
            self.entry_fc_2,
            self.entry_fc_3,
            self.entry_fc_4,
            self.entry_fc_5,
            self.entry_fc_6,
            self.entry_fc_7,
            self.entry_fc_8,
            self.entry_fc_9,
            self.entry_fc_10,
            self.entry_fc_11,
            self.entry_fc_12,
            self.entry_fc_13,
            self.entry_fc_14,
            self.entry_fc_15,
            self.entry_fc_16,
            self.entry_fc_17,
            self.entry_fc_18,
            self.entry_fc_19,
            self.entry_fc_20,
            self.entry_fc_21,
            self.entry_fc_22,
            self.entry_fc_23,
            self.entry_fc_24,
            self.entry_fc_25,
            self.entry_fc_26,
            self.entry_fc_27,
            self.entry_fc_28,
            self.entry_fc_29,
            self.entry_fc_30,
        ]
        self.tab_2_level_entry_list = [
            self.tab_2_entry_level_1,
            self.tab_2_entry_level_2,
            self.tab_2_entry_level_3,
            self.tab_2_entry_level_4,
            self.tab_2_entry_level_5,
            self.tab_2_entry_level_6,
            self.tab_2_entry_level_7,
            self.tab_2_entry_level_8,
            self.tab_2_entry_level_9,
            self.tab_2_entry_level_10,
            self.tab_2_entry_level_11,
            self.tab_2_entry_level_12,
            self.tab_2_entry_level_13,
            self.tab_2_entry_level_14,
            self.tab_2_entry_level_15,
            self.tab_2_entry_level_16,
            self.tab_2_entry_level_17,
            self.tab_2_entry_level_18,
            self.tab_2_entry_level_19,
            self.tab_2_entry_level_20,
            self.tab_2_entry_level_21,
            self.tab_2_entry_level_22,
            self.tab_2_entry_level_23,
            self.tab_2_entry_level_24,
            self.tab_2_entry_level_25,
            self.tab_2_entry_level_26,
            self.tab_2_entry_level_27,
            self.tab_2_entry_level_28,
            self.tab_2_entry_level_29,
            self.tab_2_entry_level_30,
        ]

        # Tab Datei Laden
        tab_3 = self.tabview.tab("Datei Laden")
        tab_3.grid_rowconfigure(0, weight=1)
        self.thirdband_frame = customtkinter.CTkFrame(tab_3, width=100, height=500)
        self.thirdband_frame.grid(row=0, column=3, padx=0, pady=0, sticky="N")
        self.thirdband_frame.grid_columnconfigure(3, weight=1)
        self.loadfile_frame = customtkinter.CTkFrame(tab_3, width=850, height=800)
        self.loadfile_frame.grid(row=0, column=0, padx=0, pady=0, sticky="N")
        self.amplifier_frame = customtkinter.CTkFrame(tab_3, width=100, height=500)
        self.amplifier_frame.grid(row=0, column=2, padx=20, pady=0, sticky="N")
        self.tab_3_header_label_1 = customtkinter.CTkLabel(
            self.loadfile_frame,
            text="Datei zur Berechnung der Mithörschwelle auswählen "
            "(WAV- oder Excel-Datei)",
        )
        self.tab_3_header_label_1.grid(row=0, column=0, padx=50, pady=(5, 20))
        # Datei Laden button
        self.load_file_button = customtkinter.CTkButton(
            self.loadfile_frame, text="Datei auswählen", command=self.select_file
        )
        self.load_file_button.grid(row=1, column=0, padx=20, pady=(50, 0))
        self.file_label = customtkinter.CTkLabel(
            self.loadfile_frame, text="Datei ausgewählt:"
        )
        self.file_label.grid(row=2, column=0, padx=20, pady=(10, 0))
        self.selected_file_label = customtkinter.CTkLabel(
            self.loadfile_frame,
            text="keine",
            fg_color=["grey95", "grey10"],
            text_color=["grey40", "grey60"],
            corner_radius=8,
        )
        self.selected_file_label.grid(row=3, column=0, padx=20, pady=(5, 0))
        # Terzpegel anzeigen
        self.third_levels_header = customtkinter.CTkLabel(
            self.thirdband_frame, text="Pegel\n in dB"
        )
        self.third_levels_header.grid(row=0, column=0, padx=5, pady=(10, 0))
        self.third_levels_label = customtkinter.CTkLabel(
            self.thirdband_frame,
            text="",
            fg_color=["grey95", "grey10"],
            text_color=["grey40", "grey60"],
            corner_radius=8,
            wraplength=40,
            height=500,
            width=50,
        )
        self.third_levels_label.grid(row=2, column=0, padx=5, pady=(10, 0))
        self.third_freqs_header = customtkinter.CTkLabel(
            self.thirdband_frame, text="Freq\n in Hz"
        )
        self.third_freqs_header.grid(row=0, column=1, padx=10, pady=(10, 0))
        self.third_freqs_label = customtkinter.CTkLabel(
            self.thirdband_frame,
            text="",
            fg_color=["grey95", "grey10"],
            text_color=["grey40", "grey60"],
            corner_radius=8,
            wraplength=50,
            height=500,
            width=50,
        )
        self.third_freqs_label.grid(row=2, column=1, padx=10, pady=(10, 0))
        # Terzbänder auslesen Button
        self.file_read_button = customtkinter.CTkButton(
            self.amplifier_frame,
            text="Terzpegel auslesen",
            command=self.read_third_levels,
        )
        self.file_read_button.grid(row=0, column=0, padx=20, pady=(20, 0))
        # Verstärkung Eingabe
        self.amplifier_label = customtkinter.CTkLabel(
            self.amplifier_frame, text="Verstärkung in dB:"
        )
        self.amplifier_label.grid(row=2, column=0, padx=20, pady=(50, 0))
        self.amplifier_entry = customtkinter.CTkEntry(
            self.amplifier_frame, placeholder_text="Verstärkung"
        )
        self.amplifier_entry.grid(row=3, column=0, padx=20, pady=(10, 0))
        # Pegel für 500 Hz und 1000 Hz im Ergebnis anzeigen
        self.show_amp = customtkinter.StringVar(value="off")
        self.show_amp_switch = customtkinter.CTkSwitch(
            self.amplifier_frame,
            text="Pegel von\n500 Hz und 1 kHz\nim Ergebnis anzeigen",
            variable=self.show_amp,
            onvalue="on",
            offvalue="off",
        )
        self.show_amp_switch.grid(row=4, column=0, padx=20, pady=(30, 10))
        # Mithörschwelle berechnen button
        self.file_submit_button = customtkinter.CTkButton(
            self.loadfile_frame,
            text="Mithörschwelle berechnen",
            command=self.calculate_from_file,
        )
        self.file_submit_button.grid(row=7, column=0, padx=20, pady=(80, 30))

        # Tab Terzband berechnen
        tab_4 = self.tabview.tab("Terzbandrechner")
        self.tab_4_control_frame = customtkinter.CTkFrame(tab_4)
        self.tab_4_control_frame.grid(row=1, column=0, padx=10, pady=10)
        self.tab_4_show_frame = customtkinter.CTkFrame(tab_4)
        self.tab_4_show_frame.grid(row=2, column=0, padx=10, pady=20)

        self.tab_4_header_label = customtkinter.CTkLabel(
            tab_4,
            text="Hier können Terzbänder zu entsprechenden Mittenfrequenzen (fc),\noder den unteren und oberen Grenzfrequenzen f1 und f2 berechnet werden",
        )
        self.tab_4_header_label.grid(row=0, column=0, padx=20, pady=(20, 0))

        self.tab_4_freq_entry = customtkinter.CTkEntry(
            self.tab_4_control_frame, placeholder_text="Frequenz"
        )
        self.tab_4_freq_entry.grid(row=1, column=1, padx=20, pady=20)
        self.tab_4_param_selector = customtkinter.CTkOptionMenu(
            self.tab_4_control_frame,
            values=[
                "untere Grenzfrequenz (f1)",
                "obere Grenzfrequenz (f2)",
                "Mittenfrequenz (fc)",
            ],
        )
        self.tab_4_param_selector.grid(row=1, column=0, padx=20, pady=20)
        self.tab_4_submit_button = customtkinter.CTkButton(
            self.tab_4_control_frame,
            text="Terzband berechnen",
            command=self.calculate_thirdband,
        )
        self.tab_4_submit_button.grid(row=1, column=2, padx=20, pady=20)

        self.tab_4_result_label = customtkinter.CTkLabel(
            self.tab_4_show_frame, text="Ermitteltes Terzband:"
        )
        self.tab_4_result_label.grid(row=0, column=0, padx=20, pady=20)
        self.tab_4_f1_label = customtkinter.CTkLabel(
            self.tab_4_show_frame, text="untere Grenzfrequenz (f1):"
        )
        self.f1_result = customtkinter.CTkLabel(
            self.tab_4_show_frame,
            text="keine",
            fg_color=["grey95", "grey10"],
            text_color=["grey40", "grey60"],
            corner_radius=8,
        )
        self.f1_result.grid(row=1, column=1, padx=20, pady=(10, 0))
        self.tab_4_f1_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        self.tab_4_fc_label = customtkinter.CTkLabel(
            self.tab_4_show_frame, text="Mittenfrequenz (fc):"
        )
        self.fc_result = customtkinter.CTkLabel(
            self.tab_4_show_frame,
            text="keine",
            fg_color=["grey95", "grey10"],
            text_color=["grey40", "grey60"],
            corner_radius=8,
        )
        self.fc_result.grid(row=2, column=1, padx=20, pady=(10, 0))
        self.tab_4_fc_label.grid(row=2, column=0, padx=20, pady=(10, 0))
        self.tab_4_f2_label = customtkinter.CTkLabel(
            self.tab_4_show_frame, text="obere Grenzfrequenz (f2):"
        )
        self.tab_4_f2_label.grid(row=3, column=0, padx=20, pady=(10, 20))
        self.f2_result = customtkinter.CTkLabel(
            self.tab_4_show_frame,
            text="keine",
            fg_color=["grey95", "grey10"],
            text_color=["grey40", "grey60"],
            corner_radius=8,
        )
        self.f2_result.grid(row=3, column=1, padx=20, pady=(10, 20))

        # Fehlermeldung
        self.error_message = customtkinter.CTkLabel(self, text="", text_color="red")

        # set default values
        self.appearance_mode_optionemenu.set("System")
        self.noise_selector.set("weiß")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    # Hinzufügen der Eingabefelder für ein weiteres Terzband
    def add_thirdband(self):
        if self.thirdband_count < 29:
            self.thirdband_count += 1
            self.thirdband_label_list[self.thirdband_count].grid()
            self.fc_entry_list[self.thirdband_count].grid()
            self.tab_2_level_entry_list[self.thirdband_count].grid()
            if self.thirdband_count > 28:
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
            if self.thirdband_count <= 29:
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
        msg = ""
        for i in string_list:
            if i == "":
                msg = "Ein oder mehrere Felder sind leer! Alle Felder müssen ausgefüllt sein!"
                raise Exception(msg)
            elif i.isspace():
                msg = "Ein oder mehrere Felder sind leer! Alle Felder müssen ausgefüllt sein!"
                raise Exception(msg)
            # elif i.lstrip("+-").isnumeric() is False:
            #     msg = "Ein oder mehrere Felder enthalten ungültige Werte! Bitte nur Zahlen eingeben!"
            #     raise Exception(msg)
            try:
                float(i)
            except ValueError:
                msg = "Ein oder mehrere Felder enthalten ungültige Werte! Bitte nur Zahlen eingeben!"
                raise Exception(msg)

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
        try:
            for n in range(i + 1):
                f1_entry = self.f1_entry_list[n].get().replace(",", ".")
                f2_entry = self.f2_entry_list[n].get().replace(",", ".")
                level_entry = self.tab_1_level_entry_list[n].get().replace(",", ".")
                self.validate((f1_entry, f2_entry, level_entry))
                f1 = float(f1_entry)
                f2 = float(f2_entry)
                level = float(level_entry)
                if f1 <= f2:
                    signal.append((f1, f2, level))
                else:
                    signal.append((f2, f1, level))
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
        except Exception as inst:
            self.show_error(inst)

    # Berechnen und Anzeigen der Mithörschwelle aus den eingegebenen Terzbändern
    def calculate_from_thirdband(self):
        graph.close_plots()
        print("Berechne Mithörschwelle")
        i = self.thirdband_count
        freqs = []
        levels = []
        try:
            for n in range(i + 1):
                fc_entry = self.fc_entry_list[n].get().replace(",", ".")
                level_entry = self.tab_2_level_entry_list[n].get().replace(",", ".")
                self.validate((fc_entry, level_entry))
                fc = float(fc_entry)
                level = float(level_entry)
                freqs.append(fc)
                levels.append(level)
            self.error_message.grid_remove()
            graph.render_plots(data.samples(), freqs, levels, smooth=False)
        except Exception as inst:
            self.show_error(inst)
        # self.show_error(msg)

    # Berechnen und Anzeigen der Mithörschwelle aus der geladenen Datei
    def calculate_from_file(self):
        try:
            graph.close_plots()
            if self.filename == "":
                raise AttributeError(msg)
            amp_entry = self.amplifier_entry.get().replace(",", ".")
            if amp_entry == "":
                amp_entry = "0"
            self.validate([amp_entry])
            amp = float(amp_entry)
            freqs, levels = analyzed.load_file(self.filename, amp)
            self.error_message.grid_remove()
            if self.show_amp.get() == "on":
                calibration = calc.get_calibration(freqs, levels)
                msg = (
                    "mit "
                    + str(calibration[0][1])
                    + " dB bei "
                    + str(calibration[0][0])
                    + " Hz und "
                    + str(calibration[1][1])
                    + " dB bei "
                    + str(calibration[1][0])
                    + " Hz"
                )
                graph.render_plots(data.samples(), freqs, levels, show_calibration=msg)
            elif self.show_amp.get() == "off":
                graph.render_plots(
                    data.samples(), freqs, levels, show_calibration="none"
                )
        except AttributeError as msg:
            self.show_error(msg)
        except Exception as err:
            self.show_error(err)

    # Terzpegel aus Datei auslesen und anzeigen
    def read_third_levels(self):
        try:
            if self.filename == "":
                raise AttributeError
            spl, freq = analyzed.get_third_levels(self.filename)
            self.error_message.grid_remove()
            rounded_spl = calc.round_list(spl)
            rounded_freq = calc.round_list(freq)
            self.third_levels_label.configure(text=rounded_spl)
            self.third_freqs_label.configure(text=rounded_freq)
        except AttributeError:
            self.show_error("Keine Datei ausgewählt!")
        except Exception as err:
            self.show_error(err)

    # Auswahl einer Datei zum Berechnen
    def select_file(self):
        filetypes = (("audio files", "*.wav"), ("Excel files", "*.xlsx"))

        self.filename = fd.askopenfilename(
            title="Datei auswählen", initialdir="/", filetypes=filetypes
        )

        self.selected_file_label.configure(text=self.filename)

    def testdata_callback(self, choice):
        graph.testdata(choice)

    def thirdband_switch(self):
        switch = self.show_thirdbands.get()
        graph.thirdbands(switch)

    # Terzband zu angegebener Frequenz berechnen
    def calculate_thirdband(self):
        try:
            self.error_message.grid_remove()
            choice = self.tab_4_param_selector.get()
            freq_entry = self.tab_4_freq_entry.get().replace(",", ".")
            self.validate([freq_entry])
            freq = float(freq_entry)
            if choice == "untere Grenzfrequenz (f1)":
                param = "low"
            elif choice == "obere Grenzfrequenz (f2)":
                param = "high"
            elif choice == "Mittenfrequenz (fc)":
                param = "center"
            thirdband = calc.round_list(calc.get_third_band(freq, param))
            self.f1_result.configure(text=str(thirdband[0]) + " Hz")
            self.fc_result.configure(text=str(thirdband[1]) + " Hz")
            self.f2_result.configure(text=str(thirdband[2]) + " Hz")
        except Exception as err:
            self.show_error(err)


if __name__ == "__main__":
    app = App()
    app.iconbitmap("./assets/mapavi_icon_256.ico")
    app.mainloop()
