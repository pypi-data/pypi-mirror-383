import os
import requests
import pandas as pd
import json
import time
from prettytable import PrettyTable
from .utils import safe_print

class KiteAlerts:
    """Manage Kite alerts with CSV import/export, cleanup, and history tools."""

    def __init__(self, config_path="credentials/config.json", auto_menu=False):
        self.config_path = config_path
        self.base_url = "https://api.kite.trade"

        # ✅ Define standardized directories
        self.input_dir = os.path.join("Input", "Alert")
        self.output_dir = os.path.join("output", "Alert")

        # ✅ Ensure directories exist
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        self._load_credentials()

        if auto_menu:
            self.menu()

    # ------------------- CONFIG -------------------
    def _load_credentials(self):
        """Load API credentials from config.json"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            self.api_key = config["KITE"]["API_KEY"]
            self.access_token = config["SESSION"]["ACCESS_TOKEN"]
            self.headers = {
                "X-Kite-Version": "3",
                "Authorization": f"token {self.api_key}:{self.access_token}"
            }
        except Exception as e:
            raise ValueError(f"❌ Failed to load credentials: {e}")


    # ------------------- API WRAPPERS -------------------
    def create_simple_alert(self, name, symbol, exchange, operator, price, tags=None):
        payload = {
            "name": name,
            "type": "simple",
            "lhs_exchange": exchange,
            "lhs_tradingsymbol": symbol,
            "lhs_attribute": "LastTradedPrice",
            "operator": operator,
            "rhs_type": "constant",
            "rhs_constant": price
        }
        if isinstance(tags, str) and tags.strip():
            payload["tags"] = [t.strip() for t in tags.split(",")]

        return requests.post(f"{self.base_url}/alerts", headers=self.headers, data=payload).json()

    def get_all_alerts(self, status=None):
        params = {"status": status} if status else {}
        return requests.get(f"{self.base_url}/alerts", headers=self.headers, params=params).json()

    def get_alert_history(self, uuid):
        return requests.get(f"{self.base_url}/alerts/{uuid}/history", headers=self.headers).json()

    def delete_alert(self, uuid_list):
        if isinstance(uuid_list, str):
            uuid_list = [uuid_list]
        params = [("uuid", uuid) for uuid in uuid_list]
        return requests.delete(f"{self.base_url}/alerts", headers=self.headers, params=params).json()

    def reactivate_alert(self, uuid_list):
        if isinstance(uuid_list, str):
            uuid_list = [uuid_list]

        success, failed = 0, []
        for uuid in uuid_list:
            alert = requests.get(f"{self.base_url}/alerts/{uuid}", headers=self.headers).json()
            if alert.get("status") == "success":
                payload = alert["data"]
                payload["status"] = "enabled"
                resp = requests.put(f"{self.base_url}/alerts/{uuid}", headers=self.headers, data=payload)
                if resp.status_code == 200 and resp.json().get("status") == "success":
                    success += 1
                else:
                    failed.append((uuid, resp.json()))
            else:
                failed.append((uuid, alert))

        safe_print(f"⚡ Summary: {success} reactivated, {len(failed)} failed.")
        for uuid, err in failed:
            safe_print(f"❌ Failed: {uuid} | {err}")

    # ---------------- BULK CREATE ALERTS ----------------
    def bulk_create_alerts_from_csv(self,
                                    csv_file=None,
                                    error_csv=None):
        # ✅ Paths as per your instruction
        csv_file = csv_file or os.path.join(self.input_dir, "1. Add_bulk_alerts.csv")
        error_csv = error_csv or os.path.join(self.output_dir, "2. alerts_errors.csv")

        df = pd.read_csv(csv_file)
        df = df.dropna(subset=["symbol", "exchange", "operator", "price"])

        active_alerts = self.get_all_alerts(status="enabled").get("data", [])
        active_keys = {(a["lhs_tradingsymbol"], a["lhs_exchange"], a["operator"], a["rhs_constant"]) for a in active_alerts}

        results, error_rows = [], []
        safe_print(f"\n📦 Creating Alerts from: {csv_file}\n")

        for i, row in df.iterrows():
            try:
                name = row.get("name") if pd.notna(row.get("name")) else f"{row['symbol']} Alert"
                tags = row.get("tags") if pd.notna(row.get("tags")) else None
                price = float(row["price"])

                key = (row["symbol"].strip(), row["exchange"].strip(), row["operator"].strip(), price)
                if key in active_keys:
                    safe_print(f"⚠️ Alert already active for {row['symbol']}, skipped.")
                    continue

                result = self.create_simple_alert(
                    name=name.strip(),
                    symbol=row["symbol"].strip(),
                    exchange=row["exchange"].strip(),
                    operator=row["operator"].strip(),
                    price=price,
                    tags=tags
                )

                if result.get("status") == "success":
                    safe_print(f"✅ Created alert for {row['symbol']}")
                else:
                    safe_print(f"❌ Error creating alert for {row['symbol']}")
                    error_rows.append({**row, "error": json.dumps(result)})

                results.append(result)

                if (i + 1) % 10 == 0:
                    time.sleep(1)

            except Exception as e:
                safe_print(f"❌ Exception creating alert for {row.get('symbol', 'unknown')}: {e}")
                error_rows.append({**row, "error": str(e)})

        if error_rows:
            pd.DataFrame(error_rows).to_csv(error_csv, index=False)
            safe_print(f"\n⚠️ Errors logged to {error_csv}")

        safe_print("\n🎯 Bulk alert creation completed.\n")
        return results

    # ---------------- EXPORT ACTIVE ALERTS ----------------
    def export_active_alerts_to_csv(self, csv_file=None):
        # ✅ Export path to output/Alert folder
        csv_file = csv_file or os.path.join(self.output_dir, "3. Active Alerts.csv")

        alerts = self.get_all_alerts(status="enabled").get("data", [])
        if not alerts:
            safe_print("ℹ️ No active alerts found.")
            return

        data = [{
            "uuid": a.get("uuid"),
            "name": a.get("name"),
            "symbol": a.get("lhs_tradingsymbol"),
            "exchange": a.get("lhs_exchange"),
            "operator": a.get("operator"),
            "price": a.get("rhs_constant"),
            "status": a.get("status"),
            "created_at": a.get("created_at"),
            "updated_at": a.get("updated_at"),
        } for a in alerts]

        pd.DataFrame(data).to_csv(csv_file, index=False)
        safe_print(f"💾 Exported Active Alerts to {csv_file}")

    # ---------------- CLEANUP ALERTS ----------------

    def cleanup_alerts(self):
        safe_print("\n🧹 ===== Cleanup Options ===== 🧹\n")
        safe_print("1️⃣   💣  Delete ALL alerts (Active + Triggered/Disabled)")
        safe_print("2️⃣   ⚡  Delete only ACTIVE alerts")
        safe_print("3️⃣   💤  Delete only TRIGGERED/DISABLED alerts")
        safe_print("4️⃣   ❎  Cancel / Return to main menu")

        choice = input("\nSelect cleanup option: ").strip()
        alerts = self.get_all_alerts().get("data", [])
        if not alerts:
            safe_print("ℹ️ No alerts found.")
            return
        
        uuids_to_delete = []

        if choice == "1":
            uuids_to_delete = [a["uuid"] for a in alerts]
        elif choice == "2":
            uuids_to_delete = [a["uuid"] for a in alerts if a["status"] == "enabled"]
        elif choice == "3":
            uuids_to_delete = [a["uuid"] for a in alerts if a["status"] in ["disabled", "deleted"]]
        elif choice == "4":
            safe_print("↩️ Cancelled cleanup. Returning to main menu.\n")
            return
        else:
            safe_print("❌ Invalid choice. Returning to main menu.\n")
            return

        if uuids_to_delete:
            confirm = input(f"⚠️  Are you sure you want to delete {len(uuids_to_delete)} alerts? (Y/N): ").strip().lower()
            if confirm == "y":
                self.delete_alert(uuids_to_delete)
                safe_print(f"🗑️  Deleted {len(uuids_to_delete)} alerts.")
            else:
                safe_print("↩️ Cleanup cancelled by user.")
        else:
            safe_print("ℹ️ No matching alerts found to delete.")

    # ---------------- ALERT HISTORY ----------------

    def show_alert_history(self):
        while True:
            alerts = self.get_all_alerts(status="enabled").get("data", [])
            if not alerts:
                safe_print("ℹ️ No active alerts found.")
                return

            table = PrettyTable(["No.", "Name", "Symbol", "UUID", "Status", "History"])
            for i, a in enumerate(alerts, 1):
                uuid = a["uuid"]
                status = a.get("status", "-")
                history_data = self.get_alert_history(uuid).get("data", [])
                has_history = "✅" if history_data else "❌"
                table.add_row([i, a["name"], a["lhs_tradingsymbol"], uuid, status, has_history])

            safe_print("\n📜 ===== Active Alerts =====")
            safe_print(table)
            safe_print("💡 Enter alert number to view history, or type 'X' to return to main menu.")

            choice = input("🔎 Your choice: ").strip()
            if choice.lower() == "x":
                break

            try:
                choice = int(choice) - 1
                if 0 <= choice < len(alerts):
                    uuid = alerts[choice]["uuid"]
                    history_data = self.get_alert_history(uuid).get("data", [])
                    if not history_data:
                        safe_print("⚠️ No history events found for this alert. It may have never triggered.\n")
                        continue

                    h_table = PrettyTable(["Triggered At", "Status", "Last Price", "Message"])
                    for event in history_data:
                        meta = event.get("meta", [{}])[0]
                        h_table.add_row([
                            meta.get("timestamp", "-"),
                            event.get("status", "-"),
                            meta.get("last_price", "-"),
                            event.get("condition", "-")
                        ])
                    safe_print("\n📖 Alert History:")
                    safe_print(h_table)
                else:
                    safe_print("❌ Invalid selection.")
            except ValueError:
                safe_print("⚠️ Invalid input.")


    # inside class KiteAlerts
    def menu(self):
        """Interactive CLI menu for managing alerts"""
        while True:
            safe_print("\n🚀 ===== Kite Alerts ===== 🚀\n")
            safe_print("1️⃣  📥  Bulk-create alerts from CSV")
            safe_print("2️⃣  📤  Export active alerts to CSV")
            safe_print("3️⃣  🧹  Delete alerts (cleanup)")
            safe_print("4️⃣  🔄  Reactivate disabled alerts")
            safe_print("5️⃣  📜  Show alert history")
            safe_print("6️⃣  🔙  Return to Main Menu\n")

            choice = input("👉 Enter your choice: ").strip()

            if choice == "1":
                self.bulk_create_alerts_from_csv()
            elif choice == "2":
                self.export_active_alerts_to_csv()
            elif choice == "3":
                self.cleanup_alerts()
            elif choice == "4":
                alerts = self.get_all_alerts().get("data", [])
                disabled = [a["uuid"] for a in alerts if a["status"] == "disabled"]
                if disabled:
                    self.reactivate_alert(disabled)
                else:
                    safe_print("ℹ️ No disabled alerts found.")
            elif choice == "5":
                self.show_alert_history()
            elif choice == "6":
                safe_print("↩️ Returning to Main Menu...")
                break  # ← Return to main program
            else:
                safe_print("❌ Invalid choice.")

