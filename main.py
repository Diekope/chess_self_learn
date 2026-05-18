import sys
import chess
import chess.engine
import chess.svg
import random
import math
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox, 
                             QMessageBox, QStackedWidget, QCheckBox, QFrame,
                             QTextEdit, QDialog, QRadioButton, QButtonGroup)
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint, QSize, QByteArray, QRectF, QPointF, QUrl
from PyQt6.QtGui import QPainter, QColor, QBrush, QFont, QPen, QPolygonF, QKeySequence, QShortcut
from PyQt6.QtSvg import QSvgRenderer

# Audio support
try:
    from PyQt6.QtMultimedia import QSoundEffect
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False

# Mapping of Stockfish Levels
STOCKFISH_LEVELS = [
    {"label": "Lvl 0 (~200 ELO)", "skill": 0, "depth": 1, "nodes": 100},
    {"label": "Lvl 1 (~400 ELO)", "skill": 0, "depth": 1, "nodes": 500},
    {"label": "Lvl 2 (~600 ELO)", "skill": 0, "depth": 2, "nodes": None},
    {"label": "Lvl 3 (~800 ELO)", "skill": 2, "depth": 3, "nodes": None},
    {"label": "Lvl 4 (~1000 ELO)", "skill": 4, "depth": 4, "nodes": None},
    {"label": "Lvl 5 (~1200 ELO)", "skill": 6, "depth": 5, "nodes": None},
    {"label": "Lvl 6 (~1400 ELO)", "skill": 8, "depth": 6, "nodes": None},
    {"label": "Lvl 7 (~1600 ELO)", "skill": 10, "depth": 8, "nodes": None},
    {"label": "Lvl 8 (~1800 ELO)", "skill": 12, "depth": 10, "nodes": None},
    {"label": "Lvl 9 (~2000 ELO)", "skill": 14, "depth": 12, "nodes": None},
    {"label": "Lvl 10 (~2200 ELO)", "skill": 16, "depth": 14, "nodes": None},
    {"label": "Lvl 11 (~2500 ELO)", "skill": 18, "depth": 16, "nodes": None},
    {"label": "Lvl 12 (Max ~3000+)", "skill": 20, "depth": 20, "nodes": None},
]

PIECE_VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
PIECE_UNICODE = {
    (chess.WHITE, chess.PAWN): "♙", (chess.WHITE, chess.KNIGHT): "♘", (chess.WHITE, chess.BISHOP): "♗", (chess.WHITE, chess.ROOK): "♖", (chess.WHITE, chess.QUEEN): "♕",
    (chess.BLACK, chess.PAWN): "♟", (chess.BLACK, chess.KNIGHT): "♞", (chess.BLACK, chess.BISHOP): "♝", (chess.BLACK, chess.ROOK): "♜", (chess.BLACK, chess.QUEEN): "♛",
}
QUALITY_DATA = {
    "Brilliant": {"color": "#1baca6", "symbol": "!!", "points": 120, "text": "Brillant ! Une trouvaille tactique exceptionnelle."},
    "Great": {"color": "#1baca6", "symbol": "!!", "points": 100, "text": "Excellent coup !"},
    "Best": {"color": "#96bc4b", "symbol": "★", "points": 100, "text": "Le meilleur choix selon Stockfish."},
    "Good": {"color": "#96bc4b", "symbol": "✓", "points": 80, "text": "Bon coup solide."},
    "Inaccuracy": {"color": "#f0c15c", "symbol": "?!", "points": 50, "text": "Imprécision stratégique."},
    "Mistake": {"color": "#e6912c", "symbol": "?", "points": 20, "text": "Erreur tactique, tu perds l'avantage."},
    "Blunder": {"color": "#b33430", "symbol": "??", "points": 0, "text": "Gaffe majeure ! Le meilleur coup était crucial ici."}
}

THEMES = {
    "Classic": {"dark": "#779556", "light": "#ebecd0"},
    "Wood": {"dark": "#b58863", "light": "#f0d9b5"},
    "Blue": {"dark": "#8ca2ad", "light": "#dee3e6"},
    "Dark": {"dark": "#4b7399", "light": "#eae9d2"}
}

