BulkBuy - Group Buying Web Application
BulkBuy is a modern, user-friendly Flask web application designed to facilitate group buying for vendors while allowing suppliers to manage and add products. It enables users to register as either Suppliers (who add and manage products) or Vendors (who browse products, add them to a shared cart, and complete purchases). The app incorporates role-based dashboards, real-time group cart management, and a multi-step checkout process.

Key Features
User Roles: Separate signups for Suppliers and Vendors with role-specific dashboards.

Supplier Portal: Add and manage product listings easily.

Vendor Portal:

Browse supplier products

Add multiple quantities of products to a group cart

View detailed cart summary

Confirm and checkout purchases securely

Session-based Cart: Stores the shared cart for vendors during the session.

Clean & Responsive UI: Modern, attractive interface using Bootstrap and custom CSS.

Flash Messaging: Real-time feedback on user actions such as login, signup, and cart updates.

Simple SQLite backend for handling user data and products.

JavaScript Enhancements like auto-focus on form fields and logout confirmation.

Tech Stack
Python 3 & Flask Framework

Flask-SQLAlchemy for ORM & SQLite database

HTML, CSS (with Bootstrap 5), JavaScript (vanilla)

Bootstrap Icons for modern UI elements

Getting Started
Clone the repo

Install dependencies (flask, flask_sqlalchemy)

Run app.py

Access the app at http://127.0.0.1:5000 or https://bulkbuy-group-purchase-app.onrender.com

Sign up as a Supplier or Vendor and start managing or buying products!
