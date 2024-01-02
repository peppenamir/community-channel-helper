import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import io
import json

class MovieApp(QWidget):
    def __init__(self):
        super().__init__()

        self.api_key = ""
        self.movies_list = []

        self.init_ui()

    def init_ui(self):
        # Widgets
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

        # Layout
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.title_label)
        v_layout.addWidget(self.title_entry)
        v_layout.addWidget(self.search_button)
        v_layout.addWidget(self.movie_list)
        v_layout.addWidget(self.add_button)
        v_layout.addWidget(self.link_label)
        v_layout.addWidget(self.link_entry)
        v_layout.addWidget(self.quality_label)
        v_layout.addWidget(self.quality_entry)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.poster_label)
        h_layout.addWidget(self.poster_image)

        v_layout.addLayout(h_layout)

        v_layout.addWidget(self.api_label)
        v_layout.addWidget(self.api_entry)
        v_layout.addWidget(self.save_button)

        self.setLayout(v_layout)

        # Connect signals
        self.search_button.clicked.connect(self.search_movie)
        self.movie_list.itemClicked.connect(self.display_poster)
        self.add_button.clicked.connect(self.add_movie)
        self.save_button.clicked.connect(self.save_movies_list)

    def search_movie(self):
        movie_title = self.title_entry.text()

        if movie_title:
            self.search_results = self.search_movies(movie_title)

            self.movie_list.clear()  # Pulisci la lista precedente

            if self.search_results:
                for movie in self.search_results:
                    item_text = f"{movie['title']} ({movie['release_date'].split('-')[0] if movie['release_date'] else 'Sconosciuto'})"
                    self.movie_list.addItem(item_text)
            else:
                self.movie_list.addItem("Nessun risultato trovato per il film.")

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
        selected_movie = self.search_results[self.movie_list.currentRow()]
        poster_path = selected_movie['poster_path']

        if poster_path:
            poster_url = f'https://image.tmdb.org/t/p/w300/{poster_path}'
            response = requests.get(poster_url)

            # Carica l'immagine direttamente con QPixmap
            qt_image = QPixmap()
            qt_image.loadFromData(response.content)

            # Ridimensiona l'immagine se necessario
            qt_image = qt_image.scaled(150, 200, Qt.KeepAspectRatio)

            # Imposta l'immagine sulla QLabel
            self.poster_image.setPixmap(qt_image)
        else:
            print("La locandina non è disponibile per questo film.")

    def add_movie(self):
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
        self.movie_list.clear()

        # Mostra un messaggio di conferma
        self.movie_list.addItem(f"{movie_info['title']} aggiunto alla lista.")

    def save_movies_list(self):
        # Rimuovi il campo 'poster_path' da ogni film nella lista
        for movie_info in self.movies_list:
            movie_info.pop('poster_path', None)

        # Crea un dizionario contenente la lista dei film
        data = {
            "movies_list": self.movies_list
        }

        # Scrivi i dati nel file JSON
        with open('movies_list.json', 'w') as json_file:
            json.dump(data, json_file, indent=2)

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
