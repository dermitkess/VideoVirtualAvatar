import pygame
import numpy as np
import sounddevice as sd
from moviepy.video.io.VideoFileClip import VideoFileClip
from pathlib import Path
import sys
import json
import os
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt

# Определение базовой директории для PyInstaller
if getattr(sys, 'frozen', False):
    base_dir = Path(sys._MEIPASS)
else:
    base_dir = Path(__file__).parent
assets_dir = base_dir / "assets"
config_path = base_dir / "config.json"
icon_path = base_dir / "icon.png"

# Инициализация PyGame
pygame.init()
DEFAULT_WINDOW_SIZE = [1080, 1080]
WINDOW_SIZE = DEFAULT_WINDOW_SIZE.copy()
try:
    screen = pygame.display.set_mode(WINDOW_SIZE)
    # Установка иконки окна
    if icon_path.exists():
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)
    else:
        print(f"Предупреждение: Файл иконки {icon_path} не найден")
except Exception as e:
    print(f"Ошибка при инициализации окна Pygame: {e}")
    sys.exit()
pygame.display.set_caption("VideoVirtualAvatar")

# Глобальные переменные
DEFAULT_NUM_STAGES = 2
NUM_STAGES = DEFAULT_NUM_STAGES
THRESHOLDS = [0.05]
video_paths = []
players = []
current_video = 0
show_interface = False

# Загрузка настроек из файла
def load_config():
    global NUM_STAGES, WINDOW_SIZE
    try:
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                NUM_STAGES = config.get('num_stages', DEFAULT_NUM_STAGES)
                WINDOW_SIZE = config.get('window_size', DEFAULT_WINDOW_SIZE)
                if NUM_STAGES not in [2, 3, 4]:
                    NUM_STAGES = DEFAULT_NUM_STAGES
                if WINDOW_SIZE not in [[720, 720], [1080, 1080], [1280, 720]]:
                    WINDOW_SIZE = DEFAULT_WINDOW_SIZE
    except Exception as e:
        print(f"Ошибка при загрузке конфигурации: {e}")

# Сохранение настроек в файл
def save_config():
    try:
        config = {
            'num_stages': NUM_STAGES,
            'window_size': WINDOW_SIZE
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Ошибка при сохранении конфигурации: {e}")

# Загрузка начальных настроек
load_config()

class VideoPlayer:
    def __init__(self, video_path):
        try:
            self.clip = VideoFileClip(str(video_path))
            self.fps = self.clip.fps
            self.duration = self.clip.duration
            self.current_time = 0
            if self.clip.size[0] < self.clip.size[1]:
                self.clip = self.clip.rotate(90)
        except Exception as e:
            print(f"Ошибка при загрузке видео {video_path}: {e}")
            raise

    def get_frame(self, current_time):
        try:
            frame = self.clip.get_frame(current_time % self.duration)
            return pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        except Exception as e:
            print(f"Ошибка при получении кадра: {e}")
            return None

    def close(self):
        if hasattr(self, 'clip') and self.clip:
            self.clip.close()

def update_video_paths_and_players(num_stages):
    global video_paths, players
    video_paths = [assets_dir / f"{i}.mp4" for i in range(num_stages)]
    
    # Проверка наличия видеофайлов
    for path in video_paths:
        if not path.exists():
            return False, f"Видеофайл {path} не найден"
    
    # Закрытие предыдущих плееров
    for player in players:
        player.close()
    
    # Инициализация новых плееров
    players.clear()
    try:
        players.extend([VideoPlayer(path) for path in video_paths])
        return True, ""
    except Exception as e:
        return False, f"Ошибка при инициализации видеоплееров: {e}"

def update_thresholds(num_stages):
    global THRESHOLDS
    if num_stages == 2:
        THRESHOLDS = [0.05]
    elif num_stages == 3:
        THRESHOLDS = [0.03, 0.06]
    elif num_stages == 4:
        THRESHOLDS = [0.02, 0.04, 0.06]

# Инициализация начальных видео и порогов
success, error = update_video_paths_and_players(NUM_STAGES)
if not success:
    print(error)
    pygame.quit()
    sys.exit()
update_thresholds(NUM_STAGES)

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.stages_label = QLabel("Количество стадий открытия рта:")
        layout.addWidget(self.stages_label)
        self.stages_combo = QComboBox()
        self.stages_combo.addItems(["2", "3", "4"])
        self.stages_combo.setCurrentText(str(NUM_STAGES))
        layout.addWidget(self.stages_combo)
        self.size_label = QLabel("Размер окна:")
        layout.addWidget(self.size_label)
        self.size_combo = QComboBox()
        self.size_combo.addItems(["720x720", "1080x1080", "1280x720"])
        self.size_combo.setCurrentText(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        layout.addWidget(self.size_combo)
        self.apply_button = QPushButton("Применить")
        self.apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(self.apply_button)
        self.setLayout(layout)

    def apply_settings(self):
        global NUM_STAGES, WINDOW_SIZE, screen
        new_stages = int(self.stages_combo.currentText())
        new_size = self.size_combo.currentText()
        width, height = map(int, new_size.split("x"))

        # Проверка и обновление стадий
        if new_stages != NUM_STAGES:
            success, error = update_video_paths_and_players(new_stages)
            if not success:
                QMessageBox.critical(self, "Ошибка", error)
                return
            NUM_STAGES = new_stages
            update_thresholds(NUM_STAGES)

        # Обновление размера окна
        if [width, height] != WINDOW_SIZE:
            try:
                WINDOW_SIZE = [width, height]
                screen = pygame.display.set_mode(WINDOW_SIZE)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось изменить размер окна: {e}")
                return

        # Сохранение настроек
        save_config()
        self.accept()

def audio_callback(indata, frames, time, status):
    global current_video
    if status:
        print(f"Аудио ошибка: {status}")
    try:
        rms = np.sqrt(np.mean(np.square(indata)))
        for i, threshold in enumerate(THRESHOLDS):
            if rms <= threshold:
                current_video = i
                break
        else:
            current_video = len(THRESHOLDS)
    except Exception as e:
        print(f"Ошибка в обработке аудио: {e}")

# Проверка доступности аудиоустройства
try:
    devices = sd.query_devices()
    if not devices:
        print("Ошибка: Нет доступных аудиоустройств")
        pygame.quit()
        sys.exit()
except Exception as e:
    print(f"Ошибка при проверке аудиоустройств: {e}")
    pygame.quit()
    sys.exit()

# Инициализация PyQt6
app = QApplication(sys.argv)
settings_dialog = SettingsDialog()

# Главный цикл
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()

try:
    with sd.InputStream(samplerate=44100, blocksize=1024, channels=1, callback=audio_callback):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_i:
                        if show_interface:
                            settings_dialog.hide()
                            show_interface = False
                        else:
                            settings_dialog.exec()
                            show_interface = True

            current_time = (pygame.time.get_ticks() - start_time) / 1000.0
            frame = players[current_video].get_frame(current_time)
            
            if frame is not None:
                try:
                    frame = pygame.transform.scale(frame, WINDOW_SIZE)
                    screen.blit(frame, (0, 0))
                    pygame.display.flip()
                except Exception as e:
                    print(f"Ошибка при отображении кадра: {e}")

            clock.tick(30)

except Exception as e:
    print(f"Ошибка в главном цикле: {e}")

finally:
    for player in players:
        player.close()
    pygame.quit()
    sys.exit()