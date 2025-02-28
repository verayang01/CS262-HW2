import unittest
import threading
import time
import socket
from virtualmachine import VirtualMachine

class TestVirtualMachine(unittest.TestCase):

    def setUp(self):
        """Set up three VirtualMachine instances with unique ports."""
        base_port = 6000 + (int(time.time()) % 1000)  # Generate dynamic ports 
        self.vm0 = VirtualMachine(vm_id=0, peers=[base_port+1, base_port+2], port=base_port)
        self.vm1 = VirtualMachine(vm_id=1, peers=[base_port, base_port+2], port=base_port+1)
        self.vm2 = VirtualMachine(vm_id=2, peers=[base_port, base_port+1], port=base_port+2)

        self.vm0.running = True
        self.vm1.running = True
        self.vm2.running = True

        self.listen_thread0 = threading.Thread(target=self.vm0.listen, daemon=True)
        self.listen_thread1 = threading.Thread(target=self.vm1.listen, daemon=True)
        self.listen_thread2 = threading.Thread(target=self.vm2.listen, daemon=True)

        self.listen_thread0.start()
        self.listen_thread1.start()
        self.listen_thread2.start()

        time.sleep(0.5) 

    def tearDown(self):
        """Stop all VMs after tests."""
        self.vm0.stop()
        self.vm1.stop()
        self.vm2.stop()

        if self.listen_thread0.is_alive():
            self.listen_thread0.join(timeout=1)
        if self.listen_thread1.is_alive():
            self.listen_thread1.join(timeout=1)
        if self.listen_thread2.is_alive():
            self.listen_thread2.join(timeout=1)
        time.sleep(0.5)

    def test_listen(self):
        """Test if listen correctly places received messages in the queue."""
        sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sender_socket.connect(("localhost", self.vm0.port))
        sender_socket.sendall(b"5")
        sender_socket.close()

        time.sleep(0.2)
        self.assertFalse(self.vm0.message_queue.empty())
        self.assertEqual(self.vm0.message_queue.get(), 5)

    def test_send_message(self):
        """Test send_message sends the correct logical clock value."""
        self.vm0.logical_clock = 10
        self.vm0.send_message(self.vm1.port)
        time.sleep(0.2)  
        self.assertFalse(self.vm1.message_queue.empty())
        self.assertEqual(self.vm1.message_queue.get(), 10)

    def test_process_cycle_internal_event(self):
        """Test process_cycle when no message is received (internal event)."""
        initial_clock = self.vm0.logical_clock
        self.vm0.process_cycle()
        self.assertEqual(self.vm0.logical_clock, initial_clock + 1)

    def test_process_cycle_message_received(self):
        """Test process_cycle when a message is received."""
        self.vm0.message_queue.put(7)
        self.vm0.process_cycle()
        self.assertEqual(self.vm0.logical_clock, 8)

    def test_process_cycle_sends_message(self):
        """Test process_cycle when sending a message to a peer."""
        self.vm0.logical_clock = 5
        self.vm0.process_cycle()
        time.sleep(0.2) 
        self.assertGreaterEqual(self.vm0.logical_clock, 6)

    def test_run_stops_properly(self):
        """Test that the virtual machine stops properly after running for a short duration."""
        self.vm0.running = True
        run_thread = threading.Thread(target=self.vm0.run)
        run_thread.start()
        time.sleep(1)
        self.vm0.stop()
        run_thread.join()
        self.assertFalse(self.vm0.running)

    def test_stop(self):
        """Test stop function sets running to False."""
        self.vm0.running = True
        self.vm0.stop()
        self.assertFalse(self.vm0.running)

if __name__ == "__main__":
    unittest.main()
