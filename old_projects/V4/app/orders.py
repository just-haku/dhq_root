#!/usr/bin/env python3
"""
integrated_orders_optionB.py

This module processes orders by checking the orders dictionary for the order toggle,
rather than looking at the timeline's "order" flag.
It:
  - Loops over each plot document.
  - For each timeline step, it checks the orders dict to see if the user toggled the order.
  - If toggled and the scheduled time has passed, it sends the order via the API.
  - Saves the API response for debugging.
  - Updates the order statuses for nonfinal orders.
"""

import os
import json
import logging
import requests
import time
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from app.models import get_global_api_settings  # Should return a dict with keys like "api_url", "api_key", "order_cmd", "status_cmd"
import threading

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# --- MongoDB Setup ---
client = MongoClient('mongodb://localhost:27017/')
db = client['my_database']  # Adjust as needed.
plots_collection = db['plots']

# Optional threading lock (if needed for concurrent updates)
order_lock = threading.Lock()

# Directory for saving API responses (for debugging)
RESPONSES_DIR = "api_responses"

def store_api_response(plot_id, step_index, response_data, suffix=""):
    """
    Save the API response to a JSON file.
    Filename format: "api_responses/<plot_id>_step<step_index><suffix>.json"
    """
    if not os.path.exists(RESPONSES_DIR):
        os.makedirs(RESPONSES_DIR)
    filename = os.path.join(RESPONSES_DIR, f"{plot_id}_step{step_index}{suffix}.json")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(response_data, f, indent=2)
        logging.info(f"[store_api_response] Saved server response to {filename}")
    except Exception as e:
        logging.error(f"[store_api_response] Error saving server response: {e}")

def update_order_statuses(plot_id, plot):
    """
    For each order in the plot document that has an order_id and is not in a final state,
    call the API (action=status) using the global API settings to get the latest status,
    then update the plot document.
    Final states: "Completed", "Partial", "Canceled".
    """
    global_api = get_global_api_settings()
    api_url = global_api.get("api_url", "")
    api_key = global_api.get("api_key", "")
    status_cmd = global_api.get("status_cmd", "status")
    if not (api_url and api_key):
        logging.info(f"[{plot_id}] Missing global API settings for status checks, skipping.")
        return

    orders = plot.get("orders", {})
    final_states = ["Completed", "Partial", "Canceled"]
    changed = False
    for step_key, info in orders.items():
        order_id = info.get("order_id")
        # Proceed only if we have an order_id and the current status is not final.
        if order_id and info.get("status", "pending").lower() not in [s.lower() for s in final_states]:
            payload = {
                "key": api_key,
                "action": status_cmd,
                "order": order_id
            }
            logging.info(f"[{plot_id}] Checking status for order_id {order_id} (step {step_key}).")
            try:
                resp = requests.post(api_url, data=payload, timeout=30)
                if resp.status_code == 200:
                    rjson = resp.json()
                    store_api_response(plot_id, step_key, rjson, suffix="_status")
                    new_status = rjson.get("status", "Unknown")
                    info["status"] = new_status
                    changed = True
                    logging.info(f"[{plot_id}] Step {step_key} updated status to {new_status}.")
                else:
                    logging.warning(f"[{plot_id}] HTTP {resp.status_code} during status check for order_id {order_id}.")
            except Exception as e:
                logging.error(f"[{plot_id}] Exception during status check for order_id {order_id}: {e}")
    if changed:
        plots_collection.update_one({"_id": ObjectId(plot_id)}, {"$set": {"orders": orders}})

