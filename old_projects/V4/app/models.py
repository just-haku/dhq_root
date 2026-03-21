# app/models.py
from bson.objectid import ObjectId
import math
import hashlib
import secrets
from pymongo import MongoClient

# Import the database and collections from our centralized db module.
from app.db import db

# Define collections using the database reference.
plots_collection = db['plots']
users_collection = db['users']
global_settings_collection = db['global_settings']

# Initialize your MongoDB connection (adjust connection string and database name as needed)
client = MongoClient("mongodb://localhost:27017/")
db = client["my_database"]  # Replace "chaosplots" with your database name

def update_user(user_id, update_data):
    """
    Update a user's document in the 'users' collection.
    
    Parameters:
      user_id (str or ObjectId): The ID of the user to update.
      update_data (dict): A dictionary of fields and values to update.
      
    Returns:
      int: The number of documents modified (should be 1 if successful).
    """
    # Ensure user_id is an ObjectId
    if not isinstance(user_id, ObjectId):
        try:
            user_id = ObjectId(user_id)
        except Exception as e:
            raise ValueError("Invalid user id format: " + str(e))
    
    result = db.users.update_one({"_id": user_id}, {"$set": update_data})
    return result.modified_count

# --- Plot CRUD Operations ---
def create_plot(plot_data):
    """Insert a new plot document and return its ID as a string."""
    result = plots_collection.insert_one(plot_data)
    return str(result.inserted_id)

def get_plot(plot_id):
    """Retrieve a plot document by its ID."""
    return plots_collection.find_one({"_id": ObjectId(plot_id)})

def update_plot(plot_id, update_data):
    """Update fields of a plot document."""
    plots_collection.update_one({"_id": ObjectId(plot_id)}, {"$set": update_data})

def update_gmail_credentials(user_id_str, gmail_address, app_password):
    # Convert the user_id from string to ObjectId
    user_id = ObjectId(user_id_str)
    update_data = {"gmail_address": gmail_address, "gmail_app_password": app_password}

    # Optional debug check
    test_doc = db.users.find_one({"_id": user_id})
    print("Testing find_one =>", test_doc)

    result = db.users.update_one(
        {"_id": user_id},
        {"$set": update_data}
    )
    print(f"update_gmail_credentials: matched_count={result.matched_count}, modified_count={result.modified_count}")
    return result.modified_count

def delete_plot(plot_id):
    """Delete a plot document and return the number of documents deleted."""
    result = plots_collection.delete_one({"_id": ObjectId(plot_id)})
    return result.deleted_count

def get_all_plots():
    """Return a list of all plot documents."""
    return list(plots_collection.find())

def get_plots_by_user(user_id):
    """Return all plots belonging to a specific user."""
    return list(plots_collection.find({"user_id": user_id}))

# --- User CRUD Operations ---
def create_user(user_data):
    """Insert a new user document and return its ID as a string."""
    result = users_collection.insert_one(user_data)
    return str(result.inserted_id)

def get_user_by_username(username):
    """Retrieve a user document by username."""
    return users_collection.find_one({"username": username})

def get_user_by_id(user_id):
    if not isinstance(user_id, ObjectId):
        try:
            user_id = ObjectId(user_id)
        except Exception as e:
            raise ValueError("Invalid user ID format: " + str(e))
    return db.users.find_one({"_id": user_id})

def get_all_users():
    """Return a list of all user documents."""
    return list(users_collection.find())

def delete_user_by_id(user_id):
    """Delete a user document by its ID."""
    users_collection.delete_one({"_id": ObjectId(user_id)})

# --- Global API Settings ---
def get_global_api_settings():
    """
    Retrieve global API settings from the database.
    If no document exists, return default settings.
    """
    doc = global_settings_collection.find_one({"_id": "global_api"})
    if not doc:
        return {
            "api_url": "",
            "api_key": "",
            "order_cmd": "add",
            "status_cmd": "status",
            "balance_cmd": "balance"
        }
    # Optionally, remove the internal _id key.
    doc.pop("_id", None)
    return doc

def update_global_api_settings(settings_data):
    """
    Update or insert the global API settings document.
    Always uses _id "global_api".
    """
    global_settings_collection.update_one(
        {"_id": "global_api"},
        {"$set": settings_data},
        upsert=True
    )

def get_global_collab_terms():
    # Assume there is a document with _id="collab_terms"
    doc = db.global_settings.find_one({"_id": "collab_terms"})
    if doc:
        return doc.get("terms", [])
    return []

def update_global_collab_terms(terms_list):
    # Upsert the document with _id="collab_terms"
    db.global_settings.update_one(
        {"_id": "collab_terms"},
        {"$set": {"terms": terms_list}},
        upsert=True
    )

