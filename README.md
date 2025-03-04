# Scale Models and Logical Clocks

This project simulates an asynchronous distributed system using 3 virtual machines (VMs) that communicate via sockets using Python. Each VM maintains a logical clock and can send and receive messages with peers. The system logs all activities accordingly.


## Running the Project

Execute the following command to start the system:
```sh
python virtualmachine.py
```

- This will start three virtual machines, each running in a separate thread.
- The simulation runs for 60 seconds, during which the VMs send messages, process internal events, and update their logical clocks.

## File Structure

```sh
.
├── virtualmachine.py  
├── test.py           
```

### `virtualmachine.py`
Defines the `VirtualMachine` class that represents a node in the distributed system.

Each VM:
- Maintains a logical clock
- Listens for incoming messages and processes them.
- Generates random internal events or sends messages to peers.
- Logs all events to a file (e.g., vm_0_log.txt).


### `test.py`

Contains unit tests for the `VirtualMachine` class using `unittest`.
