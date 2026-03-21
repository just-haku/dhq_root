# app/cogs/operator.py
from flask import Blueprint, render_template, session, redirect, url_for, request
from werkzeug.security import generate_password_hash
import requests
from app.models import (
    get_all_users,
    get_plots_by_user,
    create_user,
    get_plot,
    create_plot,
    ChaosGenerator,
    get_user_by_id,
    update_plot,
    delete_user_by_id,
    get_global_api_settings,
    update_global_api_settings,
    delete_plot as model_delete_plot
)

operator_bp = Blueprint("operator", __name__, url_prefix="/operator")

def operator_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_role") != "operator":
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

@operator_bp.route("/index")
@operator_required
def index():
    return render_template("operator_index.html")

@operator_bp.route("/plot/<plot_id>", methods=["GET"])
@operator_required
def view_user_plot(plot_id):
    # Fetch the plot document from the database.
    plot_data = get_plot(plot_id)
    if not plot_data:
        return "Plot not found", 404
    # Get the user that owns the plot.
    user_data = get_user_by_id(plot_data["user_id"])
    # Get all plots for this user (for dropdown/sidebar)
    plots = get_plots_by_user(user_data["_id"])
    # print("DEBUG: plot_data=", plot_data)
    return render_template("operator_view_plot.html", user=user_data, plot=plot_data, plots=plots)

@operator_bp.route("/dashboard")
@operator_required
def dashboard():
    users = get_all_users()
    return render_template("operator_dashboard.html", users=users)

@operator_bp.route("/user/<user_id>/plots")
@operator_required
def user_plots(user_id):
    user_data = get_user_by_id(user_id)
    plots = get_plots_by_user(user_id)
    return render_template("operator_user_plots.html", user=user_data, plots=plots)

@operator_bp.route("/delete_user/<user_id>", methods=["POST"])
@operator_required
def delete_user(user_id):
    delete_user_by_id(user_id)
    return redirect(url_for("operator.dashboard"))

@operator_bp.route("/create_user", methods=["GET", "POST"])
@operator_required
def create_user_route():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        hashed_password = generate_password_hash(password)
        user_data = {"username": username, "password": hashed_password}
        create_user(user_data)
        return redirect(url_for("operator.dashboard"))
    return render_template("operator_create_user.html")
    
@operator_bp.route("/user/<user_id>/create_plot", methods=["GET", "POST"])
@operator_required
def operator_create_plot(user_id):
    user_data = get_user_by_id(user_id)
    if request.method == "POST":
        try:
            x_total = int(request.form.get("x_total"))
            y_total = float(request.form.get("y_total"))
            current_x = int(request.form.get("current_x"))
            tol_percent = float(request.form.get("tol", 0)) / 100.0
            a_tol = float(request.form.get("a_tol", 30))
        except ValueError:
            return "Invalid numeric input", 400

        start_str = request.form.get("start_datetime", "").strip()
        seed = request.form.get("seed", "") or None
        step_minutes = int(request.form.get("a_step_minutes", 60))

        # Generate chaotic data
        gen = ChaosGenerator(x_total, y_total, tol_percent, seed, a_tol)
        plot_name = request.form.get("plot_name", "").strip() or gen.seed

        # 1) Compute the arrays
        x_vals, a_vals, y_vals = gen.get_data_arrays()

        # 2) Build the timeline list
        from datetime import datetime, timedelta
        timeline = []
        start_dt = None
        if start_str:
            try:
                start_dt = datetime.fromisoformat(start_str)
            except ValueError:
                pass  # or handle error

        for i in range(x_total + 1):
            dt_str = ""
            if start_dt:
                dt = start_dt + timedelta(minutes=i * step_minutes)
                dt_str = dt.isoformat()

            timeline.append({
                "step": i,
                "datetime": dt_str,
                "a": a_vals[i],
                "y": y_vals[i],
                "done": False,
                "order": False
            })

        # 3) Prepare the plot document
        plot_data = {
            "plot_name": plot_name,
            "x_total": x_total,
            "y_total": y_total,
            "tol": tol_percent,
            "a_tol": a_tol,
            "a_step_minutes": step_minutes,
            "seed": gen.seed,
            "current_x": current_x,
            "start_datetime": start_str,
            "timeline": timeline,            # <--- store timeline
            "timestamp_overrides": {},
            "timestamp_done": {},
            "orders": {},
            "order_settings": {},
            "user_id": user_id
        }
        new_plot_id = create_plot(plot_data)
        return redirect(url_for("operator.user_plots", user_id=user_id))

    return render_template("operator_create_plot.html", user=user_data)


