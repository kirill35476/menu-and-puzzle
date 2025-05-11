import sys
import abc
import pygame
import random
import os

pygame.init()
size = (1280, 720)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Игровое меню")
BACKGROUND = (190, 190, 130)
FPS = 60
clock = pygame.time.Clock()
font = pygame.font.SysFont('Impact', 64)
menu_font = pygame.font.SysFont('Impact', 48)


class State(abc.ABC):
    @abc.abstractmethod
    def handle_events(self, events):
        pass

    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def draw(self, screen):
        pass


class SplashScreen(State):
    def __init__(self):
        self.text = 'Заставка'
        self.surface = font.render(self.text, True, (255, 255, 255))
        self.hint = 'Нажмите для продолжения'
        self.hint_surface = menu_font.render(self.hint, True, (200, 200, 200))
        self.hint_visible = True
        self.hint_time = pygame.time.get_ticks()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                return MainMenu()
        return self

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.hint_time > 800:
            self.hint_visible = not self.hint_visible
            self.hint_time = current_time

    def draw(self, screen):
        screen.fill(BACKGROUND)
        rect = self.surface.get_rect(center=(size[0] // 2, size[1] // 2 - 100))
        screen.blit(self.surface, rect)
        if self.hint_visible:
            hint_rect = self.hint_surface.get_rect(center=(size[0] // 2, size[1] // 2 + 100))
            screen.blit(self.hint_surface, hint_rect)


class MainMenu(State):
    def __init__(self):
        self.options = ["Играть", "Выбрать имя", "Выйти"]
        self.selected = 0
        self.title = font.render("Главное меню", True, (255, 255, 255))
        self.hint = menu_font.render("Используйте ПРОБЕЛ для выбора", True, (200, 200, 200))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_SPACE:
                    if self.selected == 0:
                        return PuzzleGame()
                    elif self.selected == 1:
                        return NameInputScreen()
                    elif self.selected == 2:
                        pygame.quit()
                        sys.exit()
        return self

    def update(self):
        pass

    def draw(self, screen):
        screen.fill(BACKGROUND)
        screen.blit(self.title, self.title.get_rect(center=(size[0] // 2, 100)))

        for i, option in enumerate(self.options):
            color = (0, 255, 0) if i == self.selected else (255, 255, 255)
            text = menu_font.render(option, True, color)
            screen.blit(text, text.get_rect(center=(size[0] // 2, 300 + i * 80)))

        screen.blit(self.hint, self.hint.get_rect(center=(size[0] // 2, 600)))


class NameInputScreen(State):
    def __init__(self):
        self.name = "Аноним"
        self.title = font.render("Введите имя:", True, (255, 255, 255))
        self.name_surface = font.render(self.name, True, (255, 255, 255))
        self.cursor = "|"
        self.cursor_visible = True
        self.cursor_time = pygame.time.get_ticks()
        self.back_text = menu_font.render("Нажмите ESC для возврата", True, (200, 200, 200))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MainMenu()
                elif event.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]
                elif event.key == pygame.K_RETURN:
                    return MainMenu()
                elif len(self.name) < 15 and event.unicode.isprintable():
                    self.name += event.unicode
                self.name_surface = font.render(self.name, True, (255, 255, 255))
        return self

    def update(self):
        if pygame.time.get_ticks() - self.cursor_time > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_time = pygame.time.get_ticks()

    def draw(self, screen):
        screen.fill(BACKGROUND)
        screen.blit(self.title, self.title.get_rect(center=(size[0] // 2, 200)))

        name_rect = self.name_surface.get_rect(center=(size[0] // 2, 300))
        screen.blit(self.name_surface, name_rect)

        if self.cursor_visible:
            cursor = font.render(self.cursor, True, (255, 255, 255))
            screen.blit(cursor, (name_rect.right, name_rect.y))

        screen.blit(self.back_text, self.back_text.get_rect(center=(size[0] // 2, 400)))


class PuzzleGame(State):
    def __init__(self):
        self.SCREEN_WIDTH = 1000
        self.SCREEN_HEIGHT = 800
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Пазл")

        self.ROWS = 3
        self.COLS = 3
        self.MARGIN = 2
        self.BACKGROUND = (0, 0, 0)
        self.SELECT_COLOR = (0, 255, 0)
        self.FONT_COLOR = (255, 255, 255)
        self.TIME_LIMIT = 30
        self.selected = None
        self.swaps = 0
        self.completed = False
        self.game_over = False
        self.time_stopped = False
        self.final_time = 0
        self.start_time = pygame.time.get_ticks()
        self.picture_folder = 'picture'
        self.pictures = [f for f in os.listdir(self.picture_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
        self.load_image(random.choice(self.pictures))
        self.font = pygame.font.SysFont('Arial', 36)
        self.back_text = menu_font.render("Нажмите ESC для возврата", True, (200, 200, 200))
        self.result_text = ""

    def load_image(self, picture):
        self.image = pygame.image.load(os.path.join(self.picture_folder, picture))
        self.image_width, self.image_height = self.image.get_size()
        self.TILE_WIDTH = self.image_width // self.COLS
        self.TILE_HEIGHT = self.image_height // self.ROWS

        # Создание плиток
        self.tiles = []
        for i in range(self.ROWS):
            for j in range(self.COLS):
                rect = pygame.Rect(j * self.TILE_WIDTH, i * self.TILE_HEIGHT,
                                   self.TILE_WIDTH, self.TILE_HEIGHT)
                self.tiles.append(self.image.subsurface(rect))
        self.origin_tiles = self.tiles.copy()
        random.shuffle(self.tiles)

    def get_remaining_time(self):
        if self.time_stopped:
            return self.final_time
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
        remaining = max(0, self.TIME_LIMIT - elapsed)
        if remaining <= 0 and not self.completed:
            self.game_over = True
        return remaining

    def is_puzzle_completed(self):
        if all(tile == self.origin_tiles[i] for i, tile in enumerate(self.tiles)):
            if not self.time_stopped:
                self.time_stopped = True
                self.final_time = self.get_remaining_time()
                self.result_text = f"Успешно за {int(self.TIME_LIMIT - self.final_time)} секунд!"
            return True
        return False

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.display.set_mode(size)
                    return MainMenu()
                elif event.key == pygame.K_SPACE and (self.game_over or self.completed):
                    self.__init__()  # Рестарт

            if not self.game_over and not self.completed:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for i, tile in enumerate(self.tiles):
                        row, col = i // self.ROWS, i % self.COLS
                        x = col * (self.TILE_WIDTH + self.MARGIN) + self.MARGIN
                        y = row * (self.TILE_HEIGHT + self.MARGIN) + self.MARGIN

                        if (x <= mouse_pos[0] <= x + self.TILE_WIDTH and
                                y <= mouse_pos[1] <= y + self.TILE_HEIGHT):
                            if self.selected is not None and self.selected != i:
                                # Обмен плитками
                                self.tiles[i], self.tiles[self.selected] = self.tiles[self.selected], self.tiles[i]
                                self.selected = None
                                self.swaps += 1
                                self.completed = self.is_puzzle_completed()
                            elif self.selected == i:
                                self.selected = None
                            else:
                                self.selected = i
        return self

    def update(self):
        if not self.completed and not self.game_over:
            self.get_remaining_time()  # Проверяем время

    def draw(self, screen):
        self.screen.fill(self.BACKGROUND)

        # Рисуем плитки
        for i, tile in enumerate(self.tiles):
            row, col = i // self.ROWS, i % self.COLS
            x = col * (self.TILE_WIDTH + self.MARGIN) + self.MARGIN
            y = row * (self.TILE_HEIGHT + self.MARGIN) + self.MARGIN
            self.screen.blit(tile, (x, y))
            if i == self.selected:
                pygame.draw.rect(self.screen, self.SELECT_COLOR,
                                 (x - 2, y - 2, self.TILE_WIDTH + 4, self.TILE_HEIGHT + 4), 3)

        # Информация
        time_color = (0, 255, 0) if self.time_stopped else self.FONT_COLOR
        time_text = self.font.render(f"Время: {int(self.get_remaining_time())} сек", True, time_color)
        self.screen.blit(time_text, (self.SCREEN_WIDTH - 200, 20))

        swaps_text = self.font.render(f"Ходы: {self.swaps}", True, self.FONT_COLOR)
        self.screen.blit(swaps_text, (20, self.SCREEN_HEIGHT - 50))

        self.screen.blit(self.back_text,
                         self.back_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 30)))

        if self.completed:
            complete_text = self.font.render("Пазл собран!", True, (0, 255, 0))
            result_time = self.font.render(self.result_text, True, (0, 255, 0))
            self.screen.blit(complete_text,
                             complete_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 120)))
            self.screen.blit(result_time,
                             result_time.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 80)))

            restart = self.font.render("Нажмите ПРОБЕЛ для рестарта", True, (255, 255, 255))
            self.screen.blit(restart, restart.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 30)))
        elif self.game_over:
            game_over = self.font.render("Время вышло!", True, (255, 0, 0))
            restart = self.font.render("Нажмите ПРОБЕЛ для рестарта", True, (255, 255, 255))
            self.screen.blit(game_over,
                             game_over.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 50)))
            self.screen.blit(restart, restart.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 50)))

        pygame.display.flip()


# Главный игровой цикл
state = SplashScreen()
while True:
    events = pygame.event.get()
    state = state.handle_events(events)
    state.update()

    if isinstance(state, PuzzleGame):
        state.draw(None)
    else:
        state.draw(screen)
        pygame.display.flip()

    clock.tick(FPS)
