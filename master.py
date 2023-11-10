import socket
import threading
import random
import time

class MasterDrone:
    def __init__(self):
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
    
    def print_output(self, text):
        with open(f'drone{self.id}_output.txt', 'a') as f:
            f.write(text+"\n")

    def update_position(self, new_position):
        with open(f'drone{self.id}_position.txt', 'w') as f:
            f.write(new_position)

    def move_master(self, destination):
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

    
    def random_position(self):
        while(True):
            time.sleep(3)
            position = f"{random.randint(0, 100)},{random.randint(0, 100)},0"  # Atualizando posição aleatoriamente
            self.update_position(position)

    def listen_for_followers(self):
        while True:
            data, addr = self.server.recvfrom(4096)
            self.handle_message(data.decode('utf-8'), addr[0])

    def handle_message(self, message, addr):
        self.print_output(message)
        if message.startswith("POS:"):
            _, pos = message.split(":")
            self.followers[addr] = [float(i) for i in pos.split(",")]
        if message.startswith("CHECK:"):
            self.active_followers[addr] = True
        if message.startswith("MOVING"):
            self.moving_followers[addr] = True
        if message.startswith("PIC:"):
            self.followers_pics[addr] = True
        if message.startswith("VOTE:"):
            vote = (message.split(":")[-1] == "TRUE")
            if vote:
                self.followers_votes[addr] = 2
            else:
                self.followers_votes[addr] = 1
            
        return

    def request_positions(self):
        for addr in self.followers.keys():
            self.print_output(f"Sent REQ:POS to {addr}")
            self.server.sendto("REQ:POS".encode('utf-8'), (addr, self.port))

    def check_presence(self):
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
            for addr, active in self.active_followers.items():
                if active and not self.moving_followers[addr]:
                    all_moved = False
                    self.print_output(f"SENT MOVE MESSAGE TO {addr}")
                    self.server.sendto(f"REQ:MOVE:{position[0]},{position[1]},{position[2]}".encode('utf-8'), (addr, self.port))
            if all_moved:
                self.print_output("All Moving")
                break  

        moving_thread = threading.Thread(target=self.move_master, args=(position,))
        moving_thread.start()

        while True:
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

        for addr, active in self.active_followers.items():
            if active:
                self.print_output(f"SENT TAKE PICTURES MESSAGE TO {addr}")
                self.server.sendto(f"REQ:PIC".encode('utf-8'), (addr, self.port))
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
        for addr, active in self.active_followers.items():
            if active:
                self.print_output(f"SENT VOTE MESSAGE TO {addr}")
                self.server.sendto(f"REQ:VOTE".encode('utf-8'), (addr, self.port))

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


    def run(self):
        listen_thread = threading.Thread(target=self.listen_for_followers)
        listen_thread.start()

        # First RowCall
        self.check_presence()

        # Move to P2
        self.move([100,100,0])

        # Take Images
        self.order_to_take_pictures()
        self.print_output("All Pictures Taken 2")
        # Voting
        vote_result = self.order_to_vote()
        self.print_output(f"VOte result {vote_result}")
        if not vote_result:            
            self.print_output("GOING TO P3")
            # Go to P3, Take Images, Go Back to P1 and RowCall
            self.move([0,100,0])
            # Take Images
            self.order_to_take_pictures()

        self.print_output("GOING TO P1") 
        self.move([10,10,0])
        self.check_presence()
        self.print_output("FINISHED") 

if __name__ == '__main__':
    master = MasterDrone()
    try:
        master.run()
    except Exception as e:
        with open(f'drone1_output.txt', 'a') as f:
            f.write(e+"\n")