class ChaosGenerator:
    """
    Generates chaotic progress data for x-values, a-values (increment per step),
    and y-values (cumulative sum). Uses an iterative approach for efficiency.
    
    Parameters:
      x_total (int): total number of steps (must be positive).
      y_total (float): the target total value.
      tol (float): tolerance ratio (e.g., 0.1 for ±10%).
      seed (str): optional seed string; if not provided, a random one is generated.
      a_tolerance (float): percentage (0-100) tolerance for fluctuations in a-values.
    
    Methods:
      get_data_arrays(): Returns three lists: x_vals, a_vals, and y_vals.
      get_values(x): Returns the a and y values at step x.
    """
    def __init__(self, x_total, y_total, tol=0.0, seed=None, a_tolerance=30):
        if x_total <= 0:
            raise ValueError("x_total must be a positive integer.")
        self.x_total = x_total
        self.y_total = y_total
        self.tol = tol
        self.y_min = y_total * (1 - tol)
        self.y_max = y_total * (1 + tol)
        self.base_rate = y_total / x_total
        self.seed = seed or secrets.token_hex(16)
        self.a_tolerance = a_tolerance / 100.0
        
        # Initialize lists for a-values and y-values.
        # We'll compute them iteratively.
        self._a_vals = [0.0] * (self.x_total + 1)
        self._y_vals = [0.0] * (self.x_total + 1)
        # Base case: at step 0, we assume y = 0
        self._y_vals[0] = 0.0
        self._a_vals[0] = 0.0

    def _quantum_chaos(self, x):
        """Generate a pseudo-random value based on the step and seed."""
        s = f"{x}-{self.seed}"
        h = hashlib.sha3_512(s.encode()).hexdigest()
        hash_int = int(h[:16], 16)
        frac = hash_int / (1 << 64)
        return math.sin(frac * 2 * math.pi)

    def _generate_a(self, x):
        """
        Compute the hourly addition (a) at step x.
        At the final step, adjust the value so that the total y
        approaches a target determined by tolerance.
        """
        if x == self.x_total:
            # At the final step, try to reach a target within [y_min, y_max].
            y_prev = self.get_y(x - 1)
            chaos = (self._quantum_chaos(x) + 1) / 2  # value in [0,1]
            target = self.y_min + chaos * (self.y_max - self.y_min)
            a_val = max(target - y_prev, 0.0)
            return a_val
        # Otherwise, generate a value based on chaos.
        chaos = self._quantum_chaos(x)
        a_val = self.base_rate * (1 + self.a_tolerance * chaos)
        return max(a_val, 0.01 * self.base_rate)

    def get_y(self, x):
        """
        Returns the cumulative total y at step x. If not computed, it will be
        computed iteratively from the previous steps.
        """
        if x < 0:
            return 0.0
        # Compute iteratively up to x if necessary.
        for i in range(1, x + 1):
            if self._a_vals[i] == 0.0:  # not computed yet (assuming a_val should be > 0)
                self._a_vals[i] = self._generate_a(i)
            self._y_vals[i] = self._y_vals[i - 1] + self._a_vals[i]
        return self._y_vals[x]

    def get_values(self, x):
        """Returns a tuple (a, y) for a given step x."""
        a_val = self._generate_a(x)
        y_val = self.get_y(x)
        return a_val, y_val

    def get_data_arrays(self):
        """
        Computes and returns three lists: x_vals (0..x_total),
        a_vals, and y_vals.
        """
        for i in range(1, self.x_total + 1):
            if self._a_vals[i] == 0.0:
                self._a_vals[i] = self._generate_a(i)
            self._y_vals[i] = self._y_vals[i - 1] + self._a_vals[i]
        x_vals = list(range(self.x_total + 1))
        return x_vals, self._a_vals, self._y_vals

def update_user(user_id, update_data):
    # Ensure user_id is converted to ObjectId if needed
    if not isinstance(user_id, ObjectId):
        try:
            user_id = ObjectId(user_id)
        except Exception as e:
            raise ValueError("Invalid user ID format: " + str(e))
    result = db.users.update_one({"_id": user_id}, {"$set": update_data})
    return result.modified_count

def find_message_by_id(mail_history, mail_id):
    """
    Search through mail_history (a list of thread objects) for a message
    with the given mail_id. Return that message dict if found, else None.
    """
    for thread in mail_history:
        if "messages" in thread:
            # multi-message structure
            for msg in thread["messages"]:
                if msg.get("mail_id") == mail_id:
                    return msg
        else:
            # single-message structure (if you still have older data)
            if thread.get("mail_id") == mail_id:
                return thread
    return None
