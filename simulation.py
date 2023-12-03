from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference
import time
import re
import sys
import matplotlib.pyplot as plt

drones_delta = {
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

class Simulation:
    def __init__(self, panic=False, panic_type=0):
        self.net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)
        self.master = None
        self.followers = []
        self.panic = panic == "True"
        self.panic_type = int(panic_type)
    
    def create_position_files(self):
        for i in range(9):
            with open(f'drone{i+1}_position.txt', 'w') as f:
                position = f"{10 + drones_delta[i][0]},{10 + drones_delta[i][1]},0"
                f.write(position)
            with open(f'drone{i+1}_output.txt', 'w') as f:
                f.write('')

    def build_net(self):
        info("*** Creating drones Master and Followers\n")
        followers = []
        for i in range(9):
            position_value = f"{10 + drones_delta[i][0]},{10 + drones_delta[i][1]},0"
            drone_station = self.net.addStation('drone%s' % (i+1), ip6='fe80::%s' % (i+1), position=position_value)
            followers.append(drone_station)

        self.net.setPropagationModel(model="logDistance", exp=4)
        info("*** Configuring nodes\n")
        self.net.configureNodes()

        info("*** Creating links\n")
        for follower in followers:
            self.net.addLink(follower, cls=adhoc, intf='%s-wlan0' % follower.name, ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')

        self.net.build()

        info("\n*** Setting Stations\n")
        # Addressing
        for i, follower in enumerate(followers):
            follower.setIP6('2001::%s/64' % (i+1), intf="%s-wlan0" % follower.name)
        # Movement pattern
        for i, follower in enumerate(followers):
            follower.cmd('iw dev %s-wlan0 interface add mon%s type monitor' % (follower.name, i + 1))
            follower.cmd('ifconfig mon%s up' % (i + 1))
            follower.cmd('python -c "from time import sleep; sleep(%s); print(\'%s ready\')"' % (4, follower.name))
        
        info("*** Creating Position Files For Simulating\n")
        self.create_position_files()

        info("*** Started Master and Follower Processes\n")
        self.master = followers[0]
        self.master.cmd(f'python3 master.py {self.panic} {self.panic_type} &')
        info("** Finished starting master process\n")
        self.followers = followers[1:]
        for i, follower in enumerate(self.followers):
            follower.cmd('python3 follower.py %s &' %(i+2))
        info("** Finished starting followers' processes\n")
    
    def simulate(self):
        x_positions = []
        y_positions = []

        # Update master position
        with open('drone1_position.txt', 'r') as f:
            position = f.read().strip()

        x, y, z = map(float, position.split(','))
        self.master.params['position'] = x, y, z
        
        x_positions.append(x)
        y_positions.append(y)
        
        # Update follower positions
        for i, follower in enumerate(self.followers):
            with open(f'drone{i+2}_position.txt', 'r') as f:
                position = f.read().strip()

            x, y, z = map(float, position.split(','))
            follower.params['position'] = x, y, z

            x_positions.append(x)
            y_positions.append(y)

        # Plotting
        plt.clf()
        plt.scatter(x_positions, y_positions)
        plt.xlim(-10, 120)  # Define o limite do eixo X de 0 a 100
        plt.ylim(-10, 120)
        
        # Adding annotations
        for i, (x, y) in enumerate(zip(x_positions, y_positions)):
            print(f'Drone {i+1} esta na posicao ({x}, {y})')
            plt.annotate(f'D{i+1}', (x, y), textcoords="offset points", xytext=(0,10), ha='center')

        plt.pause(0.1)  # pause a bit so that plots are updated

        print("Positions and plot updated!")


if __name__ == '__main__':
    setLogLevel('info')
    sim = Simulation(panic=sys.argv[1],panic_type=sys.argv[2])
    sim.build_net()

    plt.ion()
    while (True):
        time.sleep(1)
        sim.simulate()

