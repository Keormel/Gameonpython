import pygame
import random
import sys
import json
import os
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Инициализация Pygame
pygame.init()

# Константы - мобильный формат 9:16 (540x960)
SCREEN_WIDTH = 540
SCREEN_HEIGHT = 960
FPS = 60
IS_MOBILE = True

# Границы безопасной области для элементов (отступ от краев)
SAFE_MARGIN = 5
SAFE_LEFT = SAFE_MARGIN
SAFE_RIGHT = SCREEN_WIDTH - SAFE_MARGIN
SAFE_TOP = SAFE_MARGIN
SAFE_BOTTOM = SCREEN_HEIGHT - SAFE_MARGIN
SAFE_WIDTH = SAFE_RIGHT - SAFE_LEFT
SAFE_HEIGHT = SAFE_BOTTOM - SAFE_TOP

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
RED = (220, 50, 50)
DARK_RED = (180, 30, 30)
GREEN = (50, 200, 50)
DARK_GREEN = (30, 150, 30)
BLUE = (50, 100, 200)
LIGHT_BLUE = (100, 150, 255)
YELLOW = (255, 220, 0)
ORANGE = (255, 140, 0)
UTM_PURPLE = (102, 51, 153)
UTM_DARK_PURPLE = (70, 35, 105)
UTM_GOLD = (255, 184, 28)
SKIN = (255, 220, 177)
LIGHT_BROWN = (180, 140, 100)
CREAM = (250, 248, 245)
DARK_CREAM = (240, 235, 225)

class GameState(Enum):
    MAIN_MENU = 1
    DIFFICULTY_MENU = 2
    GAME = 3
    GAME_OVER = 4
    WIN = 5

class StudentActivity(Enum):
    NORMAL = 1
    CHEAT = 2
    GAMES = 3
    SLEEP = 4
    EAT = 5

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    IMPOSSIBLE = 4

