# app/cogs/user.py
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.models import get_plots_by_user, get_user_by_id, get_plot, create_plot, ChaosGenerator, update_plot, get_global_api_settings, update_user, update_gmail_credentials, find_message_by_id
from datetime import datetime, timedelta

user_bp = Blueprint("user", __name__, url_prefix="/user")

def user_login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        user_role = session.get("user_role")
        print(f"[DEBUG] user_login_required => user_id={user_id}, user_role={user_role}")

        if user_role != "user":
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


@user_bp.route("/index")
@user_login_required
def index():
    user_id = session.get("user_id")
    plots = get_plots_by_user(user_id)
    return render_template("user_index.html", plots=plots)

@user_bp.route("/plot/<plot_id>")
@user_login_required
def plot_view(plot_id):
    plot = get_plot(plot_id)
    if plot and plot.get("user_id") == session.get("user_id"):
        return render_template("user_plot.html", plot=plot, plot_data=plot)
    return "Plot not found or access denied", 404

@user_bp.route("/create_plot", methods=["GET", "POST"])
@user_login_required
def create_plot_route():
    if request.method == "POST":
        try:
            x_total = int(request.form.get("x_total"))
            y_total = float(request.form.get("y_total"))
            current_x = int(request.form.get("current_x"))
            tol_percent = float(request.form.get("tol", 0)) / 100.0
            a_tol = float(request.form.get("a_tol", 30))
            step_minutes = int(request.form.get("a_step_minutes", 60))
        except ValueError:
            return "Invalid numeric input", 400

        start_str = request.form.get("start_datetime", "").strip()
        seed = request.form.get("seed", "") or None

        # Use ChaosGenerator to compute the data arrays.
        gen = ChaosGenerator(x_total, y_total, tol_percent, seed, a_tol)
        plot_name = request.form.get("plot_name", "").strip() or gen.seed

        try:
            x_vals, a_vals, y_vals = gen.get_data_arrays()
        except Exception as e:
            return f"Error generating data arrays: {e}", 500

        # Build timeline similar to the operator's route.
        timeline = []
        start_dt = None
        if start_str:
            try:
                start_dt = datetime.fromisoformat(start_str)
            except ValueError:
                pass

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
            "timeline": timeline,
            "timestamp_overrides": {},
            "timestamp_done": {},
            "orders": {},
            "order_settings": {},
            "user_id": session.get("user_id")
        }
        new_plot_id = create_plot(plot_data)
        return redirect(url_for("user.plot_view", plot_id=new_plot_id))
    return render_template("user_create_plot.html")

@user_bp.route("/delete_plot/<plot_id>", methods=["POST"])
@user_login_required
def delete_plot(plot_id):
    from app.models import get_plot, delete_plot as model_delete_plot
    plot_data = get_plot(plot_id)
    if not plot_data or plot_data.get("user_id") != session.get("user_id"):
        return "Plot not found or access denied", 404

    model_delete_plot(plot_id)
    return redirect(url_for("user.index"))

@user_bp.route("/rename_plot/<plot_id>", methods=["POST"])
@user_login_required
def rename_plot(plot_id):
    new_name = request.form.get("plot_name", "").strip()
    if not new_name:
        return redirect(url_for("user.plot_view", plot_id=plot_id))
    
    plot = get_plot(plot_id)
    if not plot or plot.get("user_id") != session.get("user_id"):
        return "Plot not found or access denied", 404
    
    update_plot(plot_id, {"plot_name": new_name})
    return redirect(url_for("user.plot_view", plot_id=plot_id))

