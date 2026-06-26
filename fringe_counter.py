import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QFileDialog, QMessageBox,
    QProgressBar, QSlider, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import cv2

class VideoProcessor(QThread):
    progress_updated = pyqtSignal(int)
    processing_finished = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    frame_processed = pyqtSignal(object, object)

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        try:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                self.error_occurred.emit("Cannot open video file")
                return

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frames = []
            frame_count = 0

            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    break

                original_frame = frame.copy()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frames.append(gray)
                
                self.frame_processed.emit(original_frame, gray)
                
                frame_count += 1
                progress = int((frame_count / total_frames) * 100)
                self.progress_updated.emit(progress)

                QThread.msleep(10)

            cap.release()
            if self.is_running:
                self.processing_finished.emit(frames)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class FringeAnalyzer:
    def __init__(self):
        self.prev_intensity = 0
        self.movement_direction = 0
        
    def enhance_fringes(self, frame, contrast_factor=1.0, noise_reduction=True):
        """Enhance fringe visibility"""
        enhanced = frame.copy()
        
        # 1. Noise reduction
        if noise_reduction:
            enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
            enhanced = cv2.medianBlur(enhanced, 3)
        
        # 2. Contrast enhancement
        enhanced = cv2.convertScaleAbs(enhanced, alpha=contrast_factor, beta=0)
        
        # 3. Adaptive histogram equalization
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(enhanced)
        
        # 4. Edge enhancement
        laplacian = cv2.Laplacian(enhanced, cv2.CV_64F)
        enhanced = cv2.convertScaleAbs(laplacian)
        
        return enhanced
    
    def count_fringes_advanced(self, frame):
        """Improved fringe counting algorithm"""
        results = {}
        
        # Multiple counting methods
        results['projection'] = self.projection_analysis(frame)
        results['contour'] = self.contour_analysis(frame)
        results['fft'] = self.fft_analysis(frame)
        
        # Combine results
        final_count = self.combine_results(results)
        return final_count
    
    def projection_analysis(self, frame):
        """Projection analysis of fringes"""
        # Horizontal projection
        horizontal_proj = np.mean(frame, axis=0)
        
        # Simple smoothing
        kernel = np.ones(5) / 5
        smoothed_proj = np.convolve(horizontal_proj, kernel, mode='same')
        
        # Find extreme points
        peaks = self.find_peaks_simple(smoothed_proj)
        valleys = self.find_valleys_simple(smoothed_proj)
        
        # Calculate fringe count
        fringe_points = sorted(peaks + valleys)
        if len(fringe_points) < 2:
            return 0
            
        return len(fringe_points) / 2
    
    def contour_analysis(self, frame):
        """Contour analysis of fringes"""
        try:
            # Apply adaptive threshold
            binary = cv2.adaptiveThreshold(
                frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to enhance fringes
            kernel = np.ones((3, 1), np.uint8)  # Vertical kernel
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours
            min_contour_length = frame.shape[1] * 0.6
            long_contours = [cnt for cnt in contours if cv2.arcLength(cnt, False) > min_contour_length]
            
            return len(long_contours)
            
        except Exception as e:
            print(f"Contour analysis error: {e}")
            return 0
    
    def fft_analysis(self, frame):
        """FFT frequency analysis"""
        try:
            # Select center region
            h, w = frame.shape
            roi = frame[h//4:3*h//4, w//4:3*w//4]
            
            # Apply FFT
            fft_data = np.fft.fft2(roi)
            fft_shift = np.fft.fftshift(fft_data)
            magnitude_spectrum = 20 * np.log(np.abs(fft_shift) + 1)
            
            # Analyze horizontal frequency
            center_y = magnitude_spectrum.shape[0] // 2
            horizontal_profile = magnitude_spectrum[center_y, :]
            
            # Find frequency peaks
            peaks = self.find_peaks_simple(horizontal_profile)
            
            if len(peaks) > 1:
                peak_distances = np.diff(peaks)
                avg_distance = np.mean(peak_distances)
                fringe_count = w / avg_distance if avg_distance > 0 else 0
                return int(round(fringe_count))
            
            return 0
            
        except Exception as e:
            print(f"FFT analysis error: {e}")
            return 0
    
    def find_peaks_simple(self, signal):
        """Simple peak detection"""
        peaks = []
        for i in range(2, len(signal)-2):
            if (signal[i] > signal[i-1] and signal[i] > signal[i-2] and
                signal[i] > signal[i+1] and signal[i] > signal[i+2] and
                signal[i] > np.mean(signal) + np.std(signal)*0.5):
                peaks.append(i)
        return peaks
    
    def find_valleys_simple(self, signal):
        """Simple valley detection"""
        valleys = []
        for i in range(2, len(signal)-2):
            if (signal[i] < signal[i-1] and signal[i] < signal[i-2] and
                signal[i] < signal[i+1] and signal[i] < signal[i+2] and
                signal[i] < np.mean(signal) - np.std(signal)*0.5):
                valleys.append(i)
        return valleys
    
    def combine_results(self, results):
        """Combine results from multiple methods"""
        counts = [result for result in results.values() if result > 0]
        
        if not counts:
            return 0
        
        # Use median to reduce outlier influence
        return int(np.median(counts))

class FringeCounter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("Michelson Interference Experiment - High-Precision Fringe Counting System")
        self.resize(1200, 800)
        
    def initUI(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Michelson Interference Fringe Counting System")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Video control area
        control_layout = QHBoxLayout()
        
        self.import_button = QPushButton("Import Video")
        self.import_button.setStyleSheet("QPushButton { background-color: #3498db; color: white; padding: 8px 15px; border: none; border-radius: 4px; }"
                                       "QPushButton:hover { background-color: #2980b9; }")
        self.import_button.clicked.connect(self.import_video)
        control_layout.addWidget(self.import_button)
        
        self.play_button = QPushButton("Play Video")
        self.play_button.setStyleSheet("QPushButton { background-color: #2ecc71; color: white; padding: 8px 15px; border: none; border-radius: 4px; }"
                                     "QPushButton:hover { background-color: #27ae60; }")
        self.play_button.clicked.connect(self.play_video)
        self.play_button.setEnabled(False)
        control_layout.addWidget(self.play_button)
        
        self.process_button = QPushButton("Process Video")
        self.process_button.setStyleSheet("QPushButton { background-color: #9b59b6; color: white; padding: 8px 15px; border: none; border-radius: 4px; }"
                                        "QPushButton:hover { background-color: #8e44ad; }")
        self.process_button.clicked.connect(self.process_video)
        self.process_button.setEnabled(False)
        control_layout.addWidget(self.process_button)
        
        self.count_button = QPushButton("Start Counting")
        self.count_button.setStyleSheet("QPushButton { background-color: #e67e22; color: white; padding: 8px 15px; border: none; border-radius: 4px; }"
                                      "QPushButton:hover { background-color: #d35400; }")
        self.count_button.clicked.connect(self.count_fringes)
        self.count_button.setEnabled(False)
        control_layout.addWidget(self.count_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; padding: 8px 15px; border: none; border-radius: 4px; }"
                                     "QPushButton:hover { background-color: #c0392b; }")
        self.stop_button.clicked.connect(self.stop_counting)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        control_layout.addStretch()
        main_layout.addLayout(control_layout)
        
        # Parameter adjustment area
        params_layout = QHBoxLayout()
        
        params_layout.addWidget(QLabel("Contrast:"))
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(50, 300)
        self.contrast_slider.setValue(150)
        self.contrast_slider.valueChanged.connect(self.update_processing_params)
        params_layout.addWidget(self.contrast_slider)
        
        params_layout.addWidget(QLabel("Sensitivity:"))
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(1, 100)
        self.sensitivity_slider.setValue(50)
        self.sensitivity_slider.valueChanged.connect(self.update_processing_params)
        params_layout.addWidget(self.sensitivity_slider)
        
        main_layout.addLayout(params_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("QProgressBar { height: 20px; border-radius: 10px; }"
                                      "QProgressBar::chunk { background-color: #3498db; border-radius: 10px; }")
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Data display area
        data_splitter = QSplitter(Qt.Horizontal)
        
        # Left: video display area
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        video_group = QGroupBox("Video Preview")
        video_layout = QVBoxLayout()
        
        self.video_label = QLabel("Please import a video file")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(600, 400)
        self.video_label.setStyleSheet("background-color: #000; color: #fff; font-size: 16px; border: 1px solid #34495e;")
        video_layout.addWidget(self.video_label)
        
        video_group.setLayout(video_layout)
        left_layout.addWidget(video_group)
        
        # Processing effect display
        processed_group = QGroupBox("Processing Effect")
        processed_layout = QVBoxLayout()
        
        self.processed_label = QLabel("Processing effect will be shown here")
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setMinimumSize(600, 200)
        self.processed_label.setStyleSheet("background-color: #000; color: #fff; font-size: 16px; border: 1px solid #34495e;")
        processed_layout.addWidget(self.processed_label)
        
        processed_group.setLayout(processed_layout)
        left_layout.addWidget(processed_group)
        
        left_widget.setLayout(left_layout)
        data_splitter.addWidget(left_widget)
        
        # Right: results area
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        result_group = QGroupBox("Fringe Counting Results")
        result_layout = QVBoxLayout()
        
        result_layout.addWidget(QLabel("Current Fringes:"))
        self.fringe_count_label = QLabel("0")
        self.fringe_count_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2980b9; padding: 5px;")
        result_layout.addWidget(self.fringe_count_label)
        
        result_layout.addWidget(QLabel("Total Fringe Movement:"))
        self.fringe_movement_label = QLabel("0.0 fringes")
        self.fringe_movement_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #27ae60; padding: 5px;")
        result_layout.addWidget(self.fringe_movement_label)
        
        result_layout.addWidget(QLabel("Optical Path Difference:"))
        self.path_diff_label = QLabel("0.00 μm")
        self.path_diff_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #8e44ad; padding: 5px;")
        result_layout.addWidget(self.path_diff_label)
        
        result_layout.addWidget(QLabel("Direction:"))
        self.direction_label = QLabel("Stationary")
        self.direction_label.setStyleSheet("font-size: 16px; color: #e74c3c; padding: 5px;")
        result_layout.addWidget(self.direction_label)
        
        result_layout.addWidget(QLabel("Status:"))
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-size: 14px; color: #7f8c8d; padding: 5px; background-color: #ecf0f1; border-radius: 3px;")
        result_layout.addWidget(self.status_label)
        
        result_group.setLayout(result_layout)
        right_layout.addWidget(result_group)
        
        right_widget.setLayout(right_layout)
        data_splitter.addWidget(right_widget)
        
        data_splitter.setStretchFactor(0, 3)
        data_splitter.setStretchFactor(1, 1)
        main_layout.addWidget(data_splitter)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Initialize variables
        self.video_path = ""
        self.frames = []
        self.counting_active = False
        self.playing_video = False
        self.movement_count = 0
        self.lambda_nm = 632.8  # He-Ne laser wavelength (nm)
        
        # Processing parameters
        self.contrast_factor = 1.5
        self.sensitivity = 50
        
        # Analyzer
        self.analyzer = FringeAnalyzer()
        
        # Timers
        self.video_timer = QTimer(self)
        self.video_timer.timeout.connect(self.update_video_frame)
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self.play_next_frame)
        
        self.current_frame_index = 0

    def update_processing_params(self):
        """Update processing parameters"""
        self.contrast_factor = self.contrast_slider.value() / 100.0
        self.sensitivity = self.sensitivity_slider.value()
        
        if self.frames and self.current_frame_index < len(self.frames):
            frame = self.frames[self.current_frame_index]
            self.show_processed_frame(frame)

    def import_video(self):
        """Import video file"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Import Interference Fringe Video", "", 
            "Video files (*.mp4 *.avi *.mov *.mkv *.wmv);;All files (*)", 
            options=options
        )
        
        if file_name:
            self.video_path = file_name
            self.video_label.setText(f"Imported video: {file_name.split('/')[-1]}\nClick 'Play Video' to preview")
            self.play_button.setEnabled(True)
            self.process_button.setEnabled(True)
            self.status_label.setText("Video imported. You can preview or process it.")
            self.stop_counting()

    def play_video(self):
        """Play original video"""
        if not self.video_path:
            return
            
        if not self.playing_video:
            self.cap = cv2.VideoCapture(self.video_path)
            if not self.cap.isOpened():
                QMessageBox.warning(self, "Error", "Cannot open video file")
                return
                
            self.playing_video = True
            self.play_button.setText("Pause")
            self.play_timer.start(33)  # ~30 fps
            self.status_label.setText("Playing video...")
        else:
            self.playing_video = False
            self.play_button.setText("Play Video")
            self.play_timer.stop()
            self.status_label.setText("Video paused")

    def play_next_frame(self):
        """Play next frame"""
        if self.playing_video and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame, self.video_label)
            else:
                self.play_video()
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def process_video(self):
        """Process video"""
        if not self.video_path:
            QMessageBox.warning(self, "Error", "Please import a video first")
            return
        
        self.status_label.setText("Processing video...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        
        if self.playing_video:
            self.play_video()
        
        self.processor = VideoProcessor(self.video_path)
        self.processor.progress_updated.connect(self.update_progress)
        self.processor.processing_finished.connect(self.video_processing_finished)
        self.processor.error_occurred.connect(self.video_processing_error)
        self.processor.frame_processed.connect(self.on_frame_processed)
        self.processor.start()

    def on_frame_processed(self, original_frame, processed_frame):
        """Real-time display of frames during processing"""
        self.display_frame(original_frame, self.video_label)
        self.display_frame(processed_frame, self.processed_label)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def video_processing_finished(self, frames):
        self.frames = frames
        self.progress_bar.setVisible(False)
        self.count_button.setEnabled(True)
        self.status_label.setText("Video processed. Ready to count.")
        
        if self.frames:
            self.current_frame_index = 0
            self.show_processed_frame(self.frames[0])
            self.analyzer.prev_intensity = self.get_intensity(self.frames[0])
        
        QMessageBox.information(self, "Processing Completed", "Video processing completed. You may now start counting.")

    def video_processing_error(self, error_msg):
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Processing Error", f"Video processing error: {error_msg}")
        self.status_label.setText("Processing failed")

    def display_frame(self, frame, label):
        """Display frame on specified QLabel"""
        if len(frame.shape) == 3:
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            fmt = QImage.Format_RGB888
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            q_img = QImage(frame_rgb.data, w, h, bytes_per_line, fmt)
        else:
            h, w = frame.shape
            bytes_per_line = w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
        
        pixmap = QPixmap.fromImage(q_img)
        label.setPixmap(pixmap.scaled(
            label.width(), label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

    def show_processed_frame(self, frame):
        """Show processed frame"""
        processed = self.analyzer.enhance_fringes(frame, self.contrast_factor)
        self.display_frame(processed, self.processed_label)

    def count_fringes(self):
        """Start fringe counting"""
        if not self.frames:
            return
        
        self.counting_active = True
        self.count_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Counting fringes...")
        self.movement_count = 0
        
        self.analyzer.prev_intensity = self.get_intensity(self.frames[0])
        self.current_frame_index = 0
        self.video_timer.start(50)

    def stop_counting(self):
        """Stop counting"""
        self.counting_active = False
        self.playing_video = False
        self.video_timer.stop()
        self.play_timer.stop()
        self.count_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.play_button.setText("Play Video")
        self.status_label.setText("Counting stopped")
        
        if hasattr(self, 'cap'):
            self.cap.release()

    def update_video_frame(self):
        """Update video frame and perform fringe counting"""
        if not self.counting_active or not self.frames:
            return
        
        if self.current_frame_index >= len(self.frames):
            self.current_frame_index = 0
        
        frame = self.frames[self.current_frame_index]
        self.display_frame(frame, self.video_label)
        self.show_processed_frame(frame)
        
        # Fringe counting
        fringe_count = self.analyzer.count_fringes_advanced(frame)
        current_intensity = self.get_intensity(frame)
        intensity_diff = current_intensity - self.analyzer.prev_intensity
        
        # Dynamic threshold
        threshold = self.sensitivity / 20.0
        
        # Detect fringe movement
        if abs(intensity_diff) > threshold:
            movement = 0.5
            if intensity_diff > 0:
                direction = "Outward"
                color = "#27ae60"
            else:
                direction = "Inward"
                color = "#e74c3c"
            
            self.movement_count += movement
            path_diff = self.movement_count * self.lambda_nm / 1000
            
            # Update display
            self.fringe_count_label.setText(str(int(fringe_count)))
            self.fringe_movement_label.setText(f"{self.movement_count:.1f} fringes")
            self.path_diff_label.setText(f"{path_diff:.2f} μm")
            self.direction_label.setText(direction)
            self.direction_label.setStyleSheet(f"font-size: 16px; color: {color}; padding: 5px;")
            
            self.analyzer.prev_intensity = current_intensity
        
        self.current_frame_index += 1
        self.status_label.setText(f"Counting... Frame {self.current_frame_index}/{len(self.frames)}")

    def get_intensity(self, frame):
        """Get intensity value of center region"""
        h, w = frame.shape
        roi = frame[h//4:3*h//4, w//4:3*w//4]
        return np.mean(roi)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = FringeCounter()
    window.show()
    sys.exit(app.exec_())