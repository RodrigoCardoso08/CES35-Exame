import socket
import random
import threading
import sys
import time

followers_delta = {
    0: [0, 0, 0],
    1: [-5,-10,0],
    2: [5,-10,0],
    3: [10,-5,0],
    4: [10,5,0],
    5: [5,10,0],
    6: [-5,10,0],
    7: [-10,5,0],
    8: [-10,-5,0],
}

class FollowerDrone:
    def __init__(self,id):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.master_ip = '10.0.0.1'
        self.id = int(id)
        self.port = 9999
        self.delta = followers_delta[self.id -1]
        self.position = [10 + self.delta[0], 10 + self.delta[1], 0 + self.delta[2]]
        self.client.bind((f'10.0.0.{id}', 9999))
        self.step = 5
        self.last_communication_time = None
        self.communication_timeout = 10
        self.master_in_panic = False
    
    def update_last_communication_time(self):
        self.last_communication_time = time.time()

    def update_position(self, new_position):
        with open(f'drone{self.id}_position.txt', 'w') as f:
            f.write(new_position)

    def print_output(self, text):
        with open(f'drone{self.id}_output.txt', 'a') as f:
            f.write(text+"\n")

    def send_position(self):
        position_string = f"{self.position[0]},{self.position[1]},{self.position[2]}"
        msg = f"POS:{position_string}"
        self.client.sendto(msg.encode('utf-8'), (self.master_ip, self.port))

    def move(self, destination):
        try:
            while True:
                direction_vector = [dest - curr for dest, curr in zip(destination, self.position)]
                # Verifique se o drone já chegou ao destino
                if all(coord == 0 for coord in direction_vector):
                    break
                # Normalize o vetor de direção
                magnitude = sum([coord**2 for coord in direction_vector])**0.5
                unit_direction = [coord/magnitude for coord in direction_vector]
                # Calcule a nova posição
                new_position = [curr + self.step * unit for curr, unit in zip(self.position, unit_direction)]
                # Evite ultrapassar o destino
                for i in range(3):
                    if unit_direction[i] > 0 and new_position[i] > destination[i]:
                        new_position[i] = destination[i]
                    elif unit_direction[i] < 0 and new_position[i] < destination[i]:
                        new_position[i] = destination[i]
                # Atualize a posição do drone
                self.position = new_position
                position_string = f"{new_position[0]},{new_position[1]},{new_position[2]}"
                self.update_position(position_string)
                time.sleep(1)
                if self.master_in_panic and destination != [10 + self.delta[0], 10 + self.delta[1], 0 + self.delta[2]]:
                    break
        except Exception as e:
            self.print_output(f"Erro na thread move: {e}")

    def listen_for_requests(self):
        self.print_output("LISTENING")
        while True:
            try:
                data, addr = self.client.recvfrom(4096)
                message = data.decode('utf-8')
                self.update_last_communication_time()
                self.print_output(f"Recebi a mensagem {message}")
                if message == "REQ:POS":
                    self.send_position()
                elif message == "REQ:CHECK":
                    self.client.sendto("CHECK:PRESENT".encode('utf-8'), (self.master_ip, self.port))
                elif message.startswith("REQ:MOVE:"):
                    self.client.sendto("MOVING".encode('utf-8'), (self.master_ip, self.port))
                    position = message.split(':')[-1]
                    self.print_output(position)
                    x, y, z = map(float, position.split(','))
                    time.sleep(0.5)
                    moving_thread = threading.Thread(target=self.move, args=([x + self.delta[0],y + self.delta[1],z + self.delta[2]],))
                    moving_thread.daemon = False
                    moving_thread.start()
                elif message == "REQ:PIC":
                    self.print_output(f"Vou Responder {message}")
                    self.client.sendto("PIC:TAKEN".encode('utf-8'), (self.master_ip, self.port))
                elif message == "REQ:VOTE":
                    if random.random() < 0.9:
                        self.client.sendto("VOTE:TRUE".encode('utf-8'), (self.master_ip, self.port))
                    else:
                        self.client.sendto("VOTE:FALSE".encode('utf-8'), (self.master_ip, self.port))
                elif message.startswith("REQ:PANIC"):
                    self.client.sendto("RETURNING".encode('utf-8'), (self.master_ip, self.port))
                    self.master_in_panic = True
                    returning_thread = threading.Thread(target=self.move, args=([10 + self.delta[0],10 + self.delta[1],0 + self.delta[2]],))
                    returning_thread.daemon = False
                    returning_thread.start()
            except Exception as e:
                self.print_output(f"Tomei {e}")
                
    def check_communication(self):
        # Método para verificar regularmente a comunicação
        while True:
            time.sleep(5)  # Verificar a cada 5 segundos
            if self.last_communication_time and (time.time() - self.last_communication_time > self.communication_timeout):
                self.print_output("Comunicação com o mestre perdida. Retornando ao ponto inicial.")
                # self.move([10.0,10.0,0.0])
                self.master_in_panic = True
                returning_thread = threading.Thread(target=self.move, args=([10 + self.delta[0],10 + self.delta[1],0 + self.delta[2]],))
                returning_thread.daemon = False
                returning_thread.start()
                break

    def run(self):
        listen_thread = threading.Thread(target=self.listen_for_requests)
        listen_thread.start()
        communication_check_thread = threading.Thread(target=self.check_communication)
        communication_check_thread.start()

if __name__ == '__main__':
    follower = FollowerDrone(sys.argv[1])
    try:
        follower.run()
    except Exception as e:
        with open(f'drone{sys.argv[1]}_output.txt', 'a') as f:
            f.write(e+"\n")
