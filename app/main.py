from tickets import TicketStore

def main():
    store = TicketStore()

    while True:
        print("\n=== Help Desk Ticket Simulator ===")
        print("1) List tickets")
        print("2) View ticket details")
        print("3) Create ticket")
        print("4) Update ticket status")
        print("5) Add work note")
        print("6) Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            for t in store.list_tickets():
                print(f'{t["id"]} | {t["status"]:<11} | {t["priority"]:<2} | {t["title"]}')

        elif choice == "2":
            ticket_id = input("Ticket ID (ex: TKT-001): ").strip().upper()
            t = store.get_ticket(ticket_id)
            if not t:
                print("Ticket not found.")
                continue

            print("\n--- Ticket Details ---")
            print(f'ID: {t["id"]}')
            print(f'Title: {t["title"]}')
            print(f'Status: {t["status"]}')
            print(f'Priority: {t["priority"]}')
            print(f'Category: {t["category"]}')
            print(f'User: {t["user"]}')
            print(f'Created: {t["created_at"]}')
            print(f'Updated: {t["updated_at"]}')
            print("\nSymptoms:")
            print(f'- {t["symptoms"]}')
            print("\nWork Notes:")
            if t["work_notes"]:
                for n in t["work_notes"]:
                    print(f'- [{n["at"]}] {n["note"]}')
            else:
                print("- (none)")

        elif choice == "3":
            title = input("Title: ").strip()
            user = input("User (ex: J. Smith): ").strip()
            category = input("Category (VPN/O365/AD/Hardware/etc): ").strip()
            priority = input("Priority (P1/P2/P3): ").strip().upper() or "P3"
            symptoms = input("Symptoms (1 sentence): ").strip()

            new_ticket = store.create_ticket(title, user, category, priority, symptoms)
            print(f'Created {new_ticket["id"]}.')

        elif choice == "4":
            ticket_id = input("Ticket ID: ").strip().upper()
            status = input("New status (Open/In Progress/Resolved/Escalated): ").strip().title()
            ok = store.update_status(ticket_id, status)
            print("Updated." if ok else "Update failed (check ticket ID/status).")

        elif choice == "5":
            ticket_id = input("Ticket ID: ").strip().upper()
            note = input("Work note: ").strip()
            ok = store.add_work_note(ticket_id, note)
            print("Added note." if ok else "Ticket not found.")

        elif choice == "6":
            print("Bye.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
