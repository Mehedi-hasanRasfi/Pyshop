# 🛒 PyShop — CLI Inventory & Shopping System

A Python-based command-line shop management system with OOP design, persistent JSON storage, and invoice generation.

## Features
- Dual interface for Owner 👑 and Customer 👨
- Add & update product inventory with SKU system
- Cart management with real-time stock validation
- Checkout with auto-generated .txt invoices
- Persistent data storage using JSON file
- Graceful error handling throughout

## How to Run
```bash
python pyshop.py
```

## Concepts Used
- OOP (Classes: Product, Cart, InventoryManager)
- File Handling – JSON read/write & TXT invoice generation
- Exception Handling
- Modules: json, os, datetime, sys
