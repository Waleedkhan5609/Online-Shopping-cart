
#If admin wants to change his data, he can simply change in the following:
admin_username="admin"
admin_password="admin123"
admin_firstname="Admin"
admin_lastname="User"
admin_address="123 Admin St"


#Importing modules ("abc" and "datetime")
from abc import ABC, abstractmethod
from datetime import datetime


#Represents the products in the store
class Product:
    def __init__(self, id, name, price, description):
        self.id = id
        self.name = name
        self.price = price
        self.description = description

    def __str__(self):
        return f"| {self.id:<3} | {self.name:<17} | {self.price:<10} | {self.description:<36} |"


#An abstract base class for users, requiring the implementation of view_products.
class User(ABC):
    def __init__(self, username, password, first_name, last_name, address):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.address = address

    @abstractmethod
    def view_products(self, products):
        pass

# Inherits from User, allowing customers to manage their shopping cart and view purchase history
class Customer(User):
    def __init__(self, username, password, first_name, last_name, address, cart=None, history=None):
        super().__init__(username, password, first_name, last_name, address)
        self.cart = cart if cart else ShoppingCart()
        self.history = history if history else []

    def view_products(self, products):
        print("-------------------------------------------------------------------------------")
        print("| ID. |    Product Name   | Price (Rs) |              Description             |")
        print("-------------------------------------------------------------------------------")
        for product in products:
            print(product)
        print("-------------------------------------------------------------------------------")

    def add_to_cart(self, product, quantity=1):
        self.cart.add_product(product, quantity)

    def remove_from_cart(self, product, quantity=1):
        self.cart.remove_product(product, quantity)

    def view_cart(self):
        self.cart.view_cart()

    def checkout(self):
        if not self.cart.items:
            print("Your cart is empty! Can't checkout.")
        else:
            total_price = self.cart.calculate_total()
            purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.history.append({"date": purchase_date, "items": self.cart.items.copy(), "total": total_price})
            self.cart.clear_cart()
            print(f"Checked out successfully.\nYour Total Bill: Rs.{total_price}")

    def view_history(self):
        if not self.history:
            print("\"You have no Shopping History!\"\n It will be available after checking out.")
        else:
            for record in self.history:
                print(f"Date: {record['date']}")
                for item in record['items']:
                    print(f"  {record['items'][item]['product'].name}: Rs.{record['items'][item]['product'].price} each x {record['items'][item]['quantity']}")
                print(f"Total: Rs.{record['total']}")
                print("------------------------------------------")

#Manages the products added by the customer and calculates the total price.
class ShoppingCart:
    def __init__(self):
        self.items = {}

    def add_product(self, product, quantity):
        if product.id in self.items:
            self.items[product.id]['quantity'] += quantity
        else:
            self.items[product.id] = {'product': product, 'quantity': quantity}
        print(f"{quantity} {product.name} added to your cart.")

    def remove_product(self, product, quantity):
        if product.id in self.items:
            if self.items[product.id]['quantity'] > quantity:
                if quantity>0:
                    self.items[product.id]['quantity'] -= quantity
                    print(f"{quantity} {product.name} removed from cart.")
                else:
                    print(f"Can't remove \"{quantity}\" {product.name} from your cart!")
            elif self.items[product.id]['quantity'] == quantity:
                del self.items[product.id]
                print(f"{quantity} {product.name} removed from cart.")
            else:
                print(f"Cannot remove {quantity} {product.name} as only {self.items[product.id]['quantity']} is available in the cart.")
        else:
            print("This Product is not in your cart!")

    def view_cart(self):
        if not self.items:
            print("There is nothing in your Cart! Add Some Products.\nTotal: Rs. 0.0")
        else:
            for item in self.items.values():
                product = item['product']
                print(f"--{product.name}: Rs.{product.price} each x quantity: {item['quantity']} ")
            print(f"Total: Rs. {self.calculate_total()}")

    def calculate_total(self):
        return sum(item['product'].price * item['quantity'] for item in self.items.values())

    def clear_cart(self):
        self.items.clear()

# Inherits from User and overrides view_products, allowing admins to manage the product list.
class Admin(User):
    def login(self, username, password):
        return self.username == username and self.password == password

    def view_products(self, products):
        print("-------------------------------------------------------------------------------")
        print("| ID. |    Product Name   | Price (Rs) |              Description             |")
        print("-------------------------------------------------------------------------------")
        for product in products:
            print(product)
        print("-------------------------------------------------------------------------------")

    def add_product(self, products, product):
        products.append(product)
        print(f"Added product: {product.name}")

    def remove_product(self, products, product_id):
        products[:] = [product for product in products if product.id != product_id]
        print(f"Removed product with ID: {product_id}")

#Custom exception for handling shopping cart errors.
class ShoppingCartException(Exception):
    pass

