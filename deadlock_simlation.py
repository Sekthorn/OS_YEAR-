import threading
import time
from threading import Semaphore

# Shared resources: Account classes
class Account:
    def __init__(self, account_id, balance):
        self.account_id = account_id
        self.balance = balance
        self.lock = Semaphore(1)  # Binary semaphore for critical section
    
    def __repr__(self):
        return f"Account(id={self.account_id}, balance=${self.balance})"


# Create shared resources
account1 = Account("Account1", 1000)
account2 = Account("Account2", 1000)


# Transfer function with critical section protected by semaphore lock
def transfer(from_account, to_account, amount, thread_name):
    """
    Transfer money from one account to another.
    This function demonstrates deadlock when two threads call it simultaneously.
    """
    print(f"\n[{thread_name}] Attempting to acquire lock on {from_account.account_id}")
    
    # CRITICAL SECTION 1: Acquire lock on first account
    from_account.lock.acquire()
    print(f"[{thread_name}] ✓ Acquired lock on {from_account.account_id}")
    
    # Simulate some processing time - increases chance of deadlock
    time.sleep(0.1)
    
    print(f"[{thread_name}] Attempting to acquire lock on {to_account.account_id}")
    
    # CRITICAL SECTION 2: Acquire lock on second account
    # If thread1 locks account1 and thread2 locks account2,
    # then both will wait forever for each other's lock → DEADLOCK
    to_account.lock.acquire()
    print(f"[{thread_name}] ✓ Acquired lock on {to_account.account_id}")
    
    try:
        # Perform the transfer
        if from_account.balance >= amount:
            from_account.balance -= amount
            to_account.balance += amount
            print(f"[{thread_name}] ✓ Transferred ${amount} from {from_account.account_id} to {to_account.account_id}")
            print(f"    {from_account.account_id} balance: ${from_account.balance}")
            print(f"    {to_account.account_id} balance: ${to_account.balance}")
        else:
            print(f"[{thread_name}] ✗ Insufficient funds in {from_account.account_id}")
    finally:
        # Release locks
        to_account.lock.release()
        print(f"[{thread_name}] Released lock on {to_account.account_id}")
        
        from_account.lock.release()
        print(f"[{thread_name}] Released lock on {from_account.account_id}")


# Transfer function with ORDERING (deadlock prevention)
def transfer_ordered(from_account, to_account, amount, thread_name):
    """
    Transfer money with ORDERED lock acquisition using min/max approach.
    Prevents deadlock by always acquiring locks in a consistent order.
    Based on the "Dealing With Deadlocks" approach:
    - Establish a fixed ordering to shared resources
    - All requests made in prescribed order
    """
    # Determine lock order using min/max: always acquire smaller ID first
    # Extract numeric ID for comparison (e.g., "Account1" -> 1)
    from_id = int(from_account.account_id.replace("Account", ""))
    to_id = int(to_account.account_id.replace("Account", ""))
    
    # a = min(account1, account2)
    # b = max(account1, account2)
    if from_id < to_id:
        lock_a = from_account
        lock_b = to_account
    else:
        lock_a = to_account
        lock_b = from_account
    
    print(f"\n[{thread_name}] Attempting to acquire lock on {lock_a.account_id} (min)")
    
    # wait(lock[a]) - Acquire minimum lock first
    lock_a.lock.acquire()
    print(f"[{thread_name}] ✓ wait(lock[{lock_a.account_id}])")
    
    # Simulate some processing time
    time.sleep(0.1)
    
    print(f"[{thread_name}] Attempting to acquire lock on {lock_b.account_id} (max)")
    
    # wait(lock[b]) - Acquire maximum lock second
    # No deadlock because ALL threads acquire in the SAME order (min → max)
    lock_b.lock.acquire()
    print(f"[{thread_name}] ✓ wait(lock[{lock_b.account_id}])")
    
    try:
        # Perform the transfer (critical section)
        if from_account.balance >= amount:
            from_account.balance -= amount
            to_account.balance += amount
            print(f"[{thread_name}] ✓ balance[{from_account.account_id}] = {from_account.balance}")
            print(f"[{thread_name}] ✓ balance[{to_account.account_id}] = {to_account.balance}")
            print(f"[{thread_name}] ✓ Transferred ${amount} from {from_account.account_id} to {to_account.account_id}")
        else:
            print(f"[{thread_name}] ✗ Insufficient funds in {from_account.account_id}")
    finally:
        # signal(lock[b]) - Release maximum lock first
        lock_b.lock.release()
        print(f"[{thread_name}] ✓ signal(lock[{lock_b.account_id}])")
        
        # signal(lock[a]) - Release minimum lock second
        lock_a.lock.release()
        print(f"[{thread_name}] ✓ signal(lock[{lock_a.account_id}])")