@user_bp.route("/send_order_now/<plot_id>", methods=["POST"])
@user_login_required
def send_order_now(plot_id):
    x = request.form.get("x")
    try:
        x = int(x)
    except (ValueError, TypeError):
        return {"error": "Invalid step"}, 400

    plot = get_plot(plot_id)
    if not plot or plot.get("user_id") != session.get("user_id"):
        return {"error": "Plot not found or access denied"}, 404

    timeline = plot.get("timeline", [])
    if x < 0 or x >= len(timeline):
        return {"error": "Step out of range"}, 400

    a_val = timeline[x].get("a", 0)
    quantity = int(round(a_val))
    settings = plot.get("order_settings", {})
    api_url = settings.get("api_url")
    api_key = settings.get("api_key")
    service_id = settings.get("service_id")
    order_link = settings.get("link")
    if not (api_url and api_key and service_id and order_link):
        return {"error": "Missing API settings"}, 400

    payload = {
        "key": api_key,
        "action": "add",
        "service": service_id,
        "link": order_link,
        "quantity": quantity
    }
    import requests
    try:
        resp = requests.post(api_url, data=payload, timeout=30)
        if resp.status_code == 200:
            rjson = resp.json()
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

@user_bp.route("/toggle_timestamp_done/<plot_id>", methods=["POST"])
@user_login_required
def toggle_timestamp_done(plot_id):
    from flask import request
    plot = get_plot(plot_id)
    if not plot:
        return "Plot not found", 404

    # Retrieve step and new 'done' value from the form data.
    x = request.form.get("x")
    done_str = request.form.get("done", "false").lower()
    try:
        step_index = int(x)
    except (ValueError, TypeError):
        return "Invalid step", 400

    done_flag = (done_str == "true")

    # Update the timeline's done flag.
    timeline = plot.get("timeline", [])
    if step_index < 0 or step_index >= len(timeline):
        return "Step out of range", 400

    timeline[step_index]["done"] = done_flag
    update_plot(plot_id, {"timeline": timeline})
    return "OK", 200

@user_bp.route("/update_timestamp_override/<plot_id>", methods=["POST"])
@user_login_required
def update_timestamp_override(plot_id):
    x = request.form.get("x")
    new_timestamp = request.form.get("timestamp", "").strip()
    if new_timestamp == "":
        return "No timestamp provided", 400

    plot = get_plot(plot_id)
    if not plot:
        return "Plot not found", 404

    timestamp_overrides = plot.get("timestamp_overrides", {})
    timestamp_overrides[str(x)] = new_timestamp
    update_plot(plot_id, {"timestamp_overrides": timestamp_overrides})

    return "OK", 200

@user_bp.route("/toggle_order/<plot_id>", methods=["POST"])
@user_login_required
def toggle_order(plot_id):
    x = request.form.get("x")
    order_str = request.form.get("order", "false").lower()
    order = (order_str == "true")
    
    plot = get_plot(plot_id)
    if not plot:
        return "Plot not found", 404

    orders = plot.get("orders", {})
    orders.setdefault(str(x), {})
    orders[str(x)]["order"] = order
    orders[str(x)]["status"] = "pending" if order else "none"
    
    update_plot(plot_id, {"orders": orders})
    return "OK", 200

@user_bp.route("/toggle_all_orders/<plot_id>", methods=["POST"])
@user_login_required
def toggle_all_orders(plot_id):
    """
    Toggles the 'order' flag for ALL steps in the timeline,
    ensuring each step in the timeline has an entry in plot["orders"].
    Sets 'status' to 'pending' if toggled on, or 'none' if toggled off.
    """
    # 1) Get the new toggle state from the POST form data.
    order_str = request.form.get("order", "false").lower()
    order_flag = (order_str == "true")

    # 2) Retrieve the plot from the database.
    plot = get_plot(plot_id)
    if not plot:
        return "Plot not found", 404

    # 3) Get or initialize the 'orders' dictionary and the timeline.
    orders = plot.get("orders", {})
    timeline = plot.get("timeline", [])

    changed_count = 0

    # 4) Loop over each step in the timeline and update order flags.
    for step in timeline:
        step_key = str(step.get("step"))
        if step_key not in orders:
            orders[step_key] = {}
        if orders[step_key].get("order") != order_flag:
            orders[step_key]["order"] = order_flag
            orders[step_key]["status"] = "pending" if order_flag else "none"
            changed_count += 1

    # 5) Persist the updated orders back to the database.
    update_plot(plot_id, {"orders": orders})
    return f"Toggle complete. Updated {changed_count} steps.", 200