def check_and_send_orders():
    """
    Process orders for each plot document:
      - Use plot.order_settings (must include "service_id" and "link").
      - Use global API settings (including "order_cmd" and "status_cmd").
      - For each timeline step:
           * Instead of checking timeline["order"], check the orders dictionary for the "order" toggle.
           * If the toggle is set, the order status is "pending" and not attempted, and the scheduled time has passed,
             then send the order.
           * Save the API response and update the order info accordingly.
           * Wait 30 seconds between orders.
      - Finally, update statuses for orders that are not in a final state.
    """
    logging.info("[check_and_send_orders] Starting order check...")
    for plot in plots_collection.find():
        plot_id = str(plot["_id"])
        settings = plot.get("order_settings", {})
        if not (settings.get("service_id") and settings.get("link")):
            logging.info(f"[{plot_id}] Skipping: incomplete plot order settings (service_id or link missing).")
            continue

        global_api = get_global_api_settings()
        api_url = global_api.get("api_url")
        api_key = global_api.get("api_key")
        order_cmd = global_api.get("order_cmd", "add")
        if not (api_url and api_key):
            logging.info(f"[{plot_id}] Skipping: incomplete global API settings.")
            continue

        timeline = plot.get("timeline", [])
        orders = plot.get("orders", {})

        processed_steps = set()

        for step in timeline:
            try:
                step_num = int(step.get("step"))
            except (ValueError, TypeError):
                logging.error(f"[{plot_id}] Invalid step value: {step.get('step')}")
                continue

            if step_num in processed_steps:
                logging.info(f"[{plot_id}] Step {step_num} already processed; skipping duplicate entry.")
                continue
            processed_steps.add(step_num)
            step_key = str(step_num)

            # Option B: Check the orders dictionary for the toggle.
            order_info = orders.get(step_key, {})
            if not order_info.get("order", False):
                logging.info(f"[{plot_id}] Step {step_num} => order not toggled in orders dict, skipping.")
                continue

            # Skip if this timeline step is already marked done.
            if step.get("done"):
                logging.info(f"[{plot_id}] Step {step_num} is done => skipping.")
                continue

            # Only proceed if the status is pending and not attempted.
            if order_info.get("status", "pending").lower() != "pending" or order_info.get("attempted", False):
                logging.info(f"[{plot_id}] Step {step_num} already attempted or not pending, skipping.")
                continue

            dt_str = step.get("datetime", "")
            try:
                dt_val = datetime.fromisoformat(dt_str)
            except ValueError:
                logging.error(f"[{plot_id}] Step {step_num}: invalid datetime '{dt_str}'.")
                continue

            now = datetime.now()
            if now >= dt_val:
                quantity = int(round(step.get("a", 0)))
                payload = {
                    "key": api_key,
                    "action": order_cmd,
                    "service": settings["service_id"],
                    "link": settings["link"],
                    "quantity": quantity
                }
                logging.info(f"[{plot_id}] Sending order for step {step_num}, qty={quantity}. (Scheduled: {dt_val}, Now: {now})")
                time.sleep(30)
                orders.setdefault(step_key, {})["attempted"] = True
                plots_collection.update_one({"_id": ObjectId(plot_id)}, {"$set": {"orders": orders}})

                try:
                    resp = requests.post(api_url, data=payload, timeout=30)
                    if resp.status_code == 200:
                        rjson = resp.json()
                        store_api_response(plot_id, step_num, rjson, suffix="_add")

                        if rjson.get("error") == "Duplicate order":
                            orders[step_key] = {
                                "order": True,
                                "status": "duplicate",
                                "api_response": rjson,
                                "attempted": True
                            }
                            logging.warning(f"[{plot_id}] Step {step_num} duplicate order encountered: {rjson}")
                        elif (str(rjson.get("status", "")).lower() in ["complete", "success"] or 
                              (rjson.get("order") and str(rjson.get("order")).strip())):
                            step["order_now"] = True
                            step["done"] = True
                            order_id = rjson.get("order") or rjson.get("order_id")
                            orders[step_key] = {
                                "order": True,
                                "status": "sent",
                                "order_id": order_id,
                                "api_response": rjson,
                                "attempted": True
                            }
                            logging.info(f"[{plot_id}] Step {step_num} => Order success, order_id: {order_id}")
                        else:
                            orders[step_key] = {
                                "order": True,
                                "status": "failed",
                                "api_response": rjson,
                                "attempted": True
                            }
                            logging.warning(f"[{plot_id}] Order failed for step {step_num}: {rjson}")
                    else:
                        orders[step_key] = {
                            "order": True,
                            "status": "failed",
                            "api_response": f"HTTP {resp.status_code}: {resp.text}",
                            "attempted": True
                        }
                        logging.warning(f"[{plot_id}] HTTP error {resp.status_code} for step {step_num}.")
                except Exception as e:
                    orders[step_key] = {
                        "order": True,
                        "status": "failed",
                        "api_response": str(e),
                        "attempted": True
                    }
                    logging.error(f"[{plot_id}] Exception for step {step_num}: {e}")

                plots_collection.update_one(
                    {"_id": ObjectId(plot_id)},
                    {"$set": {"orders": orders, "timeline": timeline}}
                )
                logging.info(f"[{plot_id}] Order for step {step_num} sent. Waiting 30 seconds before next order...")
                
        update_order_statuses(plot_id, plot)

    logging.info("[check_and_send_orders] Order check completed.")

def continuous_order_check():
    while True:
        check_and_send_orders()
        time.sleep(300)  # 5 minutes interval

def main():
    check_and_send_orders()

if __name__ == "__main__":
    main()