def thread1_task():
    """Thread 1: Transfer from account1 to account2"""
    transfer(account1, account2, 100, "Thread-1")


def thread2_task():
    """Thread 2: Transfer from account2 to account1"""
    transfer(account2, account1, 50, "Thread-2")


def thread1_task_ordered():
    """Thread 1: Transfer from account1 to account2 (with ordering)"""
    transfer_ordered(account1, account2, 100, "Thread-1")


def thread2_task_ordered():
    """Thread 2: Transfer from account2 to account1 (with ordering)"""
    transfer_ordered(account2, account1, 50, "Thread-2")


def main():
    print("=" * 60)
    print("DEADLOCK SIMULATION: Bank Account Transfer")
    print("=" * 60)
    print(f"\nInitial State:")
    print(f"  {account1}")
    print(f"  {account2}")
    print(f"\nStarting two threads that will attempt transfers...")
    print(f"Thread-1: Transfer $100 from Account1 to Account2")
    print(f"Thread-2: Transfer $50 from Account2 to Account1")
    print(f"\n⚠️  WARNING: This will likely cause a DEADLOCK!")
    print(f"   If the program freezes, that's the deadlock in action.")
    print("=" * 60)
    
    # Create two threads that will run concurrently
    t1 = threading.Thread(target=thread1_task, daemon=False)
    t2 = threading.Thread(target=thread2_task, daemon=False)
    
    # Start both threads at roughly the same time
    t1.start()
    t2.start()
    
    # Wait for threads to complete (or timeout)
    t1.join(timeout=3)
    t2.join(timeout=3)
    
    if t1.is_alive() or t2.is_alive():
        print("\n" + "=" * 60)
        print("🔴 DEADLOCK DETECTED!")
        print("=" * 60)
        print("The threads are stuck waiting for each other's locks.")
        print("Thread-1 has Account1 lock and is waiting for Account2 lock.")
        print("Thread-2 has Account2 lock and is waiting for Account1 lock.")
        print("\nThis is a classic circular wait deadlock condition!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Final State:")
        print(f"  {account1}")
        print(f"  {account2}")
        print("=" * 60)


def main_ordered():
    """Demonstrate deadlock prevention using min/max ORDERING"""
    # Reset account balances
    account1.balance = 1000
    account2.balance = 1000
    
    print("\n\n" + "=" * 70)
    print("DEADLOCK PREVENTION: Using Fixed Ordering (min/max approach)")
    print("=" * 70)
    print(f"\n📋 Cooperating processes approach:")
    print(f"   - Establish a fixed ordering to shared resources")
    print(f"   - Require all requests to be made in prescribed order")
    print(f"\nInitial State:")
    print(f"  {account1}")
    print(f"  {account2}")
    print(f"\nStarting two threads with ORDERED lock acquisition...")
    print(f"\nThread-1: Transfer(Account1, Account2, 100)")
    print(f"  → a = min(1, 2) = Account1")
    print(f"  → b = max(1, 2) = Account2")
    print(f"  → wait(lock[a]) → wait(lock[b]) → transfer → signal(b) → signal(a)")
    print(f"\nThread-2: Transfer(Account2, Account1, 50)")
    print(f"  → a = min(2, 1) = Account1")
    print(f"  → b = max(2, 1) = Account2")
    print(f"  → wait(lock[a]) → wait(lock[b]) → transfer → signal(b) → signal(a)")
    print(f"\n✓ Both threads acquire locks in the SAME order: Account1 → Account2")
    print(f"✓ This prevents circular wait → NO DEADLOCK!")
    print("=" * 70)
    
    # Create two threads with ordered transfer
    t1 = threading.Thread(target=thread1_task_ordered, daemon=False)
    t2 = threading.Thread(target=thread2_task_ordered, daemon=False)
    
    # Start both threads
    t1.start()
    t2.start()
    
    # Wait for completion
    t1.join(timeout=5)
    t2.join(timeout=5)
    
    if t1.is_alive() or t2.is_alive():
        print("\n" + "=" * 70)
        print("🔴 UNEXPECTED: Deadlock still occurred!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("🟢 SUCCESS! No Deadlock with Fixed Ordering!")
        print("=" * 70)
        print("Final State:")
        print(f"  {account1}")
        print(f"  {account2}")
        print("\n✓ Both transfers completed successfully!")
        print("✓ Ordering prevented the circular wait condition.")
        print("✓ This is the 'Dealing With Deadlocks' cooperating process approach!")
        print("=" * 70)


if __name__ == "__main__":
    # Run demonstration 1: Shows deadlock
    main()
    
    # Run demonstration 2: Shows deadlock prevention with ordering
    main_ordered()
