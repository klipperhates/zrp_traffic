# ZRP Traffic Enforcement System

A digital enforcement management system built for the Zimbabwe Republic Police (ZRP) to streamline traffic offence recording, reduce corruption, and provide transparent road management.

## Purpose
- Lookup drivers and vehicles by number plate
- Record and track traffic offences per driver and vehicle
- Apply warning and fine rules consistently and transparently
- Generate receipts for fines paid to eliminate corruption

## Tech Stack
- Python 3.14
- Flask
- SQLite
- Flask-SQLAlchemy
- Flask-Login
- Flask-Bcrypt

## Setup Instructions
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the seed script: `python data/seed.py`
6. Start the server: `python run.py`

## Status
Currently in active development. Prototype phase for ZINARA pitch.