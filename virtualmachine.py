import socket
import threading
import time
import random
import queue
from datetime import datetime
import multiprocessing

class VirtualMachine:
    """
    A virtual machine that simulates an asynchronous distributed system with logical clocks.
    Each virtual machine runs at a different speed, communicates via sockets, and logs events.
    """
    def __init__(self, vm_id, peers, port):
        """
        Initialize the virtual machine.
        
        Parameters:
        - vm_id (int): Unique identifier for the virtual machine.
        - peers (list): List of peer machine ports.
        - port (int): Port number for this VM to listen on.
        """
        self.vm_id = vm_id  
        self.peers = peers  # List of peer VM addresses (host, port)
        self.port = port  
        self.clock_speed = random.randint(1, 6)  # Random clock speed (1-6)
        self.logical_clock = 0  # Logical clock
        self.message_queue = queue.Queue()  # Queue for incoming messages
        self.log_file = open(f"vm_{vm_id}_log.txt", "w")
        self.log_file.write(f"VM ID: {self.vm_id}, Port: {self.port}, Clock Speed: {self.clock_speed} ticks/sec\n")
        self.log_file.flush()
        self.running = True  

    
    def listen(self):
        """
        Listen for incoming messages on a socket and add them to the message queue.
        """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("localhost", self.port))
        server.listen()
        while self.running:
            try:
                conn, _ = server.accept()
                data = conn.recv(1024).decode()
                if data:
                    self.message_queue.put(int(data))
                conn.close()
            except Exception as e:
                print(f"Error on VM {self.vm_id}: {e}")
    
    def send_message(self, target_port):
        """
        Send a message containing the logical clock to a peer.
        
        Parameters:
        - target_port (int): The port number of the target virtual machine.
        """
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("localhost", target_port))
            client.sendall(str(self.logical_clock).encode())
            client.close()
        except Exception as e:
            print(f"Error sending message from VM {self.vm_id} to port {target_port}: {e}")
    
    def process_cycle(self):
        """
        Process one cycle of execution:
        - If a message is in the queue, the machine retrieves the message, updates its logical clock
          according to the Lamport clock rules, and logs the event.
        - If no message is present, the machine generates a random number from 1 to 10 to determine
          its action:
            - If the number is 1, it sends a message to one peer, increments its logical clock, and logs the event.
            - If the number is 2, it sends a message to the other peer, increments its logical clock, and logs the event.
            - If the number is 3, it broadcasts a message to all peers, increments its logical clock, and logs the event.
            - For any other value (4-10), it treats this cycle as an internal event, increments its logical clock, and logs the event.
        """
        if not self.message_queue.empty():
            received_time = self.message_queue.get()
            self.logical_clock = max(self.logical_clock, received_time) + 1
            log_entry = f"Received message: Logical Clock = {self.logical_clock}, System Time = {datetime.now()}, Queue Length = {self.message_queue.qsize()}\n"
        else:
            action = random.randint(1, 10)
            self.logical_clock += 1
            if action == 1:
                target = self.peers[0]
                self.send_message(target)
                log_entry = f"Sent message to {target}: Logical Clock = {self.logical_clock}, System Time = {datetime.now()}\n"
            elif action == 2:
                target = self.peers[1]
                self.send_message(target)
                log_entry = f"Sent message to {target}: Logical Clock = {self.logical_clock}, System Time = {datetime.now()}\n"
            elif action == 3:
                for peer in self.peers:
                    self.send_message(peer)
                log_entry = f"Broadcast message: Logical Clock = {self.logical_clock}, System Time = {datetime.now()}\n"
            else:
                log_entry = f"Internal event: Logical Clock = {self.logical_clock}, System Time = {datetime.now()}\n"
        self.log_file.write(log_entry)
        self.log_file.flush()
    
    def run(self):
        """
        Main execution loop:
        - Starts a thread for listening.
        - Runs for a fixed duration (60 seconds), processing cycles at the machine's clock speed.
        """
        threading.Thread(target=self.listen, daemon=True).start()
        start_time = time.time()
        while self.running and (time.time() - start_time) <= 60:
            self.process_cycle()
            time.sleep(1 / self.clock_speed)
        self.stop()
    
    def stop(self):
        """
        Stop execution and close the log file.
        """
        self.running = False
        self.log_file.close()


def vm_process(vm_id, peers, port):
    """
    Create a virtual machine in a separate process and start to run the process. 

    Parameters:
        - vm_id (int): Unique identifier for the virtual machine.
        - peers (list): List of peer machine ports.
        - port (int): Port number for this VM to listen on.
    """
    vm = VirtualMachine(vm_id, peers, port)
    vm.run()


if __name__ == "__main__":
    vm_ports = [6000, 6001, 6002]
    processes = []
    
    # Start a separate process for each virtual machine
    for i, port in enumerate(vm_ports):
        peers = [p for p in vm_ports if p != port]
        p = multiprocessing.Process(target=vm_process, args=(i, peers, port))
        processes.append(p)
        p.start() 

    time.sleep(60) 

    for p in processes:
        p.terminate()
        p.join()