@operator_bp.route("/rename_plot/<plot_id>", methods=["POST"])
@operator_required
def rename_plot(plot_id):
    new_name = request.form.get("plot_name", "").strip()
    if not new_name:
        return redirect(url_for("operator.view_user_plot", plot_id=plot_id))
    update_plot(plot_id, {"plot_name": new_name})
    return redirect(url_for("operator.view_user_plot", plot_id=plot_id))

@operator_bp.route("/api_settings", methods=["GET"])
@operator_required
def api_settings():
    global_settings = get_global_api_settings()
    return render_template("operator_api_settings.html", global_settings=global_settings)

@operator_bp.route("/save_global_api_settings", methods=["POST"])
@operator_required
def save_global_api_settings():
    api_url = request.form.get("api_url", "").strip()
    api_key = request.form.get("api_key", "").strip()
    order_cmd = request.form.get("order_cmd", "add").strip()
    status_cmd = request.form.get("status_cmd", "status").strip()
    balance_cmd = request.form.get("balance_cmd", "balance").strip()
    update_global_api_settings({
        "api_url": api_url,
        "api_key": api_key,
        "order_cmd": order_cmd,
        "status_cmd": status_cmd,
        "balance_cmd": balance_cmd
    })
    return "OK"

@operator_bp.route("/check_global_balance", methods=["POST"])
@operator_required
def check_global_balance():
    settings = get_global_api_settings()
    if not settings.get("api_url") or not settings.get("api_key"):
        return {"error": "No API URL or key set"}, 400
    payload = {
        "key": settings["api_key"],
        "action": settings.get("balance_cmd", "balance")
    }

    try:
        resp = requests.post(settings["api_url"], data=payload, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"error": f"HTTP {resp.status_code}", "message": resp.text}, 400
    except Exception as e:
        return {"error": str(e)}, 500

@operator_bp.route("/toggle_timestamp_done/<plot_id>", methods=["POST"])
@operator_required
def toggle_timestamp_done(plot_id):
    from flask import request
    plot = get_plot(plot_id)
    if not plot:
        return "Plot not found", 404

    # Retrieve step and new done value from form data
    x = request.form.get("x")
    done_str = request.form.get("done", "false").lower()
    try:
        step_index = int(x)
    except (ValueError, TypeError):
        return "Invalid step", 400
    done_flag = (done_str == "true")

    # Update the timeline's done flag
    timeline = plot.get("timeline", [])
    if step_index < 0 or step_index >= len(timeline):
        return "Step out of range", 400

    timeline[step_index]["done"] = done_flag

    update_plot(plot_id, {"timeline": timeline})
    return "OK", 200


@operator_bp.route("/update_timestamp_override/<plot_id>", methods=["POST"])
@operator_required
def update_timestamp_override(plot_id):
    # Retrieve the step (x) and the new timestamp from the form data.
    x = request.form.get("x")
    new_timestamp = request.form.get("timestamp", "").strip()
    if new_timestamp == "":
        return "No timestamp provided", 400

    # Retrieve the plot document
    plot = get_plot(plot_id)
    if not plot:
        return "Plot not found", 404

    # Update the timestamp override for this step.
    timestamp_overrides = plot.get("timestamp_overrides", {})
    timestamp_overrides[str(x)] = new_timestamp
    update_plot(plot_id, {"timestamp_overrides": timestamp_overrides})

    return "OK", 200