@dataclass
class Student:
    """Главный герой - студент"""
    x: float = 400
    y: float = 500
    current_activity: StudentActivity = StudentActivity.NORMAL
    score: int = 0
    activity_progress: int = 0  # 0-100
    activity_timer: int = 0
    activity_duration: int = 0  # Длительность в кадрах
    
    # Счётчики использования каждого действия (по 1 разу)
    cheat_used: bool = False
    games_used: bool = False
    sleep_used: bool = False
    eat_used: bool = False
    
    # Длительности активностей (в кадрах при 60 FPS)
    ACTIVITY_DURATIONS = {
        StudentActivity.NORMAL: 0,      # Мгновенно
        StudentActivity.CHEAT: 180,     # 3 секунды (3 * 60)
        StudentActivity.GAMES: 120,     # 2 секунды (2 * 60)
        StudentActivity.SLEEP: 240,     # 4 секунды (4 * 60)
        StudentActivity.EAT: 150,       # 2.5 секунды (2.5 * 60)
    }
    
    def start_activity(self, activity: StudentActivity):
        """Начать новую активность"""
        self.current_activity = activity
        self.activity_timer = 0
        self.activity_progress = 0
        self.activity_duration = self.ACTIVITY_DURATIONS[activity]
    
    def update_activity(self):
        """Обновить прогресс активности"""
        if self.activity_duration > 0 and self.activity_timer < self.activity_duration:
            self.activity_timer += 1
            self.activity_progress = int((self.activity_timer / self.activity_duration) * 100)
            return False  # Активность ещё выполняется
        else:
            self.current_activity = StudentActivity.NORMAL
            self.activity_progress = 0
            self.activity_timer = 0
            return True  # Активность завершена
    
    def draw(self, screen: pygame.Surface):
        """Нарисовать студента"""
        # Голова
        pygame.draw.circle(screen, SKIN, (int(self.x), int(self.y - 20)), 12)
        
        # Туловище
        pygame.draw.rect(screen, BLUE, (int(self.x - 15), int(self.y), 30, 40))
        
        # Руки
        pygame.draw.line(screen, SKIN, (int(self.x - 15), int(self.y + 5)), 
                        (int(self.x - 30), int(self.y + 10)), 4)
        pygame.draw.line(screen, SKIN, (int(self.x + 15), int(self.y + 5)), 
                        (int(self.x + 30), int(self.y + 10)), 4)
        
        # Ноги
        pygame.draw.line(screen, DARK_GRAY, (int(self.x - 10), int(self.y + 40)), 
                        (int(self.x - 10), int(self.y + 60)), 3)
        pygame.draw.line(screen, DARK_GRAY, (int(self.x + 10), int(self.y + 40)), 
                        (int(self.x + 10), int(self.y + 60)), 3)
        
        # Иконка текущей активности над головой
        icons = {
            StudentActivity.NORMAL: "[STUDY]",
            StudentActivity.CHEAT: "[CHEAT]",
            StudentActivity.GAMES: "[GAMES]",
            StudentActivity.SLEEP: "[SLEEP]",
            StudentActivity.EAT: "[EAT]",
        }
        
        icon = icons.get(self.current_activity, "")
        if icon:
            font = pygame.font.Font(None, 28)
            icon_text = font.render(icon, True, BLACK)
            screen.blit(icon_text, (int(self.x - 15), int(self.y - 50)))
        
        # Прогресс-бар активности
        if self.activity_duration > 0 and self.activity_progress > 0:
            bar_width = 40
            bar_height = 5
            bar_x = int(self.x - bar_width // 2)
            bar_y = int(self.y - 65)
            
            # Фон прогресс-бара
            pygame.draw.rect(screen, LIGHT_GRAY, (bar_x, bar_y, bar_width, bar_height))
            
            # Заполненная часть
            filled_width = int(bar_width * self.activity_progress / 100)
            color = GREEN if self.activity_progress < 100 else ORANGE
            pygame.draw.rect(screen, color, (bar_x, bar_y, filled_width, bar_height))

@dataclass
class Teacher:
    """Учитель, следящий за студентом"""
    x: float = 1000
    y: float = 150
    looking_at_student: bool = False
    look_timer: int = 0
    look_duration: int = 0
    
    def draw(self, screen: pygame.Surface):
        """Нарисовать учителя"""
        # Голова
        pygame.draw.circle(screen, LIGHT_BROWN, (int(self.x), int(self.y - 25)), 15)
        
        # Туловище
        pygame.draw.rect(screen, (139, 69, 19), (int(self.x - 20), int(self.y), 40, 50))
        
        # Руки
        pygame.draw.line(screen, LIGHT_BROWN, (int(self.x - 20), int(self.y + 10)), 
                        (int(self.x - 40), int(self.y + 15)), 5)
        pygame.draw.line(screen, LIGHT_BROWN, (int(self.x + 20), int(self.y + 10)), 
                        (int(self.x + 40), int(self.y + 15)), 5)
        
        # Ноги
        pygame.draw.line(screen, DARK_GRAY, (int(self.x - 10), int(self.y + 50)), 
                        (int(self.x - 10), int(self.y + 80)), 4)
        pygame.draw.line(screen, DARK_GRAY, (int(self.x + 10), int(self.y + 50)), 
                        (int(self.x + 10), int(self.y + 80)), 4)
        
        # Глаза - если смотрит на студента, то красные
        eye_color = RED if self.looking_at_student else BLACK
        pygame.draw.circle(screen, eye_color, (int(self.x - 7), int(self.y - 28)), 4)
        pygame.draw.circle(screen, eye_color, (int(self.x + 7), int(self.y - 28)), 4)
        
        # Указатель внимания
        if self.looking_at_student:
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y - 50)), 12, 3)

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, action: Optional[str] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        # Современный стиль с тенью и скруглением
        color = UTM_GOLD if self.hovered else UTM_PURPLE
        hover_color = ORANGE if self.hovered else UTM_DARK_PURPLE
        
        # Тень кнопки
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(screen, (0, 0, 0, 50), shadow_rect, border_radius=15)
        
        # Основная кнопка с границей
        pygame.draw.rect(screen, color, self.rect, border_radius=15)
        pygame.draw.rect(screen, hover_color, self.rect, 3, border_radius=15)
        
        # Эффект при наведении
        if self.hovered:
            pygame.draw.rect(screen, YELLOW, self.rect, 1, border_radius=15)
        
        # Многострочный текст
        lines = self.text.split('\n')
        
        # Мобильные размеры - мельче шрифт для узких кнопок
        line_spacing = 16
        total_height = len(lines) * line_spacing
        y_start = self.rect.centery - total_height // 2
        
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, WHITE)
            text_rect = text_surface.get_rect(center=(self.rect.centerx, y_start + i * line_spacing))
            screen.blit(text_surface, text_rect)
        
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos: Tuple[int, int]):
        self.hovered = self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("UTM Cheating Simulator - Списывай, пока не видит!")
        self.clock = pygame.time.Clock()
        
        # Адаптивные размеры шрифтов для мобильного
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        self.state = GameState.MAIN_MENU
        self.student = Student()
        self.teacher = Teacher()
        self.score = 0
        self.time_remaining = 0
        self.game_time = 0
        self.buttons: List[Button] = []
        self.messages: List[Tuple[str, int]] = []
        
        # Параметры сложности
        self.difficulty = Difficulty.EASY
        self.teacher_look_chance = 15  # Вероятность в процентах
        
        # Словарь параметров сложности
        self.difficulty_settings = {
            Difficulty.EASY: {"time": 30, "chance": 15, "name": "ЛЕГКИЙ", "description": "30 сек, 15% риск"},
            Difficulty.MEDIUM: {"time": 45, "chance": 30, "name": "СРЕДНИЙ", "description": "45 сек, 30% риск"},
            Difficulty.HARD: {"time": 45, "chance": 40, "name": "СЛОЖНЫЙ", "description": "45 сек, 40% риск"},
            Difficulty.IMPOSSIBLE: {"time": 50, "chance": 50, "name": "НЕВОЗМОЖНЫЙ", "description": "50 сек, 50% риск"},
        }
        
        # Лучший счет игрока
        self.best_score = 0
        self.scores_file = "scores.json"
        self.load_best_score()
        
        self.create_menu_buttons()
    
    def load_best_score(self):
        """Загрузить лучший счет из файла"""
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r') as f:
                    data = json.load(f)
                    self.best_score = data.get('best_score', 0)
            else:
                self.best_score = 0
        except:
            self.best_score = 0
    
    def save_best_score(self):
        """Сохранить лучший счет в файл"""
        try:
            data = {'best_score': self.best_score}
            with open(self.scores_file, 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def update_best_score(self, score: int):
        """Обновить лучший счет если текущий выше"""
        if score > self.best_score:
            self.best_score = score
            self.save_best_score()
    
    def create_menu_buttons(self):
        """Создать кнопки главного меню"""
        button_width = 280
        button_height = 70
        spacing = 110
        x = SCREEN_WIDTH // 2 - button_width // 2
        
        # Расчет Y позиции для центрирования кнопок вертикально
        total_height = button_height * 3 + spacing * 2
        start_y = (SCREEN_HEIGHT - total_height) // 2
        
        self.buttons = [
            Button(x, start_y, button_width, button_height, "НАЧАТЬ ИГРУ", action="start"),
            Button(x, start_y + spacing, button_width, button_height, "ПРАВИЛА", action="rules"),
            Button(x, start_y + spacing * 2, button_width, button_height, "ВЫХОД", action="exit"),
        ]
    
    def create_difficulty_buttons(self):
        """Создать кнопки выбора сложности"""
        button_width = 280
        button_height = 70
        spacing = 110
        x = SCREEN_WIDTH // 2 - button_width // 2
        
        # Расчет Y позиции для центрирования кнопок вертикально
        total_height = button_height * 5 + spacing * 4
        start_y = (SCREEN_HEIGHT - total_height) // 2
        
        self.buttons = [
            Button(x, start_y, button_width, button_height, "ЛЕГКИЙ\n30 сек, 15% риск", action="easy"),
            Button(x, start_y + spacing, button_width, button_height, "СРЕДНИЙ\n45 сек, 30% риск", action="medium"),
            Button(x, start_y + spacing * 2, button_width, button_height, "СЛОЖНЫЙ\n45 сек, 40% риск", action="hard"),
            Button(x, start_y + spacing * 3, button_width, button_height, "НЕВОЗМОЖНЫЙ\n50 сек, 50% риск", action="impossible"),
            Button(x, start_y + spacing * 4, button_width, button_height, "← НАЗАД", action="back"),
        ]
    
    def create_game_buttons(self):
        """Создать кнопки активностей в игре"""
        button_width = 90
        button_height = 70
        start_y = 800
        spacing_x = 100
        
        # Расчет начальной X позиции для центрирования
        total_width = button_width * 5 + spacing_x * 4
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        # ЖЕСТКИЕ ОГРАНИЧЕНИЯ: кнопки не должны выходить за экран
        # Проверяем левую границу
        if start_x < SAFE_LEFT:
            start_x = SAFE_LEFT
        
        # Проверяем правую границу (самая правая кнопка)
        last_button_right = start_x + spacing_x * 4 + button_width
        if last_button_right > SAFE_RIGHT:
            start_x = SAFE_RIGHT - (spacing_x * 4 + button_width)
        
        # Проверяем нижнюю границу
        if start_y + button_height > SAFE_BOTTOM:
            start_y = SAFE_BOTTOM - button_height
        
        # Проверяем верхнюю границу
        if start_y < SAFE_TOP:
            start_y = SAFE_TOP
        
        self.buttons = [
            Button(start_x, start_y, button_width, button_height, "\nСПИСАТЬ\n3 сек", action="cheat"),
            Button(start_x + spacing_x, start_y, button_width, button_height, "\nИГРАТЬ\n2 сек", action="games"),
            Button(start_x + spacing_x * 2, start_y, button_width, button_height, "\nСПАТЬ\n4 сек", action="sleep"),
            Button(start_x + spacing_x * 3, start_y, button_width, button_height, "\nЕСТЬ\n2.5 сек", action="eat"),
            Button(start_x + spacing_x * 4, start_y, button_width, button_height, "\nОтменить\nДействие", action="normal"),
        ]
        self.update_button_labels()
    
    def update_button_labels(self):
        """Обновить текст кнопок в зависимости от использованности"""
        if self.student.cheat_used:
            self.buttons[0].text = "\nСПИСАТЬ\nиспользовано"
        else:
            self.buttons[0].text = "\nСПИСАТЬ\n3 сек"
        
        if self.student.games_used:
            self.buttons[1].text = "\nИГРАТЬ\nиспользовано"
        else:
            self.buttons[1].text = "\nИГРАТЬ\n2 сек"
        
        if self.student.sleep_used:
            self.buttons[2].text = "\nСПАТЬ\nиспользовано"
        else:
            self.buttons[2].text = "nСПАТЬ\n4 сек"
        
        if self.student.eat_used:
            self.buttons[3].text = "\nЕСТЬ\nиспользовано"
        else:
            self.buttons[3].text = "\nЕСТЬ\n2.5 сек"
    
    def start_game(self):
        """Начать новую игру"""
        self.state = GameState.GAME
        self.student = Student(score=0)
        self.teacher = Teacher()
        self.score = 0
        self.game_time = 0
        
        # Установить параметры в зависимости от сложности
        settings = self.difficulty_settings[self.difficulty]
        self.time_remaining = settings["time"] * 60  # Перевести в фреймы
        self.teacher_look_chance = settings["chance"]
        
        self.messages = []
        self.create_game_buttons()
        
        difficulty_name = settings["name"]
        self.add_message(f"{difficulty_name} уровень! Списывай и не попадайся!", 120)
        self.schedule_teacher_actions()
    
    def schedule_teacher_actions(self):
        """Запланировать движения учителя"""
        delay = random.randint(2, 5)
        # Вероятность того, что учитель посмотрит на студента
        look_duration = random.randint(60, 180)
        self.teacher.look_timer = delay * FPS
        self.teacher.look_duration = look_duration
    
    def add_message(self, text: str, duration: int = 120):
        """Добавить сообщение на экран"""
        self.messages.append((text, duration))
    
    def draw_main_menu(self):
        """Отрисовать главное меню"""
        # Градиентный фон
        for y in range(SCREEN_HEIGHT):
            color_val = int(UTM_PURPLE[0] + (UTM_DARK_PURPLE[0] - UTM_PURPLE[0]) * y / SCREEN_HEIGHT)
            pygame.draw.line(self.screen, 
                           (color_val, int(UTM_PURPLE[1] + (UTM_DARK_PURPLE[1] - UTM_PURPLE[1]) * y / SCREEN_HEIGHT), 
                            int(UTM_PURPLE[2] + (UTM_DARK_PURPLE[2] - UTM_PURPLE[2]) * y / SCREEN_HEIGHT)),
                           (0, y), (SCREEN_WIDTH, y))
        
        # Заголовок (большой)
        title = self.font_large.render("UTM CHEATING", True, UTM_GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        title2 = self.font_medium.render("SIMULATOR", True, WHITE)
        title2_rect = title2.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(title2, title2_rect)
        
        # Подзаголовок
        subtitle = self.font_small.render("Списывай пока не видит!", True, YELLOW)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Декоративная линия
        pygame.draw.line(self.screen, UTM_GOLD, (SCREEN_WIDTH // 2 - 80, 200), 
                        (SCREEN_WIDTH // 2 + 80, 200), 2)
        
        # Кнопки
        for button in self.buttons:
            button.draw(self.screen, self.font_small)
        
        # Лучший счет внизу экрана
        best_score_text = self.font_small.render(f"Лучший счет: {self.best_score}", True, UTM_GOLD)
        best_score_rect = best_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 730))
        
        # Фон для счета
        bg_rect = best_score_rect.inflate(30, 20)
        pygame.draw.rect(self.screen, (0, 0, 0, 50), bg_rect, border_radius=10)
        pygame.draw.rect(self.screen, UTM_GOLD, bg_rect, 2, border_radius=10)
        
        self.screen.blit(best_score_text, best_score_rect)
    
    def draw_difficulty_menu(self):
        """Отрисовать меню выбора сложности"""
        # Градиентный фон
        for y in range(SCREEN_HEIGHT):
            color_val = int(UTM_DARK_PURPLE[0] + (UTM_PURPLE[0] - UTM_DARK_PURPLE[0]) * y / SCREEN_HEIGHT)
            pygame.draw.line(self.screen, 
                           (color_val, int(UTM_DARK_PURPLE[1] + (UTM_PURPLE[1] - UTM_DARK_PURPLE[1]) * y / SCREEN_HEIGHT), 
                            int(UTM_DARK_PURPLE[2] + (UTM_PURPLE[2] - UTM_DARK_PURPLE[2]) * y / SCREEN_HEIGHT)),
                           (0, y), (SCREEN_WIDTH, y))
        
        # Заголовок
        title = self.font_large.render("ВЫБЕРИ СЛОЖНОСТЬ", True, UTM_GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)
        
        # Декоративная линия
        pygame.draw.line(self.screen, UTM_GOLD, (SCREEN_WIDTH // 2 - 100, 100), 
                        (SCREEN_WIDTH // 2 + 100, 100), 2)
        
        # Кнопки
        for button in self.buttons:
            button.draw(self.screen, self.font_small)
    
    def draw_game(self):
        """Отрисовать игровой экран"""
        # Красивый фон
        self.screen.fill(CREAM)
        
        # Градиент неба
        for y in range(SCREEN_HEIGHT // 2):
            color_val = int(LIGHT_BLUE[0] + (CREAM[0] - LIGHT_BLUE[0]) * y / (SCREEN_HEIGHT // 2))
            pygame.draw.line(self.screen, 
                           (color_val, int(LIGHT_BLUE[1] + (CREAM[1] - LIGHT_BLUE[1]) * y / (SCREEN_HEIGHT // 2)), 
                            int(LIGHT_BLUE[2] + (CREAM[2] - LIGHT_BLUE[2]) * y / (SCREEN_HEIGHT // 2))),
                           (0, y), (SCREEN_WIDTH, y))
        
        # Мобильный макет (вертикальный)
        # Парта учителя (вверху, маленькая)
        pygame.draw.rect(self.screen, LIGHT_BROWN, (SCREEN_WIDTH - 130, 200, 120, 90))
        pygame.draw.rect(self.screen, BLACK, (SCREEN_WIDTH - 130, 200, 120, 90), 2)
        
        # Парта студента (ниже, поближе к кнопкам)
        pygame.draw.rect(self.screen, (200, 150, 100), (15, 600, 510, 120))
        pygame.draw.rect(self.screen, BLACK, (15, 600, 510, 120), 2)
        
        # Позиции персонажей с ограничениями
        self.student.x = max(SAFE_LEFT + 30, min(SAFE_RIGHT - 30, SCREEN_WIDTH // 2))
        self.student.y = max(SAFE_TOP + 30, min(SAFE_BOTTOM - 60, 650))
        self.teacher.x = max(SAFE_LEFT + 30, min(SAFE_RIGHT - 30, SCREEN_WIDTH - 70))
        self.teacher.y = max(SAFE_TOP + 30, min(SAFE_BOTTOM - 80, 250))
        
        # Рисуем персонажей
        self.student.draw(self.screen)
        self.teacher.draw(self.screen)
        
        # UI сверху
        self.draw_ui()
        
        # Сообщения
        self.draw_messages()
        
        # Кнопки активностей (внизу, в линию)
        for button in self.buttons:
            button.draw(self.screen, self.font_small)
    
    def draw_ui(self):
        """Отрисовать UI элементы"""
        # Мобильный UI - компактнее
        # Фон для информации
        pygame.draw.rect(self.screen, UTM_DARK_PURPLE, (0, 0, SCREEN_WIDTH, 100))
        pygame.draw.line(self.screen, UTM_GOLD, (0, 100), (SCREEN_WIDTH, 100), 2)
        
        # Очки (слева)
        score_text = f"Очки: {self.score}"
        score_surface = self.font_medium.render(score_text, True, UTM_GOLD)
        self.screen.blit(score_surface, (15, 15))
        
        # Время (справа)
        time_sec = self.time_remaining // FPS
        time_text = f"Время: {time_sec}s"
        time_color = RED if time_sec < 10 else YELLOW
        time_surface = self.font_medium.render(time_text, True, time_color)
        time_rect = time_surface.get_rect(topright=(SCREEN_WIDTH - 15, 15))
        self.screen.blit(time_surface, time_rect)
        
        # Статус учителя (по центру)
        teacher_status = "[WARNING] УЧИТЕЛЬ СМОТРИТ!" if self.teacher.looking_at_student else "[OK] БЕЗОПАСНО"
        teacher_color = RED if self.teacher.looking_at_student else GREEN
        teacher_text = self.font_small.render(teacher_status, True, teacher_color)
        teacher_rect = teacher_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
        
        # Фон статуса
        status_bg = teacher_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (0, 0, 0, 50), status_bg, border_radius=5)
        pygame.draw.rect(self.screen, teacher_color, status_bg, 2, border_radius=5)
        self.screen.blit(teacher_text, teacher_rect)
    
    def draw_messages(self):
        """Отрисовать сообщения"""
        message_y = 200
        max_messages = 2
        
        for i, (msg_text, _) in enumerate(self.messages[:max_messages]):
            msg_surface = self.font_small.render(msg_text, True, BLACK)
            msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, message_y))
            
            # Фон сообщения
            bg_rect = msg_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, YELLOW, bg_rect, border_radius=10)
            pygame.draw.rect(self.screen, ORANGE, bg_rect, 2, border_radius=10)
            
            self.screen.blit(msg_surface, msg_rect)
            message_y += 50
    
    def draw_game_over(self):
        """Отрисовать экран Game Over"""
        # Полупрозрачное затемнение
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(RED)
        self.screen.blit(overlay, (0, 0))
        
        title = self.font_large.render("ПОЙМАЛИ!", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        message = self.font_small.render("Учитель увидел твою активность!", True, WHITE)
        message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(message, message_rect)
        
        score_text = self.font_medium.render(f"Очки: {self.score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        self.screen.blit(score_text, score_rect)
        
        hint = self.font_small.render("Нажми ENTER для меню", True, WHITE)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.screen.blit(hint, hint_rect)
    
    def draw_win(self):
        """Отрисовать экран победы"""
        # Градиент победы
        for y in range(SCREEN_HEIGHT):
            color_val = int(GREEN[0] + (DARK_GREEN[0] - GREEN[0]) * y / SCREEN_HEIGHT)
            pygame.draw.line(self.screen,
                           (color_val, int(GREEN[1] + (DARK_GREEN[1] - GREEN[1]) * y / SCREEN_HEIGHT),
                            int(GREEN[2] + (DARK_GREEN[2] - GREEN[2]) * y / SCREEN_HEIGHT)),
                           (0, y), (SCREEN_WIDTH, y))
        
        title = self.font_large.render("УСПЕХ!", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        message = self.font_small.render("Ты пережил экзамен безнаказанно!", True, WHITE)
        message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(message, message_rect)
        
        score_text = self.font_large.render(f"Счёт: {self.score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        self.screen.blit(score_text, score_rect)
        
        hint = self.font_small.render("Нажми ENTER для меню", True, WHITE)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.screen.blit(hint, hint_rect)
    
    def handle_menu_click(self, pos: Tuple[int, int]):
        """Обработить клик в меню"""
        for button in self.buttons:
            if button.is_clicked(pos):
                if button.action == "start":
                    self.state = GameState.DIFFICULTY_MENU
                    self.create_difficulty_buttons()
                elif button.action == "rules":
                    self.add_message("[RULES] Правила: Скрывай активности! Если учитель увидит - ты поймана! [RULES]", 240)
                elif button.action == "exit":
                    return False
        return True
    
    def handle_difficulty_click(self, pos: Tuple[int, int]):
        """Обработить клик в меню выбора сложности"""
        difficulty_map = {
            "easy": Difficulty.EASY,
            "medium": Difficulty.MEDIUM,
            "hard": Difficulty.HARD,
            "impossible": Difficulty.IMPOSSIBLE,
        }
        
        for button in self.buttons:
            if button.is_clicked(pos):
                if button.action in difficulty_map:
                    self.difficulty = difficulty_map[button.action]
                    self.start_game()
                elif button.action == "back":
                    self.state = GameState.MAIN_MENU
                    self.create_menu_buttons()
        return True
    
    def handle_game_click(self, pos: Tuple[int, int]):
        """Обработить клик в игре"""
        if self.teacher.looking_at_student:
            # Если студент в процессе выполнения активности и учитель смотрит - поймали
            if self.student.activity_duration > 0:
                self.update_best_score(self.score)
                self.add_message("[CAUGHT] ПОЙМАНА! Учитель заметил!", 180)
                self.state = GameState.GAME_OVER
            return
        
        for button in self.buttons:
            if button.is_clicked(pos) and button.action:
                # Маппинг кнопок на активности
                action_map = {
                    "cheat": StudentActivity.CHEAT,
                    "games": StudentActivity.GAMES,
                    "sleep": StudentActivity.SLEEP,
                    "eat": StudentActivity.EAT,
                }
                
                if button.action in action_map:
                    target_activity = action_map[button.action]
                    used_flags = {
                        "cheat": self.student.cheat_used,
                        "games": self.student.games_used,
                        "sleep": self.student.sleep_used,
                        "eat": self.student.eat_used,
                    }
                    
                    # Проверяем, использовалось ли это действие уже
                    if used_flags.get(button.action, False):
                        self.add_message("[ERROR] Это действие уже использовано!", 100)
                        break
                    
                    # Если было активное действие - прерываем его
                    if self.student.activity_duration > 0:
                        self.add_message("[WARNING] Прервала предыдущее действие!", 100)
                    
                    # Помечаем действие как использованное
                    if button.action == "cheat":
                        self.student.cheat_used = True
                    elif button.action == "games":
                        self.student.games_used = True
                    elif button.action == "sleep":
                        self.student.sleep_used = True
                    elif button.action == "eat":
                        self.student.eat_used = True
                    
                    # Начинаем новое действие
                    self.student.start_activity(target_activity)
                    
                    # Сообщения
                    messages = {
                        "cheat": "[CHEAT] Начала списывать ответ! (3 сек)",
                        "games": "[GAMES] Начала играть в телефон! (2 сек)",
                        "sleep": "[SLEEP] Начала спать! (4 сек)",
                        "eat": "[EAT] Начала есть! (2.5 сек)",
                    }
                    self.add_message(messages.get(button.action, ""), 120)
                
                elif button.action == "normal":
                    # "УЧИТЬ" - прерывает любое действие
                    if self.student.activity_duration > 0:
                        self.add_message("[STOP] Остановила запрещённое действие!", 100)
                    
                    self.student.current_activity = StudentActivity.NORMAL
                    self.student.activity_duration = 0
                    self.student.activity_timer = 0
                    self.add_message("[STUDY] Решаю задачу как положено...", 120)
                break
    
    def handle_click(self, pos: Tuple[int, int]):
        """Обработить клик мыши"""
        if self.state == GameState.MAIN_MENU:
            return self.handle_menu_click(pos)
        elif self.state == GameState.DIFFICULTY_MENU:
            return self.handle_difficulty_click(pos)
        elif self.state == GameState.GAME:
            self.handle_game_click(pos)
        elif self.state in [GameState.GAME_OVER, GameState.WIN]:
            pass
        return True
    
    def handle_key(self, key):
        """Обработить нажатие клавиши"""
        if key == pygame.K_RETURN:
            if self.state in [GameState.GAME_OVER, GameState.WIN]:
                self.state = GameState.MAIN_MENU
                self.create_menu_buttons()
    
    def update(self):
        """Обновить состояние игры"""
        if self.state == GameState.GAME:
            # Обновить сообщения
            self.messages = [(msg, time - 1) for msg, time in self.messages if time > 0]
            
            # Обновить метки кнопок
            self.update_button_labels()
            
            # Сохранить активность ДО обновления
            was_activity = self.student.current_activity
            
            # Обновить активность студента
            activity_completed = self.student.update_activity()
            
            # Если активность завершена - дать очки
            if activity_completed and was_activity != StudentActivity.NORMAL:
                activity = was_activity
                points = {
                    StudentActivity.CHEAT: 20,
                    StudentActivity.GAMES: 10,
                    StudentActivity.SLEEP: 5,
                    StudentActivity.EAT: 5,
                    StudentActivity.NORMAL: 0,
                }
                self.score += points.get(activity, 0)
                if points.get(activity, 0) > 0:
                    self.add_message(f"[SUCCESS] Успешно! +{points[activity]} очков", 120)
            
            # Обновить время
            self.time_remaining -= 1
            self.game_time += 1
            
            # Проверить конец времени
            if self.time_remaining <= 0:
                self.update_best_score(self.score)
                self.state = GameState.WIN
                self.add_message("[WIN] Время вышло! Ты выжил!", 240)
                return
            
            # Обновить состояние учителя
            if self.teacher.look_timer > 0:
                self.teacher.look_timer -= 1
            else:
                # Проверить вероятность того, что учитель посмотрит
                if random.randint(1, 100) <= self.teacher_look_chance:
                    # Учитель начинает смотреть
                    self.teacher.looking_at_student = True
                    
                    # Проверить - поймана ли студентка?
                    if self.student.activity_duration > 0:
                        self.update_best_score(self.score)
                        self.add_message("[CAUGHT] ПОЙМАНА! Учитель заметил активность!", 180)
                        self.state = GameState.GAME_OVER
                        return
                
                if self.teacher.look_duration > 0:
                    self.teacher.look_duration -= 1
                else:
                    # Прекратить смотреть
                    self.teacher.looking_at_student = False
                    self.schedule_teacher_actions()
        
        # Обновить позицию мыши для наведения
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update_hover(mouse_pos)
    
    def draw(self):
        """Отрисовать кадр"""
        if self.state == GameState.MAIN_MENU:
            self.draw_main_menu()
        elif self.state == GameState.DIFFICULTY_MENU:
            self.draw_difficulty_menu()
        elif self.state == GameState.GAME:
            self.draw_game()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.WIN:
            self.draw_win()
        
        pygame.display.flip()
    
    def run(self):
        """Главный цикл игры"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        running = self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
