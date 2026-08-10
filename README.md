# Guess the Word

A full-stack Wordle-style word guessing game.

The application provides two types of users — **Players** and **Administrators**. Players can play the word guessing game with a daily limit, while administrators can monitor game activity through reports.

---

## Features

### Player

* User registration and login
* Play a 5-letter word guessing game
* Maximum of **3 games per calendar day**
* Maximum of **5 guesses per game**
* Guesses are submitted as 5-letter uppercase words
* Word feedback using:

  * 🟩 **Green** — correct letter in the correct position
  * 🟧 **Orange** — correct letter in the wrong position
  * ⬜ **Grey** — letter is not present in the target word
* Previous guesses remain visible in the order they were submitted
* Game results and guesses are stored in the database

### Administrator

* Separate administrator access
* View daily activity reports
* View:

  * Number of users who played on a selected day
  * Number of correct guesses/wins
* View individual user reports
* User reports include:

  * Date
  * Number of words tried
  * Number of correct guesses

---

## Technology Stack

| Component              | Technology        |
| ---------------------- | ----------------- |
| Programming Language   | Python 3.11+      |
| Web Framework          | Flask             |
| ORM                    | SQLAlchemy        |
| Database               | SQLite            |
| Authentication         | Flask-Login       |
| Password Security      | Werkzeug          |
| Frontend               | HTML, CSS, Jinja2 |
| Testing                | Pytest            |
| Version Control        | Git / GitHub      |
| Continuous Integration | GitHub Actions    |

---

## Application Architecture

The application follows a modular Flask architecture.

```text
Browser
   │
   ▼
Flask Application
   │
   ├── Authentication
   │     ├── Registration
   │     └── Login / Logout
   │
   ├── Player Module
   │     ├── Start Game
   │     ├── Submit Guess
   │     └── View Game Result
   │
   ├── Game Scoring
   │     └── Two-pass Wordle scoring algorithm
   │
   ├── Admin Module
   │     ├── Daily Report
   │     └── User Report
   │
   ▼
SQLAlchemy
   │
   ▼
SQLite Database
```

---

## Game Rules

1. A player registers and logs into the application.
2. The player starts a new game.
3. One 5-letter word is randomly selected from the database.
4. The player can submit a maximum of **5 guesses** for the game.
5. Each guess must be a 5-letter uppercase word.
6. Each submitted letter is evaluated:

   * 🟩 **Green** — correct letter in the correct position
   * 🟧 **Orange** — correct letter in the wrong position
   * ⬜ **Grey** — letter is not present in the target word
7. Previous guesses remain visible in the same sequence in which they were submitted.
8. If the player guesses the target word correctly:

   * The player wins the game.
   * A congratulatory message is displayed.
   * The game ends.
9. If the player uses all 5 guesses without finding the word:

   * **"Better luck next time"** is displayed.
   * The game ends.
10. A player can start a maximum of **3 games per calendar day**.

---


## Database

The application uses **SQLite** as the database and **SQLAlchemy** as the ORM.

### Main Entities

```text
User
 ├── username
 ├── password_hash
 └── role

Word
 └── word

Game
 ├── user
 ├── target_word
 ├── date
 ├── status
 └── result

Guess
 ├── game
 ├── guessed_word
 ├── guess_number
 └── date
```

### Seed Data

The project includes **20 initial 5-letter English words** that are inserted into the database using the seed scripts located in the `seed/` directory.

Seed the initial words:

```bash
python seed/seed_words.py
```

Create the administrator account:

```bash
python seed/seed_admin.py
```

The administrator credentials can be configured using environment variables:

```text
ADMIN_USERNAME
ADMIN_PASSWORD
```


---

## Authentication and Authorization

The application uses **Flask-Login** for authentication and session management.

Two roles are supported.

### Player

Players can:

* Register an account
* Log in and log out
* Start a game
* Submit guesses
* View previous guesses
* View game results

### Admin

Administrators can:

* Log in to the administrator dashboard
* View daily activity reports
* View user-specific reports
* Access administrative functionality protected by role-based authorization

Role-based decorators prevent unauthorized users from accessing administrator functionality.

---

## Input Validation

The application validates user input before processing it.

Validation includes:

* Username requirements
* Password requirements
* 5-letter word guesses
* Uppercase guess input
* Maximum of 5 guesses per game
* Maximum of 3 games per calendar day
* Valid game state before accepting a guess

---

## Admin Reports

Administrators have access to two types of reports.

### Daily Report

The daily report provides:

* Number of users who played on a selected date
* Number of correct guesses/wins

### User Report

The user-specific report provides:

* Date
* Number of words tried
* Number of correct guesses

These reports are generated from the game and guess information stored in the database.

---

## Project Structure

```text
guess-the-word/
│
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── models.py            # SQLAlchemy database models
│   ├── auth.py              # Registration and authentication
│   ├── game.py              # Game routes and game logic
│   ├── admin.py             # Admin dashboard and reports
│   ├── scoring.py           # Word scoring algorithm
│   ├── decorators.py        # Role-based access control
│   │
│   ├── templates/
│   │   └── ...              # Jinja2 HTML templates
│   │
│   └── static/
│       └── ...              # CSS and static assets
│
├── seed/
│   ├── seed_words.py        # Inserts initial 20 words
│   └── seed_admin.py        # Creates administrator account
│
├── tests/
│   └── ...                  # Pytest test modules
│
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI pipeline
│
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
├── .gitignore
└── README.md
```

---

## Setup and Installation

### Prerequisites

Make sure the following are installed:

* Python **3.11 or later**
* Git

### 1. Clone the Repository

```bash
git clone https://github.com/MD-Raiyaan/word-game.git
cd word-game
```

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Database Initialization

After installing the dependencies, initialize the database with the required seed data.

### Seed the 20 Words

```bash
python seed/seed_words.py
```

### Create the Admin Account

```bash
python seed/seed_admin.py
```

If environment variables are configured, they will be used for the administrator credentials.

---

## Running the Application

Start the Flask application:

```bash
python run.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

Open the URL in a web browser to access the application.

---

## Running Tests

The project includes an automated test suite using **Pytest**.

Run all tests with:

```bash
pytest
```

The test suite covers functionality including:

* User registration
* Authentication
* Login and logout
* Input validation
* Password handling
* Game creation
* Random word selection
* Guess submission
* Word scoring
* Duplicate-letter handling
* Correct guesses
* Incorrect guesses
* Game completion
* Maximum guess limit
* Daily game limit
* Role-based access control
* Admin reports

---

## Continuous Integration

The project uses **GitHub Actions** for continuous integration.

The CI pipeline automatically runs on pushes and pull requests.

The application is tested against:

* Python 3.11
* Python 3.12
* Python 3.13

The CI workflow performs:

1. Python environment setup
2. Dependency installation
3. Database initialization
4. Seed data setup
5. Automated test execution

This helps ensure that the application remains functional across supported Python versions.

---






