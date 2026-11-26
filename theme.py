"""theme.py - ShipSmart: same-day package delivery.
Turns the theme's data into the inputs that core.py expects."""
import json, os

THEME = "ShipSmart"
TITLE = "ShipSmart"
TAGLINE = "Same-day delivery planner for a local fulfillment center"
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "orders.json")

RECORD = "order"
ID_FIELD = "tracking"
LOOKUP_FIELD, LOOKUP_LABEL = "tracking", "Tracking number"
COLUMNS = ["tracking", "zone", "weight_kg", "express", "delivery_value", "deadline"]

SORT_LABEL = "Delivery deadline"
SEARCH_PROMPT = "Show orders due at or after (HH:MM)"
SEARCH_DEFAULT = "17:00"

HEAP_TITLE = "Packing queue: most urgent order first"
HEAP_RULE = "Priority = express orders first, then earlier deadline, then higher delivery value."

PLAN_TITLE = "Load one van"
CAPACITY_LABEL, CAPACITY_UNIT = "Express van weight limit", "kg"
CAPACITY_DEFAULT, CAPACITY_MIN, CAPACITY_MAX = 48, 20, 150
POOL_DEFAULT = 15
WEIGHT_LABEL, VALUE_LABEL = "Weight (kg)", "Delivery value"

ROOT_LABEL = "SoCal Fulfillment Center"
ROAD_LABEL = "van drive time (minutes)"
NETWORK_TITLE = "Hub-to-zone link network"
MST_TEXT = "Cheapest set of delivery links that still reaches every zone from the warehouse (cost in $)."
BREAK_TEXT = "A road closes. Which zones can no longer be reached on the network?"

TEXT_TITLE = "Delivery note scanner"
TEXT_HELP = "Scan customer delivery notes so drivers see gate codes and fragile items before they arrive."

TOUR_TITLE = "One van's delivery route"
TOUR_TEXT = "Start at the warehouse, visit every chosen zone, return. Finding the shortest order is the Traveling Salesman Problem (NP-hard)."


def load(path=DATA_FILE):
    with open(path) as f:
        data = json.load(f)
    names = {n["id"]: n["name"] for n in data["nodes"]}
    for r in data["records"]:
        r["zone"] = names[r["node"]]
    return data


def to_minutes(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def sort_value(rec):
    return to_minutes(rec["deadline"])


def priority(rec):
    return (0 if rec["express"] else 1, to_minutes(rec["deadline"]), -rec["delivery_value"])


def priority_reason(rec):
    return f"{'EXPRESS' if rec['express'] else 'standard'}, due {rec['deadline']}, value {rec['delivery_value']}"


def plan_items(records):
    return [{"id": r[ID_FIELD], "weight": r["weight_kg"], "value": r["delivery_value"]} for r in records]


def describe(rec):
    return (f"{rec['tracking']} to {rec['zone']}: {rec['weight_kg']} kg, "
            f"{'express' if rec['express'] else 'standard'}, due {rec['deadline']}, value {rec['delivery_value']}.")