@user_bp.route("/save_order_settings/<plot_id>", methods=["POST"])
@user_login_required
def save_order_settings(plot_id):
    # Retrieve the plot and verify ownership.
    plot = get_plot(plot_id)
    if not plot or plot.get("user_id") != session.get("user_id"):
        return "Plot not found or access denied", 404

    # Get the global API credentials (read-only for the user)
    api_creds = get_global_api_settings()
    api_url = api_creds.get("api_url")
    api_key = api_creds.get("api_key")

    # Get plot-specific settings from the form submission.
    service_id = request.form.get("service_id", "").strip()
    link = request.form.get("link", "").strip()

    # Update the plot's order settings.
    order_settings = plot.get("order_settings", {})
    order_settings.update({
        "api_url": api_url,
        "api_key": api_key,
        "service_id": service_id,
        "link": link
    })
    update_plot(plot_id, {"order_settings": order_settings})
    return "Order settings saved", 200

@user_bp.route("/link_api/<plot_id>", methods=["POST"])
@user_login_required
def link_api(plot_id):
    plot = get_plot(plot_id)
    if not plot or plot.get("user_id") != session.get("user_id"):
        return {"status": "failed", "message": "Plot not found or access denied"}, 404

    from app.models import get_global_api_settings
    settings = get_global_api_settings()
    if not (settings.get("api_url") and settings.get("api_key")):
        settings = plot.get("order_settings", {})

    api_url = settings.get("api_url")
    api_key = settings.get("api_key")
    if not (api_url and api_key):
        return {"status": "failed", "message": "Missing API settings"}, 400

    balance_cmd = settings.get("balance_cmd", "balance")
    payload = {
        "key": api_key,
        "action": balance_cmd
    }

    import requests
    try:
        resp = requests.post(api_url, data=payload, timeout=30)
        if resp.status_code == 200:
            rjson = resp.json()
            balance = rjson.get("balance", "")
            currency = rjson.get("currency", "").upper()

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

# app/cogs/user.py
@user_bp.route("/link_gmail", methods=["GET", "POST"])
@user_login_required
def link_gmail():
    from flask import flash, redirect, url_for, request, render_template, session
    from app.models import update_gmail_credentials
    if request.method == "POST":
        gmail_address = request.form.get("gmail_address")
        app_password = request.form.get("app_password")
        if not gmail_address or not app_password:
            flash("Gmail address and App Password are required", "danger")
            return redirect(url_for("user.link_gmail"))

        user_id_str = session.get("user_id")  # This is a string like "67c2d5b3a248acae1f928940"
        print(f"Updating credentials for user {user_id_str} with {gmail_address}")

        modified = update_gmail_credentials(user_id_str, gmail_address, app_password)
        if modified:
            flash("Gmail account linked successfully", "success")
        else:
            flash("No user document was updated; verify the user ID matches the database record.", "danger")

        return redirect(url_for("user.mail_history"))
    return render_template("user_link_gmail.html")


