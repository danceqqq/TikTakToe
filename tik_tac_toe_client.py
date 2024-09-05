import pygame
import sys
import socket
import threading

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
    font = pygame.font.Font(None, 36)
    text_single = font.render('1. Одиночная игра', True, LINE_COLOR)
    text_online = font.render('2. Онлайн-игра', True, LINE_COLOR)

    screen.fill(BG_COLOR)
    screen.blit(text_single, (50, 100))
    screen.blit(text_online, (50, 150))

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
                    elif is_draw():
                        game_over = True
                    else:
                        bot_move()
                        if check_winner('O'):
                            game_over = True
                    draw_figures()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart_game()
                    game_over = False

        pygame.display.update()

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

    def handle_connection(conn):
        nonlocal my_turn, game_over
        while True:
            data = conn.recv(BUFFER_SIZE).decode()
            if data:
                row, col = map(int, data.split(','))
                board[row][col] = 'O' if player == 'X' else 'X'
                if check_winner('O' if player == 'X' else 'X'):
                    game_over = True
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
        threading.Thread(target=handle_connection, args=(conn,)).start()
    else:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((opponent_ip, PORT))
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

        pygame.display.update()

while True:
    mode = main_menu()
    if mode == 'single':
        single_player_game()
    elif mode == 'online':
        online_game()