#This class loads and saves products and accounts. Also manage creation of account and login.
class AccountManager:
    def __init__(self, products=[], filename="User_data.txt"):
        self.products = products
        self.filename = filename
        self.load_products()
        self.load_accounts()

    def save_products(self):
        try:
            with open('product_data.txt', 'w') as f:
                pdts = [[item.id, item.name, item.price, item.description] for item in self.products]
                f.write(str(pdts))
        except IOError as e:
            print(f"Error saving products: {e}")

    def load_products(self):
        try:
            with open('product_data.txt', 'r') as f:
                data = eval(f.read())
                self.products.extend(Product(item[0], item[1], item[2], item[3]) for item in data)
        except FileNotFoundError:
            print("No product data file found.")
        except (IOError, ValueError) as e:
            print(f"Error loading products: {e}")

    def load_accounts(self):
        self.accounts = {}
        try:
            with open(self.filename, 'r') as file:
                for line in file:
                    data = line.strip().split(';')
                    username, password, first_name, last_name, address = data[:5]
                    cart_data = data[5]
                    history_data = data[6:]
                    cart = self.deserialize_cart(cart_data)
                    history = self.deserialize_history(history_data)
                    self.accounts[username] = Customer(username, password, first_name, last_name, address, cart, history)
        except FileNotFoundError:
            print("No account data file found.")
        except Exception as e:
            print(f"Error loading accounts: {e}")

    def save_accounts(self):
        try:
            with open(self.filename, 'w') as file:
                for username, customer in self.accounts.items():
                    cart_data = self.serialize_cart(customer.cart)
                    history_data = self.serialize_history(customer.history)
                    file.write(f"{customer.username};{customer.password};{customer.first_name};{customer.last_name};{customer.address};{cart_data};{history_data}\n")
        except IOError as e:
            print(f"Error saving accounts: {e}")

    def serialize_cart(self, cart):
        return ','.join([f"{item['product'].id}:{item['quantity']}" for item in cart.items.values()])

    def deserialize_cart(self, cart_data):
        cart = ShoppingCart()
        if cart_data:
            items = cart_data.split(',')
            for item in items:
                product_id, quantity = map(int, item.split(':'))
                cart.items[product_id] = {'product': next((p for p in self.products if p.id == product_id), None), 'quantity': quantity}
        return cart

    def serialize_history(self, history):
        serialized_records = []
        for record in history:
            items_str = ",".join([f"{item['product'].id}:{item['quantity']}" for item in record['items'].values()])
            serialized_record = f"{record['date']}|{items_str}|{record['total']}"
            serialized_records.append(serialized_record)
        return ';'.join(serialized_records)

    def deserialize_history(self, history_data):
        history = []
        for record in history_data:
            if not record:
                return history
            else:
                date, items, total = record.split('|')
                items_dict = {}
                for item in items.split(','):
                    product_id, quantity = map(int, item.split(':'))
                    items_dict[product_id] = {'product': next((p for p in self.products if p.id == product_id), None), 'quantity': quantity}
                history.append({'date': date, 'items': items_dict, 'total': float(total)})
        return history

    def create_account(self):
        try:
            username = input("Enter username: ").strip()
            if not username:
                print("Invalid username!, Can't be left empty.")
                return None

            if username in self.accounts:
                print("Account already exists.")
                return None

            password = input("Enter password: ").strip()
            if not password:
                print("Invalid password, Can't be left empty.")
                return None

            first_name = input("Enter first name: ").strip()
            if not first_name:
                print("Invalid first name, Can't be left empty.")
                return None

            last_name = input("Enter last name: ").strip()
            if not last_name:
                print("Invalid last name, Can't be left empty.")
                return None

            address = input("Enter address: ").strip()
            if not address:
                print("Invalid address, Can't be left empty.")
                return None

            customer = Customer(username, password, first_name, last_name, address)
            self.accounts[username] = customer
            self.save_accounts()
            print("Account created successfully.")
            return customer
        except Exception as e:
            print(f"Error creating account: {e}")

    def login(self):
        try:
            username = input("Enter username: ").strip()
            if username not in self.accounts:
                print("Account does not exist.")
                return None

            password = input("Enter password: ").strip()
            if self.accounts[username].password == password:
                print(f"Login successful as {username}.")
                return self.accounts[username]
            else:
                print("Incorrect password.")
                return None
        except Exception as e:
            print(f"Error during login: {e}")
            return None

