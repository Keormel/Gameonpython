# 🔧 Примеры изменения игры - Готовые код-снипеты

Копируй-вставляй коды в `main.py` для быстрого добавления функций!

## 1️⃣ УВЕЛИЧИТЬ ВРЕМЯ ИГРЫ (с 30 сек на 60)

**Найди строку:**
```python
self.time_remaining = 30 * 60  # 30 секунд
```

**Замени на:**
```python
self.time_remaining = 60 * 60  # 60 секунд
```

---

## 2️⃣ ИЗМЕНИТЬ ОЧКИ ЗА АКТИВНОСТИ

**Найди в методе `handle_game_click`:**
```python
if button.action == "cheat":
    self.student.current_activity = StudentActivity.CHEAT
    self.score += 20  # <-- ВОТ ЭТО ЧИСЛО
    self.add_message("📝 Успешно списал ответ! +20 очков", 120)
```

**Измени числа:**
```python
self.score += 50  # Теперь 50 очков вместо 20!
self.add_message("📝 Успешно списал ответ! +50 очков", 120)
```

---

## 3️⃣ ДАТЬ ОДИН ШАНС ВЫЖИВАНИЯ

Если поймали - получить второй шанс вместо GAME OVER:

**Найди:**
```python
def handle_game_click(self, pos: Tuple[int, int]):
    """Обработить клик в игре"""
    if self.teacher.looking_at_student:
        self.add_message("😱 ПОЙМАНА! Учитель заметил!", 180)
        self.state = GameState.GAME_OVER
        return
```

**Замени на:**
```python
def handle_game_click(self, pos: Tuple[int, int]):
    """Обработить клик в игре"""
    if self.teacher.looking_at_student:
        self.score = max(0, self.score - 50)  # Штраф 50 очков
        self.add_message("😰 Почти поймана! Будь осторожнее! (-50 очков)", 180)
        return  # Не GAME OVER, просто штраф!
```

---

## 4️⃣ ДОБАВИТЬ КНОПКУ "ПАУЗА"

**Добавь в класс Game:**
```python
self.paused = False
```

**Добавь обработку клавиши:**
```python
def handle_key(self, key):
    """Обработить нажатие клавиши"""
    if key == pygame.K_SPACE:
        self.paused = not self.paused
    elif key == pygame.K_RETURN:
        if self.state in [GameState.GAME_OVER, GameState.WIN]:
            self.state = GameState.MAIN_MENU
            self.create_menu_buttons()
```

**Добавь в update():**
```python
def update(self):
    """Обновить состояние игры"""
    if self.paused and self.state == GameState.GAME:
        return  # Не обновляемся, если пауза
    
    # ... остальной код ...
```

---

## 5️⃣ ДОБАВИТЬ ЗВУК ПОИМКИ

**Добавь в __init__:**
```python
try:
    self.caught_sound = pygame.mixer.Sound("sounds/caught.wav")
except:
    self.caught_sound = None
```

**Замени в handle_game_click:**
```python
if self.teacher.looking_at_student:
    if self.caught_sound:
        self.caught_sound.play()
    self.add_message("😱 ПОЙМАНА! Учитель заметил!", 180)
    self.state = GameState.GAME_OVER
```

---

## 6️⃣ ДОБАВИТЬ СЧЁТЧИК ПОПЫТОК

**В __init__:**
```python
self.attempts = 0
self.attempts_limit = 3
```

**В start_game:**
```python
self.attempts += 1
```

**В draw_game_over:**
```python
attempt_text = self.font_small.render(
    f"Попыток: {self.attempts}/{self.attempts_limit}", 
    True, WHITE
)
self.screen.blit(attempt_text, (SCREEN_WIDTH // 2 - 100, 430))
```

---

## 7️⃣ СЛОЖНОСТИ ДЛЯ ИГРЫ

**Добавь после GameState:**
```python
class Difficulty(Enum):
    EASY = 1      # Учитель смотрит редко
    NORMAL = 2    # Обычно
    HARD = 3      # Учитель всегда смотрит
```

**В __init__:**
```python
self.difficulty = Difficulty.NORMAL
```

**В schedule_teacher_actions:**
```python
def schedule_teacher_actions(self):
    """Запланировать движения учителя"""
    if self.difficulty == Difficulty.EASY:
        delay = random.randint(4, 8)
        look_duration = random.randint(30, 60)
    elif self.difficulty == Difficulty.HARD:
        delay = random.randint(1, 2)
        look_duration = random.randint(120, 240)
    else:  # NORMAL
        delay = random.randint(2, 5)
        look_duration = random.randint(60, 180)
    
    self.teacher.look_timer = delay * FPS
    self.teacher.look_duration = look_duration
```

---

## 8️⃣ МЕНЮ ВЫБОРА СЛОЖНОСТИ

**В create_menu_buttons:**
```python
self.buttons = [
    Button(SCREEN_WIDTH // 2 - 200, 250, 400, 80, "ЛЕГКО", action="easy"),
    Button(SCREEN_WIDTH // 2 - 200, 370, 400, 80, "НОРМАЛЬНО", action="normal"),
    Button(SCREEN_WIDTH // 2 - 200, 490, 400, 80, "СЛОЖНО", action="hard"),
    Button(SCREEN_WIDTH // 2 - 200, 610, 400, 80, "ВЫХОД", action="exit"),
]
```

