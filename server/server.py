import socket, threading
import random
 
HOST = 'localhost'
PORT = 5432 
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))

#color
RED = (255,0,0)
GREEN = (0,255,0)
BLACK = (0, 0, 0)

s.listen(5)

clients = {}

#game data 
points = [[100, -20], [200, -10], [300, 0]]
score = [0, 0]
color = [BLACK, BLACK, BLACK]
colors_choice = [RED, GREEN, BLACK]
game_status = "Waiting"
winner = -1

def strTodict(string):
    return eval(string)

def strToPos(data):
    split_data = data.split(',')
    return [int(split_data[0]), int(split_data[1])]

def handle(connection, addr):
    global color
    global game_status
    global winner
    global score
    try:
        while True:
            #recieve data from client
            data = connection.recv(1024)
            data_dict = strTodict(data.decode())
            #get protocol_name
            protocol = data_dict['protocol']
            print(data_dict)
            #STATUS CHECKING: return current status and 
            #if the game is over (player that make 5 points) change status to "Waiting" for new game
            if protocol == "STATUS CHECKING":
                if score[0] >= 5: 
                    winner = 0
                    game_status = "Waiting"
                elif score[1] >= 5: 
                    winner = 1
                    game_status = "Waiting"
                connection.sendall(str({
                    "status": game_status,
                    "winner": winner
                }).encode())

            #CHANGE STATUS: change status "Waiting" -> "Playing" when host press enter   
            elif protocol == "CHANGE STATUS":
                game_status = data_dict["status"]
                if winner != -1:
                    score = [0, 0]
                    for i in range(len(points)):
                        points[i][1] = 0
                        points[i][0] = random.randrange(100, 700)
                        color[i] = random.choice(colors_choice)
                    game_status = "Playing"
                connection.sendall(str(game_status).encode())
            
            #GET POSITIONS: get all player positions 
            elif protocol == "GET POSITIONS":
                clients[addr] = data_dict["position"]
                print(clients)
                connection.sendall(str(clients).encode())

            #GET POINT POSITION: get all game_point positions
            elif protocol == "GET POINT POSITION":
                for i in range(len(points)):
                    points[i][1] += 1
                    if points[i][1] >= 600:
                        points[i][1] = 0
                        points[i][0] = random.randrange(100, 700)
                        color[i] = random.choice(colors_choice)

                point_data = {
                    "positions": points,
                    "colors": color
                }
                
                connection.sendall(str(point_data).encode())

            #GET SCORE: get all player scores
            elif protocol == "GET SCORE":
                connection.sendall(str(score).encode())

            #CHANGE SCORE: increase or decrease player scores and return game_point to top again
            elif protocol == "CHANGE SCORE":
                point_index = int(data_dict["point"])
                score[data_dict["client_num"]] += data_dict["score_point"]
                points[point_index][1] = 0
                points[point_index][0] = random.randrange(100, 700)
                color[point_index] = random.choice(colors_choice)
                connection.sendall(str(score).encode())

            #if not found data, disconnected
            elif not data:
                remove_conn(connection, addr)
                return
    except:
        remove_conn(connection, addr)
        return

def remove_conn(connection, addr):
    if addr in clients.keys():
        print(connection)
        connection.close()
        clients.pop(addr)
 
while True:
    print("Waiting for connection")
    connection, client_address = s.accept()
    try:
        print("Connection from", client_address)
        #add client to clients list
        clients[client_address] = {
            "position": 400
        }
        #start new thread to handle client
        threading.Thread(target=handle, args=[connection, client_address]).start()
    finally:
        if len(clients) == 0:
            connection.close()
            print("closed connection")