@operator_bp.route("/toggle_order/<plot_id>", methods=["POST"])
@operator_required
def toggle_order(plot_id):
    # Retrieve the step number (x) and the order flag from the request.
    x = request.form.get("x")
    order_str = request.form.get("order", "false").lower()
    order = (order_str == "true")
    
    # Fetch the plot document.
    plot = get_plot(plot_id)
    if not plot:
        return "Plot not found", 404

    # Retrieve the current orders dictionary (or initialize it).
    orders = plot.get("orders", {})
    # Ensure we have an entry for this step.
    orders.setdefault(str(x), {})
    # Update the order flag and, optionally, the status.
    orders[str(x)]["order"] = order
    orders[str(x)]["status"] = "pending" if order else "none"
    
    # Save the updated orders back to the database.
    update_plot(plot_id, {"orders": orders})
    
    return "OK", 200

@operator_bp.route("/toggle_all_orders/<plot_id>", methods=["POST"])
@operator_required
def toggle_all_orders(plot_id):
    """
    Toggles the 'order' flag for ALL steps in the timeline,
    ensuring each step_key in the timeline also has an entry in plot["orders"].
    Sets 'status' to 'pending' if toggled on, or 'none' if toggled off.
    """

    # 1) Get the new toggle state from the POST form
    order_str = request.form.get("order", "false").lower()
    order_flag = (order_str == "true")

    # 2) Retrieve the plot from the DB
    plot = get_plot(plot_id)
    if not plot:
        return "Plot not found", 404

    # 3) Get or initialize the 'orders' dictionary
    orders = plot.get("orders", {})
    timeline = plot.get("timeline", [])

    changed_count = 0

    # 4) Loop over every timeline step
    for step in timeline:
        step_key = str(step.get("step"))
        # If that step doesn't exist in orders, create an empty record
        if step_key not in orders:
            orders[step_key] = {}

        # Optionally skip steps that are "done":
        # if step.get("done"):
        #     continue

        # If the 'order' value is already correct, you can skip. Otherwise, update:
        if orders[step_key].get("order") != order_flag:
            orders[step_key]["order"] = order_flag
            orders[step_key]["status"] = "pending" if order_flag else "none"
            changed_count += 1

    # 5) Persist the updated 'orders' back to the database
    update_plot(plot_id, {"orders": orders})

    return f"Toggle complete. Updated {changed_count} steps.", 200



@operator_bp.route("/save_order_settings/<plot_id>", methods=["POST"])
@operator_required
def save_order_settings(plot_id):
    # Retrieve the plot
    plot = get_plot(plot_id)
    if not plot:
        return "Plot not found", 404
    api_creds = get_global_api_settings()
    # Get order settings from the form
    api_url = api_creds.get("api_url")
    api_key = api_creds.get("api_key")
    service_id = request.form.get("service_id", "").strip()
    link = request.form.get("link", "").strip()

    # Update the plot's order settings
    order_settings = plot.get("order_settings", {})
    order_settings.update({
        "api_url": api_url,
        "api_key": api_key,
        "service_id": service_id,
        "link": link
    })
    update_plot(plot_id, {"order_settings": order_settings})
    return "Order settings saved", 200

@operator_bp.route("/link_api/<plot_id>", methods=["POST"])
@operator_required
def link_api(plot_id):
    """
    Sends a 'balance' request to the external API to verify API linking.
    Returns JSON with:
      { "status": "linked", "message": "...", "balance": "...", "currency": "..." }
    or
      { "status": "failed", "message": "..." }
    """
    plot = get_plot(plot_id)
    if not plot:
        return {"status": "failed", "message": "Plot not found"}, 404

    # First try to get global API settings; fall back to plot settings if not found.
    settings = get_global_api_settings()
    if not (settings.get("api_url") and settings.get("api_key")):
        settings = plot.get("order_settings", {})

    api_url = settings.get("api_url")
    api_key = settings.get("api_key")
    if not (api_url and api_key):
        return {"status": "failed", "message": "Missing API settings"}, 400

    # Use the global balance command if available; default to "balance"
    balance_cmd = settings.get("balance_cmd", "balance")
    payload = {
        "key": api_key,
        "action": balance_cmd
    }

    try:
        resp = requests.post(api_url, data=payload, timeout=30)
        if resp.status_code == 200:
            rjson = resp.json()  # e.g. { "balance": "68.6868", "currency": "USD" }
            balance = rjson.get("balance", "")
            currency = rjson.get("currency", "").upper()

            # Optionally update the plot doc with new balance info.
            new_settings = plot.get("order_settings", {}).copy()
            new_settings["last_balance"] = balance
            new_settings["last_currency"] = currency
            update_plot(plot_id, {"order_settings": new_settings})

            return {
                "status": "linked",
                "message": f"API linked successfully. Balance: {balance} {currency}",
                "balance": balance,
                "currency": currency
            }, 200
        else:
            return {
                "status": "failed",
                "message": f"HTTP {resp.status_code}: {resp.text}"
            }, 400
    except Exception as e:
        return {"status": "failed", "message": str(e)}, 500