# Rich opening database with Opening and Defense/Variation
COMMON_OPENINGS = {
    "e2e4": "Ouverture du Pion Roi",
    "e2e4 e7e5": "Partie Ouverte",
    "e2e4 e7e5 g1f3": "Ouverture du Cavalier Roi",
    "e2e4 e7e5 g1f3 b8c6 f1b5": "Partie Espagnole (Ruy Lopez)",
    "e2e4 e7e5 g1f3 b8c6 f1c4": "Partie Italienne",
    "e2e4 e7e5 g1f3 b8c6 d2d4": "Partie Écossaise",
    "e2e4 e7e5 f2f4": "Gambit du Roi",
    "e2e4 c7c5": "Défense Sicilienne",
    "e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b8c6 a7a6": "Défense Sicilienne : Variante Najdorf",
    "e2e4 c7c5 g1f3 e7e6 d2d4 c5d4 f3d4 a7a6": "Défense Sicilienne : Variante Kan",
    "e2e4 c7c5 g1f3 b8c6 d2d4 c5d4 f3d4 g8f6 b8c3 e7e5": "Défense Sicilienne : Variante Svechnikov",
    "e2e4 c7c6": "Défense Caro-Kann",
    "e2e4 e7e6": "Défense Française",
    "e2e4 d7d5": "Défense Scandinave",
    "e2e4 g7g6": "Défense Moderne",
    "d2d4": "Ouverture du Pion Dame",
    "d2d4 d7d5": "Partie Fermée",
    "d2d4 d7d5 c2c4": "Gambit de la Dame",
    "d2d4 d7d5 c2c4 e7e6": "Gambit de la Dame Refusé",
    "d2d4 d7d5 c2c4 c7c6": "Défense Slave",
    "d2d4 g8f6": "Défense Indienne",
    "d2d4 g8f6 c2c4 e7e6 g1f3 b7b6": "Défense Ouest-Indienne",
    "d2d4 g8f6 c2c4 g7g6 b8c3 f8g7 e2e4 d7d6": "Défense Est-Indienne",
    "d2d4 g8f6 c2c4 c5 d5": "Défense Benoni",
    "c2c4": "Ouverture Anglaise",
    "g1f3": "Début Réti",
    "f2f4": "Ouverture Bird",
    "b2b3": "Ouverture Larsen",
}

class PromotionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("Promotion"); self.setModal(True)
        layout = QVBoxLayout(self); self.group = QButtonGroup(self)
        options = [("Dame", chess.QUEEN), ("Tour", chess.ROOK), ("Fou", chess.BISHOP), ("Cavalier", chess.KNIGHT)]
        for text, pt in options:
            radio = QRadioButton(text); layout.addWidget(radio); self.group.addButton(radio, pt)
            if pt == chess.QUEEN: radio.setChecked(True)
        btn = QPushButton("Valider"); btn.clicked.connect(self.accept); layout.addWidget(btn)
    def selected_piece(self): return self.group.checkedId()

class EngineThread(QThread):
    move_ready = pyqtSignal(str); score_ready = pyqtSignal(int); eval_ready = pyqtSignal(int, str); error_occurred = pyqtSignal(str)
    def __init__(self, fen, level_config, stockfish_path, task="play"):
        super().__init__(); self.fen = fen; self.config = level_config; self.stockfish_path = stockfish_path; self.task = task
    def run(self):
        try:
            board = chess.Board(self.fen)
            with chess.engine.SimpleEngine.popen_uci(self.stockfish_path) as engine:
                engine.configure({"Skill Level": self.config["skill"]})
                if self.task == "score":
                    info = engine.analyse(board, chess.engine.Limit(depth=10))
                    self.score_ready.emit(info["score"].white().score(mate_score=10000))
                elif self.task == "evaluate":
                    info = engine.analyse(board, chess.engine.Limit(depth=14))
                    score = info["score"].white().score(mate_score=10000)
                    best_move = info["pv"][0].uci() if "pv" in info and info["pv"] else None
                    self.eval_ready.emit(score, best_move)
                else:
                    limit = chess.engine.Limit(depth=self.config["depth"])
                    if self.config.get("nodes"): limit.nodes = self.config["nodes"]
                    self.move_ready.emit(engine.play(board, limit).move.uci())
        except Exception as e: self.error_occurred.emit(str(e))

