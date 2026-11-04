
import pandas as pd

def main():
    print("AI Support Intelligence Platform")
    print("--------------------------------")

    tickets = pd.DataFrame([
        {
            "ticket_id": 1,
            "product": "Dahua NVR",
            "description": "NVR not recording"
        },
        {
            "ticket_id": 2,
            "product": "Akuvox Intercom",
            "description": "Monitor not receiving calls"
        },
        {
            "ticket_id": 3,
            "product": "Ajax Alarm",
            "description": "Hub showing offline"
        }
    ])

    print(tickets)
    print(f"\nTotal tickets: {len(tickets)}")

if __name__ == "__main__":
    main()
