import socket
import threading
import random
import time

class MasterDrone:
    def __init__(self, timeout=10):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = 9999
        self.id = 1
        self.server.bind(('10.0.0.1', 9999))
        self.position = [10, 10, 0]
        self.followers =  {
            '10.0.0.2': [12, 10, 0],
            '10.0.0.3': [14, 10, 0],
            '10.0.0.4': [16, 10, 0],
            '10.0.0.5': [18, 10, 0],
            '10.0.0.6': [20, 10, 0],
            '10.0.0.7': [22, 10, 0],
            '10.0.0.8': [24, 10, 0],
            '10.0.0.9': [26, 10, 0]
        } # Key is IP address, value is position
        self.active_followers = {
            '10.0.0.2': False,
            '10.0.0.3': False,
            '10.0.0.4': False,
            '10.0.0.5': False,
            '10.0.0.6': False,
            '10.0.0.7': False,
            '10.0.0.8': False,
            '10.0.0.9': False
        }
        self.moving_followers = {
            '10.0.0.2': False,
            '10.0.0.3': False,
            '10.0.0.4': False,
            '10.0.0.5': False,
            '10.0.0.6': False,
            '10.0.0.7': False,
            '10.0.0.8': False,
            '10.0.0.9': False
        }
        self.returning_followers = {
            '10.0.0.2': False,
            '10.0.0.3': False,
            '10.0.0.4': False,
            '10.0.0.5': False,
            '10.0.0.6': False,
            '10.0.0.7': False,
            '10.0.0.8': False,
            '10.0.0.9': False
        }
        self.followers_pics = {
            '10.0.0.2': False,
            '10.0.0.3': False,
            '10.0.0.4': False,
            '10.0.0.5': False,
            '10.0.0.6': False,
            '10.0.0.7': False,
            '10.0.0.8': False,
            '10.0.0.9': False
        }
        self.followers_votes = {
            '10.0.0.2': 0,
            '10.0.0.3': 0,
            '10.0.0.4': 0,
            '10.0.0.5': 0,
            '10.0.0.6': 0,
            '10.0.0.7': 0,
            '10.0.0.8': 0,
            '10.0.0.9': 0
        }
        self.step = 5
        self.expected_msgs = {
            'CHECK': 0,
            'POS': 0,
            'MOVING': 0,
            'PIC': 0,
            'VOTE': 0
        }
        self.panic_mode = False
        self.timeout = timeout
    
    def print_output(self, text):
        with open(f'drone{self.id}_output.txt', 'a') as f:
            f.write(text+"\n")

    def enter_panic_mode(self):
        self.panic_mode = True
        for addr in list(self.followers.keys()):
            self.print_output(f"SENT PANIC MESSAGE TO {addr}")
            self.server.sendto("REQ:PANIC".encode('utf-8'), (addr, self.port))
        self.print_output("ENTERING PANIC MODE!!")
        # self.move([10, 10, 0])
        # Movimenta apenas o drone master para a posição [10, 10, 0]
        master_returning_thread = threading.Thread(target=self.move_master, args=([10, 10, 0],))
        master_returning_thread.start()
         

    def update_position(self, new_position):
        with open(f'drone{self.id}_position.txt', 'w') as f:
            f.write(new_position)

    def move_master(self, first_destination):
        destination =  first_destination
        while True:
            if self.panic_mode:
                destination = [10, 10, 0]
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

    def random_position(self):
        while(True):
            time.sleep(3)
            position = f"{random.randint(0, 100)},{random.randint(0, 100)},0"  # Atualizando posição aleatoriamente
            self.update_position(position)

    def listen_for_followers(self):
        while True:
            data, addr = self.server.recvfrom(4096)
            self.handle_message(data.decode('utf-8'), addr[0])
        # start_time = time.time()
        # while not self.panic_mode:  # Enquanto não estiver no modo de pânico
        #     if time.time() - start_time > self.timeout:  # Se passar do timeout
        #         break  # Interrompe o loop
        #     data, addr = self.server.recvfrom(4096)
        #     self.handle_message(data.decode('utf-8'), addr[0])

    def handle_message(self, message, addr):
        self.print_output(message)
        if message.startswith("POS:"):
            _, pos = message.split(":")
            self.followers[addr] = [float(i) for i in pos.split(",")]
            self.expected_msgs['POS'] -= 1

        if message.startswith("CHECK:"):
            self.active_followers[addr] = True
            self.expected_msgs['CHECK'] -= 1

        if message.startswith("MOVING"):
            self.moving_followers[addr] = True
            self.expected_msgs['MOVING'] -= 1

        if message.startswith("PIC:"):
            self.followers_pics[addr] = True
            self.expected_msgs['PIC'] -= 1

        if message.startswith("VOTE:"):
            vote = (message.split(":")[-1] == "TRUE")
            if vote:
                self.followers_votes[addr] = 2
            else:
                self.followers_votes[addr] = 1
            self.expected_msgs['VOTE'] -= 1
        
        if message.startswith("RETURNING"):
            self.returning_followers[addr] = True
            # self.print_output("Follower returning")
            
        return

    def request_positions(self):
        self.expected_msgs['POS'] = 8
        for addr in self.followers.keys():
            self.print_output(f"Sent REQ:POS to {addr}")
            self.server.sendto("REQ:POS".encode('utf-8'), (addr, self.port))
        # self.wait_for_responses('POS')

    def check_presence(self):
        self.expected_msgs['CHECK'] = 8
        self.active_followers = {
            '10.0.0.2': False,
            '10.0.0.3': False,
            '10.0.0.4': False,
            '10.0.0.5': False,
            '10.0.0.6': False,
            '10.0.0.7': False,
            '10.0.0.8': False,
            '10.0.0.9': False
        }
        for addr in list(self.followers.keys()):
            self.print_output(f"SENT MESSAGE TO {addr}")
            self.server.sendto("REQ:CHECK".encode('utf-8'), (addr, self.port))
        # self.wait_for_responses('CHECK') Comentei aqui porque quero que sempre passe daqui
        while True:
            time.sleep(2)
            actives = True
            for addr,active in self.active_followers.items():
                if not active:
                    actives = False
                    self.print_output(f"SENT MESSAGE TO {addr}")
                    self.server.sendto("REQ:CHECK".encode('utf-8'), (addr, self.port))
            if actives:
                self.print_output("All Checked")
                break 

    def all_at_destination(self, destination):
        all_reach = True
        for addr, position in self.followers.items():
            direction_vector = [dest - curr for dest, curr in zip(destination, position)]
            # Verifique se o drone já chegou ao destino
            if not all(coord == 0 for coord in direction_vector) and self.active_followers[addr]:
                all_reach = False

        direction_vector = [dest - curr for dest, curr in zip(destination, self.position)]
        if not all(coord == 0 for coord in direction_vector):
            all_reach = False
        return all_reach
    
    def move(self, position):
        self.moving_followers = {
            '10.0.0.2': False,
            '10.0.0.3': False,
            '10.0.0.4': False,
            '10.0.0.5': False,
            '10.0.0.6': False,
            '10.0.0.7': False,
            '10.0.0.8': False,
            '10.0.0.9': False
        }
        while True:
            time.sleep(3)
            all_moved = True
            self.expected_msgs['MOVING'] = 8
            for addr, active in self.active_followers.items():
                if active and not self.moving_followers[addr]:
                    all_moved = False
                    self.print_output(f"SENT MOVE MESSAGE TO {addr}")
                    self.server.sendto(f"REQ:MOVE:{position[0]},{position[1]},{position[2]}".encode('utf-8'), (addr, self.port))
            # self.wait_for_responses('MOVING')
            if all_moved:
                self.print_output("All Moving")
                break  
        moving_thread = threading.Thread(target=self.move_master, args=(position,))
        moving_thread.start()
        while True:
            if self.panic_mode:  # Verifica se o panic mode foi ativado
                self.print_output("Panic mode activated during movement")
                break
            self.request_positions()
            time.sleep(1)
            if self.all_at_destination(position):
                break
    
    def order_to_take_pictures(self):
        self.followers_pics = {
            '10.0.0.2': False,
            '10.0.0.3': False,
            '10.0.0.4': False,
            '10.0.0.5': False,
            '10.0.0.6': False,
            '10.0.0.7': False,
            '10.0.0.8': False,
            '10.0.0.9': False
        }
        self.expected_msgs['PIC'] = 8
        for addr, active in self.active_followers.items():
            if active:
                self.print_output(f"SENT TAKE PICTURES MESSAGE TO {addr}")
                self.server.sendto(f"REQ:PIC".encode('utf-8'), (addr, self.port))
        # self.wait_for_responses('PIC')
        while True:
            time.sleep(2)
            pics_taken = True
            for addr,pic in self.followers_pics.items():
                if not pic and self.active_followers[addr]:
                    pics_taken = False
                    self.print_output(f"SENT TAKE PICTURES MESSAGE TO {addr}")
                    self.server.sendto("REQ:PIC".encode('utf-8'), (addr, self.port))
                    
            if pics_taken:
                self.print_output("All Pictures Taken")
                break
        
    def order_to_vote(self):
        self.expected_msgs['VOTE'] = 8
        for addr, active in self.active_followers.items():
            if active:
                self.print_output(f"SENT VOTE MESSAGE TO {addr}")
                self.server.sendto(f"REQ:VOTE".encode('utf-8'), (addr, self.port))
        # self.wait_for_responses('VOTE')
        while True:
            time.sleep(2)
            all_votes = True
            for addr,vote in self.followers_votes.items():
                if vote == 0 and self.active_followers[addr]:
                    all_votes = False
                    self.print_output(f"SENT VOTE MESSAGE TO {addr}")
                    self.server.sendto(f"REQ:VOTE".encode('utf-8'), (addr, self.port))
            if all_votes:
                self.print_output("All Drones Voted")
                break
            
        count_votes = 0
        total_votes = 0
        for vote in self.followers_votes.values():
            if vote == 1:
                count_votes += 1
            
            if vote != 0:
                total_votes += 1
        
        decision = (count_votes/total_votes >= 0.5)
        return decision

    def handle_timeout(self):
        # Método para tratar o timeout e comandar a movimentação
        self.print_output("TIMEOUT REACHED!! MOVING TO: [10, 10, 0]")
        self.enter_panic_mode()
        
    def run(self):
        listen_thread = threading.Thread(target=self.listen_for_followers)
        listen_thread.start()
        self.check_presence() # First RowCall
        if self.panic_mode:
            return
        # self.move([100,100,0]) # Move to P2
        move_thread = threading.Thread(target=self.move, args=([100, 100, 0],))
        move_thread.start()
        # Aguarde um pouco e entre em panic mode para fins de simulação
        time.sleep(10)
        self.enter_panic_mode()
        if self.panic_mode:
            return
        self.order_to_take_pictures() # Take Images
        if self.panic_mode:
            return
        vote_result = self.order_to_vote()  # Voting
        self.print_output(f"Vote result {vote_result}")
        if not vote_result:            
            self.print_output("GOING TO P3")  # Go to P3, Take Images, Go Back to P1 and RowCall
            self.move([0,100,0])
            if self.panic_mode:
                return
            self.order_to_take_pictures() # Take Images
        self.print_output("GOING TO P1") 
        self.move([10,10,0])
        if self.panic_mode:
            return
        self.check_presence()
        self.print_output("FINISHED") 

    def wait_for_responses(self, request_type):
        start_time = time.time()
        # while self.expected_msgs[request_type] > 0:
        while self.expected_msgs[request_type] == 8:
            if (time.time() - start_time) > self.timeout:
                self.print_output(f"Timeout reached for {request_type}, with expected_msgs = {self.expected_msgs[request_type]}")
                self.handle_timeout()
                break
            time.sleep(0.1)  # Pausa breve para evitar uso excessivo da CPU

if __name__ == '__main__':
    master = MasterDrone()
    try:
        master.run()
    except Exception as e:
        with open(f'drone1_output.txt', 'a') as f:
            f.write(e+"\n")