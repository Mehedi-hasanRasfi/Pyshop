import json
import os
import datetime
import sys

# Define the inventory file path for persistence
INVENTORY_FILE = 'pyshop_inventory.json'

class Product:
    """Represents a single product in the inventory. (OOP Constraint)"""
    def __init__(self, sku, name, price, stock):
        self.sku = sku
        self.name = name
        self.price = price
        self.stock = stock

    def to_dict(self):
        """Helper to convert object to dictionary for JSON serialization."""
        return {"name": self.name, "price": self.price, "stock": self.stock}

    @staticmethod
    def from_dict(sku, data):
        """Helper to create object from dictionary during loading."""
        return Product(sku, data['name'], data['price'], data['stock'])

class Cart:
    """Manages a customer's shopping cart items and checkout logic. (OOP Constraint)"""
    def __init__(self):
        self.items = {}

    def add_item(self, sku, quantity, inventory_manager):
        try:
            product = inventory_manager.get_product(sku)
            if quantity > product.stock:
                raise ValueError(f"Not enough stock for '{product.name}'. Available: {product.stock}")
            if sku in self.items:
                self.items[sku] += quantity
            else:
                self.items[sku] = quantity
            print(f"✅ Added {quantity} of '{product.name}' to cart.")
        except (KeyError, ValueError) as e:
            print(f"❌ Error adding item: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def checkout(self, inventory_manager):
        if not self.items:
            print("Your cart is empty.")
            return False

        print("\n🛒 Processing Checkout...")
        items_to_invoice = []
        total_cost = 0.0

        try:
            for sku, quantity_ordered in self.items.items():
                product = inventory_manager.get_product(sku)
                if quantity_ordered > product.stock:
                    raise ValueError(f"Out of Stock: '{product.name}'. Only {product.stock} available.")

            for sku, quantity_ordered in self.items.items():
                product = inventory_manager.get_product(sku)
                subtotal = quantity_ordered * product.price
                total_cost += subtotal
                items_to_invoice.append((product.name, quantity_ordered, product.price, subtotal))
                inventory_manager.reduce_stock(sku, quantity_ordered)

            self._generate_invoice(items_to_invoice, total_cost)
            inventory_manager.save_inventory()
            print("✅ Checkout successful. Invoice generated and stock updated.")
            self.items = {}
            return True

        except (KeyError, ValueError) as e:
            print(f"\n❌ Checkout failed due to inventory issue: {e}")
            print("Cart remains unchanged. Please adjust your order.")
            return False

    def _generate_invoice(self, items, total_cost):
        """Generates a unique TXT receipt file (File Writing Constraint)."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        invoice_id = f"Invoice_ID_{timestamp}"
        file_name = f"{invoice_id}.txt"

        with open(file_name, 'w') as f:
            f.write(f"--- PyShop Receipt: {invoice_id} ---\n")
            f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"{'Item':<20} | {'Qty':<5} | {'Price':<10} | {'Total':<10}\n")
            f.write("-" * 52 + "\n")
            for name, qty, price, subtotal in items:
                f.write(f"{name:<20} | {qty:<5} | ${price:<9.2f} | ${subtotal:<9.2f}\n")
            f.write("-" * 52 + "\n")
            f.write(f"{'TOTAL COST':<38} | ${total_cost:<9.2f}\n")
            f.write("-" * 52 + "\n")

        print(f"📄 Receipt saved to {file_name}")

    def view_cart(self, inventory_manager):
        if not self.items:
            print("Your cart is empty.")
            return
        print("\n--- Your Shopping Cart ---")
        total_price = 0.0
        for sku, quantity in self.items.items():
            try:
                product = inventory_manager.get_product(sku)
                subtotal = quantity * product.price
                total_price += subtotal
                print(f"{product.name:<20} (SKU: {sku}) x {quantity:<3} = ${subtotal:.2f}")
            except KeyError:
                print(f"Unknown item (SKU: {sku}) x {quantity} (Error: Item missing from shop)")
        print("-" * 30)
        print(f"Total Price: ${total_price:.2f}")
        print("-" * 30)

class InventoryManager:
    """Manages loading, saving, and accessing the master inventory."""
    def __init__(self, file_path):
        self.file_path = file_path
        self.inventory = {}
        self.load_inventory()

    def load_inventory(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    for sku, details in data.items():
                        self.inventory[sku] = Product.from_dict(sku, details)
                print("Inventory loaded successfully.")
            except json.JSONDecodeError:
                print("Error reading inventory file. Starting with empty inventory.")
        else:
            print("No saved data file found. Creating default inventory.")
            self.inventory = {
                "SKU001": Product("SKU001", "Laptop", 999.99, 100),
                "SKU002": Product("SKU002", "Mouse", 19.99, 100),
                "SKU003": Product("SKU003", "Keyboard", 45.50, 100),
                'SKU004': Product('SKU004', 'Charger', 12.12, 100),
                'SKU005': Product('SKU005', 'Monitor', 78.12, 100),
                'SKU006': Product('SKU006', 'Power Supply', 45.12, 100),
                'SKU007': Product('SKU007', 'RAM', 112.12, 100),
                'SKU008': Product('SKU008', 'SSD', 68.35, 100),
                'SKU009': Product('SKU009', 'CPU', 234.22, 100),
                'SKU010': Product('SKU010', 'Mic', 12.12, 100),
            }
            self.save_inventory()

    def save_inventory(self):
        data_to_save = {sku: product.to_dict() for sku, product in self.inventory.items()}
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data_to_save, f, indent=4)
        except IOError as e:
            print(f"Error saving inventory to file: {e}")

    def get_product(self, sku):
        if sku not in self.inventory:
            raise KeyError(f"Product SKU {sku} not found.")
        return self.inventory[sku]

    def reduce_stock(self, sku, quantity):
        if sku in self.inventory:
            self.inventory[sku].stock -= quantity
            if self.inventory[sku].stock < 0:
                self.inventory[sku].stock = 0

    def display_inventory(self):
        print("\n--- PyShop Inventory ---")
        print(f"{'SKU':<10} | {'Name':<20} | {'Price':<10} | {'Stock':<5}")
        print("-" * 52)
        for product in self.inventory.values():
            print(f"{product.sku:<10} | {product.name:<20} | ${product.price:<9.2f} | {product.stock:<5}")
        print("-" * 52)

    def add_or_update_product(self):
        sku = input("Enter SKU to add/update: ").upper()
        name = input(f"Enter product name for {sku}: ")
        price_str = input("Enter price: ")
        stock_str = input("Enter stock quantity: ")
        try:
            price = float(price_str)
            stock = int(stock_str)
            if price <= 0 or stock < 0:
                raise ValueError("Price must be positive, stock non-negative.")
            self.inventory[sku] = Product(sku, name, price, stock)
            self.save_inventory()
            print(f"✅ Updated inventory for {sku}.")
        except ValueError as e:
            print(f"❌ Invalid input: {e}")


def customer_interface(inv_manager):
    cart = Cart()
    while True:
        print("\n🛍️ Welcome Customer 🛍️")
        print("1.Shop\n2.View Cart\n3.Checkout\n4.Quit Shopping")
        choice = input("Enter your choice: ").lower()
        if choice == '4':
            if cart.items:
                print("Don't forget your items in your cart!")
            break
        elif choice == '1':
            inv_manager.display_inventory()
            sku = input("Enter SKU to add to cart: ").upper()
            qty_str = input("Enter quantity: ")
            try:
                qty = int(qty_str)
                if qty < 1: raise ValueError("Quantity must be positive.")
                cart.add_item(sku, qty, inv_manager)
            except ValueError as e:
                print(f"Invalid quantity input: {e}")
        elif choice == '2':
            cart.view_cart(inv_manager)
        elif choice == '3':
            if cart.checkout(inv_manager):
                cart = Cart()

def owner_interface(inv_manager):
    while True:
        print("\n🔑 Welcome Owner 🔑")
        print("1.Display Inventory\n2.Add/Update Stock\n3.Quit")
        choice = input("Enter your choice: ").lower()
        if choice == '3':
            inv_manager.save_inventory()
            break
        elif choice == '1':
            inv_manager.display_inventory()
        elif choice == '2':
            inv_manager.add_or_update_product()


def main():
    """Main application loop to select user type."""
    inventory_manager = InventoryManager(INVENTORY_FILE)
    while True:
        print("\n🏠 PyShop Main Menu 🏠")
        print("Select User Type:\n1.Owner👑\n2.Customer👨\n3.Exit👋")
        user_type = input("Enter your choice: ").lower()
        if user_type == '1':
            owner_interface(inventory_manager)
        elif user_type == '2':
            customer_interface(inventory_manager)
        elif user_type == '3':
            print("Exiting system. Goodbye!")
            sys.exit()
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
