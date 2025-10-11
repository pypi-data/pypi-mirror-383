import sys
import time
from chronometre import Chronometre

class Loading():
    def __init__(self):
        self.bar = ""
        self.sart_percent = 0
        self.start = False
        self.percent = 0
        self.total_task = 0
        self.status = 0
        self.size_bar = 25
        self.final_time = False
        self.chrono = None
        self.border = "|"
        self.fill = "█"
        self.empty = " "
        self.show_percent = True
        self.show_percent_symbol = True
        self.show_bar = True
        self.show_detail = True
        self.title = ""
        self.show_time = False
        self.style = "bar"

        self.liste = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

        self.a = 1
        self.b = 4
        self.c = 6

        # Directions pour chaque indice
        self.dir_a = 1
        self.dir_b = 1
        self.dir_c = 1

    def info(self):
        print("""
Disponible methods:
              
    - style_bar() : customize the loading bar style and display options :
        - border : character for the border of the bar (default "|")
        - fill : character for the filled part of the bar (default "█")
        - empty : character for the empty part of the bar (default " ")
        - show_percent : boolean to show/hide the percentage (default True)
        - final_time : boolean to enable/disable the timer (default False)
        - show_percent_symbol : boolean to show/hide the percent symbol (default True)
        - show_bar : boolean to show/hide the loading bar (default True)
        - show_detail : boolean to show/hide the task detail (default True)
        - Title : string to add a title before the loading bar (default "")
        - show_time : boolean to show/hide the elapsed time (default False)
        - style : "bar" for a classic loading bar, "graphic" for a graphic loading animation (default "bar")
              
    - create_loading_bar() : Init a new loading bar :
        - total_task : total number of tasks to complete
        - size_bar : size of the loading bar (default 25)
              
    - update_task() : update the current task progress :
        - status : current number of completed tasks
              
    - update_bar() : update the loading bar based on progress:
        - percent : number of tasks completed since the last update
              
    - get_bar() : return the current state of the loading bar as a string.
              
    - get_time() : return the elapsed time if final_time is enabled.
              
    - close() : close and reset the loading bar.
              
    - infinite_load() : display an infinite loading animation :
        - size : size of the loading bar (default 25)
        - interval : time interval between updates in seconds (default 0.1)
              
    - simple_load() : display a simple loading bar with a fixed interval :
        - interval : time interval between updates in seconds
              
    - graphic_load() : return a frame of the graphic loading animation.
              
    - test_load() : run a test loading sequence.
""")

    def graphic_load(self):
        # Mettre à jour les indices en fonction de leur direction
        self.a += self.dir_a
        self.b += self.dir_b
        self.c += self.dir_c

        # Inverser la direction si on atteint les limites
        if self.a == len(self.liste) - 1 or self.a == 0:
            self.dir_a *= -1
        if self.b == len(self.liste) - 1 or self.b == 0:
            self.dir_b *= -1
        if self.c == len(self.liste) - 1 or self.c == 0:
            self.dir_c *= -1
        return (f"{self.liste[self.a]}{self.liste[self.b]}{self.liste[self.c]}")


    def infinite_load(self, size=25, interval=0.1):
        if not self.start:
            self.start = True
            self.bar = self.border
            self.size_bar = size
            for k in range(size):
                self.bar += self.empty
            self.bar += self.border
            self.total_task = "∞"
            self.percent = -1
        while self.start:
            for k in range(self.size_bar):
                self.status +=1
                self.bar = self.bar[:k+1] + self.fill + self.bar[k+2:]
                if k != 0:
                    self.bar = self.bar[:k] + self.empty + self.bar[k+1:]
                print("\r",self.get_bar(), end='', flush=True)
                time.sleep(interval)
            for k in range(self.size_bar-1, -1, -1):
                self.status +=1
                
                self.bar = self.bar[:k+1] + self.fill + self.bar[k+2:]
                if k != self.size_bar-1:
                    self.bar = self.bar[:k+2] + self.empty + self.bar[k+3:]
                print("\r",self.get_bar(), end='', flush=True)
                time.sleep(interval)

    def test_load(self):
        load()

    def create_loading_bar(self, total_task, size_bar=25):
        if not self.start:
            self.total_task = total_task
            self.start = True
            self.size_bar = size_bar


    def update_task(self, status):
        if self.start: 
            self.status = status
            self.percent = float(f"{(self.status/self.total_task)*100:.2f}")

    def update_bar(self, percent):
        if self.start: 
            if self.status <= self.total_task:
                if self.status == 0 and self.final_time:
                        self.chrono = Chronometre()
                        self.chrono.start()
                if self.style == "bar":
                    self.bar=''
                    self.status += percent

                    self.percent = float(f"{(self.status/self.total_task)*100:.2f}")

                    blocknumber = int(self.percent / float(100/self.size_bar))
                    self.bar = self.border
                    for k in range(self.size_bar):
                        if k <= blocknumber:
                            self.bar = self.bar[:k+1] + self.fill + self.bar[k+2:]
                        else:
                            self.bar = self.bar[:k+1] + self.empty + self.bar[k+2:]
                    self.bar += self.border
                else :
                    self.bar=''
                    self.status += percent

                    self.percent = float(f"{(self.status/self.total_task)*100:.2f}")

                    blocknumber = int(self.percent / float(100/self.size_bar))

                    self.bar = self.graphic_load()


    def style_bar(self, border="|", 
                  fill="█", empty=" ", 
                  show_percent=True, 
                  final_time=False, 
                  show_percent_symbol=True, 
                  show_bar=True, 
                  show_detail=True,
                  Title="",
                  show_time=False,
                  style="bar"
                  ):
        self.border = str(border)
        self.fill = str(fill)
        self.empty = str(empty)
        self.final_time = final_time
        self.show_percent = show_percent
        self.show_percent_symbol = show_percent_symbol
        self.show_bar = show_bar
        self.show_detail = show_detail
        self.title = str(Title)
        self.style = str(style)
        self.show_time = show_time

    def get_time(self):
        if self.start: 
            self.chrono.stop()
            return self.chrono.elapsed()

    def simple_load(self, interval):
        inverval = interval
        print("Temps éstimé :", inverval*100, "secondes")
        chrono = Chronometre()
        chrono.start()
        for k in range(100):
            print(f"\r{k+1:.2f} % {loading_bar(k+1)} {chrono.elapsed():.2f}s", end='', flush=True)
            time.sleep(inverval)
        print(f"\nTemps écoulé : {chrono.elapsed():.2f} secondes")

    def close(self):
        if self.start: 
            self.start = False
            self.bar = ""
            self.percent = 0
            self.total_task = 0
            self.status = 0
            self.chrono = None
            self.style_bar()

    def get_bar(self):
        if self.start: 
            final = self.title  # Ajout du titre
            if self.show_percent:
                final += f"{self.percent:.2f} "  # Ajout du pourcentage
                if self.show_percent_symbol:
                    final += "% "
            if self.show_bar:
                final += self.bar  # Ajout de la barre
            if self.show_detail:
                final += f" {self.status}/{self.total_task} "  # Ajout des détails
            if self.show_time:
                if self.chrono is not None:
                    final += f" {self.chrono.elapsed():.2f}s"  # Ajout du temps écoulé
            return final

def choice_text():
    try:
        interval = float(input("\nEntrer un interval de temps en seconde\n> "))
        return interval
    except ValueError:
        print("Veuillez entrer un nombre valide.")
        return choice_text()

def loading_bar(percent):
    percent /= 4
    bloc = "|"
    for k in range(26):
        if k <= percent:
            bloc += "█"
        else:
            bloc += " "
    bloc += "|"
    return bloc

def load():
    inverval = choice_text()
    print("Temps éstimé :", inverval*100, "secondes")
    chrono = Chronometre()
    chrono.start()
    for k in range(100):
        print(f"\r{k+1:.2f} % {loading_bar(k+1)} {chrono.elapsed():.2f}s", end='', flush=True)
        time.sleep(inverval)
    print(f"\nTemps écoulé : {chrono.elapsed():.2f} secondes")

if __name__ == "__main__":
    load()
