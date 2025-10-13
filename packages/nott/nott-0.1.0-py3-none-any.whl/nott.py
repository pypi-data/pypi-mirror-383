"""
    Author: Umiko (https://github.com/umikoio)
    Project: Nott (https://github.com/umikoio/nott)
"""

import os, getpass, tempfile, shlex, uuid, datetime
import json, sqlite3, base64, hmac, hashlib, pathlib
from typing import Optional
import typer
from rich import box
from rich.table import Table
from rich.prompt import Confirm
from rich.console import Console

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

APP_DIR = os.path.expanduser("~/.nott")
CONFIG_PATH = os.path.join(APP_DIR, "nott_config.json")
DB_PATH = os.path.join(APP_DIR, "nott.sqlite")
SESSION_PATH = os.path.join(APP_DIR, "nott_session.key")

app = typer.Typer(add_completion=False)
console = Console()


def ensure_app_dir() -> None:
    """
    Ensure the directory exists. If not, create it
    """
    os.makedirs(APP_DIR, exist_ok=True)

    try:
        os.chmod(APP_DIR, 0o700)
    except Exception:
        pass


def save_session_file(path: str, data: bytes) -> None:
    """
    Save session data to a key file to remember and persist during actions
    """
    with open(path, "wb") as f:
        f.write(data)

    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


def derive_key(
    password: str,
    salt: bytes,
    n: int = 2**14,
    r: int = 8,
    p: int = 1,
    key_length: int = 32
) -> bytes:
    """
    The primary salting algorithm for building a robust KDF (Key Derivation Function)

    - password: The user's password input
    - salt: Random bytes (makes every derived key unique, this way even if the same password is used, it still works)
    - n: CPU/memory cost (higher means slower (default 16384))
    - r: Block size (default 8)
    - p: Parallelization parameter (default 1)
    - key_length: Desired key length in bytes (default 32 (256 bits for AES-256, etc.))
    """
    kdf = Scrypt(salt=salt, n=n, r=r, p=p, length=key_length)
    return kdf.derive(password.encode("utf-8"))


def hmac_verify_tag(key: bytes) -> bytes:
    """
    Hash-based auth code verification object using SHA-256
    """
    return hmac.new(key, b"nott-verify", hashlib.sha256).digest()


def nott_encrypt(key: bytes, plaintext: bytes, aad: bytes = b"") -> bytes:
    """
    Encrypt data using AES-GCM and shares the required data to later decrypt
    """
    aes_gcm_init = AESGCM(key)
    aes_r = os.urandom(12)
    aes_enc = aes_gcm_init.encrypt(aes_r, plaintext, aad)
    return aes_r + aes_enc


def nott_decrypt(key: bytes, blob: bytes, aad: bytes = b"") -> bytes:
    """
    Decrypt the data using AES-GCM
    """
    aes_gcm_init = AESGCM(key)
    aes_r, aes_dec = blob[:12], blob[12:]
    return aes_gcm_init.decrypt(aes_r, aes_dec, aad)


def load_config() -> dict:
    """
    If a config file exists, we need to read the saved valued
    """
    if not os.path.exists(CONFIG_PATH):
        raise typer.Exit("Program not initialized. Run: \"nott init\"")

    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(cfg: dict):
    """
    We handle this on initialization and when the password is changed (the config is important to handling auth)
    """
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

    try:
        os.chmod(CONFIG_PATH, 0o600)
    except Exception:
        pass


def get_key_from_session() -> Optional[bytes]:
    """
    If an encoded session key exists, we access it here
    """
    try:
        with open(SESSION_PATH, "rb") as f:
            data = f.read()

        return base64.b64decode(data)
    except Exception:
        return None


def set_session_key(key: bytes):
    """
    Set the session key when the session is created
    """
    save_session_file(SESSION_PATH, base64.b64encode(key))


def clear_session():
    """
    Basic method to clear the current session
    """
    try:
        os.remove(SESSION_PATH)
    except FileNotFoundError:
        pass


def prompt_password(prompt: str = "Password: ") -> str:
    """
    Prompt the user for a password
    """
    try:
        return getpass.getpass(prompt)
    except Exception:
        # Fallback for environments without TTY
        return input(prompt)


