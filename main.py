import pygame
from player import Player
from client.client import Client
from point import Rect
import random

pygame.init()

#resolution
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS= 60

#color 
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLACK = (0, 0, 0)
COLORS = [RED, GREEN, BLACK]

client_num = 0

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Test")

player = Player(400, RED)
player2 = Player(400,GREEN)
players = [player, player2]
scores = [0, 0]

point = Rect(random.randrange(100, 700), 0, random.choice(COLORS))
point2 = Rect(random.randrange(100, 700), 0, random.choice(COLORS))
point3 = Rect(random.randrange(100, 700), 0, random.choice(COLORS))
points = [point, point2, point3]

button_surface = pygame.Surface((100, 50))
button_rect = pygame.Rect(0, 0, 100, 50)

def draw_window(player, player2, point):
    screen.fill(WHITE)
    font = pygame.font.Font('asset/mitr.ttf', 32)
    score_0_text = font.render(str(scores[0]), True, RED)
    score_1_text = font.render(str(scores[1]), True, GREEN)
    score_0_Rect = score_0_text.get_rect()
    score_1_Rect = score_1_text.get_rect()
    score_0_Rect.center = (200, 100)
    score_1_Rect.center = (600, 100)
    screen.blit(score_0_text, score_0_Rect)
    screen.blit(score_1_text, score_1_Rect)
    player.draw(screen)
    player2.draw(screen)
    for point in points:
        point.draw(screen)
    pygame.display.update()

def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def menu(client_num, winner):
    font = pygame.font.Font('asset/mitr.ttf', 32)
    screen.fill(WHITE)
    title = "Socket Programming Project"
    if winner == 0:
        title = "Player 1 win!"
    if winner == 1:
        title = "Player 2 win!"
    draw_text(title, font, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    font_lower = pygame.font.Font('asset/mitr.ttf', 24)
    title_2 = "Press Enter to start new game"
    if client_num == 1:
        title_2 = "Waiting for host"
    draw_text(title_2, font_lower, BLACK, SCREEN_WIDTH // 2,SCREEN_HEIGHT // 2)
    pygame.display.update()
    
def make_pos(player):
    return str(player.x) + ',' + str(player.y)

def strTodict(data):
    return eval(data)

def main():
    
    moving = False
    clock = pygame.time.Clock()
    client = Client()

    data = client.send(str({
        "protocol": "GET POSITIONS",
        "position": 400
    }))
    client_num = len(strTodict(data)) - 1
    print(client_num)
    players[client_num].update()
    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(FPS)

        status_dict = strTodict(client.send(str({
            "protocol": "STATUS CHECKING"
        })))

        status = status_dict["status"]
        winner = status_dict["winner"]

        positions_dict = strTodict(client.send(str({
            "protocol": "GET POSITIONS",
            "position": players[client_num].x
        })))
        positions = list(positions_dict.values())

        point_dict = strTodict(client.send(str({
            "protocol": "GET POINT POSITION"
        })))


        for i in range(len(points)):
            points[i].x = point_dict['positions'][i][0]
            points[i].y = point_dict['positions'][i][1]
            points[i].color = point_dict['colors'][i]
            points[i].update()

        score_list = eval(client.send(str({
            "protocol": "GET SCORE"
        })))
        scores[0] = score_list[0] 
        scores[1] = score_list[1] 

        if len(positions) != 1:
            x = positions[1 - client_num]
            players[1 - client_num].x = x
            players[1 - client_num].update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(positions) == 2:
                    client.send(str({
                        "protocol": "CHANGE STATUS",
                        "status": "Playing"
                    }))
                    moving = True

        for i in range(len(points)):
            if points[i].rect.colliderect(players[client_num].rect):
                if points[i].color == players[client_num].color:
                    client.send(str({
                        "protocol": "CHANGE SCORE",
                        "client_num": client_num,
                        "score_point": 1,
                        "point": i
                    }))
                else:
                    client.send(str({
                        "protocol": "CHANGE SCORE",
                        "client_num": client_num,
                        "score_point": -1,
                        "point": i
                    }))
                points[i].update()
        if status == "Waiting":
            menu(client_num, winner)
        elif status == "Playing":
            players[client_num].move()
            draw_window(player, player2, points)

    pygame.quit()
    
if __name__ == "__main__":
    main()
