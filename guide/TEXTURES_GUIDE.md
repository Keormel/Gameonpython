# 🎨 Как добавить свои текстуры

## Подготовка текстур

### 1. Спрайты персонажей

Создайте папку `assets/` и положите туда изображения:

```
assets/
├── student_normal.png       # Студент (обычное состояние)
├── student_cheat.png        # Студент (списывает)
├── student_games.png        # Студент (играет)
├── student_sleep.png        # Студент (спит)
├── student_eat.png          # Студент (ест)
├── teacher_normal.png       # Преподаватель (не смотрит)
├── teacher_looking.png      # Преподаватель (смотрит)
└── backgrounds/
    ├── classroom.png        # Фон класса
    └── desk_student.png     # Парта студента
```

### 2. Размеры спрайтов (рекомендуемые)

- **Студент**: 80x120 пикселей
- **Преподаватель**: 100x150 пикселей
- **Фон**: 1400x800 пикселей (во весь экран)
- **Парта**: 250x150 пикселей

## Модификация кода

### Загрузка спрайтов

Добавьте в метод `__init__` класса `Game`:

```python
def __init__(self):
    # ... существующий код ...
    
    # Загрузка спрайтов
    self.load_assets()

def load_assets(self):
    """Загрузить графические ресурсы"""
    try:
        self.student_sprites = {
            StudentActivity.NORMAL: pygame.image.load("assets/student_normal.png"),
            StudentActivity.CHEAT: pygame.image.load("assets/student_cheat.png"),
            StudentActivity.GAMES: pygame.image.load("assets/student_games.png"),
            StudentActivity.SLEEP: pygame.image.load("assets/student_sleep.png"),
            StudentActivity.EAT: pygame.image.load("assets/student_eat.png"),
        }
        
        self.teacher_sprites = {
            True: pygame.image.load("assets/teacher_looking.png"),   # Смотрит
            False: pygame.image.load("assets/teacher_normal.png"),   # Не смотрит
        }
        
        self.classroom_bg = pygame.image.load("assets/backgrounds/classroom.png")
        self.student_desk = pygame.image.load("assets/backgrounds/desk_student.png")
        
    except FileNotFoundError as e:
        print(f"Warning: Could not load asset: {e}")
        print("Using default geometric rendering")
```

### Использование спрайтов в draw()

Замените в методе `Student.draw()`:

```python
def draw(self, screen: pygame.Surface, sprites: dict):
    """Нарисовать студента со спрайтом"""
    sprite = sprites.get(self.current_activity)
    
    if sprite:
        # Использовать спрайт
        screen.blit(sprite, (int(self.x - 40), int(self.y - 60)))
    else:
        # Fallback на геометрию (если нет спрайта)
        # ... старый код рисования фигур ...
        pass
```

Аналогично для `Teacher.draw()`:

```python
def draw(self, screen: pygame.Surface, sprites: dict):
    """Нарисовать преподавателя со спрайтом"""
    sprite = sprites.get(self.looking_at_student)
    
    if sprite:
        screen.blit(sprite, (int(self.x - 50), int(self.y - 75)))
    else:
        # ... старый код рисования фигур ...
        pass
```

### Использование фона класса

В методе `draw_game()`:

```python
def draw_game(self):
    """Отрисовать игровой экран"""
    # Фон аудитории
    if hasattr(self, 'classroom_bg'):
        self.screen.blit(self.classroom_bg, (0, 0))
    else:
        self.screen.fill((245, 245, 220))  # Fallback
    
    # ... остальной код ...
```

## Добавление звуков

### 1. Структура папок

```
sounds/
├── menu_start.mp3       # Звук начала игры
├── cheat_success.mp3    # Успешный прогул
├── caught.mp3           # Поимка
├── victory.mp3          # Победа
└── time_tick.mp3        # Тик таймера
```

### 2. Инициализация звуков

