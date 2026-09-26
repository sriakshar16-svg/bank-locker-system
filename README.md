# 25CC3071-P019 Bank Locker Rent and Agreement Renewal Tracker

**Domain:** Retail Branch Banking

## Project Overview
This repository contains a lightweight web application designed to automate safe deposit locker records and streamline rent collections. It replaces manual ledger tracking with a digital dashboard for managing branch locker agreements securely.

## Use Cases Achieved
- **Track locker allotment, rent due, and renewal dates.**
- **Generate rent-due notices and auto-debit files** via a CSV export functionality.

## Bottlenecks Solved
- **Locker sizes have different rent slabs:** Solved by mapping dropdown size selections to integer rent values in the backend before database insertion.
- **Joint locker holders and nominee updates:** Solved by building a dedicated edit route that executes an SQL `UPDATE` strictly on those two fields.

## Tech Stack
- **Backend:** Python, FastAPI
- **Database:** SQLite
- **Frontend:** HTML, Tailwind CSS, Jinja2 Templating

## Local Setup & Run Instructions

To run the application locally, execute the following commands in your terminal:

```bash
pip install fastapi uvicorn jinja2 python-multipart
uvicorn main:app --reload
```

Once the server is running, access the dashboard at:
[http://127.0.0.1:8000](http://127.0.0.1:8000)
