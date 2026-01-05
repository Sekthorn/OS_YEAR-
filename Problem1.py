import threading
import time
import random

BUFFER_SIZE = 100
buffer = []

space = threading.Semaphore(BUFFER_SIZE)
full = threading.Semaphore(0)

lock = threading.Semaphore(1)


def producer(pid):
    while True:
        P1,P2 = f"P{pid}-A", f"P{pid}-B"
        space.acquire()
        space.acquire()

        lock.acquire()
        buffer.append(P1)
        buffer.append(P2)
        print(f"Producer {pid} produced: pair : {P1}, {P2} | Buffer size: {len(buffer)}")
        lock.release()

        full.release()
        full.release()

        time.sleep(random.uniform(0.5, 1))
def consumer(cid):
    while True:
        full.acquire()
        full.acquire()

        lock.acquire()
        P1 = buffer.pop(0)
        P2 = buffer.pop(0)
        print(f"Consumer {cid} consumed: pair : {P1}, {P2} | Buffer size: {len(buffer)}")
        lock.release()

        space.release()
        space.release()
        time.sleep(random.uniform(1, 2))

producers = [threading.Thread(target=producer, args=(i,)) for i in range(3)]
consumer_thread = threading.Thread(target=consumer, args=(0,))
for p in producers:
    p.start()
consumer_thread.start()