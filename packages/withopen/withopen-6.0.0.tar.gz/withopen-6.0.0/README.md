# 🧾 WithOpen — "Your code's .txt guide"

> A Zero Dependency and Robust structured `.txt` files file manager for automation, pipelines, and bot-friendly data with confidence.  
> Replacing 20+ lines of code and logic with a single one-liner.

This project started from a simple frustration:  
After writing **hundreds of `with open(file) as ..` lines**, building backups, validating structures, and hacking delete filters... I realized I was reinventing the same patterns over and over.

So I made **withopen**:  
A zero-dependency Python utility that treats plain `.txt` files like structured datasets — safely and scalably.

It’s **not a database**. It’s a reliable, structured backend for:

- **Automations**
- **Bots**
- **CLI tools**
- **Low-overhead microservices**

## 🎯 Key Capabilities

- **Structure Enforcement**: First write or append defines whether data is 1D or 2D; future data must match.
- **CRUD Operations**: `w()` (write), `r()` (read), `a()` (append), `d()` (delete/trim/filter).
- **Multi-console safe**: Handles concurrent processes to avoid corruption.
- **Backups & Snapshots**: Automatic and manual backups, plus time-based snapshots.
- **Auto Folder Organization**: All files, backups, and snapshots are kept in structured folders — no clutter.
- **Anti-Tamper Safe Mode**: Hidden files and structure-locking help protect against manual edits or file corruption.
- **Debug & Recovery**: Scan for structural errors and selectively repair.
- **Hide / Unhide**: Protect files from accidental user tampering.
- **Zero dependencies**, intuitive API, and minimal setup.

## 🔑 Core Functions

### ✅ `w()` — Write / Overwrite

```python
w(txt_name, write_list, is2d=None)
```

| Parameter    | Type             | Description                                                                                         |
| ------------ | ---------------- | --------------------------------------------------------------------------------------------------- |
| `txt_name`   | `str`            | Name of the file (without extension).                                                               |
| `write_list` | `list`           | Data to write (1D or 2D list). Overwrites existing content.                                         |
| `is2d`       | `bool` or `None` | Specify structure type on first write or when resetting. Only required if the file is new or empty. |

📝 *Use `[]` to reset file structure.*

### 📖 `r()` — Read

```python
r(txt_name, index=None, set_new=[], notify_new=True)
```

| Parameter    | Type                     | Description                                                    |
| ------------ | ------------------------ | -------------------------------------------------------------- |
| `txt_name`   | `str`                    | Name of the file.                                              |
| `index`      | `int`, `list`, or `None` | Return only data from specific index/column(s).                |
| `set_new`    | `list`                   | If file doesn’t exist, create it using this list.              |
| `notify_new` | `bool`                   | Print a message if the file was auto-created. Default: `True`. |

### ➕ `a()` — Append

```python
a(txt_name, append_list, is2d=None)
```

| Parameter     | Type             | Description                                     |
| ------------- | ---------------- | ----------------------------------------------- |
| `txt_name`    | `str`            | Name of the file.                               |
| `append_list` | `list`           | Data to append (must match existing structure). |
| `is2d`        | `bool` or `None` | Required only for new or empty files.           |

### ❌ `d()` — Delete / Filter / Trim

```python
d(txt_name, del_list=[], index=None, cutoff=None, keep=None, reverse=False, size=None)
```

| Parameter  | Type                           | Description                                            |
| ---------- | ------------------------------ | ------------------------------------------------------ |
| `txt_name` | `str`                          | Name of the file.                                      |
| `del_list` | `list` or `str`                | Values to match for deletion.                          |
| `index`    | `int`, `list`, `"*"` or `None` | Column(s) to match values in. `"*"` matches whole row. |
| `cutoff`   | `int`                          | Maximum number of deletions per value.                 |
| `keep`     | `int`                          | Retain only N matching rows.                           |
| `reverse`  | `bool`                         | Delete from end instead of top.                        |
| `size`     | `int`                          | Trim the file to only last N rows.                     |

🧠 *You can mix-and-match these for precise cleanup strategies.*

## ⚙️ Installation

```bash
pip install withopen
```

## 🏃 Example Workflow

```python
import withopen as f

# Write 2D data (first write locks structure)
f.w("tasks", [["Name", "Status"], ["Ping", "Done"], ["Build", "Pending"]])

# Append new row (must match shape)
f.a("tasks", [["Test", "Pending"]])

# Read all rows
print(f.r("tasks"))

# Read specific column or row
print(f.r("tasks", index=1))      # second column across all rows
print(f.r("tasks", index=[0, 2])) # columns 0 and 2

# Delete by matching value
f.d("tasks", del_list=["Done"], index=1)

# Trim to last N rows
f.d("tasks", size=3)

# Backup & snapshot
wo.backup("tasks")
f.snapshot("tasks", unit="h", gap=4)

# Debug / fix structure errors
f.debug("tasks", is2d=True, length=2)

# Hide / unhide
f.hide("tasks")
f.unhide("tasks")
```

## 📋 Data Models: 1D & 2D