@operator_bp.route("/send_order_now/<plot_id>", methods=["POST"])
@operator_required
def send_order_now(plot_id):
    """
    Immediately sends an order for a specific timeline step.
    Expects a form field 'x' representing the step index.
    """
    # Get the step index from the form.
    x = request.form.get("x")
    try:
        x = int(x)
    except (ValueError, TypeError):
        return {"error": "Invalid step"}, 400

    plot = get_plot(plot_id)
    if not plot:
        return {"error": "Plot not found"}, 404

    timeline = plot.get("timeline", [])
    if x < 0 or x >= len(timeline):
        return {"error": "Step out of range"}, 400

    a_val = timeline[x].get("a", 0)
    quantity = int(round(a_val))

    # Retrieve global API settings.
    global_settings = get_global_api_settings()
    if not (global_settings.get("api_url") and global_settings.get("api_key")):
        return {"error": "Global API settings are missing"}, 400

    # Retrieve plot-specific settings for service ID and link.
    order_settings = plot.get("order_settings", {})
    service_id = order_settings.get("service_id")
    order_link = order_settings.get("link")
    if not (service_id and order_link):
        return {"error": "Missing plot order settings (service_id or link)"}, 400

    # Use global order command if available; default to "add"
    order_cmd = global_settings.get("order_cmd", "add")

    # Build the payload using global API key and URL, and plot-specific service/link.
    payload = {
        "key": global_settings["api_key"],
        "action": order_cmd,
        "service": service_id,
        "link": order_link,
        "quantity": quantity
    }

    try:
        # Send the order using the global API URL.
        resp = requests.post(global_settings["api_url"], data=payload, timeout=30)
        if resp.status_code == 200:
            rjson = resp.json()
            # Ensure there's an 'orders' field.
            if "orders" not in plot:
                plot["orders"] = {}
            plot["orders"][str(x)] = {
                "order": True,
                "status": "sent",
                "order_id": rjson.get("order") or rjson.get("order_id"),
                "api_response": rjson,
                "attempted": True
            }
            update_plot(plot_id, {"orders": plot["orders"]})
            return {
                "status": "sent",
                "order_id": rjson.get("order") or rjson.get("order_id"),
                "api_response": rjson
            }, 200
        else:
            return {
                "status": "failed",
                "api_response": f"HTTP {resp.status_code}: {resp.text}"
            }, 200
    except Exception as e:
        return {"error": str(e)}, 500



@operator_bp.route("/delete_plot/<plot_id>", methods=["POST"])
@operator_required
def delete_plot(plot_id):
    # Retrieve the plot to verify it exists.
    plot = get_plot(plot_id)
    if not plot:
        return "Plot not found", 404
    # Delete the plot using the model function.
    model_delete_plot(plot_id)
    # Redirect back to the user's plot list.
    return redirect(url_for("operator.user_plots", user_id=plot["user_id"]))