#Demonstrates the usage of these classes to manage an online shopping cart.
def main():
    account_manager = AccountManager()
    products = account_manager.products
    while True:
        # Welcome statement (Interface)
        print("\n\t\t\t\t----WELCOME----\t\t\t\n\t----Online Electronic Devices Store----\n")
        print("1. Admin Login")
        print("2. Customer Login")
        print("3. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            # Admin login process
            print("\n\t\t----\"Admin Control Panel\"----\t\t\n")
            admin = Admin(admin_username,admin_password ,admin_firstname ,admin_lastname , admin_address)
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()

            if admin.login(username, password):
                print("Login successful as Admin!")
                while True:
                    print("\n\t\t\t----Admin Menu----\t\t\t\n")
                    print("1. View Products")
                    print("2. Add Product")
                    print("3. Remove Product")
                    print("4. Logout")
                    admin_choice = input("Enter your choice: ").strip()
                    products_id = [product.id for product in products]
                    if admin_choice == "1":
                        print(f"\n\t\t\t\t\t\t-----\"Product Catalog\"-----\n")
                        admin.view_products(products)
                    elif admin_choice == "2":
                        print(f"\n\t----\"Add Product In Store\"----\t\n")
                        while True:
                            try:
                                id = int(input("Enter product ID: ").strip())
                                if id in products_id:
                                    print(f"Already a product exists with id: {id}")
                                else:
                                    break
                            except ValueError:
                                print("Invalid ID. Please enter a numeric value.")
                        name = input("Enter product name: ").strip()
                        try:
                            price = float(input("Enter product price: ").strip())
                        except ValueError:
                            print("Invalid price. Please enter a numeric value.")
                            continue
                        description = input("Enter product description: ").strip()
                        new_product = Product(id, name, price, description)
                        admin.add_product(products, new_product)
                        account_manager.save_products()
                    elif admin_choice == "3":
                        print(f"\n\t----\"Remove Product From Store\"----\t\n")
                        while True:
                            try:
                                product_id = int(input("Enter product ID to remove: ").strip())
                                if product_id not in products_id:
                                    print(f"Product does not exist with id: {product_id}")
                                else:
                                    break
                            except ValueError:
                                print("Invalid ID. Please enter a numeric value.")
                        admin.remove_product(products, product_id)
                        account_manager.save_products()
                    elif admin_choice == "4":
                        print("Logging out...")
                        break
                    else:
                        print("Invalid choice. Please try again.")
            else:
                print("Invalid credentials. Access denied.")

        elif choice == "2":
            # Customer login process
            while True:
                print("\n\t\t----\"Customer Control Panel\"----\t\t\n")
                print("1. Sign up\n2. Log in\n3. Main Menu")
                cus_choice = input("Enter choice: ").strip()
                if cus_choice == '1':
                    print("\n\t\t\t----\"Sign up\"----\t\t\t\n")
                    account_manager.create_account()
                elif cus_choice == '2':
                    print("\n\t\t\t----\"Log in\"----\t\t\t\n")
                    customer = account_manager.login()
                    if customer:
                        while True:
                            print("\n\t\t----\"Customer Menu\"----\t\t\t\n")
                            print("1. View Products\n2. Add to Cart\n3. Remove from Cart\n4. View Cart\n5. Checkout\n6. View History\n7. Logout")
                            user_choice = input("Enter choice: ").strip()

                            if user_choice == '1':
                                print("\n\t\t\t\t\t\t-----\"Product Catalog\"-----\t\n")
                                customer.view_products(products)
                            elif user_choice == '2':
                                print(f"\n\t\t\t\t\t----\"Add Product To Cart\"----\t\n")
                                customer.view_products(products)
                                try:
                                    product_id = int(input("Enter product ID to add to cart: ").strip())
                                    quantity = int(input("Enter quantity: ").strip())
                                    product = next((p for p in products if p.id == product_id), None)
                                    if product:
                                        customer.add_to_cart(product, quantity)
                                        account_manager.save_accounts()
                                    else:
                                        print("Product not found.")
                                except ValueError:
                                    print("Invalid input. Please enter numeric values for product ID and quantity.")
                            elif user_choice == '3':
                                print(f"\n\t\t\t\t\t----\"Remove Product From Cart\"----\t\n")
                                customer.view_products(products)
                                try:
                                    product_id = int(input("Enter product ID to remove from cart: ").strip())
                                    quantity = int(input("Enter quantity: ").strip())
                                    product = next((p for p in products if p.id == product_id), None)
                                    if product:
                                        customer.remove_from_cart(product, quantity)
                                        account_manager.save_accounts()
                                    else:
                                        print("Product not found.")
                                except ValueError:
                                    print("Invalid input. Please enter numeric values for product ID and quantity.")
                            elif user_choice == '4':
                                print(f"\n\t\t\t----\"Your Cart\"----\t\t\t\n")
                                customer.view_cart()
                            elif user_choice == '5':
                                print(f"\n\t\t\t----\"Checkout\"----\t\t\t\n")
                                customer.checkout()
                                account_manager.save_accounts()
                            elif user_choice == '6':
                                print(f"\n\t\t----\"Your Shopping History\"----\t\t\t\n")
                                customer.view_history()
                            elif user_choice == '7':
                                print("Logging out...")
                                break
                            else:
                                print("Invalid choice.")
                elif cus_choice == '3':
                    break
                else:
                    print("Invalid choice.")
        elif choice == "3":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()