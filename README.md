# Faym SDE Intern Assignment – Creator Payout System

## Overview

This project is a backend system built using **FastAPI** to simulate a creator payout workflow for a creator-commerce platform like Faym.

The system manages:

- Creator authentication
- Sales creation
- Advance payout (10%)
- Sale reconciliation (Approved / Rejected)
- Withdrawals
- JWT Authentication & Role-Based Authorization

---

# Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic v2
- JWT Authentication
- Bcrypt Password Hashing

---

# Features

### Authentication

- Login using JWT
- Password hashing using bcrypt
- HttpOnly Cookie Authentication
- Role Based Access Control

Roles:
- ADMIN
- CREATOR

---

### Creator Features

- Login
- View own profile
- View available balance
- Create sale (Assignment implementation)
- Request withdrawal

---

### Admin Features

- View any user
- Process advance payout
- Approve / Reject sales
- Update withdrawal status

---

# Business Rules

## Sale Creation

Every newly created sale:

- Status = Pending
- is_advance_paid = False

---

## Advance Payout

Admin processes advance payout.

Rules:

- Only Pending sales are considered.
- Sales that already received advance are ignored.
- Creator receives **10%** of sale earnings.
- Sale is marked:

```
is_advance_paid = True
```

---

## Sale Reconciliation

### Approved

Remaining **90%** is credited to creator.

Example

Sale Earnings

```
₹100
```

Advance already paid

```
₹10
```

Remaining credited

```
₹90
```

---

### Rejected

If advance was already paid,

that amount is deducted from creator balance.

If the creator has already withdrawn the advance,

balance may become negative.

Future earnings automatically offset this negative balance before new withdrawals.

---

## Withdrawal

Rules

- User cannot withdraw more than available balance.
- Only one withdrawal request every 24 hours.
- Balance is deducted immediately when request is created.
- If withdrawal fails,
  amount is refunded.

---

# API List

## Authentication

| Method | Endpoint |
|---------|----------|
| POST | /auth/login |
| GET | /auth/me |

---

## Users

| Method | Endpoint |
|---------|----------|
| GET | /users/{user_id} |
| GET | /users/balance |

---

## Sales

| Method | Endpoint |
|---------|----------|
| POST | /sales |
| POST | /sales/advance |
| PATCH | /sales/{sale_id} |

---

## Withdrawals

| Method | Endpoint |
|---------|----------|
| POST | /withdrawals |
| PATCH | /withdrawals/{withdrawal_id} |

---

# Authentication

The application uses JWT Authentication.

After successful login,

JWT is stored inside an HttpOnly Cookie.

Protected APIs automatically verify the logged-in user before processing requests.

---

# Running the Project

## Clone Repository

```bash
git clone <https://github.com/princeSinglacoder/faym_assignment>
```

---

## Create Virtual Environment

```bash
python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env`

```env
DATABASE_URL=your_postgresql_database_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## Run Server

```bash
uvicorn app.main:app --reload
```

Swagger

```
http://localhost:8000/docs
```

---

# Default Admin Account

> **Update these credentials before submission if you change them.**

Email

```
admin@faym.com
```

Password

```
admin123
```

---

# Assumptions

- One sale belongs to one creator.
- Brand is stored as a string (no separate Brand table).
- Advance payout is fixed at **10%**.
- Remaining **90%** is credited only after approval.
- Negative balances are allowed if a previously advanced sale is later rejected after withdrawal.
- Future earnings first offset negative balances.
- Advance payout is manually triggered through an API (can be scheduled using a Cron Job in production).

---

# Future Improvements

- Brand Management Module
- Automated Cron Job for Advance Payout
- Payment Gateway Integration
- Email Notifications
- Audit Logs
- Transaction Ledger
- Docker Support
- Unit Tests
- CI/CD Pipeline
- Refresh Tokens
- Rate Limiting

---

# Project Structure

```
app/
│
├── models/
├── schemas/
├── services/
├── routers/
├── database/
├── utils/
├── config.py
└── main.py
```

---

# Notes

This assignment focuses on backend architecture, business logic, authentication, authorization, and payout workflow implementation.

The project has been implemented with clean separation of concerns using:

- Routers
- Services
- Models
- Schemas

to keep the codebase modular and maintainable.