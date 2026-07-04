# 🚗 AutoDrive – Smart Car Rental Management Platform

### Live Demo

[AutoDrive Live Project](https://anshukumar1021.pythonanywhere.com)

## 📌 Overview

AutoDrive is a full-stack Django-based vehicle rental platform designed to streamline the entire car booking lifecycle. The system enables customers to discover vehicles, check availability, reserve rentals, make payments, and track bookings, while administrators and staff efficiently manage inventory, maintenance schedules, customer verification, and rental operations.

Built with scalability and usability in mind, AutoDrive provides a seamless experience for both customers and management teams.

---

## ✨ Core Features

### 👤 Authentication & Role Management

* Secure user authentication system
* Separate dashboards for Customers, Staff, and Administrators
* Password reset with OTP verification
* Profile management and account security

### 🚘 Vehicle Management

* Dynamic vehicle catalog
* Search and filter functionality
* Real-time availability status
* Vehicle categorization
* Image uploads with media handling

### 📅 Rental Workflow

* Booking request submission
* Booking approval and rejection
* Pickup scheduling
* Return management
* Rental completion tracking
* Booking history management

### 💳 Payment System

* Rental payment tracking
* Invoice generation support
* Payment status monitoring
* Transaction records

### 🔧 Maintenance Module

* Vehicle servicing records
* Maintenance scheduling
* Availability blocking during repairs
* Service history tracking

### ⭐ Customer Engagement

* Rating and review system
* Feedback collection
* Rental experience evaluation

---

## 🛠 Technology Stack

| Layer          | Technologies                 |
| -------------- | ---------------------------- |
| Backend        | Python, Django               |
| Database       | SQLite                       |
| Frontend       | HTML, CSS                    |
| Media Handling | Pillow                       |
| Authentication | Django Authentication System |
| Deployment     | PythonAnywhere               |

---

## 🚀 Installation Guide

```bash
git clone <repository-url>

cd Djproject

python -m venv .venv

.venv\Scripts\activate

pip install django pillow

python manage.py migrate

python seed_db.py

python manage.py runserver
```

Visit:

http://127.0.0.1:8000/

---

##

---

## 📈 Key Highlights

✔ Role-Based Access Control
✔ Smart Booking Workflow
✔ Vehicle Availability Tracking
✔ Maintenance Management System
✔ Payment & Invoice Support
✔ Customer Reviews & Ratings
✔ OTP-Based Password Recovery
✔ Responsive and User-Friendly Interface

---

## Future Enhancements

* Online payment gateway integration
* PDF invoice generation
* Email notifications
* REST API support
* Analytics dashboard
* Recommendation system for rentals
