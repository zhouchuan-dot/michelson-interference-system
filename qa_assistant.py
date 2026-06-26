import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QGroupBox,
    QListWidget, QMessageBox, QFileDialog, QComboBox
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor, QDesktopServices  # ✅ 正确位置

class QAHelper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_questions()
        self.setWindowTitle("Michelson Interference Experiment - Smart Q&A Assistant")
        self.resize(1000, 700)
        
    def initUI(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Michelson Interference Experiment - Smart Q&A Assistant")
        title_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #2c3e50;
            padding: 15px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                        stop:0 #1a2980, stop:1 #26d0ce);
            border-radius: 10px;
            color: white;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left side: FAQ list
        faq_group = QGroupBox("📚 FAQ Library")
        faq_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 16px;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #3498db;
                color: white;
                border-radius: 4px;
            }
        """)
        faq_layout = QVBoxLayout()
        self.faq_list = QListWidget()
        self.faq_list.setStyleSheet("""
            font-size: 14px; 
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 5px;
        """)
        self.faq_list.itemClicked.connect(self.show_answer)
        faq_layout.addWidget(self.faq_list)
        
        # 手动选择 + 智能诊断 模块
        img_group = QGroupBox("📷 Fringe Intelligent Diagnosis")
        img_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 16px;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #2ecc71;
                color: white;
                border-radius: 4px;
            }
        """)
        img_layout = QVBoxLayout()
        
        # 图片显示
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: #f0f0f0;
            border: 2px dashed #ccc;
            border-radius: 5px;
            min-height: 150px;
        """)
        self.image_label.setText("Upload your interference fringe image")
        self.image_label.setFont(QFont("Arial", 12))
        
        # 上传按钮
        self.upload_btn = QPushButton("Upload Image")
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.upload_btn.clicked.connect(self.upload_image)

        # 条纹类型选择
        self.fringe_combo = QComboBox()
        self.fringe_combo.addItems([
            "Please select fringe type",
            "Perfect circular fringes",
            "Elliptical fringes",
            "Straight fringes",
            "Curved fringes",
            "Blurry / shaking fringes",
            "Too dense fringes"
        ])
        self.fringe_combo.setStyleSheet("font-size:14px; padding:6px;")

        # 诊断按钮
        self.analyze_btn = QPushButton("Start Diagnosis")
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                padding: 8px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        self.analyze_btn.clicked.connect(self.analyze_fringes)
        
        # 打开豆包主页按钮
        self.doubao_btn = QPushButton("Open Doubao Home")
        self.doubao_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 8px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.doubao_btn.clicked.connect(self.open_doubao_home)
        
        # 布局
        img_layout.addWidget(self.image_label)
        img_layout.addWidget(self.upload_btn)
        img_layout.addWidget(self.fringe_combo)
        img_layout.addWidget(self.analyze_btn)
        img_layout.addWidget(self.doubao_btn)
        img_group.setLayout(img_layout)
        
        faq_layout.addWidget(img_group)
        faq_group.setLayout(faq_layout)
        
        # Right side: Q&A area
        qa_group = QGroupBox("💡 Smart Q&A")
        qa_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 16px;
                border: 2px solid #9b59b6;
                border-radius: 8px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #9b59b6;
                color: white;
                border-radius: 4px;
            }
        """)
        qa_layout = QVBoxLayout()
        
        # Input area
        input_layout = QHBoxLayout()
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Enter your question about the Michelson interference experiment...")
        self.question_input.setStyleSheet("""
            font-size: 14px; 
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
        """)
        input_layout.addWidget(self.question_input, 5)
        
        self.ask_button = QPushButton("Ask")
        self.ask_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.ask_button.clicked.connect(self.answer_question)
        input_layout.addWidget(self.ask_button, 1)
        qa_layout.addLayout(input_layout)
        
        # Answer display area
        self.answer_display = QTextEdit()
        self.answer_display.setReadOnly(True)
        self.answer_display.setStyleSheet("""
            font-size: 14px; 
            padding: 15px; 
            background-color: #f9f9f9; 
            border: 2px solid #ddd;
            border-radius: 5px;
        """)
        qa_layout.addWidget(self.answer_display)
        
        # Example questions
        example_group = QGroupBox("💡 Example Questions")
        example_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 14px;
                border: 1px solid #f39c12;
                border-radius: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                background-color: #f39c12;
                color: white;
                border-radius: 3px;
            }
        """)
        example_layout = QVBoxLayout()
        examples = [
            "What is the working principle of a Michelson interferometer?",
            "How to adjust the interferometer to see clear fringes?",
            "What is the relationship between fringe movement and optical path difference?",
            "What are equal inclination fringes and equal thickness fringes?",
            "How to calculate the optical path change corresponding to fringe movement?",
            "Why are my fringes curved instead of circular?",
            "What if the fringes are too dense to see clearly?",
            "How to measure the wavelength of a laser?"
        ]
        for example in examples:
            example_label = QLabel(f"• {example}")
            example_label.setStyleSheet("font-size: 13px; color: #7f8c8d; padding: 2px;")
            example_layout.addWidget(example_label)
        
        example_group.setLayout(example_layout)
        qa_layout.addWidget(example_group)
        
        qa_group.setLayout(qa_layout)
        
        content_layout.addWidget(faq_group, 1)
        content_layout.addWidget(qa_group, 2)
        main_layout.addLayout(content_layout, 1)
        
        # Bottom info
        info_label = QLabel("Tip: Upload image → select fringe type → get intelligent diagnosis.")
        info_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 10px; background: #f0f0f0; border-radius: 5px;")
        info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(info_label)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.current_image_path = ""

    # 打开豆包主页
    def open_doubao_home(self):
        QDesktopServices.openUrl(QUrl("https://www.doubao.com"))

    def load_questions(self):
        self.questions = {
            "What is the working principle of a Michelson interferometer?": 
                "<b>Principle Overview:</b><br>"
                "The Michelson interferometer uses a beam splitter to divide a beam of light into two beams, which travel different paths and then recombine to produce interference. The interference pattern depends on the optical path difference between the two beams.<br><br>"
                "<b>Key Components:</b><br>"
                "1. Light source<br>"
                "2. Beam splitter<br>"
                "3. Fixed mirror (M1) and movable mirror (M2)<br>"
                "4. Observation screen<br><br>"
                "Bright fringe: ΔL = mλ<br>"
                "Dark fringe: ΔL = (m+1/2)λ",
            
            "What determines the shape of interference fringes?":
                "<b>Analysis of Fringe Shapes:</b><br>"
                "• Circular fringes: Equal inclination interference (M1⊥M2)<br>"
                "• Straight fringes: Equal thickness interference (air wedge)<br>"
                "• Elliptical fringes: Two arms not perpendicular<br>"
                "• Curved fringes: Mirror surface defects<br>"
                "• Blurry fringes: Vibration or misalignment",
            
            "How to adjust a Michelson interferometer?":
                "<b>Adjustment Steps:</b><br>"
                "1. Adjust laser to horizontal<br>"
                "2. Make two reflected spots coincide<br>"
                "3. Fine-tune mirror screws<br>"
                "4. Observe until clear fringes appear<br><br>"
                "<b>Common fixes:</b><br>"
                "• No fringes: Check optical path<br>"
                "• Blurry: Reduce vibration<br>"
                "• Too dense: Reduce mirror angle",
            
            "What is the relationship between fringe movement and optical path difference change?":
                "<b>Formula:</b><br>"
                "ΔL = N × λ/2<br><br>"
                "ΔL: Optical path change<br>"
                "N: Number of moved fringes<br>"
                "λ: Light wavelength<br><br>"
                "Each fringe moves → path changes λ/2",
            
            "What are equal inclination fringes and equal thickness fringes?":
                "<b>Equal inclination:</b> Circular fringes, M1⊥M2<br>"
                "<b>Equal thickness:</b> Straight fringes, small angle between mirrors",
            
            "How to count fringe movement during an experiment?":
                "1. Select center as reference<br>"
                "2. Move mirror slowly<br>"
                "3. Count fringes passing the center<br>"
                "4. Record N for calculation",
            
            "What are some practical applications of the Michelson interferometer?":
                "• Length measurement (nm level)<br>"
                "• Refractive index measurement<br>"
                "• Surface flatness test<br>"
                "• Gravitational wave detection (LIGO)",
            
            "Why are my interference fringes curved?":
                "• Mirrors not perpendicular<br>"
                "• Mirror surface defects<br>"
                "• Beam not incident vertically",
            
            "What if the fringes are too dense to see clearly?":
                "• Reduce angle between mirrors<br>"
                "• Make M1 closer to perpendicular with M2<br>"
                "• Increase observation distance"
        }
        
        self.faq_list.clear()
        for question in self.questions:
            self.faq_list.addItem(question)
    
    def show_answer(self, item):
        question = item.text()
        self.answer_display.setText(f"<h3 style='color:#2c3e50;'>{question}</h3><hr><p>{self.questions.get(question, 'Answer not found')}</p>")
    
    def answer_question(self):
        question = self.question_input.text()
        if not question:
            QMessageBox.warning(self, "Input Error", "Please enter your question")
            return
        
        answer = ""
        if "principle" in question.lower() or "work" in question.lower():
            answer = self.questions["What is the working principle of a Michelson interferometer?"]
        elif "shape" in question.lower() or "fringe" in question.lower():
            answer = self.questions["What determines the shape of interference fringes?"]
        elif "adjust" in question.lower() or "set up" in question.lower():
            answer = self.questions["How to adjust a Michelson interferometer?"]
        elif "movement" in question.lower() or "change" in question.lower():
            answer = self.questions["What is the relationship between fringe movement and optical path difference change?"]
        elif "equal inclination" in question.lower() or "equal thickness" in question.lower():
            answer = self.questions["What are equal inclination fringes and equal thickness fringes?"]
        elif "count" in question.lower():
            answer = self.questions["How to count fringe movement during an experiment?"]
        elif "application" in question.lower() or "use" in question.lower():
            answer = self.questions["What are some practical applications of the Michelson interferometer?"]
        elif "curved" in question.lower():
            answer = self.questions["Why are my interference fringes curved?"]
        elif "dense" in question.lower():
            answer = self.questions["What if the fringes are too dense to see clearly?"]
        else:
            answer = "Please ask a specific question about Michelson interference."
        
        self.answer_display.setText(f"<h3 style='color:#2c3e50;'>Question: {question}</h3><hr><p>{answer}</p>")
        self.question_input.clear()
    
    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.current_image_path = file_path
            pixmap = QPixmap(file_path)
            scaled = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)
            self.image_label.setText("")

    def analyze_fringes(self):
        select = self.fringe_combo.currentText()

        if select == "Please select fringe type":
            QMessageBox.warning(self, "Tip", "Please select fringe type first!")
            return

        diag = {
            "Perfect circular fringes": {
                "color": "#27ae60",
                "title": "Perfect Circular Fringes",
                "reason": "Equal inclination interference, M1 and M2 are strictly perpendicular, ideal state.",
                "suggest": [
                    "Current status is excellent",
                    "You can start measuring wavelength",
                    "Slowly move M2 to observe fringe changes",
                    "Count N to calculate optical path difference"
                ]
            },
            "Elliptical fringes": {
                "color": "#8e44ad",
                "title": "Elliptical Fringes",
                "reason": "M1 and M2 are not completely perpendicular, two arms have slight angle.",
                "suggest": [
                    "Fine-tune the mirror adjustment screws",
                    "Make M1 and M2 gradually perpendicular",
                    "Observe until fringes become circular"
                ]
            },
            "Straight fringes": {
                "color": "#3498db",
                "title": "Straight Equal Thickness Fringes",
                "reason": "Air wedge formed between mirrors, typical equal thickness interference.",
                "suggest": [
                    "If you want circles: adjust mirror to be perpendicular",
                    "If you want straight fringes: keep current state",
                    "Can be used to measure film thickness"
                ]
            },
            "Curved fringes": {
                "color": "#f39c12",
                "title": "Curved Fringes",
                "reason": "Mirror surface is not flat, or optical elements have defects.",
                "suggest": [
                    "Check if mirrors are clean",
                    "Check for surface damage",
                    "Slightly adjust angle to reduce distortion"
                ]
            },
            "Blurry / shaking fringes": {
                "color": "#e74c3c",
                "title": "Blurry / Unstable Fringes",
                "reason": "Environmental vibration, table shaking, or unstable light source.",
                "suggest": [
                    "Reduce table vibration",
                    "Check device fixing",
                    "Wait for light source to stabilize",
                    "Keep indoor quiet"
                ]
            },
            "Too dense fringes": {
                "color": "#7f8c8d",
                "title": "Too Dense Fringes",
                "reason": "Angle between M1 and M2 is too large, or optical path difference is too big.",
                "suggest": [
                    "Adjust mirror to reduce angle",
                    "Make M1 closer to perpendicular with M2",
                    "Increase observation distance"
                ]
            }
        }

        res = diag[select]
        html = f"""
        <div style='border:3px solid {res['color']}; border-radius:10px; padding:20px;'>
        <h2 style='color:{res['color']};'>📊 Fringe Diagnosis Report</h2>
        <hr>
        <p><b>Current Type:</b> {res['title']}</p>
        <p><b>Physical Reason:</b> {res['reason']}</p>
        <p><b>✅ Adjustment Suggestions:</b></p>
        <ul>
        """
        for s in res["suggest"]:
            html += f"<li>{s}</li>"
        html += "</ul></div>"
        self.answer_display.setHtml(html)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 245, 249))
    palette.setColor(QPalette.WindowText, QColor(44, 62, 80))
    app.setPalette(palette)
    
    window = QAHelper()
    window.show()
    sys.exit(app.exec_())