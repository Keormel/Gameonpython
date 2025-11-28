# 🎮 Примеры расширений игры

Этот файл содержит готовые код-примеры для добавления новых функций в игру.

## 1. Система уровней сложности

### Добавить в GameState:

```python
@dataclass
class Difficulty:
    name: str
    teacher_reaction_speed: float  # 0.5 = вдвое медленнее, 2.0 = вдвое быстрее
    max_time: int                  # макс время на уровень (в секундах)
    min_score: int                 # мин очки для прохода
```

### Использование в Game:

```python
class Game:
    def __init__(self):
        # ... существующий код ...
        self.difficulty = Difficulty(
            name="Normal",
            teacher_reaction_speed=1.0,
            max_time=30,
            min_score=0
        )
    
    def schedule_teacher_actions(self):
        """Запланировать движения учителя с учётом сложности"""
        delay = random.randint(2, 5)
        delay = int(delay / self.difficulty.teacher_reaction_speed)
        look_duration = random.randint(60, 180)
        
        self.teacher.look_timer = delay * FPS
        self.teacher.look_duration = look_duration
```

## 2. Система энергии студента

```python
@dataclass
class StudentStats:
    energy: int = 100  # 0-100
    stress: int = 0    # 0-100
    focus: int = 50    # 0-100
    caught_count: int = 0

class Student:
    def __init__(self):
        # ... существующий код ...
        self.stats = StudentStats()
    
    def perform_activity(self, activity: StudentActivity):
        """Выполнить активность со влиянием на статистику"""
        if activity == StudentActivity.CHEAT:
            self.stats.energy -= 5
            self.stats.stress += 10
            self.stats.focus -= 5
            
        elif activity == StudentActivity.GAMES:
            self.stats.energy -= 3
            self.stats.stress -= 5
            self.stats.focus -= 10
            
        elif activity == StudentActivity.SLEEP:
            self.stats.energy += 15
            self.stats.stress -= 10
            
        # Если энергия упадёт ниже 10 - студент спит и не может действовать
        if self.stats.energy < 10:
            self.current_activity = StudentActivity.SLEEP
            self.stats.energy = 0
```

## 3. Система множественных преподавателей

```python
@dataclass
class TeacherPersonality:
    name: str
    strictness: float       # 0.5-2.0
    attention_span: tuple   # (min_seconds, max_seconds)
    look_frequency: tuple   # (min_delay, max_delay)

class TeacherManager:
    PERSONALITIES = {
        "Строгий профессор": TeacherPersonality(
            name="Dr. Petrov",
            strictness=2.0,
            attention_span=(2, 5),
            look_frequency=(2, 4)
        ),
        "Рассеянный лектор": TeacherPersonality(
            name="Prof. Smirnov",
            strictness=0.5,
            attention_span=(1, 2),
            look_frequency=(5, 10)
        ),
        "Нормальный учитель": TeacherPersonality(
            name="Mr. Ivanov",
            strictness=1.0,
            attention_span=(2, 4),
            look_frequency=(3, 6)
        ),
    }
    
    @staticmethod
    def create_random_teacher():
        """Создать случайного преподавателя"""
        personality = random.choice(list(TeacherManager.PERSONALITIES.values()))
        return Teacher(personality=personality)

class Teacher:
    def __init__(self, personality: TeacherPersonality = None):
        # ... существующий код ...
        self.personality = personality or TeacherPersonality("Default", 1.0, (2,4), (3,6))
    
    def schedule_actions(self):
        """Запланировать действия с учётом личности"""
        min_delay, max_delay = self.personality.look_frequency
        delay = random.randint(min_delay, max_delay)
        
        min_look, max_look = self.personality.attention_span
        look_duration = random.randint(min_look, max_look)
        
        self.look_timer = delay * FPS
        self.look_duration = look_duration * FPS
```

## 4. Система достижений

```python
@dataclass
class Achievement:
    id: str
    name: str
    description: str
    icon: str
    condition: callable

class AchievementSystem:
    ACHIEVEMENTS = [
        Achievement(
            id="first_cheat",
            name="Первый прогул",
            description="Успешно списал ответ",
            icon="📝",
            condition=lambda game: game.student.stats.caught_count == 0 and game.score >= 20
        ),
        Achievement(
            id="speed_demon",
            name="Скоростной тип",
            description="Набрал 200 очков за 30 секунд",
            icon="🚀",
            condition=lambda game: game.score >= 200 and game.time_remaining > 0
        ),
        Achievement(
            id="survival_master",
            name="Мастер выживания",
            description="Пережил 3 мин без поимки",
            icon="🛡️",
            condition=lambda game: game.game_time >= 180 * FPS
        ),
    ]
    
    def __init__(self):
        self.unlocked = set()
    
    def check_achievements(self, game):
        """Проверить условия достижений"""
        for achievement in self.ACHIEVEMENTS:
            if achievement.id not in self.unlocked:
                if achievement.condition(game):
                    self.unlock(achievement)
    
    def unlock(self, achievement: Achievement):
        """Разблокировать достижение"""
        self.unlocked.add(achievement.id)
        print(f"Achievement Unlocked: {achievement.name}! {achievement.icon}")
```

## 5. Таблица рекордов

