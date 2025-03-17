import cv2
import numpy as np
import pytesseract

class ScreenAnalyzer:
    def __init__(self):
        # Template matching configuration
        self.templates = self._load_templates()
        self.match_threshold = 0.82
        self.min_contour_area = 600
        self.max_contour_area = 18000
        
        # Card tracking
        self.last_detected_cards = set()
        self.min_confidence = 0.8
        
        # Debug settings
        self.debug_mode = True

    def _load_templates(self):
        # Load card symbol templates
        templates = {}
        symbols = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        
        for symbol in symbols:
            path = f'card_templates/{symbol}.png'
            template = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if template is not None:
                templates[symbol] = cv2.Canny(template, 50, 200)
        
        return templates
    
    def detect_cards(self, image):
        """
        Rileva le carte visibili nell'immagine usando template matching
        Restituisce una lista di carte rilevate (es. ['A', 'K', '10'])
        """
        detected_cards = set()
        debug_image = image.copy() if self.debug_mode else None

        # Advanced preprocessing pipeline
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(blurred)

        # Add adaptive thresholding
        adaptive_thresh = cv2.adaptiveThreshold(enhanced, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Combine edges with threshold
        edges = cv2.bitwise_or(
            cv2.Canny(enhanced, 50, 200),
            cv2.Canny(adaptive_thresh, 50, 200)
        )

        # Find contours using preprocessed image
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process detected contours
        for contour in contours:
                # Filtra i contorni in base all'area (per escludere elementi troppo piccoli o troppo grandi)
                area = cv2.contourArea(contour)
                if self.min_contour_area < area < self.max_contour_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Validate aspect ratio
                    aspect_ratio = w / h
                    if 0.55 < aspect_ratio < 1.45:
                        card_roi = edges[y:y+h, x:x+w]
                        
                        best_match = None
                        max_confidence = 0
                        
                        # Perform template matching
                        for symbol, template in self.templates.items():
                            resized = cv2.resize(card_roi, (template.shape[1], template.shape[0]))
                            result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
                            _, confidence, _, _ = cv2.minMaxLoc(result)
                            
                            if confidence > self.min_confidence and confidence > max_confidence:
                                max_confidence = confidence
                                best_match = symbol
                        
                        if best_match and max_confidence >= self.match_threshold:
                            detected_cards.add(best_match)
                            
                            if self.debug_mode and debug_image is not None:
                                cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                                cv2.putText(debug_image, f"{best_match} ({max_confidence:.2f})", (x, y-10), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Mostra l'immagine di debug
        if self.debug_mode and debug_image is not None:
            cv2.imshow("Card Detection Debug", debug_image)
        
        # Trova le nuove carte (quelle non presenti nell'ultimo frame)
        new_cards = detected_cards - self.last_detected_cards
        
        # Aggiorna le carte rilevate
        self.last_detected_cards = detected_cards
        
        return list(new_cards)