@user_bp.route("/collab_mail_settings", methods=["GET", "POST"])
@user_login_required
def collab_mail_settings():
    from flask import flash, redirect, url_for, request, render_template, session
    from app.models import get_user_by_id, update_user

    user_id = session.get("user_id")
    user_data = get_user_by_id(user_id)
    # Get existing collaboration settings or empty dict if none exist.
    collab_settings = user_data.get("collab_mail_settings", {})

    if request.method == "POST":
        # Get list of platforms checked in the form.
        selected_platforms = request.form.getlist("platform")
        updated_prices = {}

        # For each selected platform, store its price (even if blank).
        for platform in selected_platforms:
            price_key = f"price_{platform}"
            price_val = request.form.get(price_key, "").strip()
            updated_prices[platform] = price_val

        # If both TikTok and Instagram are selected, store the cross-posting price.
        if "TikTok" in selected_platforms and "Instagram" in selected_platforms:
            cross_price = request.form.get("cross_post_price", "").strip()
            updated_prices["cross_post"] = cross_price

        # 5) Preserve any previously stored platform if the user didn’t uncheck it
        #    (Optional logic if you want to keep old data for unselected platforms.)
        #    Typically, you might remove unselected platforms, so if user unchecks them,
        #    they’re gone. But if you want to keep them, you'd merge them here.
        #    For example:
        for platform, old_price in collab_settings.items():
            if platform not in updated_prices:
                updated_prices[platform] = old_price


        # Process extra fields (any key starting with "extra_")
        extra_fields_dict = {}
        for key, value in request.form.items():
            if key.startswith("extra_"):
                field_name = key[len("extra_"):]
                extra_fields_dict[field_name] = value.strip()
        if extra_fields_dict:
            updated_prices["extra_fields"] = extra_fields_dict

        # Update the user's collaboration settings in the database.
        update_user(user_id, {"collab_mail_settings": updated_prices})
        flash("Collaboration Mail Settings saved", "success")
        return redirect(url_for("user.collab_mail_settings"))

    return render_template("user_collab_mail_settings.html", settings=collab_settings)


@user_bp.route("/mail_history")
@user_login_required
def mail_history():
    from flask import flash, redirect, url_for, render_template, session
    from app.models import get_user_by_id
    user_id = session.get("user_id")
    user_data = get_user_by_id(user_id)
    if not user_data:
        flash("User not found", "danger")
        return redirect(url_for("auth.login"))
    mails = user_data.get("mail_history", [])
    return render_template("user_mail_history.html", mails=mails, mail=(mails[0] if mails else None))


@user_bp.route("/collab_chat/<mail_id>", methods=["GET", "POST"])
@user_login_required
def collab_chat(mail_id):
    from flask import flash, redirect, url_for, render_template, request
    import g4f
    user_id = session.get("user_id")
    user_data = get_user_by_id(user_id)
    mail_history = user_data.get("mail_history", [])

    def find_message_by_id(mail_history, mail_id):
        for thread in mail_history:
            if "messages" in thread:
                for msg in thread["messages"]:
                    if msg.get("mail_id") == mail_id:
                        return msg
            else:
                if thread.get("mail_id") == mail_id:
                    return thread
        return None

    collab_message = find_message_by_id(mail_history, mail_id)
    if not collab_message:
        flash("Mail not found", "danger")
        return redirect(url_for("user.mail_history"))

    subject = collab_message.get("subject", "")
    snippet = collab_message.get("snippet", "")
    collab_settings = user_data.get("collab_mail_settings", {})
    rates_list = []
    for platform, price in collab_settings.items():
        rates_list.append(f"{platform}: ${price}")
    rates_str = ", ".join(rates_list)
    
    user_input = ""
    ai_reply = ""  # Initialize ai_reply to an empty string
    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()
        if user_input:
            prompt = f"""Draft a response for the following collaboration email:

Subject: {subject}
Snippet: {snippet}

My Collaboration Settings: {rates_str}

User Command: {user_input}

Please generate a draft response that reflects these details.
"""
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # or another model supported by your g4f setup
                    messages=[{"role": "user", "content": prompt}],
                    web_search=False
                )
                # If response is a string, use it directly; otherwise, extract from response.choices.
                if isinstance(response, str):
                    draft_response = response
                else:
                    draft_response = response.choices[0].message.content
            except Exception as e:
                draft_response = f"Error generating response: {str(e)}"

            if "chat_history" not in collab_message:
                collab_message["chat_history"] = []
            collab_message["chat_history"].append({"role": "user", "content": user_input})
            collab_message["chat_history"].append({"role": "ai", "content": ai_reply})

            update_user(user_id, {"mail_history": mail_history})
            flash("Draft response generated.", "success")
    
    return render_template("user_mail_chat.html", mail=collab_message, mails=mail_history, user_input=user_input)
