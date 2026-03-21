Luckfox Pico Ultra: User & Operational Manual

Companion to README.md

This document details the operational logic, user workflows, and specific feature behaviors of the Luckfox Server.

1. Access & Authentication

The Covert Interface

Standard View: The device boots into a full-screen Digital Clock. This is the "Covert" mode.

Admin Access: You must manually navigate to /secret-kuro-grp in the browser URL bar.

Login Logic:

Session: Uses Flask-Login with secure cookies.

Banned Users: If a user has is_banned=True in the database, they will see a red "ACCOUNT SUSPENDED" message upon login attempt.

Operator: The username kuro is hardcoded to bypass ban checks.

2. Collaboration & Order Management (Deep Dive)

This is the core function of the device. It allows you to schedule "natural" looking social media growth.

A. Creating a Collaboration

Navigate to Place Order. You will see the following parameters:

Field

Description

Technical Logic

Collaboration Name

A human-readable tag (e.g., "Client A - Instagram").

Stored in Collaboration.name.

Target Link

The URL to boost.

Sent as link to the API.

Service ID

The numeric/string ID of the service provider.

Sent as service to the API.

Total Quantity (a)

The final goal amount.

The algorithm ensures the sum of all steps equals this number.

Duration (Days)

How long the campaign runs.

Used to calculate Total Hours.

Step (Hours)

How often an order is placed.

Determines the number of database rows generated.

Tolerance (%)

Randomness factor.

+ or - percentage deviation from the average required quantity.

B. The "Crooked Growth" Preview

Before saving, clicking "Preview Graph" runs app/utils.py:calculate_crooked_growth.

Chart 1 (Bar): Shows the quantity per step. You should see "crooked" bars (not a flat line) due to the tolerance factor.

Chart 2 (Line): Shows the accumulated total over time. This should look like a natural growth curve.

C. Execution & Management

Navigate to Manage Orders.

1. Status Indicators:

Auto (Green Sync Icon): The Cron job is actively monitoring this collaboration.

Manual (Yellow Hand Icon): Automation is paused. This happens if:

An API error occurred (Auto-pause safety).

The collaboration is finished.

2. The Detail View & "NOW!!!" Button:
Clicking "Orders" opens a modal with every single scheduled step.

Checkboxes: Allow you to select specific Pending rows.

"EXECUTE SELECTED" Button:

Bypasses the scheduled_time.

Bypasses the Cron job.

Immediately sends a POST request to the API.

Use Case: Fixing a "stuck" order or rushing a campaign.

3. Media Gallery & Privacy System

A. Upload Architecture

Widget: The upload button opens a modal. Upon selection, a minimized progress bar appears in the bottom left.

Storage: Files are written to /home/haku/usb/videos or /images.

Naming: We use secure_filename but preserve the original extension.

B. Visibility Logic

The system uses a 3-tier privacy check in app/blueprints/media.py:

Public: is_public = True. Visible to any logged-in user.

Private: Visible only to the Uploader and Admins/Operators.

Shared (Allowed Users): A specific list of User IDs is stored in the allowed_users column (JSON).

Example: [2, 5, 9]

If current_user.id is in that list, they can view the file even if it is private.

C. Social Features

Reactions: Toggling a reaction (Heart, Like) updates the MediaReaction table. It is an AJAX call that instantly updates the count UI without reloading.

Comments: Stored in MediaComment. rendered using textContent to prevent XSS attacks (no HTML allowed in comments).

4. User & Permission Management

A. The Operator (kuro)

This is a special account class.

ID: usually 1.

Hardcoded Protections: The delete_user and permissions routes have explicit checks: if target.role == 'operator': return error.

Master Key: The Operator's API Key (settings page) is used by the cron_worker.py script to execute automated orders for all collaborations.

B. Admin Restrictions

Max Admins: The create_user route checks User.query.filter_by(role='admin').count(). If >= 5, creation is blocked. This prevents permission inflation.

C. Granular Permissions (The Matrix)

We do not just rely on "Roles". We use specific capability flags stored as JSON.

Inheritance: User.has_perm(key) checks:

Is user Operator? -> True.

Does User have specific perm set? -> Return value.

Does User belong to a Group? -> Check Group perm.

Is user Admin? -> True.

Available Flags:

user_create, user_ban, user_delete

media_view_all (See private files of others)

media_manage (Rename/Edit others' files)

group_create, group_manage

5. Task Management

Assignment: Admins can assign tasks to specific users via the "Task Manager".

Dashboard: Users see a filtered list: Task.query.filter_by(user_id=current_user.id).

Completion: Toggling a task sends a request to /dashboard/toggle_task/<id>. It strictly checks if t.user_id == current_user.id to prevent users from completing each other's tasks.