**В handle_menu_click:**
```python
if button.action == "easy":
    self.difficulty = Difficulty.EASY
    self.start_game()
elif button.action == "normal":
    self.difficulty = Difficulty.NORMAL
    self.start_game()
elif button.action == "hard":
    self.difficulty = Difficulty.HARD
    self.start_game()
```

---

## 9️⃣ ТАБЛИЦА РЕКОРДОВ (Простая версия)

**В __init__:**
```python
self.high_scores = []
self.load_scores()
```

**Добавь методы:**
```python
def load_scores(self):
    """Загрузить рекорды (если есть сохранённые)"""
    try:
        with open("highscores.txt", "r") as f:
            self.high_scores = [int(line.strip()) for line in f.readlines()]
        self.high_scores.sort(reverse=True)
        self.high_scores = self.high_scores[:10]  # Топ 10
    except:
        self.high_scores = []

def save_score(self, score: int):
    """Сохранить новый рекорд"""
    self.high_scores.append(score)
    self.high_scores.sort(reverse=True)
    self.high_scores = self.high_scores[:10]
    
    with open("highscores.txt", "w") as f:
        for score in self.high_scores:
            f.write(f"{score}\n")

def draw_highscores(self):
    """Показать рекорды"""
    self.screen.fill(UTM_PURPLE)
    
    title = self.font_large.render("TOP 10 РЕКОРДОВ", True, UTM_GOLD)
    self.screen.blit(title, (SCREEN_WIDTH // 2 - 150, 50))
    
    y = 150
    for i, score in enumerate(self.high_scores, 1):
        text = self.font_medium.render(f"{i}. {score} очков", True, WHITE)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - 100, y))
        y += 50
    
    hint = self.font_small.render("Нажми ENTER для меню", True, YELLOW)
    self.screen.blit(hint, (SCREEN_WIDTH // 2 - 100, 700))
```

---

## 🔟 СЛУЧАЙНОЕ ПОЯВЛЕНИЕ STUDENTS

**Добавь случайное поведение:**
```python
def schedule_teacher_actions(self):
    """Запланировать движения учителя"""
    # 30% шанс что учитель заснёт
    if random.random() < 0.3:
        self.teacher.look_timer = 600  # 10 секунд!
    else:
        delay = random.randint(2, 5)
        self.teacher.look_timer = delay * FPS
    
    look_duration = random.randint(60, 180)
    self.teacher.look_duration = look_duration
```

---

## 1️⃣1️⃣ ИНВЕРТИРОВАННАЯ МЕХАНИКА (Сложная версия)

Учитель НЕ смотрит, если студент учится:

```python
def handle_game_click(self, pos: Tuple[int, int]):
    """Обработить клик в игре"""
    
    for button in self.buttons:
        if button.is_clicked(pos) and button.action:
            if button.action == "normal":
                self.student.current_activity = StudentActivity.NORMAL
                # Если учишься - учитель перестаёт смотреть
                if self.teacher.looking_at_student:
                    self.teacher.looking_at_student = False
                    self.add_message("Учитель больше не смотрит! Хорошая работа!", 120)
            
            elif self.teacher.looking_at_student:
                # Для других активностей - если смотрит, GAME OVER
                self.add_message("😱 ПОЙМАНА!", 180)
                self.state = GameState.GAME_OVER
                return
            else:
                # Но если не смотрит - можешь делать что угодно
                if button.action == "cheat":
                    self.score += 20
            
            break
```

---

## 1️⃣2️⃣ COMBO СИСТЕМА (Очень сложная)

```python
@dataclass
class ComboSystem:
    combo_count: int = 0
    combo_multiplier: float = 1.0
    combo_timer: int = 0
    combo_timeout: int = 180  # 3 сек

def update_combo(self):
    """Обновить комбо"""
    if self.combo_timer > 0:
        self.combo_timer -= 1
    else:
        if self.combo_count > 0:
            self.add_message(f"Комбо сбро! Было: x{self.combo_multiplier}", 60)
        self.combo_count = 0
        self.combo_multiplier = 1.0

def add_to_combo(self):
    """Добавить действие в комбо"""
    self.combo_count += 1
    self.combo_multiplier = 1.0 + (self.combo_count * 0.1)  # +10% за каждое
    self.combo_timer = self.combo_system.combo_timeout
    self.add_message(f"COMBO x{self.combo_multiplier:.1f}!", 90)
```

---

## Советы по использованию

1. ✅ Всегда сохраняй бэкап до изменений
2. ✅ Протестируй изменения перед использованием
3. ✅ Комбинируй несколько примеров для новых функций
4. ✅ Если что-то сломалось - верни последнюю рабочую версию
5. ✅ Читай ошибки в консоли - они подскажут что не так

## Нужна помощь?

1. Проверь синтаксис Python
2. Убедись что все импорты на месте
3. Смотри примеры в EXTENSIONS.md
4. Гугли ошибку + "pygame"

## Готово! 

Твоя игра теперь даже лучше! 🚀