class InteractiveBoardWidget(QSvgWidget):
    move_requested = pyqtSignal(chess.Move); interaction_started = pyqtSignal()
    def __init__(self, board, orientation=chess.WHITE):
        super().__init__(); self.board = board; self.orientation = orientation
        self.selected_square = None; self.dragging_square = None; self.right_click_start_square = None
        self.mouse_pos = QPoint(); self.best_move_arrow = None; self.user_arrows = []
        self.current_right_drag_arrow = None; self.last_move_quality = None; self.premove = None
        self.colors = THEMES["Classic"]
        self.square_size = 600 / 8; self.setFixedSize(600, 600); self.setMouseTracking(True); self.piece_renderer = QSvgRenderer(); self.update_board()
    def set_theme(self, theme_name): self.colors = THEMES.get(theme_name, THEMES["Classic"]); self.update_board()
    def set_orientation(self, orientation): self.orientation = orientation; self.update_board()
    def clear_premove(self): self.premove = None; self.update_board()
    def update_board(self, selected_square=None):
        self.selected_square = selected_square; fill = {}
        if self.board.move_stack:
            last = self.board.peek(); fill[last.from_square] = "#f5f682cc"; fill[last.to_square] = "#f5f682cc"
        if self.selected_square is not None: fill[self.selected_square] = "#769656cc"
        if self.dragging_square is not None:
            temp = self.board.copy(); piece = temp.remove_piece_at(self.dragging_square)
            if piece: self.piece_renderer.load(QByteArray(chess.svg.piece(piece, size=int(self.square_size)).encode("utf-8")))
            svg = chess.svg.board(temp, orientation=self.orientation, fill=fill, lastmove=None, colors={"square light": self.colors["light"], "square dark": self.colors["dark"]}).encode("utf-8")
        else: svg = chess.svg.board(self.board, orientation=self.orientation, fill=fill, lastmove=None, colors={"square light": self.colors["light"], "square dark": self.colors["dark"]}).encode("utf-8")
        self.load(svg); self.update()
    def get_square_at(self, pos):
        f = int(pos.x() // self.square_size); r = 7 - int(pos.y() // self.square_size)
        if self.orientation == chess.BLACK: f = 7 - f; r = 7 - r
        return chess.square(f, r) if 0 <= f <= 7 and 0 <= r <= 7 else None
    def mousePressEvent(self, event):
        square = self.get_square_at(event.position().toPoint())
        if square is None: return
        if event.button() == Qt.MouseButton.LeftButton:
            self.interaction_started.emit()
            self.user_arrows = []; self.current_right_drag_arrow = None; self.best_move_arrow = None; self.last_move_quality = None
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.dragging_square = square; self.selected_square = square; self.mouse_pos = event.position().toPoint(); self.update_board(square)
            else:
                if self.selected_square is not None: self.attempt_move(self.selected_square, square)
                else: self.update_board(None)
        elif event.button() == Qt.MouseButton.RightButton: self.right_click_start_square = square
    def mouseMoveEvent(self, event):
        self.mouse_pos = event.position().toPoint()
        if self.dragging_square is not None: self.update()
        if event.buttons() & Qt.MouseButton.RightButton:
            end = self.get_square_at(self.mouse_pos)
            self.current_right_drag_arrow = (self.right_click_start_square, end) if end and end != self.right_click_start_square else None
            self.update()
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.dragging_square is not None:
                release = self.get_square_at(event.position().toPoint())
                from_sq = self.dragging_square; self.dragging_square = None
                if release and release != from_sq: self.attempt_move(from_sq, release)
                else: self.update_board(self.selected_square)
        elif event.button() == Qt.MouseButton.RightButton:
            if self.current_right_drag_arrow:
                if self.current_right_drag_arrow in self.user_arrows: self.user_arrows.remove(self.current_right_drag_arrow)
                else: self.user_arrows.append(self.current_right_drag_arrow)
            self.current_right_drag_arrow = None; self.right_click_start_square = None; self.update()
    def attempt_move(self, from_sq, to_sq):
        move = chess.Move(from_sq, to_sq); piece = self.board.piece_at(from_sq)
        if piece and piece.piece_type == chess.PAWN:
            r = chess.square_rank(to_sq)
            if (piece.color == chess.WHITE and r == 7) or (piece.color == chess.BLACK and r == 0):
                diag = PromotionDialog(self)
                if diag.exec(): move.promotion = diag.selected_piece()
                else: self.update_board(None); return
        if move in self.board.legal_moves: self.move_requested.emit(move); self.update_board(None)
        else:
            p = self.board.piece_at(to_sq)
            if p and p.color == self.board.turn: self.selected_square = to_sq; self.update_board(to_sq)
            else: self.update_board(None)
    def paintEvent(self, event):
        super().paintEvent(event); painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        def draw_arrow(f_sq, t_sq, col):
            def get_c(sq):
                f = chess.square_file(sq); r = chess.square_rank(sq)
                if self.orientation == chess.BLACK: f = 7 - f; r = 7 - r
                return QPointF((f + 0.5) * self.square_size, (7 - r + 0.5) * self.square_size)
            s_p = get_c(f_sq); e_p = get_c(t_sq); pen = QPen(col, 5); pen.setCapStyle(Qt.PenCapStyle.RoundCap); painter.setPen(pen); painter.drawLine(s_p, e_p)
            ang = math.atan2(e_p.y() - s_p.y(), e_p.x() - s_p.x()); hs = 18; poly = QPolygonF([e_p, QPointF(e_p.x() - hs * math.cos(ang - math.pi / 6), e_p.y() - hs * math.sin(ang - math.pi / 6)), QPointF(e_p.x() - hs * math.cos(ang + math.pi / 6), e_p.y() - hs * math.sin(ang + math.pi / 6))])
            painter.setBrush(QBrush(col)); painter.setPen(Qt.PenStyle.NoPen); painter.drawPolygon(poly)
        if self.best_move_arrow: draw_arrow(self.best_move_arrow[0], self.best_move_arrow[1], QColor(50, 100, 255, 180))
        for arrow in self.user_arrows: draw_arrow(arrow[0], arrow[1], QColor(255, 165, 0, 180))
        if self.current_right_drag_arrow: draw_arrow(self.current_right_drag_arrow[0], self.current_right_drag_arrow[1], QColor(255, 165, 0, 100))
        if self.last_move_quality:
            sq, qtype = self.last_move_quality; f = chess.square_file(sq); r = chess.square_rank(sq)
            if self.orientation == chess.BLACK: f = 7 - f; r = 7 - r
            ix = f * self.square_size + 2; iy = (7 - r) * self.square_size + 2; isz = 22; dat = QUALITY_DATA[qtype]; painter.setBrush(QBrush(QColor(dat["color"]))); painter.setPen(Qt.PenStyle.NoPen); painter.drawEllipse(QRectF(ix, iy, isz, isz))
            painter.setPen(QPen(Qt.GlobalColor.white)); painter.setFont(QFont("Arial", 9, QFont.Weight.Black)); painter.drawText(QRectF(ix, iy, isz, isz), Qt.AlignmentFlag.AlignCenter, dat["symbol"])
        if self.dragging_square and self.piece_renderer.isValid():
            rect = QRectF(self.mouse_pos.x() - self.square_size/2, self.mouse_pos.y() - self.square_size/2, self.square_size, self.square_size)
            self.piece_renderer.render(painter, rect)
        painter.end()

class EvaluationBar(QFrame):
    def __init__(self): super().__init__(); self.setFixedWidth(20); self.score = 0; self.setStyleSheet("background-color: #403d39; border: 1px solid #3d3b38;")
    def set_score(self, s): self.score = max(min(s, 500), -500); self.update()
    def paintEvent(self, e):
        p = QPainter(self); h = self.height(); w = self.width(); pct = 0.5 + (self.score / 1000.0); sy = int(h * (1.0 - pct))
        p.fillRect(0, 0, w, sy, QColor("#121212")); p.fillRect(0, sy, w, h - sy, QColor("#ffffff"))

class ChessWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Chess AI - Ultimate Edition"); self.board = chess.Board(); self.stockfish_path = self.find_stockfish(); self.player_color = chess.WHITE; self.undos_remaining = float('inf'); self.difficulty = "Easy"; self.current_level_config = STOCKFISH_LEVELS[2]; self.game_active = False; self.engine_thinking = False; self.eval_mode = True; self.last_fen_before_human = None; self.real_board = None; self.review_index = -1
        self.move_history_data = []
        self.init_audio(); self.init_ui(); self.setup_shortcuts()
    def init_audio(self):
        self.sounds = {}
        if HAS_AUDIO:
            for s in ["move", "capture", "check", "gameover", "error"]:
                eff = QSoundEffect()
                path = os.path.join("assets", f"{s}.wav")
                if os.path.exists(path): eff.setSource(QUrl.fromLocalFile(os.path.abspath(path))); eff.setVolume(0.5); self.sounds[s] = eff
    def play_sound(self, name):
        if name in self.sounds: self.sounds[name].play()
    def find_stockfish(self):
        import shutil, os; path = shutil.which("stockfish")
        if not path:
            common = ["/opt/homebrew/bin/stockfish", "/usr/local/bin/stockfish"]
            for p in common:
                if os.path.exists(p): return p
        return path
    def setup_shortcuts(self):
        self.undo_shortcut = QShortcut(QKeySequence.StandardKey.Undo, self); self.undo_shortcut.activated.connect(self.trigger_review_back)
        self.esc_shortcut = QShortcut(QKeySequence("Esc"), self); self.esc_shortcut.activated.connect(self.exit_review_mode)
    def trigger_review_back(self):
        if not self.game_active: return
        if self.review_index == -1: self.real_board = self.board.copy(); self.review_index = len(self.real_board.move_stack)
        if self.review_index > 0:
            self.review_index -= 1; temp = chess.Board(); live = list(self.real_board.move_stack)
            for i in range(self.review_index): temp.push(live[i])
            self.board = temp; self.board_widget.board = self.board; self.board_widget.update_board(None); self.game_status_label.setText(f"MODE REVUE ({self.review_index})"); self.game_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #f0c15c;")
    def exit_review_mode(self):
        if self.review_index == -1: return
        self.board = self.real_board; self.board_widget.board = self.board; self.review_index = -1; self.board_widget.update_board(None); self.update_status_labels(); self.game_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
    def get_captured_pieces(self):
        full = {chess.WHITE: {chess.PAWN: 8, chess.KNIGHT: 2, chess.BISHOP: 2, chess.ROOK: 2, chess.QUEEN: 1}, chess.BLACK: {chess.PAWN: 8, chess.KNIGHT: 2, chess.BISHOP: 2, chess.ROOK: 2, chess.QUEEN: 1}}
        curr = {chess.WHITE: {}, chess.BLACK: {}}
        for col in [chess.WHITE, chess.BLACK]:
            for pt in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]: curr[col][pt] = len(self.board.pieces(pt, col))
        cap = {chess.WHITE: [], chess.BLACK: []}; sc = {chess.WHITE: 0, chess.BLACK: 0}
        for col in [chess.WHITE, chess.BLACK]:
            for pt in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
                diff = full[col][pt] - curr[col][pt]
                if diff > 0: cap[col].extend([pt] * diff); sc[col] += diff * PIECE_VALUES[pt]
        return cap, sc
    def update_material_ui(self):
        cap, sc = self.get_captured_pieces(); p_color = self.player_color; o_color = not p_color
        p_adv = sc[o_color] - sc[p_color]; o_adv = sc[p_color] - sc[o_color]
        top_pieces = "".join([PIECE_UNICODE[(p_color, pt)] for pt in cap[p_color]]); top_adv_str = f" +{o_adv}" if o_adv > 0 else ""
        self.top_material_label.setText(f"{top_pieces}<span style='color: #a04040; font-weight: bold;'>{top_adv_str}</span>")
        bot_pieces = "".join([PIECE_UNICODE[(o_color, pt)] for pt in cap[o_color]]); bot_adv_str = f" +{p_adv}" if p_adv > 0 else ""
        self.bottom_material_label.setText(f"{bot_pieces}<span style='color: #769656; font-weight: bold;'>{bot_adv_str}</span>")
    def update_move_list(self):
        moves = list(self.board.move_stack); temp = chess.Board(); text = ""
        for i in range(0, len(moves), 2):
            num = (i // 2) + 1; wm = temp.san(moves[i]); temp.push(moves[i]); bm = ""
            if i + 1 < len(moves): bm = temp.san(moves[i+1]); temp.push(moves[i+1])
            text += f"{num}. {wm} {bm}  "
            if num % 2 == 0: text += "\n"
        self.move_list_text.setPlainText(text); self.move_list_text.verticalScrollBar().setValue(self.move_list_text.verticalScrollBar().maximum())
    def detect_opening(self):
        moves_uci = " ".join([m.uci() for m in self.board.move_stack])
        best_match = ""
        for sequence, name in COMMON_OPENINGS.items():
            if moves_uci.startswith(sequence):
                if len(sequence) > len(best_match): best_match = sequence
        return COMMON_OPENINGS.get(best_match, "")
    def init_ui(self):
        central = QWidget(); central.setStyleSheet("background-color: #262421; color: #bababa;"); self.setCentralWidget(central); layout = QHBoxLayout(central); layout.setContentsMargins(30, 50, 30, 50); layout.setSpacing(20)
        self.eval_bar = EvaluationBar(); layout.addWidget(self.eval_bar)
        board_area = QVBoxLayout(); self.top_material_label = QLabel(""); self.top_material_label.setStyleSheet("font-size: 24px; color: #8a8885; margin-bottom: 5px;"); board_area.addWidget(self.top_material_label)
        self.board_widget = InteractiveBoardWidget(self.board); self.board_widget.move_requested.connect(self.handle_human_move); self.board_widget.interaction_started.connect(self.clear_coaching_display); board_area.addWidget(self.board_widget)
        self.bottom_material_label = QLabel(""); self.bottom_material_label.setStyleSheet("font-size: 24px; color: #8a8885; margin-top: 5px;"); board_area.addWidget(self.bottom_material_label); layout.addLayout(board_area)
        self.sidebar_stack = QStackedWidget(); self.sidebar_stack.setFixedWidth(350); layout.addWidget(self.sidebar_stack)
        cfg_w = QWidget(); cfg_l = QVBoxLayout(cfg_w); title = QLabel("CHESS AI"); title.setStyleSheet("font-size: 32px; font-weight: 900; color: white; margin-bottom: 20px;"); title.setAlignment(Qt.AlignmentFlag.AlignCenter); cfg_l.addWidget(title)
        def itm(lab, cmb): l = QLabel(lab.upper()); l.setStyleSheet("font-size: 11px; font-weight: bold; color: #8a8885; letter-spacing: 2px; margin-top: 10px;"); cfg_l.addWidget(l); cfg_l.addWidget(cmb)
        style = "padding: 10px; background: #3d3b38; border: none; border-radius: 5px; color: white;"
        self.side_combo = QComboBox(); self.side_combo.addItems(["Blancs", "Noirs"]); self.side_combo.setStyleSheet(style); itm("Ton Camp", self.side_combo)
        self.level_combo = QComboBox(); self.level_combo.addItems([l["label"] for l in STOCKFISH_LEVELS]); self.level_combo.setCurrentIndex(2); self.level_combo.setStyleSheet(style); itm("Force de l'IA (ELO)", self.level_combo)
        self.undo_combo = QComboBox(); self.undo_combo.addItems(["Facile", "Moyen", "Difficile"]); self.undo_combo.setStyleSheet(style); itm("Règles Undo", self.undo_combo)
        self.theme_combo = QComboBox(); self.theme_combo.addItems(list(THEMES.keys())); self.theme_combo.setStyleSheet(style); itm("Thème Visuel", self.theme_combo)
        self.eval_checkbox = QCheckBox("Mode Coaching (Analyse)"); self.eval_checkbox.setChecked(True); self.eval_checkbox.setStyleSheet("margin-top: 15px;"); cfg_l.addWidget(self.eval_checkbox)
        self.play_btn = QPushButton("JOUER"); self.play_btn.setFixedHeight(55); self.play_btn.setStyleSheet("background-color: #769656; color: white; font-weight: 900; border-radius: 10px; margin-top: 20px;"); self.play_btn.clicked.connect(self.start_game); cfg_l.addWidget(self.play_btn); cfg_l.addStretch(); self.sidebar_stack.addWidget(cfg_w)
        gm_w = QWidget(); gm_l = QVBoxLayout(gm_w); self.game_status_label = QLabel("Au tour des Blancs"); self.game_status_label.setStyleSheet("font-size: 22px; font-weight: bold; color: white; margin-bottom: 5px;"); self.game_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter); gm_l.addWidget(self.game_status_label)
        self.opening_label = QLabel(""); self.opening_label.setStyleSheet("font-size: 11px; color: #8a8885; font-weight: bold;"); self.opening_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.opening_label.setWordWrap(True); gm_l.addWidget(self.opening_label)
        self.coaching_frame = QFrame(); self.coaching_frame.setStyleSheet("background-color: #3d3b38; border-radius: 8px; margin: 10px 0;"); cf_l = QVBoxLayout(self.coaching_frame)
        self.coaching_label = QLabel(""); self.coaching_label.setStyleSheet("font-size: 15px; color: #769656; font-weight: bold; border: none;"); self.coaching_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.coaching_label.setWordWrap(True); cf_l.addWidget(self.coaching_label); gm_l.addWidget(self.coaching_frame)
        self.move_list_text = QTextEdit(); self.move_list_text.setReadOnly(True); self.move_list_text.setStyleSheet("background: #1e1e1e; border: 1px solid #3d3b38; color: #bababa; font-family: 'Menlo', 'Courier New', 'DejaVu Sans Mono', monospace;"); gm_l.addWidget(self.move_list_text)
        self.undo_info_label = QLabel("Retours: ∞"); self.undo_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.undo_info_label.setStyleSheet("color: #8a8885; margin-bottom: 20px;"); gm_l.addWidget(self.undo_info_label)
        self.game_undo_btn = QPushButton("RETOUR"); self.game_undo_btn.setFixedHeight(45); self.game_undo_btn.setStyleSheet("background-color: #3d3b38; color: white; font-weight: bold; border-radius: 5px;"); self.game_undo_btn.clicked.connect(self.undo_move); gm_l.addWidget(self.game_undo_btn)
        gm_l.addSpacing(10); self.draw_btn = QPushButton("OFFRIR NULLE"); self.draw_btn.setFixedHeight(45); self.draw_btn.setStyleSheet("background-color: #3d3b38; color: white; font-weight: bold; border-radius: 5px;"); self.draw_btn.clicked.connect(self.offer_draw); gm_l.addWidget(self.draw_btn)
        self.resign_btn = QPushButton("ABANDONNER"); self.resign_btn.setFixedHeight(45); self.resign_btn.setStyleSheet("background-color: #a04040; color: white; font-weight: bold; border-radius: 5px;"); self.resign_btn.clicked.connect(self.resign); gm_l.addWidget(self.resign_btn); gm_l.addStretch(); self.sidebar_stack.addWidget(gm_w)
    def start_game(self):
        if not self.stockfish_path: QMessageBox.critical(self, "Erreur", "Stockfish introuvable."); return
        self.board = chess.Board(); self.player_color = chess.WHITE if self.side_combo.currentText() == "Blancs" else chess.BLACK; self.board_widget.board = self.board; self.board_widget.set_orientation(self.player_color); self.board_widget.set_theme(self.theme_combo.currentText()); self.board_widget.best_move_arrow = None; self.board_widget.last_move_quality = None; self.last_fen_before_human = self.board.fen()
        diff = self.undo_combo.currentText(); self.difficulty = diff; self.undos_remaining = float('inf') if diff == "Facile" else (3 if diff == "Moyen" else 0)
        self.current_level_config = STOCKFISH_LEVELS[self.level_combo.currentIndex()]; self.eval_mode = self.eval_checkbox.isChecked(); self.game_active = True; self.engine_thinking = False; self.review_index = -1; self.move_history_data = []
        self.update_undo_button_state(); self.update_status_labels(); self.update_material_ui(); self.update_move_list(); self.eval_bar.set_score(0); self.sidebar_stack.setCurrentIndex(1); self.board_widget.update_board(None); self.coaching_label.setText(""); self.opening_label.setText(""); self.coaching_frame.setVisible(False)
        if self.player_color == chess.BLACK: self.ask_engine()
    def update_undo_button_state(self):
        can_undo = self.undos_remaining > 0 and not self.engine_thinking and len(self.board.move_stack) > 0
        self.game_undo_btn.setEnabled(can_undo); self.game_undo_btn.setVisible(self.difficulty != "Difficile"); undo_text = f"Retours: {'∞' if self.difficulty == 'Facile' else int(self.undos_remaining)}"; self.undo_info_label.setText(undo_text); self.undo_info_label.setVisible(self.difficulty != "Difficile")
    def update_status_labels(self):
        if self.board.is_game_over(): self.game_status_label.setText("Partie Terminée"); return
        turn = "Blancs" if self.board.turn == chess.WHITE else "Noirs"; status = f"Aux {turn} de jouer"
        if self.board.is_check(): status += " (Échec !)"
        self.game_status_label.setText(status); op = self.detect_opening()
        if op: self.opening_label.setText(op)
    def clear_coaching_display(self): self.coaching_label.setText(""); self.coaching_frame.setVisible(False)
    def handle_human_move(self, move):
        if self.engine_thinking or not self.game_active or self.review_index != -1: return
        self.exit_review_mode(); self.last_fen_before_human = self.board.fen()
        is_capture = self.board.is_capture(move)
        self.board.push(move); self.board_widget.update_board(None); self.update_status_labels(); self.update_undo_button_state(); self.update_material_ui(); self.update_move_list()
        if self.board.is_check(): self.play_sound("check")
        elif is_capture: self.play_sound("capture")
        else: self.play_sound("move")
        if self.eval_mode and not self.board.is_game_over(): self.evaluate_move_quality(move)
        elif not self.board.is_game_over(): self.ask_engine()
        else: self.check_game_over()
    def evaluate_move_quality(self, move):
        self.engine_thinking = True; self.game_status_label.setText("Analyse...")
        self.thread = EngineThread(self.last_fen_before_human, self.current_level_config, self.stockfish_path, task="evaluate")
        self.thread.eval_ready.connect(lambda s, bm: self.on_evaluation_complete(s, bm, move)); self.thread.start()
    def on_evaluation_complete(self, pb, bm, hm):
        self.score_thread = EngineThread(self.board.fen(), self.current_level_config, self.stockfish_path, task="score")
        self.score_thread.score_ready.connect(lambda cs: self.compare_and_play(pb, cs, bm, hm)); self.score_thread.start()
    def compare_and_play(self, pb, cs, bm, hm):
        self.eval_bar.set_score(cs); b = chess.Board(self.last_fen_before_human); turn = b.turn
        sl = (pb-cs) if turn==chess.WHITE else (cs-pb)
        q = "Good"
        if sl < 10: q = "Best"
        elif sl < 50: q = "Good"
        elif sl < 150: q = "Inaccuracy"
        elif sl < 300: q = "Mistake"
        else: q = "Blunder"
        if q in ["Inaccuracy", "Mistake", "Blunder"]: self.play_sound("error")
        self.board_widget.last_move_quality = (hm.to_square, q); self.move_history_data.append(q)
        if q in ["Inaccuracy", "Mistake", "Blunder"] and bm and hm.uci()!=bm:
            m = chess.Move.from_uci(bm); self.board_widget.best_move_arrow = (m.from_square, m.to_square)
        self.coaching_label.setText(QUALITY_DATA[q]["text"]); self.coaching_frame.setVisible(True)
        self.board_widget.update_board(None); self.engine_thinking=False; self.ask_engine()
    def ask_engine(self):
        if self.board.is_game_over(): return
        self.engine_thinking = True; self.game_status_label.setText("Réflexion...")
        self.thread = EngineThread(self.board.fen(), self.current_level_config, self.stockfish_path, task="play")
        self.thread.move_ready.connect(self.on_engine_move); self.thread.error_occurred.connect(self.on_engine_error); self.thread.start()
    def on_engine_move(self, uci):
        move = chess.Move.from_uci(uci); is_cap = self.board.is_capture(move)
        self.board.push(move); self.board_widget.update_board(None); self.engine_thinking=False; self.update_status_labels(); self.update_undo_button_state(); self.update_material_ui(); self.update_move_list()
        self.board_widget.last_move_quality = None
        if self.board.is_check(): self.play_sound("check")
        elif is_cap: self.play_sound("capture")
        else: self.play_sound("move")
        self.score_thread = EngineThread(self.board.fen(), self.current_level_config, self.stockfish_path, task="score"); self.score_thread.score_ready.connect(lambda s: self.eval_bar.set_score(s)); self.score_thread.start()
        self.check_game_over()
    def on_engine_error(self, e): self.engine_thinking=False; QMessageBox.warning(self, "Erreur", e); self.update_status_labels()
    def undo_move(self):
        if self.undos_remaining <= 0 or self.engine_thinking: return
        self.exit_review_mode(); self.board_widget.best_move_arrow=None; self.board_widget.last_move_quality=None
        if len(self.board.move_stack)>=2: self.board.pop(); self.board.pop()
        elif len(self.board.move_stack)==1: self.board.pop()
        if self.difficulty=="Moyen": self.undos_remaining-=1
        self.board_widget.update_board(None); self.update_status_labels(); self.update_undo_button_state(); self.update_material_ui(); self.update_move_list(); self.coaching_label.setText(""); self.coaching_frame.setVisible(False)
    def resign(self):
        if not self.game_active: return
        self.show_accuracy_report("Tu as abandonné.")
    def offer_draw(self):
        if self.engine_thinking or not self.game_active: return
        self.game_status_label.setText("Demande de nulle..."); self.score_thread = EngineThread(self.board.fen(), self.current_level_config, self.stockfish_path, task="score")
        self.score_thread.score_ready.connect(self.handle_draw_logic); self.score_thread.start()
    def handle_draw_logic(self, s):
        if -100<s<100 or (abs(s)<200 and random.random()<0.3): QMessageBox.information(self, "Nulle", "Acceptée !"); self.show_accuracy_report("Nulle.")
        else: QMessageBox.information(self, "Nulle", "Refusée."); self.update_status_labels()
    def check_game_over(self):
        if self.board.is_game_over():
            res = self.board.result(); msg = "Nulle"
            if res=="1-0": msg="Victoire des Blancs !"
            elif res=="0-1": msg="Victoire des Noirs !"
            self.play_sound("gameover"); self.show_accuracy_report(msg)
    def show_accuracy_report(self, title):
        if not self.move_history_data: self.end_game(); return
        counts = {k: self.move_history_data.count(k) for k in QUALITY_DATA.keys()}
        total_p = sum([counts[k] * QUALITY_DATA[k]["points"] for k in counts])
        max_p = len(self.move_history_data) * 100
        acc = (total_p / max_p * 100) if max_p > 0 else 0
        rep = f"<b>{title}</b><br><br><b>Précision : {acc:.1f}%</b><br><br>"
        for k, v in counts.items():
            if v > 0: rep += f"<span style='color:{QUALITY_DATA[k]['color']}'>{QUALITY_DATA[k]['symbol']} {k}: {v}</span><br>"
        QMessageBox.information(self, "Match Report", rep); self.end_game()
    def end_game(self):
        self.game_active=False; self.sidebar_stack.setCurrentIndex(0); self.board=chess.Board(); self.board_widget.board=self.board; self.board_widget.update_board(None); self.top_material_label.setText(""); self.bottom_material_label.setText(""); self.coaching_label.setText(""); self.move_list_text.clear(); self.coaching_frame.setVisible(False)

if __name__ == "__main__":
    app = QApplication(sys.argv); window = ChessWindow(); window.showMaximized(); sys.exit(app.exec())
