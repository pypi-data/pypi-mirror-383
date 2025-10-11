# automation-flow-tracker

**automation-flow-tracker** is a helper library for the Python automation system.  
It provides automatic tracking of script executions ("runs"), detailed logging, and log file maintenance using an SQLite database.

---

## Features

- Tracks all runs and their status in an SQLite database  
- Automatically creates and cleans up log files  
- Logs detailed errors and stack traces  
- Supports different trigger types (`manual` or `scheduler`)  
- Integrates easily into any automation flow  

---

## Installation

```bash
pip install automation-flow-tracker
