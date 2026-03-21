import imaplib
import email
from email.header import decode_header
from app.models import get_all_users, update_user, get_global_collab_terms

def decode_subject(subject):
    """Decode a possibly encoded email subject."""
    if not subject:
        return ""
    dh = decode_header(subject)
    subject_parts = []
    for s, enc in dh:
        if isinstance(s, bytes):
            enc = enc or "utf-8"
            try:
                subject_parts.append(s.decode(enc, errors="ignore"))
            except Exception as e:
                subject_parts.append(s.decode("utf-8", errors="ignore"))
        else:
            subject_parts.append(s)
    return " ".join(subject_parts)

def build_email_body(msg):
    """Extract the text/plain part of the email body."""
    if not msg.is_multipart():
        try:
            return msg.get_payload(decode=True).decode(errors="ignore")
        except Exception as e:
            return msg.get_payload()
    else:
        body = ""
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body += part.get_payload(decode=True).decode(errors="ignore")
                except Exception as e:
                    pass
        return body

def fetch_collab_emails_for_all_users():
    """
    1. For each user, fetch all UNSEEN emails with UID greater than last_scanned_uid.
    2. Filter emails locally for global collaboration keywords (in subject or body, case-insensitive).
    3. Group emails by sender; if the same sender sends another email, append it to the thread.
    4. Update the user document with the new highest UID and the updated mail history.
    """
    global_terms = get_global_collab_terms() or []
    print("Global collaboration keywords:", global_terms)

    # Folders to search. Adjust or add "[Gmail]/Spam" as desired.
    folders = ["INBOX", "[Gmail]/Spam"]
    users = get_all_users()

    for user in users:
        gmail_address = user.get("gmail_address")
        app_password = user.get("gmail_app_password")
        user_id = user.get("_id")
        last_uid = user.get("last_scanned_uid", 0)
        print(f"User {user_id}: last_scanned_uid = {last_uid}")

        if not gmail_address or not app_password:
            print(f"Skipping user {user_id}: No Gmail credentials found.")
            continue

        new_emails = []
        highest_uid = last_uid

        try:
            print(f"Connecting to Gmail for user {user_id} with {gmail_address}")
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(gmail_address, app_password)
            
            # List available folders for debugging (inside try block, after login)
            status, mailboxes = mail.list()
            if status == "OK":
                print("Available folders:")
                for m in mailboxes:
                    print(m.decode())
            else:
                print("Could not list folders for user", user_id)
            
            for folder in folders:
                print(f"Selecting folder: {folder} for user {user_id}")
                try:
                    status, _ = mail.select(folder)
                    if status != 'OK':
                        print(f"Could not select folder {folder} for user {user_id}")
                        continue
                except imaplib.IMAP4.error as e:
                    print(f"IMAP error selecting folder {folder} for user {user_id}: {e}")
                    continue

                # Use UID search to fetch only emails with UID greater than last_uid
                search_command = f"(UID {last_uid + 1}:*)"
                print(f"Searching with UID command: {search_command} in folder {folder}")
                typ, data = mail.uid('SEARCH', None, search_command)
                if typ != 'OK':
                    print(f"UID search failed in folder {folder} for user {user_id}")
                    continue

                uids = data[0].split()
                print(f"Found {len(uids)} new emails (UID > {last_uid}) in {folder} for user {user_id}")
                for uid in uids:
                    try:
                        uid_int = int(uid)
                    except Exception:
                        continue
                    if uid_int > highest_uid:
                        highest_uid = uid_int

                    typ, msg_data = mail.uid('FETCH', uid, '(RFC822)')
                    if typ != "OK":
                        print(f"Fetch failed for UID {uid.decode()} for user {user_id}")
                        continue
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # Use Message-ID if available; otherwise, fallback to UID
                    message_id = msg.get("Message-ID") or uid.decode()
                    subject = decode_subject(msg.get("Subject", ""))
                    body = build_email_body(msg)

                    # Check for keyword presence in subject or body (case-insensitive)
                    subject_lower = subject.lower()
                    body_lower = body.lower()
                    if any(term.lower() in subject_lower or term.lower() in body_lower for term in global_terms):
                        from_addr = msg.get("From", "")
                        date = msg.get("Date", "")
                        new_thread = {
                            "from_addr": from_addr,
                            "messages": [
                                {
                                    "mail_id": message_id,
                                    "subject": subject,
                                    "snippet": body[:300],
                                    "date": date,
                                    "chat_history": []
                                }
                            ]
                        }
                        new_emails.append(new_thread)
            # End folder loop

            # Merge new_emails with existing mail history
            current_history = user.get("mail_history", [])
            existing_ids = set()
            for entry in current_history:
                if "messages" in entry:
                    for m in entry["messages"]:
                        existing_ids.add(m.get("mail_id"))
                else:
                    existing_ids.add(entry.get("mail_id"))

            added = 0
            for email_item in new_emails:
                # Skip if the message ID is already present
                if email_item["messages"][0]["mail_id"] in existing_ids:
                    continue

                # Group emails by sender (from_addr)
                existing_thread = next((th for th in current_history if th.get("from_addr") == email_item["from_addr"]), None)
                if existing_thread:
                    if "messages" in existing_thread:
                        existing_thread["messages"].append(email_item["messages"][0])
                    else:
                        old_item = {
                            "mail_id": existing_thread.get("mail_id"),
                            "subject": existing_thread.get("subject"),
                            "date": existing_thread.get("date"),
                            "snippet": existing_thread.get("snippet")
                        }
                        existing_thread["messages"] = [old_item, email_item["messages"][0]]
                        for key in ["mail_id", "subject", "date", "snippet"]:
                            existing_thread.pop(key, None)
                else:
                    current_history.append(email_item)
                added += 1

            # Update the last_scanned_uid in the user document (only if new highest UID found)
            if highest_uid > last_uid:
                update_user(user_id, {"last_scanned_uid": highest_uid})
            update_user(user_id, {"mail_history": current_history})
            print(f"User {user_id}: Fetched and stored {added} new collaboration emails. Highest UID scanned: {highest_uid}")

        except Exception as e:
            print(f"Error fetching emails for user {user_id}: {str(e)}")
