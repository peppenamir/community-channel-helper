import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QFileDialog, QRadioButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import json
import requests

class MovieApp(QWidget):
    def __init__(self):
        super().__init__()

        self.api_key = ""  # Inserisci qui la tua chiave API di TMDb
        self.movies_list = []
        self.search_results = []
        self.mode = "search"  # Modalità predefinita: ricerca online

        self.init_ui()

    def init_ui(self):
        # Creazione del layout
        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()

        # Widget
        self.title_label = QLabel("Inserisci il titolo del film:")
        self.title_entry = QLineEdit()
        self.search_button = QPushButton("Cerca")
        self.movie_list = QListWidget()
        self.add_button = QPushButton("Aggiungi alla lista")
        self.link_label = QLabel("Url dello stream:")
        self.link_entry = QLineEdit()
        self.quality_label = QLabel("Qualità del film:")
        self.quality_entry = QLineEdit()
        self.poster_label = QLabel("Locandina:")
        self.poster_image = QLabel()
        self.api_label = QLabel("API Key:")
        self.api_entry = QLineEdit()
        self.save_button = QPushButton("Salva Lista")
        self.load_button = QPushButton("Carica Lista da JSON")
        self.search_radio = QRadioButton("Ricerca Online")
        self.edit_radio = QRadioButton("Modifica Lista da JSON")

        # Aggiunta dei widget al layout
        v_layout.addWidget(self.title_label)
        v_layout.addWidget(self.title_entry)
        v_layout.addWidget(self.search_button)
        v_layout.addWidget(self.movie_list)
        v_layout.addWidget(self.add_button)
        v_layout.addWidget(self.link_label)
        v_layout.addWidget(self.link_entry)
        v_layout.addWidget(self.quality_label)
        v_layout.addWidget(self.quality_entry)

        h_layout.addWidget(self.poster_label)
        h_layout.addWidget(self.poster_image)

        v_layout.addLayout(h_layout)

        v_layout.addWidget(self.api_label)
        v_layout.addWidget(self.api_entry)
        v_layout.addWidget(self.save_button)
        v_layout.addWidget(self.load_button)
        v_layout.addWidget(self.search_radio)
        v_layout.addWidget(self.edit_radio)

        # Connetti i segnali
        self.search_button.clicked.connect(self.search_movie)
        self.movie_list.itemClicked.connect(self.display_poster)
        self.add_button.clicked.connect(self.add_movie)
        self.save_button.clicked.connect(self.save_movies_list)
        self.load_button.clicked.connect(self.load_movies_list)
        self.search_radio.toggled.connect(lambda: self.set_mode("search"))
        self.edit_radio.toggled.connect(lambda: self.set_mode("edit"))

        self.setLayout(v_layout)

    def set_mode(self, mode):
        # Imposta la modalità di operazione
        self.mode = mode
        if mode == "search":
            self.clear_edit_widgets()
            self.clear_movie_list()
        elif mode == "edit":
            self.clear_search_widgets()
            self.search_results = []

    def search_movie(self):
        # Logica per la ricerca online
        if self.mode == "search":
            movie_title = self.title_entry.text()

            if movie_title:
                self.search_results = self.search_movies(movie_title)

                self.clear_movie_list()  # Pulisci la lista precedente

                if self.search_results:
                    for movie in self.search_results:
                        item_text = f"{movie['title']} ({movie['release_date'].split('-')[0] if movie['release_date'] else 'Sconosciuto'})"
                        self.movie_list.addItem(item_text)
                else:
                    self.movie_list.addItem("Nessun risultato trovato per il film.")

        # Logica per la modifica della lista da JSON
        elif self.mode == "edit":
            # Qui puoi implementare la logica per la modifica della lista da JSON
            pass

    def search_movies(self, movie_title):
        # URL per cercare film su TMDb
        search_url = 'https://api.themoviedb.org/3/search/movie'

        # Parametri della richiesta
        params = {
            'api_key': self.api_entry.text(),
            'query': movie_title
        }

        # Effettua la richiesta GET a TMDb
        response = requests.get(search_url, params=params)
        data = response.json()

        # Verifica se la chiave 'results' è presente nel dizionario
        if 'results' in data:
            # Verifica se ci sono risultati
            if data['results']:
                # Restituisci la lista di risultati
                return data['results']
            else:
                return None
        else:
            # Se 'results' non è presente, potrebbe essere un errore o una risposta diversa
            print("Errore nella risposta API:")
            print(data)
            return None

    def display_poster(self, item):
        # (Resto del codice rimane invariato)
        pass

    def add_movie(self):
        # Logica per l'aggiunta di un film alla lista
        if self.mode == "search":
            selected_movie = self.search_results[self.movie_list.currentRow()]
            movie_info = self.get_movie_info(selected_movie['id'])

            # Aggiungi il link e la qualità alle informazioni del film
            link_url = self.link_entry.text()
            link_quality = self.quality_entry.text()

            movie_info['links'].append({
                'url': link_url,
                'quality': link_quality
            })

            # Aggiungi il film alla lista
            self.movies_list.append(movie_info)

            # Pulisci la lista di risultati
            self.clear_movie_list()

            # Mostra un messaggio di conferma
            self.movie_list.addItem(f"{movie_info['title']} aggiunto alla lista.")

        # Logica per l'aggiunta di un film dalla lista JSON
        elif self.mode == "edit":
            # Qui puoi implementare la logica per l'aggiunta di un film dalla lista JSON
            pass

    def save_movies_list(self):
        # Logica per il salvataggio della lista
        if self.mode == "search":
            # Rimuovi il campo 'poster_path' da ogni film nella lista
            for movie_info in self.movies_list:
                movie_info.pop('poster_path', None)

            # Crea un dizionario contenente la lista dei film
            data = {
                "movies_list": self.movies_list
            }

            # Scrivi i dati nel file JSON
            try:
                with open('movies_list.json', 'w') as json_file:
                    json.dump(data, json_file, indent=2)

                # Visualizza un messaggio di conferma nella console
                print("Lista salvata con successo.")
            except Exception as e:
                # Visualizza un messaggio di errore nella console
                print(f"Errore durante il salvataggio del file JSON: {e}")

    def load_movies_list(self):
        # Logica per il caricamento della lista da JSON
        if self.mode == "edit":
            file_name, _ = QFileDialog.getOpenFileName(self, "Carica Lista da JSON", "", "JSON Files (*.json)")
            if file_name:
                try:
                    with open(file_name, 'r') as json_file:
                        data = json.load(json_file)
                        self.populate_interface_from_json(data)
                except Exception as e:
                    print(f"Errore durante il caricamento del file JSON: {e}")

    def populate_interface_from_json(self, data):
        # Pulizia dell'interfaccia e della lista dei film
        self.clear_search_widgets()
        self.movies_list = []

        # Aggiunta dei film dalla lista JSON
        for movie_data in data.get('movies_list', []):
            self.movies_list.append(movie_data)
            item_text = f"{movie_data['title']} ({movie_data['year'] if movie_data['year'] else 'Sconosciuto'})"
            self.movie_list.addItem(item_text)

        # Visualizzazione di un messaggio di conferma
        self.movie_list.addItem("Lista caricata da JSON")

    def clear_movie_list(self):
        self.movie_list.clear()

    def clear_search_widgets(self):
        self.title_entry.clear()
        self.clear_movie_list()
        self.link_entry.clear()
        self.quality_entry.clear()
        self.poster_image.clear()

    def clear_edit_widgets(self):
        self.api_entry.clear()
        self.clear_movie_list()

    def get_movie_info(self, movie_id):
        # URL per ottenere informazioni su un film specifico su TMDb
        movie_url = f'https://api.themoviedb.org/3/movie/{movie_id}'

        # Parametri della richiesta
        params = {
            'api_key': self.api_entry.text()
        }

        # Effettua la richiesta GET a TMDb
        response = requests.get(movie_url, params=params)
        data = response.json()

        # Rimuovi il campo 'poster_path' dalle informazioni del film
        data.pop('poster_path', None)

        # Estrai le informazioni desiderate
        movie_info = {
            'title': data['title'],
            'year': data['release_date'].split('-')[0] if data['release_date'] else "",
            'tmdb_id': data['id'],
            'links': []  # Inizializza la lista dei link
        }

        return movie_info

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MovieApp()
    ex.show()
    sys.exit(app.exec_())
