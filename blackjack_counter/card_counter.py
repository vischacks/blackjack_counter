class CardCounter:
    def __init__(self, strategy="hi_lo"):
        # Inizializza il conteggio a 0
        self.count = 0
        # Tieni traccia del numero di mazzi rimanenti (stima)
        self.decks_remaining = 6  # Assumi 6 mazzi all'inizio
        
        # Strategia di conteggio corrente
        self.strategy = strategy
        
        # Definisci diverse strategie di conteggio
        self.counting_strategies = {
            "hi_lo": {
                '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
                '7': 0, '8': 0, '9': 0,
                '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
            },
            "ko": {  # Knock Out
                '2': 1, '3': 1, '4': 1, '5': 1, '6': 1, '7': 1,
                '8': 0, '9': 0,
                '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
            },
            "omega2": {  # Omega II
                '2': 1, '3': 1, '4': 2, '5': 2, '6': 2,
                '7': 1, '8': 0, '9': -1,
                '10': -2, 'J': -2, 'Q': -2, 'K': -2, 'A': 0
            },
            "zen": {  # Zen Count
                '2': 1, '3': 1, '4': 2, '5': 2, '6': 2,
                '7': 1, '8': 0, '9': 0,
                '10': -2, 'J': -2, 'Q': -2, 'K': -2, 'A': -1
            }
        }
        
        # Imposta la strategia di conteggio corrente
        self.card_values = self.counting_strategies[self.strategy]
    
    def update_count(self, card):
        """
        Aggiorna il conteggio in base alla carta vista
        """
        if card in self.card_values:
            self.count += self.card_values[card]
    
    def get_count(self):
        """
        Restituisce il running count
        """
        return self.count
    
    def get_true_count(self):
        """
        Restituisce il true count (running count diviso per mazzi rimanenti)
        """
        if self.decks_remaining > 0:
            return self.count / self.decks_remaining
        return self.count
    
    def update_decks_remaining(self, decks):
        """
        Aggiorna la stima dei mazzi rimanenti
        """
        self.decks_remaining = decks
    
    def change_strategy(self, strategy):
        """
        Cambia la strategia di conteggio
        """
        if strategy in self.counting_strategies:
            self.strategy = strategy
            self.card_values = self.counting_strategies[self.strategy]
            return True
        return False
    
    def get_strategy(self):
        """
        Restituisce la strategia di conteggio corrente
        """
        return self.strategy
    
    def get_available_strategies(self):
        """
        Restituisce le strategie di conteggio disponibili
        """
        return list(self.counting_strategies.keys())