def unlock_key() -> bytes:
    """
    Attempt to unlock the application by using the session key and config
    """
    ensure_app_dir()
    cfg = load_config()
    key = get_key_from_session()

    # If the key exists, and it's verified via the config, return it
    # If not, clear the session
    if key is not None:
        # Verify key matches the current config
        if hmac.compare_digest(hmac_verify_tag(key), base64.b64decode(cfg["verify"])):
            return key
        else:
            clear_session()

    # Attempt to unlock the "vault" up to 3 times before finally quitting
    # NOTE: May eventually add something here where if there's x numer of incorrect attempts, it automatically deletes or locks the database
    for _ in range(3):
        pw = prompt_password()

        try:
            # Derive the key by using the previously generated salt and kdf values
            key = derive_key(password=pw, salt=base64.b64decode(cfg["salt"]), **cfg["kdf"])

            # Key matches, return accordingly
            if hmac.compare_digest(hmac_verify_tag(key), base64.b64decode(cfg["verify"])):
                return key

        except Exception:
            pass

        console.print("[red]Incorrect password. Try again.[/red]")

    raise typer.Exit("Failed to unlock.")


def db_controller() -> sqlite3.Connection:
    """
    Configure and communicate with the local database
    """
    ensure_app_dir()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            tags TEXT DEFAULT '',
            body BLOB NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
    """)
    return conn


def current_time_iso() -> str:
    """
    Get the current time in ISO format
    """
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def open_editor(initial_text: str) -> str:
    """
    Open the default editor in certain circumstances
    """
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")

    if not editor:
        # If we need to open a terminal edito for any reason, use nano (vi as a backup)
        editor = "nano" if os.system("command -v nano >/dev/null 2>&1") == 0 else "vi"

    # Create a temporary file, so there's no direct reads
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".md") as tf:
        tf.write(initial_text)
        tf.flush()
        path = tf.name

    try:
        os.system(f"{editor} {shlex.quote(path)}")

        with open(path, "r") as f:
            return f.read()
    finally:
        try:
            os.remove(path)
        except Exception:
            pass

"""
-----------------------------------------------|
|                                              |
| All commands currently available within nott |
|                                              |
-----------------------------------------------|
"""


@app.command("init")
def init(overwrite: bool = typer.Option(False, "--overwrite", help = "Recreate config / database if they exist")):
    """
    Initialize the local database and config, even if they already exist
    """
    ensure_app_dir()

    # If the config file already exists and the "overwrite" flag isn't provided, just exit
    if os.path.exists(CONFIG_PATH) and not overwrite:
        console.print("[yellow]Already initialized[/yellow]")
        raise typer.Exit()

    # If the "overwrite" flag is provided, and the db exists, we wipe the database
    if overwrite and (os.path.exists(CONFIG_PATH) or os.path.exists(DB_PATH)):
        if not Confirm.ask("[red]This will wipe the database[/red]. Continue?"):
            raise typer.Exit("Aborted.")

        try:
            os.remove(DB_PATH)
        except FileNotFoundError:
            pass

    # Handle the creation of the user's password
    while True:
        pw = prompt_password("Create password: ")
        confirm_pwd = prompt_password("Confirm password: ")

        # May eventually add extra checks for special characters, etc., but for now, as long as it's more than 8 characters, it's fine
        if pw != confirm_pwd:
            console.print("[red]Passwords do not match. Try again.[/red]")
        elif len(pw) < 8:
            console.print("[red]Use at least 8 characters.[/red]")
        else:
            break

    # Here we build the config file and make sure it's formatted properly
    salt = os.urandom(16)
    kdf_params = {"n": 2**14, "r": 8, "p": 1, "key_length": 32}
    key = derive_key(pw, salt, **kdf_params)
    verify = hmac_verify_tag(key)

    cfg = {
        "salt": base64.b64encode(salt).decode(),
        "kdf": kdf_params,
        "verify": base64.b64encode(verify).decode(),
        "version": 1
    }

    save_config(cfg)
    db_controller().close()

    console.print("[green]Nott initialized.[/green] You can now add notes")
    console.print("Tip: run [bold]nott login[/bold] to cache a session key (optional)")


@app.command("login")
def login():
    """
    Cache a session key locally (mode 0o600)
    """
    key = unlock_key()
    set_session_key(key)
    console.print("[green]Unlocked.[/green] Session key cached.")


@app.command("logout")
def logout():
    """
    Clear the local cached session key
    """
    clear_session()
    console.print("[green]Locked.[/green] Session cleared.")


@app.command("add")
def add_note(
    title: str = typer.Argument(help = "The title of the note (plaintext)"),
    tags: str = typer.Option("", "--tags", help="Comma-separated tags for the note (plaintext)"),
    body: Optional[str] = typer.Option(None, "--body", help="The actual content within the note (encrypted)"),
):
    """
    Add a new note. Body is encrypted, but title/tags are plaintext
    """
    key = unlock_key()

    if body is None:
        body = open_editor("")

        if body.strip() == "":
            raise typer.Exit("Aborting. Empty body")

    blob = nott_encrypt(key, body.encode("utf-8"))
    new_id = str(uuid.uuid4())
    now = current_time_iso()

    # INSERT a new note into the database
    with db_controller() as conn:
        conn.execute(
            "INSERT INTO notes (id, title, tags, body, created_at, updated_at) VALUES (?,?,?,?,?,?)",
            (new_id, title, tags, blob, now, now)
        )

    console.print(f"[green]Created[/green] {new_id}")


@app.command("list")
def list(
    tag: Optional[str] = typer.Option(None, "--tag", help="Filter by a specific tag (substring match)"),
    q: Optional[str] = typer.Option(None, "--query", help="Filter the title by substring"),
    limit: int = typer.Option(50, "--limit", help="The number of notes to view/query"),
):
    """
    List all notes by title/tags
    """
    _ = unlock_key()

    # Construct the SQL query for the local database
    with db_controller() as conn:
        sql = "SELECT id, title, tags, created_at, updated_at FROM notes"
        clauses = []
        args = []

        # Check if a tag exists with the provided input
        if tag:
            clauses.append("tags LIKE ?")
            args.append(f"%{tag}%")

        # Check if a title exists with the provided input
        if q:
            clauses.append("title LIKE ?")
            args.append(f"%{q}%")

        if clauses:
            sql += " WHERE " + " AND ".join(clauses)

        sql += " ORDER BY updated_at DESC LIMIT ?"
        args.append(limit)
        rows = conn.execute(sql, args).fetchall()

    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("ID", overflow="fold")
    table.add_column("Title")
    table.add_column("Tags")
    table.add_column("Updated")

    for rid, title, tags, _, updated in rows:
        table.add_row(rid, title, tags, updated)

    console.print(table)


@app.command("show")
def show(id: str = typer.Argument(help="Note ID")):
    """
    Decrypt the note's body and show it in stdout, provided the user gives the correct ID
    """
    key = unlock_key()

    # Fetch the single note being requested
    with db_controller() as conn:
        row = conn.execute("SELECT title, tags, body, created_at, updated_at FROM notes WHERE id=?", (id,)).fetchone()

    if not row:
        raise typer.Exit("Not found")

    title, tags, body, created_at, updated_at = row

    try:
        # Attempt to decrypt the note
        text = nott_decrypt(key, body).decode("utf-8")
    except Exception:
        # Unable to decrypt the note
        raise typer.Exit("Decryption failed (wrong key?)")
    
    # Entire contents of the note is presented, unlocked
    console.rule(f"[bold]{title}[/bold]")
    console.print(f"[dim]Tags:[/dim] {tags or '-'}")
    console.print(f"[dim]Created:[/dim] {created_at}")
    console.print(f"[dim]Updated:[/dim] {updated_at}")
    console.print()
    console.print(text)


@app.command("edit")
def edit(id: str = typer.Argument(help="Note ID")):
    """
    Edit a note in the default $EDITOR (Body remains encrypted at rest)
    """
    key = unlock_key()

    with db_controller() as conn:
        row = conn.execute("SELECT title, tags, body FROM notes WHERE id=?", (id,)).fetchone()

    if not row:
        raise typer.Exit("Unable to find note")

    title, tags, body = row

    # Decrypt and open default file editor (this is usually nano or vi)
    text = nott_decrypt(key, body).decode("utf-8")
    new_text = open_editor(text)

    # Detect if any changes were made and notify accordingly
    if new_text.strip() == text.strip():
        console.print("[yellow]No changes made[/yellow]")
        raise typer.Exit()

    blob = nott_encrypt(key, new_text.encode("utf-8"))
    now = current_time_iso()

    with db_controller() as conn:
        conn.execute("UPDATE notes SET body=?, updated_at=? WHERE id=?", (blob, now, id))

    console.print("[green]Saved[/green]")


@app.command("update-title")
def update_title(
    id: str,
    title: str = typer.Option("", "--title", help="The new title of the note (plaintext)"),
):
    """
    Update a note's title (plaintext)
    """
    _ = unlock_key()
    now = current_time_iso()

    with db_controller() as conn:
        cur = conn.execute("UPDATE notes SET title=?, updated_at=? WHERE id=?", (title, now, id))

        if cur.rowcount == 0:
            raise typer.Exit("Not found")

    console.print("[green]Updated title.[/green]")

@app.command("set-tags")
def set_tags(
    id: str,
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags for the note"),
):
    """
    Update a note's tags (comma-separated, plaintext)
    """
    _ = unlock_key()
    now = current_time_iso()

    with db_controller() as conn:
        cur = conn.execute("UPDATE notes SET tags=?, updated_at=? WHERE id=?", (tags, now, id))

        if cur.rowcount == 0:
            raise typer.Exit("Not found")

    console.print("[green]Updated tags[/green]")


@app.command("search")
def search(term: str):
    """
    Decrypt-on-the-fly full-text search across bodies (slower for large notes, but more secure if you don't want to open the full contents)
    """
    key = unlock_key()

    with db_controller() as conn:
        rows = conn.execute("SELECT id, title, tags, body, updated_at FROM notes").fetchall()

    matches = []
    term_lower = term.lower()

    # Iterate over all rows and decrypt per row to check if term is present
    for n_id, title, tags, body, updated in rows:
        try:
            text = nott_decrypt(key, body).decode("utf-8")
        except Exception:
            continue

        if term_lower in text.lower():
            matches.append((n_id, title, tags, updated))

    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("ID", overflow="fold")
    table.add_column("Title")
    table.add_column("Tags")
    table.add_column("Updated")

    for n_id, title, tags, updated in matches:
        table.add_row(n_id, title, tags, updated)

    console.print(table)


@app.command("rm")
def remove(id: str, yes: bool = typer.Option(False, "--yes", help="Skip confirmation")):
    """
    Delete a note from the database
    """
    _ = unlock_key()

    if not yes and not Confirm.ask(f"Delete note {id}?"):
        raise typer.Exit("Aborted")

    with db_controller() as conn:
        cur = conn.execute("DELETE FROM notes WHERE id=?", (id,))

        if cur.rowcount == 0:
            raise typer.Exit("Not found")

    console.print("[green]Deleted[/green]")


@app.command("change-pass")
def change_pass():
    """
    Rotate the vault password; re-encrypts note bodies with the new key
    """
    old_key = unlock_key()
    cfg = load_config()

    # New password flow (not too different from initial setup)
    while True:
        pw = prompt_password("New password: ")
        confirm_pw = prompt_password("Confirm new password: ")

        if pw != confirm_pw:
            console.print("[red]Passwords do not match[/red]")
        elif len(pw) < 8:
            console.print("[red]Use at least 8 characters[/red]")
        else:
            break

    new_salt = os.urandom(16)
    kdf_params = cfg["kdf"]
    new_key = derive_key(pw, new_salt, **kdf_params)

    # Re-encrypt bodies with new password
    with db_controller() as conn:
        rows = conn.execute("SELECT id, body FROM notes").fetchall()

        for n_id, body in rows:
            # We need to decrypt first with the old key, then update with the new key
            plaintext = nott_decrypt(old_key, body)
            new_blob = nott_encrypt(new_key, plaintext)
            conn.execute("UPDATE notes SET body=? WHERE id=?", (new_blob, n_id))

    # Update config file and session key
    cfg["salt"] = base64.b64encode(new_salt).decode()
    cfg["verify"] = base64.b64encode(hmac_verify_tag(new_key)).decode()
    save_config(cfg)
    set_session_key(new_key)
    console.print("[green]Password updated[/green]")


@app.command("export")
def export(path: str = typer.Option("nott_out", "--path", help="Export all notes as decrypted markdown files")):
    """
    Export all notes as decrypted Markdown files
    """
    key = unlock_key()
    dest = pathlib.Path(path).expanduser()
    dest.mkdir(parents=True, exist_ok=True)

    with db_controller() as conn:
        rows = conn.execute("SELECT id, title, tags, body FROM notes").fetchall()

    # Decrypt everything and push to a formatted Markdown file
    # This is not fully customized with headers, tables, etc. in most Markdown
    # It's a simple export, nothing too complex right now
    for n_id, title, tags, body in rows:
        text = nott_decrypt(key, body).decode("utf-8")
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ","-","_")).rstrip()
        fname = f"{safe_title or n_id}.md"
        p = dest / fname
        content = f"---\nid: {n_id}\ntags: {tags}\n---\n\n{text}\n"
        p.write_text(content, encoding="utf-8")

    console.print(f"[green]Exported {len(rows)} notes to {dest}[/green]")


if __name__ == "__main__":
    app()
