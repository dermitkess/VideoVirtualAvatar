import pygame
import numpy as np
import sounddevice as sd
from moviepy.video.io.VideoFileClip import VideoFileClip
from pathlib import Path
import sys
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel
from PyQt6.QtCore import Qt

# Инициализация PyGame
pygame.init()
WINDOW_SIZE = [1080, 1080]  # Изменено на список для возможности модификации
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Video Avatar")

# Глобальные переменные
NUM_STAGES = 2  # Начальное количество стадий (2: закрыт/открыт)
THRESHOLDS = [0.05]  # Начальные пороги для 2 стадий
video_paths = []
players = []
current_video = 0
show_interface = False

# Проверка существования директории assets и видеофайлов
assets_dir = Path(__file__).parent / "assets"

class VideoPlayer:
    def __init__(self, video_path):
        try:
            self.clip = VideoFileClip(str(video_path))
            self.fps = self.clip.fps
            self.duration = self.clip.duration
            self.current_time = 0
            
            # Автоповорот (если видео вертикальное)
            if self.clip.size[0] < self.clip.size[1]:
                self.clip = self.clip.rotate(90)
        except Exception as e:
            print(f"Ошибка при загрузке видео {video_path}: {e}")
            pygame.quit()
            sys.exit()

    def get_frame(self, current_time):
        try:
            frame = self.clip.get_frame(current_time % self.duration)
            return pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        except Exception as e:
            print(f"Ошибка при получении кадра: {e}")
            return None

    def close(self):
        """Закрытие видеоклипа для освобождения ресурсов"""
        if hasattr(self, 'clip') and self.clip:
            self.clip.close()

def update_video_paths_and_players(num_stages):
    """Обновление путей к видео и игроков в зависимости от количества стадий"""
    global video_paths, players
    video_paths = [assets_dir / f"{i}.mp4" for i in range(num_stages)]
    
    # Проверка наличия видеофайлов
    for path in video_paths:
        if not path.exists():
            print(f"Ошибка: Видеофайл {path} не найден")
            pygame.quit()
            sys.exit()
    
    # Закрытие предыдущих плееров
    for player in players:
        player.close()
    
    # Инициализация новых плееров
    players.clear()
    players.extend([VideoPlayer(path) for path in video_paths])

def update_thresholds(num_stages):
    """Обновление порогов в зависимости от количества стадий"""
    global THRESHOLDS
    if num_stages == 2:
        THRESHOLDS = [0.05]
    elif num_stages == 3:
        THRESHOLDS = [0.03, 0.06]
    elif num_stages == 4:
        THRESHOLDS = [0.02, 0.04, 0.06]

# Инициализация начальных видео и порогов
update_video_paths_and_players(NUM_STAGES)
update_thresholds(NUM_STAGES)

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Выбор количества стадий
        self.stages_label = QLabel("Количество стадий открытия рта:")
        layout.addWidget(self.stages_label)
        self.stages_combo = QComboBox()
        self.stages_combo.addItems(["2", "3", "4"])
        self.stages_combo.setCurrentText(str(NUM_STAGES))
        layout.addWidget(self.stages_combo)

        # Выбор размера окна
        self.size_label = QLabel("Размер окна:")
        layout.addWidget(self.size_label)
        self.size_combo = QComboBox()
        self.size_combo.addItems(["720x720", "1080x1080", "1280x720"])
        self.size_combo.setCurrentText(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        layout.addWidget(self.size_combo)

        # Кнопка "Применить"
        self.apply_button = QPushButton("Применить")
        self.apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)

    def apply_settings(self):
        global NUM_STAGES, WINDOW_SIZE, screen
        # Обновление количества стадий
        new_stages = int(self.stages_combo.currentText())
        if new_stages != NUM_STAGES:
            NUM_STAGES = new_stages
            update_thresholds(NUM_STAGES)
            update_video_paths_and_players(NUM_STAGES)

        # Обновление размера окна
        new_size = self.size_combo.currentText()
        width, height = map(int, new_size.split("x"))
        if [width, height] != WINDOW_SIZE:
            WINDOW_SIZE = [width, height]
            screen = pygame.display.set_mode(WINDOW_SIZE)

        self.accept()

def audio_callback(indata, frames, time, status):
    global current_video
    if status:
        print(f"Аудио ошибка: {status}")
    try:
        rms = np.sqrt(np.mean(np.square(indata)))
        # Выбор видео на основе порогов
        for i, threshold in enumerate(THRESHOLDS):
            if rms <= threshold:
                current_video = i
                break
        else:
            current_video = len(THRESHOLDS)  # Последняя стадия
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
                    elif event.key == pygame.K_i:  # Показать/скрыть интерфейс по клавише I
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