```python
def load_sounds(self):
    """Загрузить звуковые эффекты"""
    pygame.mixer.init()
    
    try:
        self.sounds = {
            'start': pygame.mixer.Sound("sounds/menu_start.mp3"),
            'cheat': pygame.mixer.Sound("sounds/cheat_success.mp3"),
            'caught': pygame.mixer.Sound("sounds/caught.mp3"),
            'victory': pygame.mixer.Sound("sounds/victory.mp3"),
            'tick': pygame.mixer.Sound("sounds/time_tick.mp3"),
        }
    except:
        print("Sounds not available")
        self.sounds = {}

def play_sound(self, sound_name: str):
    """Воспроизвести звук"""
    if sound_name in self.sounds:
        self.sounds[sound_name].play()
```

### 3. Использование звуков

```python
def handle_game_click(self, pos: Tuple[int, int]):
    """Обработить клик в игре"""
    if self.teacher.looking_at_student:
        self.play_sound('caught')
        self.state = GameState.GAME_OVER
        return
    
    # ... обработка нажатия ...
    self.play_sound('cheat')  # Для успешной активности
```

## Добавление анимаций

### Система анимаций

```python
class Animation:
    def __init__(self, frames: List[pygame.Surface], duration: int = 10):
        self.frames = frames
        self.duration = duration  # Кадры между смещением
        self.current_frame = 0
        self.timer = 0
    
    def update(self):
        self.timer += 1
        if self.timer >= self.duration:
            self.timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
    
    def get_frame(self):
        return self.frames[self.current_frame]
```

### Использование анимаций

```python
def load_animations(self):
    """Загрузить анимации"""
    # Анимация студента списывающего
    cheat_frames = [
        pygame.image.load("assets/animations/cheat_1.png"),
        pygame.image.load("assets/animations/cheat_2.png"),
        pygame.image.load("assets/animations/cheat_3.png"),
    ]
    self.cheat_animation = Animation(cheat_frames, duration=5)

def update(self):
    # ... существующий код ...
    
    # Обновление анимации
    if self.student.current_activity == StudentActivity.CHEAT:
        self.cheat_animation.update()
```

## Примеры использования Pygame

### Преобразование изображений

```python
# Масштабирование
sprite = pygame.transform.scale(sprite, (new_width, new_height))

# Поворот
sprite = pygame.transform.rotate(sprite, angle_degrees)

# Отражение
sprite = pygame.transform.flip(sprite, horizontal=True, vertical=False)

# Смешивание (прозрачность)
sprite.set_alpha(128)  # 0-255, где 0 = полностью прозрачно
```

### Работа с прямоугольниками спрайтов

```python
# Получить прямоугольник спрайта
rect = sprite.get_rect()
rect.center = (x, y)  # Центрировать по координатам

# Проверить столкновение
if rect.collidepoint(mouse_pos):
    print("Cursor over sprite")
```

## Чеклист для добавления текстур

- [ ] Создана папка `assets/`
- [ ] Подготовлены спрайты персонажей (разные состояния)
- [ ] Добавлен фон класса
- [ ] Добавлены парты
- [ ] Реализована загрузка ресурсов в `load_assets()`
- [ ] Модифицированы методы `draw()` для использования спрайтов
- [ ] Добавлены fallback'и для случаев когда спрайты не загружены
- [ ] Протестирована игра с новыми текстурами

## Советы по оптимизации

1. **Кэширование спрайтов** - загружайте один раз в `__init__`
2. **Масштабирование** - масштабируйте один раз, не каждый кадр
3. **Альфа-канал** - используйте PNG с прозрачностью
4. **Размер файлов** - оптимизируйте изображения (max 100KB за спрайт)
5. **Формат** - используйте PNG для графики, MP3/OGG для звуков

## Помощь и примеры

Больше информации о Pygame:
- https://www.pygame.org/docs/
- https://www.pygame.org/wiki/tutorials

Генератор спрайтов:
- Piskel (https://www.piskelapp.com/) - простой sprite editor
- Aseprite - профессиональный инструмент
- LibreSprite - бесплатная альтернатива Aseprite
