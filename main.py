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

#client_num for identify player 1 or player 2
client_num = 0

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Socket Programming")

#players and all players scores
player = Player(400, RED)
player2 = Player(400,GREEN)
players = [player, player2]
scores = [0, 0]

#game_point for collect player's score
game_point = Rect(random.randrange(100, 700), 0, random.choice(COLORS))
game_point2 = Rect(random.randrange(100, 700), 0, random.choice(COLORS))
game_point3 = Rect(random.randrange(100, 700), 0, random.choice(COLORS))
points = [game_point, game_point2, game_point3]

#game scene
def draw_window(player, player2, point, client_num):
    screen.fill(WHITE)
    font = pygame.font.Font('asset/mitr.ttf', 32)
    score_0_text = font.render(str(scores[0]), True, RED)
    score_1_text = font.render(str(scores[1]), True, GREEN)
    score_0_Rect = score_0_text.get_rect()
    score_1_Rect = score_1_text.get_rect()
    score_0_Rect.center = (200, 100)
    score_1_Rect.center = (600, 100)
    font = pygame.font.Font('asset/mitr.ttf', 16)
    color = ["red", "green"]
    player_text = font.render(f"You are: player{client_num + 1} ({color[client_num]})", True, COLORS[client_num])
    player_text_Rect =  player_text.get_rect()
    player_text_Rect.center = (400, 100)
    screen.blit(score_0_text, score_0_Rect)
    screen.blit(score_1_text, score_1_Rect)
    screen.blit(player_text, player_text_Rect)
    player.draw(screen)
    player2.draw(screen)
    for point in points:
        point.draw(screen)
    pygame.display.update()

#draw text in menu scene
def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

#menu scene for start new game
def menu(client_num, winner):
    font = pygame.font.Font('asset/mitr.ttf', 32)
    screen.fill(WHITE)
    
    title = "Socket Programming Project"

    title_3_1 = "Collecting a square box of its own color earns 5 points, and only then will you be the winner."
    title_3_2 = "If you collect other colors, you will be deducted 1 point."  
    title_3_3 = "Use 'a' or the left arrow to move left, and 'd' or the right arrow to move right."
    title_3_4 = "Press enter to start the game."

    if winner == 0:
        title = "Player 1 win!"
    if winner == 1:
        title = "Player 2 win!"
    draw_text(title, font, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    font_lower = pygame.font.Font('asset/mitr.ttf', 24)
    title_2 = "Press Enter to start new game"
    if client_num == 1:
        title_2 = "Waiting for host"
    font_lowest = pygame.font.Font('asset/mitr.ttf', 16)
    draw_text(title_2, font_lower, BLACK, SCREEN_WIDTH // 2,SCREEN_HEIGHT // 2)
    draw_text(title_3_1, font_lowest, RED, SCREEN_WIDTH // 2, 500)
    draw_text(title_3_2, font_lowest, RED, SCREEN_WIDTH // 2, 516)
    draw_text(title_3_3, font_lowest, RED, SCREEN_WIDTH // 2, 532)
    draw_text(title_3_4, font_lowest, RED, SCREEN_WIDTH // 2, 548)

    pygame.display.update()

def make_pos(player):
    return str(player.x) + ',' + str(player.y)

def strTodict(data):
    return eval(data)

def main():
    
    clock = pygame.time.Clock()
    #connect client
    client = Client()

    #first sending for add player in clients list
    data = client.send(str({
        "protocol": "GET POSITIONS",
        "position": 400
    }))
    
    client_num = len(strTodict(data)) - 1
    players[client_num].update()

    run = True

    while run:
        clock.tick(FPS)

        #get game status and winner from server
        status_dict = strTodict(client.send(str({
            "protocol": "STATUS CHECKING"
        })))
        status = status_dict["status"]
        winner = status_dict["winner"]

        #get all player positions
        positions_dict = strTodict(client.send(str({
            "protocol": "GET POSITIONS",
            "position": players[client_num].x
        })))
        positions = list(positions_dict.values())

        #get all game_point positions
        point_dict = strTodict(client.send(str({
            "protocol": "GET POINT POSITION"
        })))

        #update all game_points
        for i in range(len(points)):
            points[i].x = point_dict['positions'][i][0]
            points[i].y = point_dict['positions'][i][1]
            points[i].color = point_dict['colors'][i]
            points[i].update()

        #update score
        score_list = eval(client.send(str({
            "protocol": "GET SCORE"
        })))
        scores[0] = score_list[0] 
        scores[1] = score_list[1] 

        #update all positions if player amount is 2
        if len(positions) != 1:
            x = positions[1 - client_num]
            players[1 - client_num].x = x
            players[1 - client_num].update()

        #quit game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            #press enter to play new game
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(positions) == 2:
                    client.send(str({
                        "protocol": "CHANGE STATUS",
                        "status": "Playing"
                    }))

        #detect all game_point collision to calculate player's score 
        #if player take wrong color game_point, decrease player's score 
        #and if player take correct color game_point, increase player's score 
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

        #check game_status
        if status == "Waiting":
            menu(client_num, winner)
        elif status == "Playing":
            players[client_num].move()
            draw_window(player, player2, points, client_num)

    pygame.quit()
    
if __name__ == "__main__":
    main()
