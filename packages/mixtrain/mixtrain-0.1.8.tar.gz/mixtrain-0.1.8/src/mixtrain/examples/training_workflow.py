"""
Training Workflow Example
This example demonstrates a complete training workflow using the Postrix SDK.
"""

import time

from postrix.client import create_dataset, get_training_status, start_training


def setup_training_environment():
    """Set up the training environment by creating necessary datasets."""
    print("Setting up training environment...")
    create_dataset("training_data")
    create_dataset("validation_data")

def monitor_training():
    """Monitor the training progress."""
    print("\nStarting training...")
    start_training()

    # Monitor training status for a few iterations
    print("\nMonitoring training progress...")
    for _ in range(5):
        get_training_status()
        time.sleep(2)  # Check status every 2 seconds

def main():
    print("=== Training Workflow Example ===")

    # Set up the training environment
    setup_training_environment()

    # Start and monitor training
    monitor_training()

    print("\nTraining workflow completed!")

if __name__ == "__main__":
    main()
