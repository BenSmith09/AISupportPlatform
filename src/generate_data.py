
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Set a seed so our random data is reproducible
random.seed(42)

# Find the project's root folder
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Create the data folder if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

# Fictional support ticket categories
ISSUES = {
    "Dahua NVR": [
        "NVR not recording footage",
        "Hard drive not overwriting",
        "Unable to access NVR remotely",
        "Camera showing offline",
        "Motion detection not working"
    ],
    "Akuvox Intercom": [
        "Monitor not receiving calls",
        "Door station not connecting",
        "SmartPlus app not ringing",
        "Unable to unlock door remotely",
        "Intercom audio not working"
    ],
    "Ajax Alarm": [
        "Hub showing offline",
        "Motion detector false alarms",
        "Keypad not arming system",
        "Device not pairing with hub",
        "Alarm notifications delayed"
    ],
    "Networking": [
        "PoE switch not powering cameras",
        "Wireless bridge losing connection",
        "IP address conflict",
        "Network connection dropping",
        "Insufficient bandwidth for cameras"
    ]
}

STATUSES = ["Open", "In Progress", "Resolved", "Closed"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]

CUSTOMERS = [
    "ABC Electrical",
    "Northside Security",
    "Brisbane Installations",
    "SecureTech Solutions",
    "XYZ Electrical",
    "Coastal CCTV",
    "Metro Security",
    "Reliable Installers"
]

def generate_ticket(ticket_id):
    """Generate one fictional support ticket."""

    product = random.choice(list(ISSUES.keys()))
    description = random.choice(ISSUES[product])

    # Random date within the last 180 days
    created_at = datetime(2026, 11, 1) - timedelta(
        days=random.randint(0, 180)
    )

    return {
        "ticket_id": ticket_id,
        "customer": random.choice(CUSTOMERS),
        "product": product,
        "description": description,
        "priority": random.choices(
            PRIORITIES,
            weights=[20, 50, 25, 5]
        )[0],
        "status": random.choice(STATUSES),
        "created_at": created_at.strftime("%Y-%m-%d")
    }


def main():
    # Generate 500 support tickets
    tickets = [
        generate_ticket(i)
        for i in range(1, 501)
    ]

    # Introduce 10 duplicate records
    duplicates = random.sample(tickets, 10)
    tickets.extend(duplicates)

    # Introduce missing product values
    for ticket in random.sample(tickets, 15):
        ticket["product"] = ""

    # Save the dataset
    output_file = DATA_DIR / "raw_tickets.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=tickets[0].keys()
        )

        writer.writeheader()
        writer.writerows(tickets)

    print(f"Generated {len(tickets)} ticket rows")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()
