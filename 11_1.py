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
font = pygame.font.SysFont('Impact"', 64)
menu_font = pygame.font.SysFont('Impact"', 48)


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

        rect = self.surface.get_rect()
        rect.centerx = screen.get_rect().centerx
        rect.centery = screen.get_rect().centery - 100
        screen.blit(self.surface, rect)

        if self.hint_visible:
            hint_rect = self.hint_surface.get_rect()
            hint_rect.centerx = screen.get_rect().centerx
            hint_rect.centery = screen.get_rect().centery + 100
            screen.blit(self.hint_surface, hint_rect)


class MainMenu(State):
    def __init__(self):
        self.options = ["Играть", "Выбрать имя", "Выйти"]
        self.selected = 0
        self.menu_surfaces = [menu_font.render(opt, True, (255, 255, 255)) for opt in self.options]
        self.title = font.render("Главное меню", True, (255, 255, 255))

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
                    if self.selected == 0:  #
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


        title_rect = self.title.get_rect()
        title_rect.centerx = screen.get_rect().centerx
        title_rect.centery = 100
        screen.blit(self.title, title_rect)


        for i, surface in enumerate(self.menu_surfaces):
            color = (0, 255, 0) if i == self.selected else (255, 255, 255)
            surface = menu_font.render(self.options[i], True, color)
            rect = surface.get_rect()
            rect.centerx = screen.get_rect().centerx
            rect.centery = 300 + i * 80
            screen.blit(surface, rect)


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
                else:
                    if len(self.name) < 15 and event.unicode.isprintable():
                        self.name += event.unicode
                self.name_surface = font.render(self.name, True, (255, 255, 255))

        return self

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_time > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_time = current_time

    def draw(self, screen):
        screen.fill(BACKGROUND)

        title_rect = self.title.get_rect()
        title_rect.centerx = screen.get_rect().centerx
        title_rect.centery = 200
        screen.blit(self.title, title_rect)

        name_rect = self.name_surface.get_rect()
        name_rect.centerx = screen.get_rect().centerx
        name_rect.centery = 300
        screen.blit(self.name_surface, name_rect)

        if self.cursor_visible:
            cursor_surface = font.render(self.cursor, True, (255, 255, 255))
            cursor_rect = cursor_surface.get_rect()
            cursor_rect.midleft = name_rect.midright
            screen.blit(cursor_surface, cursor_rect)

        back_rect = self.back_text.get_rect()
        back_rect.centerx = screen.get_rect().centerx
        back_rect.centery = 400
        screen.blit(self.back_text, back_rect)


class PuzzleGame(State):
    def __init__(self):
        self.SCREEN_WIDTH = 1000
        self.SCREEN_HEIGHT = 800
        self.ROWS = 3
        self.COLS = 3
        self.MARGIN = 2
        self.BACKGROUND = (0, 0, 0)
        self.SELECT_COLOR = (0, 255, 0)
        self.FONT_COLOR = (255, 255, 255)
        self.TIME_LIMIT = 30  # 30 секунд на сборку пазла

        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Пазл")
        self.screen.fill(self.BACKGROUND)

        try:
            self.font = pygame.font.Font(None, 36)
        except:
            self.font = pygame.font.SysFont('arial', 36)

        self.picture_folder = 'picture'
        self.pictures = [f for f in os.listdir(self.picture_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

        self.picture = random.choice(self.pictures)
        self.image = pygame.image.load(os.path.join(self.picture_folder, self.picture))
        self.image_width, self.image_height = self.image.get_size()
        self.TILE_WIDTH = self.image_width // self.COLS
        self.TILE_HEIGHT = self.image_height // self.ROWS

        self.tiles = []
        for i in range(self.ROWS):
            for j in range(self.COLS):
                rect = pygame.Rect(j * self.TILE_WIDTH, i * self.TILE_HEIGHT, self.TILE_WIDTH, self.TILE_HEIGHT)
                tile = self.image.subsurface(rect)
                self.tiles.append(tile)

        self.origin_tiles = self.tiles.copy()
        random.shuffle(self.tiles)

        self.selected = None
        self.swaps = 0
        self.completed = False
        self.game_over = False
        self.start_time = pygame.time.get_ticks()
        self.back_text = menu_font.render("Нажмите ESC для возврата", True, (200, 200, 200))

    def get_remaining_time(self):
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000  # в секундах
        remaining = max(0, self.TIME_LIMIT - elapsed)
        return remaining

    def draw_tiles(self):
        for i in range(len(self.tiles)):
            tile = self.tiles[i]
            row = i // self.ROWS
            col = i % self.COLS
            x = col * (self.TILE_WIDTH + self.MARGIN) + self.MARGIN
            y = row * (self.TILE_HEIGHT + self.MARGIN) + self.MARGIN
            self.screen.blit(tile, (x, y))
            if i == self.selected:
                pygame.draw.rect(self.screen, self.SELECT_COLOR,
                                 (x - 2, y - 2, self.TILE_WIDTH + 4, self.TILE_HEIGHT + 4), 3)

    def is_puzzle_completed(self):
        return all(tile == self.origin_tiles[i] for i, tile in enumerate(self.tiles))

    def draw_info(self):
        # Отображение оставшегося времени
        remaining_time = self.get_remaining_time()
        time_text = self.font.render(f"Время: {int(remaining_time)} сек", True, self.FONT_COLOR)
        self.screen.blit(time_text, (self.SCREEN_WIDTH - 200, 20))

        swaps_text = self.font.render(f"Ходы: {self.swaps}", True, self.FONT_COLOR)
        self.screen.blit(swaps_text, (20, self.SCREEN_HEIGHT - 50))

        # Отрисовка подсказки
        back_rect = self.back_text.get_rect()
        back_rect.centerx = self.SCREEN_WIDTH // 2
        back_rect.centery = self.SCREEN_HEIGHT - 30
        self.screen.blit(self.back_text, back_rect)

        if self.completed:
            complete_text = self.font.render("Пазл собран!", True, (0, 255, 0))
            text_rect = complete_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - 80))
            self.screen.blit(complete_text, text_rect)
        elif self.game_over:
            game_over_text = self.font.render("Время вышло!", True, (255, 0, 0))
            restart_text = self.font.render("Нажмите R для рестарта", True, (255, 255, 255))

            go_rect = game_over_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(game_over_text, go_rect)

            rs_rect = restart_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(restart_text, rs_rect)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.display.set_mode(size)
                    return MainMenu()
                elif event.key == pygame.K_r and (self.game_over or self.completed):
                    self.__init__()  # Рестарт игры

            if not self.game_over and not self.completed:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    for i in range(len(self.tiles)):
                        row = i // self.ROWS
                        col = i % self.COLS
                        x = col * (self.TILE_WIDTH + self.MARGIN) + self.MARGIN
                        y = row * (self.TILE_HEIGHT + self.MARGIN) + self.MARGIN

                        if x <= mouse_x <= x + self.TILE_WIDTH and y <= mouse_y <= y + self.TILE_HEIGHT:
                            if self.selected is not None and self.selected != i:
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
            if self.get_remaining_time() <= 0:
                self.game_over = True

    def draw(self, screen):
        self.screen.fill(self.BACKGROUND)
        self.draw_tiles()
        self.draw_info()
        pygame.display.flip()


# Запуск игры
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
