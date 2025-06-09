# VideoVirtualAvatar

VideoVirtualAvatar — это приложение, которое воспроизводит видеофайлы в зависимости от уровня громкости звука с микрофона, с возможностью настройки количества стадий открытия рта и размера окна через интерфейс PyQt6.

---

## Русский

### Описание
Приложение использует Pygame для отображения видео, PyQt6 для интерфейса настроек, и `moviepy` для обработки видеофайлов. Оно анализирует аудиовход с микрофона и переключает видеофайлы (`0.mp4`, `1.mp4`, и т.д.) в зависимости от громкости.

### Требования
- **Python**: Версия 3.8 или выше
- **FFmpeg**: Требуется для работы `moviepy`
- **Операционная система**: Windows, macOS или Linux
- **Видеофайлы**: Файлы `0.mp4`, `1.mp4` (и, опционально, `2.mp4`, `3.mp4`) в папке `assets`

### Установка

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/dermitkess/VideoVirtualAvatar.git
   cd VideoVirtualAvatar
   ```

2. **Установите Python-зависимости**:
   Убедитесь, что у вас установлен Python 3.8+. Установите зависимости с помощью `pip`:
   ```bash
   pip install moviepy numpy sounddevice pygame PyQt6
   ```

3. **Установите FFmpeg**:
   - **Windows**:
     1. Скачайте FFmpeg с [официального сайта](https://ffmpeg.org/download.html).
     2. Распакуйте архив и добавьте папку `bin` (содержащую `ffmpeg.exe`) в системную переменную PATH.
     3. Или поместите `ffmpeg.exe` в корень папки проекта (`VideoVirtualAvatar`).
   - **macOS**:
     ```bash
     brew install ffmpeg
     ```
   - **Linux**:
     ```bash
     sudo apt-get install ffmpeg
     ```

4. **Поместите видеофайлы**:
   - Создайте папку `assets` в корне проекта, если её нет.
   - Поместите видеофайлы (`0.mp4`, `1.mp4`, и, если используете 3 или 4 стадии, `2.mp4`, `3.mp4`) в папку `assets`.
   - Скачать видеофайлы можно по ссылке: [вставьте ссылку на Google Drive/Dropbox].

5. **Запустите программу**:
   ```bash
   python main.py
   ```

### Использование
- Нажмите клавишу `I`, чтобы открыть интерфейс настроек.
- Выберите количество стадий открытия рта (2, 3 или 4) и размер окна (720x720, 1080x1080, 1280x720).
- Нажмите «Применить» для сохранения настроек.
- Нажмите `ESC` или закройте окно для выхода.
- Настройки сохраняются в `config.json`.

### Компиляция в `.exe` (Windows)
1. Установите PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Скомпилируйте программу:
   - Если `ffmpeg.exe` находится в папке проекта:
     ```bash
     pyinstaller --onefile --add-data "assets;assets" --add-binary "ffmpeg.exe;." --add-data "config.json;." --name VideoAvatar main.py
     ```
   - Если FFmpeg установлен в системе:
     ```bash
     pyinstaller --onefile --add-data "assets;assets" --add-data "config.json;." --name VideoAvatar main.py
     ```
3. Найдите `VideoAvatar.exe` в папке `dist`.

### Устранение неполадок
- **Отсутствуют видеофайлы**: Убедитесь, что файлы `0.mp4`, `1.mp4` (и, при необходимости, `2.mp4`, `3.mp4`) находятся в папке `assets`.
- **FFmpeg не найден**: Проверьте, что `ffmpeg.exe` доступен в PATH или в папке проекта.
- **Программа вылетает при изменении настроек**: Убедитесь, что все видеофайлы для выбранного количества стадий присутствуют.

---

## English

### Description
VideoVirtualAvatar is an application that plays videofiles based on the microphone's audio volume, with a PyQt6 interface to configure the number of mouth-opening stages and window size.

### Requirements
- **Python**: Version 3.8 or higher
- **FFmpeg**: Required for `moviepy`
- **Operating System**: Windows, macOS, or Linux
- **Videofiles**: Files `0.mp4`, `1.mp4` (and optionally `2.mp4`, `3.mp4`) in the `assets` folder

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dermitkess/VideoVirtualAvatar.git
   cd VideoVirtualAvatar
   ```

2. **Install Python dependencies**:
   Ensure Python 3.8+ is installed. Install dependencies using `pip`:
   ```bash
   pip install moviepy numpy sounddevice pygame PyQt6
   ```

3. **Install FFmpeg**:
   - **Windows**:
     1. Download FFmpeg from [the official website](https://ffmpeg.org/download.html).
     2. Extract the archive and add the `bin` folder (containing `ffmpeg.exe`) to the system PATH.
     3. Alternatively, place `ffmpeg聦
ffmpeg.exe` in the project root (`VideoVirtualAvatar`).
   - **macOS**:
     ```bash
     brew install ffmpeg
     ```
   - **Linux**:
     ```bash
     sudo apt-get install ffmpeg
     ```

4. **Place videofiles**:
   - Create an `assets` folder in the project root if it doesn't exist.
   - Place videofiles (`0.mp4`, `1.mp4`, and, if using 3 or 4 stages, `2.mp4`, `3.mp4`) in the `assets` folder.
   - Download videofiles from: [insert Google Drive/Dropbox link].

5. **Run the program**:
   ```bash
   python main.py
   ```

### Usage
- Press `I` to open the settings interface.
- Select the number of mouth-opening stages (2, 3, or 4) and window size (720x720, 1080x1080, 1280x720).
- Click "Apply" to save settings.
- Press `ESC` or close the window to exit.
- Settings are saved in `config.json`.

### Compiling to `.exe` (Windows)
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Compile the program:
   - If `ffmpeg.exe` is in the project folder:
     ```bash
     pyinstaller --onefile --add-data "assets;assets" --add-binary "ffmpeg.exe;." --add-data "config.json;." --name VideoAvatar main.py
     ```
   - If FFmpeg is installed system-wide:
     ```bash
     pyinstaller --onefile --add-data "assets;assets" --add-data "config.json;." --name VideoAvatar main.py
     ```
3. Find `VideoAvatar.exe` in the `dist` folder.

### Troubleshooting
- **Missing videofiles**: Ensure `0.mp4`, `1.mp4` (and, if needed, `2.mp4`, `3.mp4`) are in the `assets` folder.
- **FFmpeg not found**: Verify that `ffmpeg.exe` is in PATH or the project folder.
- **Program crashes on settings change**: Ensure all videofiles for the selected number of stages are present.