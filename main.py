import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QFileDialog,
                             QVBoxLayout, QHBoxLayout, QComboBox, QSlider, QCheckBox,
                             QGridLayout)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, pyqtSignal
import cv2
import numpy as np

class ImageEnhancer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.original_image = None  # Imagen original
        self.processed_image = None  # Imagen procesada
        self.filters_applied = []

    def initUI(self):
        self.setWindowTitle('Aplicación Interactiva de Mejora de Imágenes')
        self.resize(1000, 700)

        # Aplicar estilo a la ventana
        self.setStyleSheet("""
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px;
                text-align: center;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 14px;
            }
            QComboBox {
                background-color: #3E3E3E;
                border: 1px solid #555;
                padding: 5px;
                font-size: 14px;
                color: #FFFFFF;
            }
            QComboBox QAbstractItemView {
                background-color: #3E3E3E;
                selection-background-color: #4CAF50;
                color: #FFFFFF;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #3E3E3E;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
        """)

        # Botón para cargar imagen
        self.load_button = QPushButton('Cargar Imagen')
        self.load_button.clicked.connect(self.load_image)

        # ComboBox para seleccionar el filtro
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            'Selecciona una mejora',
            'Mejora de Contraste',
            'Filtro de Suavizado',
            'Umbralización',
            'Detección de Bordes',
            'Ajuste de Brillo',
            'Ajuste de Saturación',
            'Corrección Gamma',
            'Invertir Colores',
            'Filtro Sepia',
            'Reducción de Ruido',
            'Sharpening'
        ])
        self.filter_combo.currentIndexChanged.connect(self.filter_selected)

        # Botón para añadir el filtro a la lista
        self.add_filter_button = QPushButton('Añadir Mejora')
        self.add_filter_button.clicked.connect(self.add_filter)

        # Layout para los controles superiores
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.load_button)
        controls_layout.addWidget(self.filter_combo)
        controls_layout.addWidget(self.add_filter_button)

        # Lista de filtros aplicados
        self.applied_filters_layout = QVBoxLayout()
        self.applied_filters_widget = QWidget()
        self.applied_filters_widget.setLayout(self.applied_filters_layout)
        self.applied_filters_widget.setFixedWidth(300)

        # Labels para mostrar las imágenes
        self.original_label = QLabel('Imagen Original')
        self.result_label = QLabel('Imagen Procesada')

        # Establecer tamaño mínimo para las etiquetas de imagen
        self.original_label.setMinimumSize(400, 400)
        self.result_label.setMinimumSize(400, 400)

        # Alinear etiquetas
        self.original_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layout para las imágenes
        images_layout = QHBoxLayout()
        images_layout.addWidget(self.original_label)
        images_layout.addWidget(self.result_label)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addLayout(controls_layout)
        main_layout.addLayout(images_layout)

        # Layout general con los filtros aplicados
        general_layout = QHBoxLayout()
        general_layout.addLayout(main_layout)
        general_layout.addWidget(self.applied_filters_widget)

        self.setLayout(general_layout)

    def load_image(self):
        # Abrir diálogo para seleccionar imagen
        options = QFileDialog.Option.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, 'Abrir imagen', '', 'Imágenes (*.png *.jpg *.bmp)')
        if file_name:
            # Cargar imagen con cv2
            self.original_image = cv2.imread(file_name)
            self.processed_image = self.original_image.copy()
            self.display_image(self.original_image, self.original_label)
            self.update_image()

    def display_image(self, img, label):
        # Convertir imagen cv2 a QImage y mostrarla
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        height, width, channel = img_rgb.shape
        bytes_per_line = channel * width
        qimg = QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        # Ajustar tamaño de la imagen al label
        pixmap = pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(pixmap)

    def filter_selected(self):
        # Al seleccionar un filtro, podríamos mostrar parámetros específicos si es necesario
        pass

    def add_filter(self):
        selected_filter = self.filter_combo.currentText()
        if selected_filter == 'Selecciona una mejora':
            return

        # Crear un widget para el filtro seleccionado
        filter_widget = QWidget()
        filter_layout = QHBoxLayout()
        filter_label = QLabel(selected_filter)
        remove_button = QPushButton('Eliminar')
        remove_button.setFixedWidth(60)

        # Conectar botón de eliminar
        remove_button.clicked.connect(lambda: self.remove_filter(filter_widget))

        # Slider para ajustar la intensidad
        intensity_slider = QSlider(Qt.Orientation.Horizontal)
        intensity_slider.setMinimum(1)
        intensity_slider.setMaximum(100)
        intensity_slider.setValue(50)
        intensity_slider.setFixedWidth(100)
        intensity_slider.valueChanged.connect(self.update_image)

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(intensity_slider)
        filter_layout.addWidget(remove_button)
        filter_widget.setLayout(filter_layout)

        # Añadir el filtro a la lista
        self.applied_filters_layout.addWidget(filter_widget)
        self.filters_applied.append({
            'name': selected_filter,
            'widget': filter_widget,
            'slider': intensity_slider
        })

        self.update_image()

    def remove_filter(self, filter_widget):
        # Eliminar filtro de la lista
        for filter in self.filters_applied:
            if filter['widget'] == filter_widget:
                self.filters_applied.remove(filter)
                break
        # Eliminar widget de la interfaz
        filter_widget.setParent(None)
        self.update_image()

    def update_image(self):
        if self.original_image is None:
            return

        img = self.original_image.copy()

        for filter in self.filters_applied:
            name = filter['name']
            value = filter['slider'].value()
            if name == 'Mejora de Contraste':
                img = self.adjust_contrast(img, value)
            elif name == 'Filtro de Suavizado':
                img = self.smoothing_filter(img, value)
            elif name == 'Umbralización':
                img = self.thresholding(img, value)
            elif name == 'Detección de Bordes':
                img = self.edge_detection(img, value)
            elif name == 'Ajuste de Brillo':
                img = self.adjust_brightness(img, value)
            elif name == 'Ajuste de Saturación':
                img = self.adjust_saturation(img, value)
            elif name == 'Corrección Gamma':
                img = self.gamma_correction(img, value)
            elif name == 'Invertir Colores':
                img = self.invert_colors(img)
            elif name == 'Filtro Sepia':
                img = self.sepia_filter(img)
            elif name == 'Reducción de Ruido':
                img = self.noise_reduction(img, value)
            elif name == 'Sharpening':
                img = self.sharpen_image(img, value)
            # Añadir más filtros si es necesario

        self.processed_image = img
        self.display_image(self.processed_image, self.result_label)

    # Implementación de filtros
    def adjust_contrast(self, img, level):
        alpha = level / 50  # Escala de 0 a 2
        img_output = cv2.convertScaleAbs(img, alpha=alpha, beta=0)
        return img_output

    def smoothing_filter(self, img, level):
        kernel_size = int(level / 10) * 2 + 1  # Convertir nivel en tamaño de kernel impar
        img_output = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
        return img_output

    def thresholding(self, img, level):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, img_output = cv2.threshold(gray, level * 255 / 100, 255, cv2.THRESH_BINARY)
        img_output = cv2.cvtColor(img_output, cv2.COLOR_GRAY2BGR)
        return img_output

    def edge_detection(self, img, level):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, level, level * 2)
        img_output = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return img_output

    def adjust_brightness(self, img, level):
        beta = (level - 50) * 2  # Rango de -100 a 100
        img_output = cv2.convertScaleAbs(img, alpha=1, beta=beta)
        return img_output

    def adjust_saturation(self, img, level):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        s = cv2.multiply(s, level / 50)
        s = np.clip(s, 0, 255)
        hsv_output = cv2.merge([h, s, v])
        img_output = cv2.cvtColor(hsv_output, cv2.COLOR_HSV2BGR)
        return img_output

    def gamma_correction(self, img, level):
        gamma = level / 50  # Escala de 0 a 2
        if gamma == 0:
            gamma = 0.01  # Evitar división por cero
        inv_gamma = 1.0 / gamma
        table = np.array([(i / 255.0) ** inv_gamma * 255 for i in np.arange(256)]).astype('uint8')
        img_output = cv2.LUT(img, table)
        return img_output

    def invert_colors(self, img):
        img_output = cv2.bitwise_not(img)
        return img_output

    def sepia_filter(self, img):
        kernel = np.array([[0.272, 0.534, 0.131],
                           [0.349, 0.686, 0.168],
                           [0.393, 0.769, 0.189]])
        img_output = cv2.transform(img, kernel)
        img_output = np.clip(img_output, 0, 255).astype(np.uint8)
        return img_output

    def noise_reduction(self, img, level):
        h = level / 10  # Nivel de h para filtro bilateral
        img_output = cv2.bilateralFilter(img, 9, h * 2, h / 2)
        return img_output

    def sharpen_image(self, img, level):
        kernel = np.array([[0, -1, 0],
                           [-1, 5 + level / 10, -1],
                           [0, -1, 0]])
        img_output = cv2.filter2D(img, -1, kernel)
        return img_output

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageEnhancer()
    ex.show()
    sys.exit(app.exec())