```python
import json
from pathlib import Path

class Scoreboard:
    SCOREBOARD_FILE = "scoreboard.json"
    MAX_SCORES = 10
    
    def __init__(self):
        self.scores = self.load_scores()
    
    def load_scores(self):
        """Загрузить рекорды из файла"""
        if Path(self.SCOREBOARD_FILE).exists():
            with open(self.SCOREBOARD_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def save_scores(self):
        """Сохранить рекорды в файл"""
        with open(self.SCOREBOARD_FILE, 'w') as f:
            json.dump(self.scores, f, indent=2)
    
    def add_score(self, name: str, score: int, time: int):
        """Добавить новый рекорд"""
        entry = {
            'name': name,
            'score': score,
            'time': time,
            'date': str(datetime.now())
        }
        
        self.scores.append(entry)
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:self.MAX_SCORES]
        self.save_scores()
    
    def is_high_score(self, score: int):
        """Проверить, является ли это высоким рекордом"""
        return len(self.scores) < self.MAX_SCORES or score > self.scores[-1]['score']
```

## 6. Мини-игры на переменах

```python
class MiniGame:
    @staticmethod
    def typing_speed_test(duration=5):
        """Тест скорости печати"""
        words = ["python", "pygame", "university", "exam", "cheat"]
        target_word = random.choice(words)
        # Реализация игры...
        return random.randint(50, 200)  # очки
    
    @staticmethod
    def reaction_time_game(duration=3):
        """Тест реакции"""
        # Реализация игры...
        return random.randint(30, 150)  # очки
    
    @staticmethod
    def memory_game(duration=10):
        """Игра на память"""
        # Реализация игры...
        return random.randint(20, 100)  # очки
```

## 7. Система подсказок

```python
class HintSystem:
    HINTS = [
        "Смотри за глазами учителя!",
        "Красные глаза = учитель смотрит на тебя!",
        "Зелёные глаза = можно действовать!",
        "Списывание даёт больше всего очков!",
        "Быстро нажимай кнопку перед тем как учитель посмотрит!",
        "Обычная учёба безопасна, но скучна (0 очков)",
        "Не все активности дают одинаковые очки",
    ]
    
    @staticmethod
    def get_random_hint():
        return random.choice(HintSystem.HINTS)
    
    @staticmethod
    def show_hint(screen, font):
        hint = HintSystem.get_random_hint()
        hint_surface = font.render(f"Подсказка: {hint}", True, YELLOW)
        screen.blit(hint_surface, (20, SCREEN_HEIGHT - 30))
```

## 8. Система сохранения прогресса

```python
import pickle

class SaveManager:
    SAVE_FILE = "game_save.pkl"
    
    @staticmethod
    def save_game(game):
        """Сохранить текущее состояние игры"""
        save_data = {
            'score': game.score,
            'time_remaining': game.time_remaining,
            'student_activity': game.student.current_activity,
            'achievements': game.achievements.unlocked,
        }
        with open(SaveManager.SAVE_FILE, 'wb') as f:
            pickle.dump(save_data, f)
    
    @staticmethod
    def load_game(game):
        """Загрузить сохранённое состояние игры"""
        if Path(SaveManager.SAVE_FILE).exists():
            with open(SaveManager.SAVE_FILE, 'rb') as f:
                save_data = pickle.load(f)
                game.score = save_data['score']
                game.time_remaining = save_data['time_remaining']
                return True
        return False
```

## 9. Система предметов (Power-ups)

```python
@dataclass
class PowerUp:
    name: str
    description: str
    icon: str
    effect: callable
    duration: int  # в кадрах

class PowerUpManager:
    POWER_UPS = {
        "invisible": PowerUp(
            name="Невидимость",
            description="Учитель не может видеть на 10 сек",
            icon="👻",
            effect=lambda game: setattr(game.teacher, 'blind', True),
            duration=10 * FPS
        ),
        "slow_time": PowerUp(
            name="Замедление времени",
            description="Время идёт медленнее на 5 сек",
            icon="⏱️",
            effect=lambda game: None,  # Замедлить таймер
            duration=5 * FPS
        ),
        "extra_points": PowerUp(
            name="Двойные очки",
            description="Следующее действие даёт двойные очки",
            icon="2️⃣",
            effect=lambda game: setattr(game, 'double_points', True),
            duration=1 * FPS
        ),
    }
    
    def __init__(self):
        self.active_powerups = []
    
    def activate_powerup(self, powerup_key: str):
        """Активировать power-up"""
        powerup = self.POWER_UPS[powerup_key]
        self.active_powerups.append((powerup, powerup.duration))
```

## 10. Система мультиплеера (локальная сеть)

```python
import socket
import threading

class MultiplayerManager:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.clients = []
    
    def start_server(self):
        """Запустить сервер для мультиплеера"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(2)
        print(f"Server started at {self.host}:{self.port}")
        
        # Использовать threading для принятия подключений...
    
    def send_game_state(self, game_state):
        """Отправить состояние игры другим игрокам"""
        # Сериализировать и отправить...
        pass
```

## Как использовать эти примеры

1. Скопируйте нужный блок кода
2. Интегрируйте в `main.py`
3. Добавьте необходимые импорты
4. Протестируйте функциональность
5. Отладьте ошибки

## Сложность реализации

- ⭐ Система уровней - легко
- ⭐ Энергия студента - легко
- ⭐⭐ Множественные преподаватели - средне
- ⭐⭐ Достижения - средне
- ⭐⭐⭐ Мультиплеер - сложно
- ⭐⭐⭐ Сохранение - сложно

Начните с простых расширений и постепенно добавляйте более сложную функциональность!
