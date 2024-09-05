import pygame
import sys
import socket
import threading
import json
import os
import random
from urllib.request import urlopen
from io import BytesIO

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 300, 350
LINE_WIDTH = 5
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

# Цвета
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (84, 84, 84)
WIN_LINE_COLOR = (255, 0, 0)

# Установка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Крестики-нолики')
screen.fill(BG_COLOR)

# Игровое поле
board = [[None]*BOARD_COLS for _ in range(BOARD_ROWS)]

# Сетевые параметры
HOST = ''
PORT = 12345
BUFFER_SIZE = 1024

# Путь к файлу данных
DATA_FILE = "player_data.json"

# Загрузка и сохранение данных
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"avatar_url": "", "rating": 100}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

player_data = load_data()

# Загрузка аватарки
def load_avatar(url):
    try:
        image_str = urlopen(url).read()
        image_file = BytesIO(image_str)
        avatar = pygame.image.load(image_file)
        return pygame.transform.scale(avatar, (50, 50))
    except Exception as e:
        print(f"Ошибка загрузки аватарки: {e}")
        return None

def draw_avatar(x, y, avatar, default_color):
    if avatar:
        avatar = pygame.transform.scale(avatar, (50, 50))
        pygame.draw.circle(screen, default_color, (x + 25, y + 25), 25)
        screen.blit(avatar, (x, y))
    else:
        pygame.draw.circle(screen, default_color, (x + 25, y + 25), 25)

avatar_image = load_avatar(player_data["avatar_url"])
if not avatar_image:
    avatar_color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
else:
    avatar_color = (255, 255, 255)