@operator_bp.route("/manage_orders", methods=["GET"])
@operator_required
def manage_orders():
    """
    Display a hierarchical view of all orders grouped by user, then by plot, sorted by step,
    optionally filtered by a status query parameter (?status=pending).
    """
    from app.models import get_all_plots, get_user_by_id
    # 1) Grab the filter from the query string
    status_filter = request.args.get("status", "").strip().lower()  # e.g. "pending", "canceled", "sent", etc.

    user_map = {}  # { user_name: { plot_name: [ {step, order_id, status, api_response, plot_db_id} ] } }
    plots = get_all_plots()

    for plot_doc in plots:
        user_id = plot_doc.get("user_id")
        if not user_id:
            continue
        user_doc = get_user_by_id(user_id)
        if not user_doc:
            continue

        user_name = user_doc.get("username", "Unknown")
        plot_name = plot_doc.get("plot_name", "Unnamed Plot")
        orders_dict = plot_doc.get("orders", {})

        # Build an array of order records for each step
        order_records = []
        for step_str, order_info in orders_dict.items():
            try:
                step = int(step_str)
            except ValueError:
                step = 0
            order_status = order_info.get("status", "none").lower()

            # 2) If we have a status_filter and it doesn't match, skip
            if status_filter and order_status != status_filter:
                continue

            order_records.append({
                "step": step,
                "order_id": order_info.get("order_id", ""),
                "status": order_status,  # store it in lowercase or original, your choice
                "api_response": order_info.get("api_response", {}),
                "plot_db_id": str(plot_doc["_id"])
            })

        # If no records remain for this plot after filtering, skip
        if not order_records:
            continue

        # Sort by step ascending
        order_records.sort(key=lambda r: r["step"])

        # Insert into user_map
        if user_name not in user_map:
            user_map[user_name] = {}
        if plot_name not in user_map[user_name]:
            user_map[user_name][plot_name] = []

        user_map[user_name][plot_name].extend(order_records)

    # Sort user names
    sorted_user_names = sorted(user_map.keys())

    return render_template(
        "operator_manage_orders.html",
        user_map=user_map,
        sorted_user_names=sorted_user_names,
        status_filter=status_filter  # pass the current filter to the template
    )


@operator_bp.route("/cancel_order/<plot_id>", methods=["POST"])
@operator_required
def cancel_order(plot_id):
    """
    Toggle an order's 'canceled' status for a specific step in a plot.
    Expects form data: step, cancel (true/false).
    """
    from flask import request
    from app.models import get_plot, update_plot

    step_str = request.form.get("step")
    cancel_str = request.form.get("cancel", "false").lower()

    # Convert step to an int if possible
    try:
        step = int(step_str)
    except (ValueError, TypeError):
        return {"error": "Invalid step"}, 400

    # Convert cancel to a boolean
    cancel_flag = (cancel_str == "true")

    plot = get_plot(plot_id)
    if not plot:
        return {"error": "Plot not found"}, 404

    orders = plot.get("orders", {})
    step_key = str(step)
    if step_key not in orders:
        # If no order info yet, create an entry
        orders[step_key] = {}

    # If cancel_flag is True, set status="canceled"
    # Otherwise revert to "none" or your desired default
    if cancel_flag:
        orders[step_key]["status"] = "canceled"
        orders[step_key]["order"] = False  # up to you if you want "order" = False
    else:
        # Revert to "none" or "pending" or however you want un-cancel to appear
        orders[step_key]["status"] = "none"

    update_plot(plot_id, {"orders": orders})
    return {"status": orders[step_key]["status"]}, 200

@operator_bp.route("/edit_collab_terms", methods=["GET", "POST"])
@operator_required
def edit_collab_terms():
    from flask import flash, request, redirect, url_for, render_template
    from app.models import get_global_collab_terms, update_global_collab_terms
    if request.method == "POST":
        # Expect a textarea with comma-separated keywords.
        terms_str = request.form.get("collab_terms", "")
        # Clean and split the terms.
        terms_list = [term.strip() for term in terms_str.split(",") if term.strip()]
        update_global_collab_terms(terms_list)
        flash("Collaboration terms updated successfully", "success")
        return redirect(url_for("operator.edit_collab_terms"))
    else:
        current_terms = get_global_collab_terms() or []
        terms_str = ", ".join(current_terms)
        return render_template("operator_edit_collab_terms.html", collab_terms=terms_str)