| Mode   | Example                                       | Notes                                  |
| ------ | --------------------------------------------- | -------------------------------------- |
| **1D** | `["apple", "banana", "pear"]`                 | Use `is2d=False` on first write/append |
| **2D** | `[["user","score"], ["alice",10], ["bob",8]]` | Use `is2d=True` on first write/append  |

To reset structure (clear file):

```python
f.w("filename", [], is2d=None)
```

## 🧹 Deletion & Filtering

`d()` is versatile. Combine arguments:

- `del_list` (values or rows)
- `index` (column index, list of indices, or `"*"` for full row)
- `cutoff` (max deletes per value)
- `keep` (retain only N matches)
- `reverse` (delete from end)
- `size` (keep only last N rows)

### Examples

**Delete rows where status == “Done”:**

```python
f.d("tasks", del_list=["Done"], index=1)
```

**Delete a full exact row:**

```python
f.d("tasks", del_list=[["Ping","Done"]], index="*")
```

**Trim to last 5 rows:**

```python
f.d("tasks", size=5)
```

**Keep only N occurrences of a value:**

```python
f.d("tasks", del_list=["Pending"], index=1, keep=2)
```

## 🔢 Index Matching Patterns

### 1. Match by Single Index (Column)

```python
f.d("tasks", del_list=["Pending"], index=1)
```

*Deletes all rows where column `1` (status) is `"Pending"`.*

### 2. Match by Multiple Indexes (Multi-Column Logic)

```python
f.d("tasks", del_list=[["Fix Bug", "High"]], index=[0, 2])
```

*Deletes rows where column `0` = `"Fix Bug"` and column `2` = `"High"`.*

### 3. Match Entire Row

```python
f.d("tasks", del_list=[["Fix Bug", "Done", "Low"]], index="*")
```

*Deletes exact row match across all columns.*

### 4. Match Multiple Rows by Value in a Column

```python
f.d("tasks", del_list=[["Deploy"], ["Write Docs"]], index=0)
```

*Deletes any row where column `0` (task name) matches `"Deploy"` or `"Write Docs"`.*

### 5. Selective Cutoff Deletes

```python
f.d("tasks", del_list=["Pending"], index=1, cutoff=2)
```

*Deletes only the first 2 rows where column `1` = `"Pending"`.*

### 6. Reverse Delete

```python
f.d("tasks", del_list=["Done"], index=1, reverse=True)
```

*Deletes from the bottom up, not top-down.*

### 7. Trim by Row Count (No `index`)

```python
f.d("tasks", size=5)
```

*Keeps only the last 5 rows — trims the rest.*

## 🛠 Debugging & Recovery

When a file's structure is compromised:

```python
debug("tasks", is2d=True, length=2)
```

- Flags bad rows and optionally cleans them.
- Use majority-vote backups to restore

when corruption occurs.

## 📁 Backups & Snapshots

* `backup("tasks")` → manual backup
* `snapshot("tasks", unit, gap, trim=None, begin=0)` → time-based backup

  * Units: `'s'`, `'m'`, `'h'`, `'d'`, `'mo'`, `'y'`
  * `gap`: minimum time between snapshots
  * `trim`: max rows in snapshot

Backups and snapshots are stored in structured subfolders.

## 🔐 Hide / Unhide Files

* `hide("tasks")`: prevents accidental edits or reads
* `unhide("tasks")`: makes file visible again
* Use `"*"` to hide/unhide all files

## 🧠 Best Practices

1. Always use the API (`w`, `a`, `r`, `d`) — avoid manual edits.
2. Run `debug()` periodically for long-lived files.
3. Use `snapshot()` in scripts that run continuously.
4. Use `hide()` when bundling scripts to protect internal files.
5. Reset structure if your shape definition changes (with `w("file", [])`).

## 🔧 Utility Functions

### 🖥️ `consoles()` — Console Mode Config

```python
f.consoles(txt_name, multiple=True, alert=True)
```

Sets console interaction mode for:

* Multiple scripts
* Multiple tabs
* Bots and automation tools

Ensures safe concurrent access by coordinating file locks per console context.  
Use this when your files are read/written by multiple parallel environments.

---

### 🔕 `warning()` — Enable or Disable Read Alerts

```python
f.warning(alert=False)
```

Turns on or off the warning that appears when reading a file outside of console-safe mode.

Useful for bots or CI/CD logs where alerts aren’t needed.

---

### 🗑️ `remove(txt_name, display=True)`

Deletes the target file along with all backups and snapshots.  
⚠️ Use with caution — irreversible.

### ℹ️ `info(txt_name, display=True)`

Returns metadata such as structure type, total rows, shape, and last modified time.

### 🧪 `debug(txt_name, is2d=None, length=None, display=True)`

Scans for structure issues like row length mismatches or corrupted lines.  
Can auto-fix when used with `length` or `is2d`.

### 📂 `listdir(display=True)`

Lists all structured text files currently being tracked.

### 🆘 `help()`

Prints a quick-reference summary of all available functions and parameters.  
Great for in-terminal use.

## 📄 License

This project is licensed under the **MIT License**.  
Use freely, modify, share — no warranties.