def draw_lines():
    pygame.draw.line(screen, LINE_COLOR, (0, SQUARE_SIZE), (WIDTH, SQUARE_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (0, 2 * SQUARE_SIZE), (WIDTH, 2 * SQUARE_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (SQUARE_SIZE, 0), (SQUARE_SIZE, HEIGHT - 50), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (2 * SQUARE_SIZE, 0), (2 * SQUARE_SIZE, HEIGHT - 50), LINE_WIDTH)

def draw_figures():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 'O':
                pygame.draw.circle(screen, CIRCLE_COLOR, (int(col * SQUARE_SIZE + SQUARE_SIZE//2), int(row * SQUARE_SIZE + SQUARE_SIZE//2)), CIRCLE_RADIUS, CIRCLE_WIDTH)
            elif board[row][col] == 'X':
                pygame.draw.line(screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE), CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), CROSS_WIDTH)

def check_winner(player):
    for row in range(BOARD_ROWS):
        if all([board[row][col] == player for col in range(BOARD_COLS)]):
            draw_win_line(row, 0, row, BOARD_COLS - 1)
            return True
    for col in range(BOARD_COLS):
        if all([board[row][col] == player for row in range(BOARD_ROWS)]):
            draw_win_line(0, col, BOARD_ROWS - 1, col)
            return True
    if all([board[i][i] == player for i in range(BOARD_ROWS)]):
        draw_win_line(0, 0, BOARD_ROWS - 1, BOARD_COLS - 1)
        return True
    if all([board[i][BOARD_ROWS - i - 1] == player for i in range(BOARD_ROWS)]):
        draw_win_line(0, BOARD_COLS - 1, BOARD_ROWS - 1, 0)
        return True
    return False

def draw_win_line(start_row, start_col, end_row, end_col):
    start_pos = (start_col * SQUARE_SIZE + SQUARE_SIZE//2, start_row * SQUARE_SIZE + SQUARE_SIZE//2)
    end_pos = (end_col * SQUARE_SIZE + SQUARE_SIZE//2, end_row * SQUARE_SIZE + SQUARE_SIZE//2)
    pygame.draw.line(screen, WIN_LINE_COLOR, start_pos, end_pos, LINE_WIDTH)

def is_draw():
    return all(all(cell is not None for cell in row) for row in board)

def restart_game():
    screen.fill(BG_COLOR)
    draw_lines()
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            board[row][col] = None

def main_menu():
    global avatar_image
    font = pygame.font.Font(None, 36)
    text_single = font.render('1. Одиночная игра', True, LINE_COLOR)
    text_online = font.render('2. Онлайн-игра', True, LINE_COLOR)
    text_rating = font.render(f'Рейтинг: {player_data["rating"]} 🏆', True, LINE_COLOR)

    screen.fill(BG_COLOR)
    draw_avatar(WIDTH//2 - 25, 10, avatar_image, avatar_color)
    screen.blit(text_single, (50, 100))
    screen.blit(text_online, (50, 150))
    screen.blit(text_rating, (50, 200))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 'single'
                elif event.key == pygame.K_2:
                    return 'online'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(WIDTH//2 - 25, 10, 50, 50).collidepoint(event.pos):
                    avatar_url = input_avatar_url()
                    if avatar_url:
                        player_data["avatar_url"] = avatar_url
                        avatar_image = load_avatar(avatar_url)
                        save_data(player_data)

def input_avatar_url():
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(50, 100, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill(BG_COLOR)
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()

def single_player_game():
    restart_game()
    player = 'X'
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mouseX = event.pos[0] // SQUARE_SIZE
                mouseY = event.pos[1] // SQUARE_SIZE

                if board[mouseY][mouseX] is None:
                    board[mouseY][mouseX] = player
                    if check_winner(player):
                        game_over = True
                        player_data["rating"] += 25
                        save_data(player_data)
                    elif is_draw():
                        game_over = True
                    else:
                        bot_move()
                        if check_winner('O'):
                            game_over = True
                            player_data["rating"] -= 25
                            save_data(player_data)
                    draw_figures()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart_game()
                    game_over = False
                if event.key == pygame.K_m and game_over:
                    return

        if game_over:
            font = pygame.font.Font(None, 36)
            text_menu = font.render('Нажмите M для меню', True, WIN_LINE_COLOR)
            screen.blit(text_menu, (50, HEIGHT - 40))

        pygame.display.update()

def bot_move():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] is None:
                board[row][col] = 'O'
                return

def online_game():
    screen.fill(BG_COLOR)
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(50, 100, 200, 50)
    button_host = pygame.Rect(50, 200, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive

                if button_host.collidepoint(event.pos):
                    done = True
                    play_online_game('')

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                        play_online_game(text)
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill(BG_COLOR)
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.draw.rect(screen, color_inactive, button_host)
        host_text = font.render('ХОСТ', True, (0, 0, 0))
        screen.blit(host_text, (button_host.x + 50, button_host.y + 10))

        pygame.display.flip()

def play_online_game(opponent_ip):
    restart_game()
    player = 'X'
    game_over = False
    my_turn = True

    opponent_data = {"avatar_url": "", "rating": 100}
    opponent_avatar = None

    def handle_connection(conn):
        nonlocal my_turn, game_over, opponent_data, opponent_avatar
        while True:
            data = conn.recv(BUFFER_SIZE).decode()
            if data:
                if data.startswith("DATA:"):
                    opponent_data = json.loads(data[5:])
                    opponent_avatar = load_avatar(opponent_data["avatar_url"])
                else:
                    row, col = map(int, data.split(','))
                    board[row][col] = 'O' if player == 'X' else 'X'
                    if check_winner('O' if player == 'X' else 'X'):
                        game_over = True
                        player_data["rating"] -= 25
                        save_data(player_data)
                    elif is_draw():
                        game_over = True
                    my_turn = True
                    draw_figures()
            if game_over:
                break

    if opponent_ip == '':
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        conn, addr = server_socket.accept()
        conn.send(f"DATA:{json.dumps(player_data)}".encode())
        threading.Thread(target=handle_connection, args=(conn,)).start()
    else:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((opponent_ip, PORT))
        client_socket.send(f"DATA:{json.dumps(player_data)}".encode())
        threading.Thread(target=handle_connection, args=(client_socket,)).start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and my_turn:
                mouseX = event.pos[0] // SQUARE_SIZE
                mouseY = event.pos[1] // SQUARE_SIZE

                if board[mouseY][mouseX] is None:
                    board[mouseY][mouseX] = player
                    if check_winner(player):
                        game_over = True
                        player_data["rating"] += 25
                        save_data(player_data)
                    elif is_draw():
                        game_over = True
                    draw_figures()
                    my_turn = False

                    data = f"{mouseY},{mouseX}"
                    if opponent_ip == '':
                        conn.send(data.encode())
                    else:
                        client_socket.send(data.encode())

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart_game()
                    game_over = False
                    my_turn = player == 'X'
                if event.key == pygame.K_m and game_over:
                    return

        screen.fill(BG_COLOR)
        draw_lines()
        draw_figures()

        # Отображение аватарок и рейтинга
        draw_avatar(10, 10, avatar_image, avatar_color)
        if opponent_avatar:
            draw_avatar(WIDTH - 60, 10, opponent_avatar, (255, 255, 255))

        font = pygame.font.Font(None, 24)
        my_rating_text = font.render(f"{player_data['rating']} 🏆", True, LINE_COLOR)
        screen.blit(my_rating_text, (10, 70))
        opponent_rating_text = font.render(f"{opponent_data['rating']} 🏆", True, LINE_COLOR)
        screen.blit(opponent_rating_text, (WIDTH - 70, 70))

        turn_text = "Твой ход" if my_turn else "Ход оппонента"
        turn_surface = font.render(turn_text, True, LINE_COLOR)
        screen.blit(turn_surface, (WIDTH//2 - turn_surface.get_width()//2, 40))

        pygame.display.update()

while True:
    mode = main_menu()
    if mode == 'single':
        single_player_game()
    elif mode == 'online':
        online_game()
