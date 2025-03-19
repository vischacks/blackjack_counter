import tkinter as tk
from tkinter import ttk, messagebox
import sys
from card_counter import CardCounter

class BlackjackCounterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack Counter Pro")
        self.root.geometry("850x650")
        self.root.resizable(True, True)
        
        # Set theme colors
        self.bg_color = "#1E1E1E"  # Dark background
        self.text_color = "#FFFFFF"  # White text
        self.accent_color = "#4CAF50"  # Green accent
        self.warning_color = "#F44336"  # Red warning
        self.neutral_color = "#9E9E9E"  # Gray neutral
        self.first_card_color = "#00BFFF"  # Azzurro per la prima carta di ogni mano
        
        # Configure style
        style = ttk.Style()
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        style.configure("TButton", background=self.accent_color, foreground=self.text_color)
        style.configure("TLabelframe", background=self.bg_color, foreground=self.text_color)
        style.configure("TLabelframe.Label", background=self.bg_color, foreground=self.text_color)
        
        # Initialize card counter
        self.counter = CardCounter()
        
        # Card history
        self.card_history = []
        self.current_hand_cards = []  # Cards in the current hand
        self.total_cards_used = 0  # Contatore per il totale delle carte inserite
        self.decks_used = 0  # Contatore per i mazzi utilizzati
        
        # Card type counter - tracks how many of each card type have been played
        self.card_type_counter = {
            'A': 0, '2': 0, '3': 0, '4': 0, '5': 0,
            '6': 0, '7': 0, '8': 0, '9': 0, '10': 0,
            'J': 0, 'Q': 0, 'K': 0
        }
        
        # Budget tracking
        self.initial_budget = 0
        self.current_budget = 0
        self.base_bet = 0  # Default base bet amount
        self.previous_bet = 0  # Track the previous bet amount
        
        # Session statistics
        self.hands_played = 0
        self.hands_won = 0
        self.hands_lost = 0
        self.hands_pushed = 0
        self.session_bets = []
        self.session_results = []
        self.hand_history = []  # Store complete hand history with cards and results
        
        # Edge calculation (default advantage for player with perfect strategy)
        self.player_edge = 0.005  # 0.5% advantage with perfect basic strategy and favorable count
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (card input and controls)
        left_panel = ttk.Frame(main_frame, padding="5")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right panel (statistics and history)
        right_panel = ttk.Frame(main_frame, padding="5")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Budget frame
        budget_frame = ttk.LabelFrame(left_panel, text="Budget Settings", padding="5")
        budget_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(budget_frame, text="Initial Budget:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.budget_entry = ttk.Entry(budget_frame)
        self.budget_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(budget_frame, text="Set Budget", command=self.set_budget).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(budget_frame, text="Current Budget:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.current_budget_var = tk.StringVar(value="0.00")
        ttk.Label(budget_frame, textvariable=self.current_budget_var, font=("Arial", 12, "bold")).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Base bet input
        ttk.Label(budget_frame, text="Base Bet:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.base_bet_entry = ttk.Entry(budget_frame)
        self.base_bet_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(budget_frame, text="Set Base Bet", command=self.set_base_bet).grid(row=2, column=2, padx=5, pady=5)
        
        # Card input frame
        card_frame = ttk.LabelFrame(left_panel, text="Card Input", padding="5")
        card_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Card buttons
        cards = [
            ('A', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
            ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '0'),
            ('J', 'j'), ('Q', 'q'), ('K', 'k')
        ]
        
        # Create a grid of card buttons
        row, col = 0, 0
        for card_value, key in cards:
            btn = ttk.Button(
                card_frame, 
                text=f"{card_value} ({key})", 
                width=8,
                command=lambda c=card_value: self.add_card(c)
            )
            btn.grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col > 4:  # 5 buttons per row
                col = 0
                row += 1
        
        # Card type counter frame - Moved here from right panel
        card_counter_frame = ttk.LabelFrame(card_frame, text="Card Type Counts", padding="5")
        card_counter_frame.grid(row=row+1, column=0, columnspan=5, sticky=tk.W+tk.E, padx=5, pady=10)
        
        # Create a grid for card counts
        self.card_count_labels = {}
        count_row, count_col = 0, 0
        for card in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']:
            ttk.Label(card_counter_frame, text=f"{card}:").grid(row=count_row, column=count_col*2, sticky=tk.W, padx=5, pady=2)
            self.card_count_labels[card] = tk.StringVar(value="0")
            ttk.Label(card_counter_frame, textvariable=self.card_count_labels[card]).grid(row=count_row, column=count_col*2+1, sticky=tk.W, padx=5, pady=2)
            count_col += 1
            if count_col > 4:  # 5 cards per row
                count_col = 0
                count_row += 1
        
        # Hand result tracking frame
        hand_frame = ttk.LabelFrame(left_panel, text="Hand Result Tracking", padding="5")
        hand_frame.pack(fill=tk.X, pady=5)
        
        # Bet amount entry
        ttk.Label(hand_frame, text="Bet Amount:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.bet_entry = ttk.Entry(hand_frame, width=10)
        self.bet_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Result buttons
        result_frame = ttk.Frame(hand_frame)
        result_frame.grid(row=1, column=0, columnspan=3, pady=5)
        
        ttk.Button(result_frame, text="Win", command=lambda: self.record_hand_result("win")).pack(side=tk.LEFT, padx=5)
        ttk.Button(result_frame, text="Loss", command=lambda: self.record_hand_result("loss")).pack(side=tk.LEFT, padx=5)
        ttk.Button(result_frame, text="Push", command=lambda: self.record_hand_result("push")).pack(side=tk.LEFT, padx=5)
        
        # Strategy selection
        strategy_frame = ttk.Frame(left_panel)
        strategy_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(strategy_frame, text="Counting Strategy:").pack(side=tk.LEFT, padx=5)
        self.strategy_var = tk.StringVar(value="hi_lo")
        self.strategy_combo = ttk.Combobox(strategy_frame, textvariable=self.strategy_var, 
                                          values=["hi_lo", "ko", "omega2", "zen"])
        self.strategy_combo.pack(side=tk.LEFT, padx=5)
        self.strategy_combo.bind("<<ComboboxSelected>>", self.change_strategy)
        
        # Control buttons
        control_frame = ttk.Frame(left_panel, padding="5")
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="Reset Count", command=self.reset_count).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Reset Session", command=self.reset_session).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Exit", command=self.root.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(right_panel, text="Statistics", padding="5")
        stats_frame.pack(fill=tk.X, pady=5)
        
        # Running count
        ttk.Label(stats_frame, text="Running Count:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.running_count_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.running_count_var, font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Carte inserite
        ttk.Label(stats_frame, text="Carte Inserite:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.cards_used_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.cards_used_var, font=("Arial", 12, "bold")).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # True count
        ttk.Label(stats_frame, text="True Count:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.true_count_var = tk.StringVar(value="0.00")
        ttk.Label(stats_frame, textvariable=self.true_count_var, font=("Arial", 12, "bold")).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Deck status
        ttk.Label(stats_frame, text="Deck Status:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.deck_status_var = tk.StringVar(value="Neutral")
        self.deck_status_label = ttk.Label(stats_frame, textvariable=self.deck_status_var, font=("Arial", 12, "bold"))
        self.deck_status_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Betting recommendation
        ttk.Label(stats_frame, text="Bet Recommendation:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.bet_recommendation_var = tk.StringVar(value="--")
        ttk.Label(stats_frame, textvariable=self.bet_recommendation_var, font=("Arial", 12, "bold")).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Kelly criterion toggle
        self.kelly_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(stats_frame, text="Use Kelly Criterion", variable=self.kelly_var, 
                       command=self.update_statistics).grid(row=3, column=2, padx=5, pady=5)
        
        # Decks remaining
        ttk.Label(stats_frame, text="Decks Remaining:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.decks_frame = ttk.Frame(stats_frame)
        self.decks_frame.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.decks_var = tk.StringVar(value="6")
        ttk.Entry(self.decks_frame, textvariable=self.decks_var, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.decks_frame, text="Update", command=self.update_decks).pack(side=tk.LEFT, padx=2)
        
        # Mazzi utilizzati
        ttk.Label(stats_frame, text="Mazzi Utilizzati:").grid(row=4, column=2, sticky=tk.W, padx=5, pady=5)
        self.decks_used_var = tk.StringVar(value="0.00")
        ttk.Label(stats_frame, textvariable=self.decks_used_var, font=("Arial", 12, "bold")).grid(row=4, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Session statistics
        ttk.Label(stats_frame, text="Hands Played:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.hands_played_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.hands_played_var).grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(stats_frame, text="Win/Loss/Push:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        self.wlp_var = tk.StringVar(value="0/0/0")
        ttk.Label(stats_frame, textvariable=self.wlp_var).grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(stats_frame, text="Session Profit:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
        self.profit_var = tk.StringVar(value="0.00")
        self.profit_label = ttk.Label(stats_frame, textvariable=self.profit_var, font=("Arial", 12, "bold"))
        self.profit_label.grid(row=7, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Initialize empty trend data
        self.count_trend = []
        
        # History frame
        history_frame = ttk.LabelFrame(right_panel, text="Hand History", padding="5")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create text widget for history
        self.history_text = tk.Text(history_frame, width=40, height=10, bg=self.bg_color, fg=self.text_color)
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar to history text
        history_scrollbar = ttk.Scrollbar(self.history_text, command=self.history_text.yview)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.config(yscrollcommand=history_scrollbar.set)
        
        # Trend graph frame
        trend_frame = ttk.LabelFrame(right_panel, text="Count Trend", padding="5")
        trend_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create canvas for trend graph
        self.trend_canvas = tk.Canvas(trend_frame, bg=self.bg_color, height=150)
        self.trend_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Version label (only one instance)
        version_label = ttk.Label(self.root, text="v 1.3", foreground=self.neutral_color, font=("Arial", 8))
        version_label.pack(side=tk.BOTTOM, anchor=tk.SE, padx=5, pady=2)
        
        # Key bindings for card input
        self.setup_key_bindings()
    
    def setup_key_bindings(self):
        # Map keys to card values
        key_mappings = {
            '1': 'A', '2': '2', '3': '3', '4': '4', '5': '5',
            '6': '6', '7': '7', '8': '8', '9': '9', '0': '10',
            'j': 'J', 'q': 'Q', 'k': 'K'
        }
        
        # Bind keys to add_card function only when not in entry widgets
        for key, card in key_mappings.items():
            self.root.bind(key, lambda event, c=card: self.handle_key_press(event, c))
    
    def handle_key_press(self, event, card):
        # Only process key if focus is not in an Entry widget
        if not isinstance(event.widget, tk.Entry):
            self.add_card(card)
    
    def add_card(self, card):
        # Update counter
        self.counter.update_count(card)
        
        # Update card history
        self.card_history.append(card)
        self.current_hand_cards.append(card)  # Add to current hand
        
        # Incrementa il contatore delle carte usate
        self.total_cards_used += 1
        
        # Aggiorna il contatore dei mazzi utilizzati (52 carte per mazzo)
        self.decks_used = self.total_cards_used / 52
        
        # Update card type counter
        if card in self.card_type_counter:
            self.card_type_counter[card] += 1
        
        # Add to count trend
        self.count_trend.append(self.counter.get_count())
        
        # Update UI
        self.update_statistics()
        self.update_history()
        self.update_trend_graph()
    
    def reset_count(self):
        # Reset counter but keep the same strategy
        current_strategy = self.counter.get_strategy()
        self.counter = CardCounter(strategy=current_strategy)
        self.card_history = []
        self.current_hand_cards = []
        self.count_trend = []
        self.total_cards_used = 0
        self.decks_used = 0
        
        # Reset card type counter
        for card in self.card_type_counter:
            self.card_type_counter[card] = 0
        
        # Update UI
        self.update_statistics()
        self.update_history()
        self.update_trend_graph()
        
        messagebox.showinfo("Reset", "Card count has been reset.")
        
    def update_trend_graph(self):
        # Clear canvas
        self.trend_canvas.delete("all")
        
        # If no trend data, just return
        if not self.count_trend:
            self.trend_canvas.create_text(
                self.trend_canvas.winfo_width() // 2, 
                self.trend_canvas.winfo_height() // 2,
                text="No count data yet", fill="#FFFFFF"
            )
            return
        
        # Get canvas dimensions
        width = self.trend_canvas.winfo_width()
        height = self.trend_canvas.winfo_height()
        
        # Draw zero line
        self.trend_canvas.create_line(
            0, height // 2, width, height // 2, 
            fill="#9E9E9E", dash=(4, 2)
        )
        
        # Calculate scaling factors - DYNAMIC SCALING
        padding = 2  # Aggiungi un padding per evitare che i punti tocchino i bordi
        max_count = max(max(self.count_trend, default=0), 1)
        min_count = min(min(self.count_trend, default=0), -1)
        
        # Assicurati che ci sia sempre un range minimo per evitare scaling eccessivo
        range_min = 5
        if max_count - min_count < range_min:
            # Espandi il range mantenendo il centro
            center = (max_count + min_count) / 2
            max_count = center + range_min / 2
            min_count = center - range_min / 2
        
        # Aggiungi padding per evitare che i punti tocchino i bordi
        max_count += padding
        min_count -= padding
        
        # Calculate vertical scaling
        y_scale = (height - 20) / (max_count - min_count)
        
        # Calculate horizontal scaling
        x_scale = width / max(len(self.count_trend), 1)
        if len(self.count_trend) > 1:
            x_scale = width / (len(self.count_trend) - 1)
        
        # Trova gli indici delle prime carte di ogni mano
        first_card_indices = []
        hand_start_idx = 0
        
        # Aggiungi l'indice della prima carta della mano corrente
        if self.current_hand_cards and len(self.current_hand_cards) == 1 and len(self.count_trend) > 0:
            first_card_indices.append(len(self.count_trend) - 1)
        
        # Aggiungi gli indici delle prime carte delle mani precedenti
        for hand in self.hand_history:
            if 'first_card_index' in hand and hand['first_card_index'] is not None and hand['first_card_index'] < len(self.count_trend):
                first_card_indices.append(hand['first_card_index'])
        
        # Draw trend line
        points = []
        for i, count in enumerate(self.count_trend):
            x = i * x_scale
            # Calcola la posizione y in base al range dinamico
            # Nota: invertiamo le coordinate y (0,0 è in alto a sinistra nel canvas)
            y = height - ((count - min_count) * y_scale + 10)
            points.extend([x, y])
        
        # Draw line if we have at least 2 points
        if len(points) >= 4:  # At least 2 points (each point is x,y pair)
            self.trend_canvas.create_line(
                points, fill="#4CAF50", width=2, smooth=True
            )
        
        # Draw points
        for i in range(0, len(points), 2):
            x, y = points[i], points[i+1]
            point_idx = i // 2
            
            # Determina il colore del punto
            if point_idx in first_card_indices:
                # Prima carta di una mano - colore azzurro
                color = self.first_card_color
            else:
                # Altre carte - verde se positivo, rosso se negativo
                color = "#4CAF50" if self.count_trend[point_idx] >= 0 else "#F44336"
            
            self.trend_canvas.create_oval(
                x-3, y-3, x+3, y+3, fill=color, outline=""
            )
        
        # Draw current count and range
        current_count = self.count_trend[-1] if self.count_trend else 0
        self.trend_canvas.create_text(
            width - 10, 10, 
            text=f"Current: {current_count}", 
            fill="#FFFFFF", anchor="ne"
        )
        
        # Mostra il range del grafico
        self.trend_canvas.create_text(
            10, 10,
            text=f"Range: {min_count:.1f} to {max_count:.1f}",
            fill="#FFFFFF", anchor="nw"
        )
    
    def reset_session(self):
        # Reset session statistics
        self.hands_played = 0
        self.hands_won = 0
        self.hands_lost = 0
        self.hands_pushed = 0
        self.session_bets = []
        self.session_results = []
        self.hand_history = []
        self.base_bet = 0  # Reset base bet
        self.previous_bet = 0  # Reset previous bet
        
        # Reset budget to initial value
        self.current_budget = self.initial_budget
        
        # Update UI
        self.update_statistics()
        self.current_budget_var.set(f"{self.current_budget:.2f}")
        self.wlp_var.set("0/0/0")
        self.hands_played_var.set("0")
        self.profit_var.set("0.00")
        
        messagebox.showinfo("Reset", "Session has been reset.")
    
    def record_hand_result(self, result):
        try:
            bet_amount = float(self.bet_entry.get())
            if bet_amount <= 0:
                messagebox.showerror("Error", "Bet amount must be greater than zero.")
                return
                
            if self.current_budget <= 0:
                messagebox.showerror("Error", "You have no budget left. Please reset or add more budget.")
                return
                
            # Store the current bet as previous bet for future recommendations
            self.previous_bet = bet_amount
                
            self.hands_played += 1
            self.session_bets.append(bet_amount)
            
            if result == "win":
                self.hands_won += 1
                self.current_budget += bet_amount
                self.session_results.append(bet_amount)
                result_text = f"Win: +{bet_amount:.2f}"
            elif result == "loss":
                self.hands_lost += 1
                self.current_budget -= bet_amount
                self.session_results.append(-bet_amount)
                result_text = f"Loss: -{bet_amount:.2f}"
            else:  # push
                self.hands_pushed += 1
                self.session_results.append(0)
                result_text = "Push: 0.00"
            
            # Calcola l'indice della prima carta della mano corrente
            # Se abbiamo carte nella mano corrente, l'indice della prima carta è
            # la lunghezza del count_trend meno il numero di carte nella mano corrente
            first_card_index = len(self.count_trend) - len(self.current_hand_cards) if self.current_hand_cards else None
            
            # Store hand information
            hand_info = {
                'hand_number': self.hands_played,
                'cards': self.current_hand_cards.copy(),
                'result': result,
                'bet_amount': bet_amount,
                'result_text': result_text,
                'first_card_index': first_card_index
            }
            self.hand_history.append(hand_info)
            
            # Reset current hand cards
            self.current_hand_cards = []
            
            # Update UI
            self.update_statistics()
            self.current_budget_var.set(f"{self.current_budget:.2f}")
            self.wlp_var.set(f"{self.hands_won}/{self.hands_lost}/{self.hands_pushed}")
            self.hands_played_var.set(str(self.hands_played))
            
            # Calculate profit/loss
            profit = self.current_budget - self.initial_budget
            self.profit_var.set(f"{profit:.2f}")
            if profit > 0:
                self.profit_label.config(foreground="green")
            elif profit < 0:
                self.profit_label.config(foreground="red")
            else:
                self.profit_label.config(foreground="black")
            
            # Add to history with cards and result
            self.update_history()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for bet amount.")
    
    def change_strategy(self, event):
        strategy = self.strategy_var.get()
        if self.counter.change_strategy(strategy):
            messagebox.showinfo("Strategy", f"Counting strategy changed to {strategy}")
            self.update_statistics()
        else:
            messagebox.showerror("Error", f"Invalid strategy: {strategy}")
            # Reset combobox to current strategy
            self.strategy_var.set(self.counter.get_strategy())
    
    def set_budget(self):
        try:
            budget = float(self.budget_entry.get())
            if budget <= 0:
                messagebox.showerror("Error", "Budget must be greater than zero.")
                return
                
            self.initial_budget = budget
            self.current_budget = budget
            messagebox.showinfo("Budget", f"Budget set to {budget:.2f}")
            self.update_statistics()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for budget.")
    
    def set_base_bet(self):
        try:
            base_bet = float(self.base_bet_entry.get())
            if base_bet <= 0:
                messagebox.showerror("Error", "Base bet must be greater than zero.")
                return
                
            self.base_bet = base_bet
            messagebox.showinfo("Base Bet", f"Base bet set to {base_bet:.2f}")
            self.update_statistics()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for base bet.")
    
    def update_decks(self):
        try:
            decks = float(self.decks_var.get())
            if decks <= 0:
                messagebox.showerror("Error", "Decks remaining must be greater than zero.")
                return
                
            self.counter.update_decks_remaining(decks)
            self.update_statistics()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for decks remaining.")
    
    def update_statistics(self):
        # Update running count
        running_count = self.counter.get_count()
        self.running_count_var.set(str(running_count))
        
        # Update true count
        true_count = self.counter.get_true_count()
        self.true_count_var.set(f"{true_count:.2f}")
        
        # Update deck status
        if true_count >= 2:
            status = "High (Favorable)"
            self.deck_status_label.config(foreground="green")
        elif true_count <= -2:
            status = "Low (Unfavorable)"
            self.deck_status_label.config(foreground="red")
        else:
            status = "Neutral"
            self.deck_status_label.config(foreground="black")
        
        self.deck_status_var.set(status)
        
        # Aggiorna i contatori delle carte e dei mazzi
        self.cards_used_var.set(str(self.total_cards_used))
        self.decks_used_var.set(f"{self.decks_used:.2f}")
        
        # Update card type counter display
        for card, count in self.card_type_counter.items():
            self.card_count_labels[card].set(str(count))
        
        # Update betting recommendation
        if self.initial_budget > 0:
            self.update_bet_recommendation(true_count)
    
    def update_bet_recommendation(self, true_count):
        # Use user-defined base bet if available, otherwise calculate as percentage of budget
        if self.base_bet > 0:
            base_bet = self.base_bet
        else:
            base_bet = self.initial_budget * 0.02  # 2% of initial budget as default base bet
        
        # Adjust base bet based on recent performance
        win_rate = 0.5  # Default win rate
        if self.hands_played > 0:
            win_rate = self.hands_won / self.hands_played
        
        # Adjust base bet up if winning, down if losing
        performance_factor = 1.0
        if self.hands_played >= 5:  # Only adjust after a few hands
            if win_rate > 0.6:  # Winning more than 60%
                performance_factor = 1.2
            elif win_rate < 0.4:  # Winning less than 40%
                performance_factor = 0.8
        
        # Calculate adjusted base bet
        adjusted_base_bet = base_bet * performance_factor
        
        # Consider previous bet for smoother transitions
        previous_bet_factor = 1.0
        if self.previous_bet > 0:
            # Use previous bet as a reference point to avoid large fluctuations
            previous_bet_factor = self.previous_bet / base_bet
            # Limit the influence of previous bet (between 0.7 and 1.3 of the factor)
            previous_bet_factor = max(0.7, min(previous_bet_factor, 1.3))
        
        if self.kelly_var.get():
            # Kelly criterion calculation
            # Adjust edge based on true count
            # Each +1 in true count adds approximately 0.5% to player advantage
            edge = self.player_edge + (true_count * 0.005)
            
            if edge > 0:
                # Kelly formula: f* = edge/variance = edge/(1-edge)
                # For blackjack, we use a simplified version
                kelly_fraction = edge / (1 - edge)
                # Cap at 5% of bankroll for conservative betting
                kelly_fraction = min(kelly_fraction, 0.05)
                
                # Apply previous bet influence for smoother transitions
                if self.previous_bet > 0:
                    # Blend previous bet with new calculation (70% new, 30% previous influence)
                    bet = (self.current_budget * kelly_fraction * 0.7) + \
                          (self.previous_bet * 0.3)
                else:
                    bet = self.current_budget * kelly_fraction
                    
                exact_bet = round(bet, 2)
                recommendation = f"Kelly: x{kelly_fraction:.2f} {kelly_fraction*100:.1f}% → {exact_bet:.2f}"
            else:
                min_bet = round(self.current_budget * 0.01, 2)  # 1% minimum bet
                recommendation = f"Kelly: Minimum bet {min_bet:.2f} or sit out"
        else:
            # Traditional betting strategy based on true count
            if true_count >= 4:
                # Very favorable - bet 4x base
                multiplier = 4.0
            elif true_count >= 2:
                # Favorable - bet 2x base
                multiplier = 2.0
            elif true_count >= 1:
                # Slightly favorable - bet 1.5x base
                multiplier = 1.5
            elif true_count >= -1:
                # Neutral - bet minimum
                multiplier = 1.0
            else:
                # Unfavorable - bet minimum or sit out
                multiplier = 0.5
            
            # Apply previous bet influence for smoother transitions
            if self.previous_bet > 0:
                # Calculate target bet based on current conditions
                target_bet = adjusted_base_bet * multiplier
                
                # Blend with previous bet for smoother transitions
                # If count is improving, move faster toward target (70% target, 30% previous)
                # If count is worsening, move slower (50% target, 50% previous)
                if self.previous_bet < target_bet:
                    # Count improving - move faster toward higher bet
                    bet = (target_bet * 0.7) + (self.previous_bet * 0.3)
                else:
                    # Count worsening - move slower toward lower bet
                    bet = (target_bet * 0.5) + (self.previous_bet * 0.5)
                
                exact_bet = round(bet, 2)
                recommendation = f"Bet x{multiplier:.1f} → {exact_bet:.2f} (smoothed)"
            else:
                # No previous bet to consider
                bet = adjusted_base_bet * multiplier
                exact_bet = round(bet, 2)
                recommendation = f"Bet x{multiplier:.1f} → {exact_bet:.2f}"
        
        self.bet_recommendation_var.set(recommendation)
    
    def update_history(self):
        # Enable text widget for editing
        self.history_text.config(state=tk.NORMAL)
        
        # Clear current content
        self.history_text.delete(1.0, tk.END)
        
        # Display current hand cards first in reverse order (newest first)
        if self.current_hand_cards:
            self.history_text.insert(tk.END, "Current Hand:\n")
            # Reverse the order so newest card is at the top
            for i, card in enumerate(reversed(self.current_hand_cards)):
                # Maintain original card numbering but display in reverse
                card_num = len(self.current_hand_cards) - i
                self.history_text.insert(tk.END, f"  {card_num}. {card}\n")
            self.history_text.insert(tk.END, "\n")
        
        # Display completed hands with cards and results
        if self.hand_history:
            self.history_text.insert(tk.END, "Hand History:\n")
            # Display in reverse order (newest first)
            for hand in reversed(self.hand_history):
                self.history_text.insert(tk.END, f"Hand #{hand['hand_number']}: {hand['result_text']}\n")
                self.history_text.insert(tk.END, "Cards: ")
                self.history_text.insert(tk.END, ", ".join(hand['cards']))
                self.history_text.insert(tk.END, "\n")
                self.history_text.insert(tk.END, "-"*30 + "\n")
        elif not self.current_hand_cards:
            self.history_text.insert(tk.END, "No cards yet.")
        
        # Scroll to the beginning to show the most recent card
        self.history_text.see("1.0")
        
        # Disable editing
        self.history_text.config(state=tk.DISABLED)
    
    def add_to_history(self, text):
        # Enable text widget for editing
        self.history_text.config(state=tk.NORMAL)
        
        # Add text at the beginning with a separator
        self.history_text.insert(1.0, f"{text}\n{'-'*30}\n")
        
        # Scroll to the beginning
        self.history_text.see(1.0)
        
        # Scroll to the beginning to show the most recent card
        self.history_text.see("1.0")
        
        # Disable editing
        self.history_text.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = BlackjackCounterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()