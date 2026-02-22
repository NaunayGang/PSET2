"""
Banking System Frontend using Streamlit.

Provides UI for creating customers and accounts with proper validation and error handling.
"""

import streamlit as st
import requests
from enum import Enum
import os

# ==================== Configuration ====================

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
ENDPOINTS = {
    "create_customer": f"{API_BASE_URL}/customers",
    "create_account": f"{API_BASE_URL}/accounts",
    "get_account": f"{API_BASE_URL}/accounts",
    "get_transactions": f"{API_BASE_URL}/accounts",
    "deposit": f"{API_BASE_URL}/transactions/deposit",
    "withdraw": f"{API_BASE_URL}/transactions/withdraw",
    "transfer": f"{API_BASE_URL}/transactions/transfer",
}


class Currency(str, Enum):
    """Available currencies."""
    USD = "USD"
    EUR = "EUR"
    MXN = "MXN"


# ==================== Page Configuration ====================

st.set_page_config(
    page_title="Banking System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏦 Banking System")
st.markdown("---")


# ==================== Utility Functions ====================

def is_valid_email(email: str) -> bool:
    """Basic email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_customer_form(name: str, email: str) -> tuple[bool, str]:
    """Validate customer form inputs."""
    if not name.strip():
        return False, "❌ Name is required"
    
    if len(name.strip()) > 255:
        return False, "❌ Name must be 255 characters or less"
    
    if not email.strip():
        return False, "❌ Email is required"
    
    if not is_valid_email(email):
        return False, "❌ Please enter a valid email address"
    
    return True, ""


def validate_account_form(customer_id: str, currency: str) -> tuple[bool, str]:
    """Validate account form inputs."""
    if not customer_id.strip():
        return False, "❌ Customer ID is required"
    
    # Try to parse as UUID
    try:
        from uuid import UUID
        UUID(customer_id.strip())
    except ValueError:
        return False, "❌ Invalid customer ID format (must be a valid UUID)"
    
    if not currency:
        return False, "❌ Currency is required"
    
    return True, ""


def validate_deposit_form(account_id: str, amount: float) -> tuple[bool, str]:
    """Validate deposit form inputs."""
    if not account_id.strip():
        return False, "❌ Account ID is required"
    
    try:
        from uuid import UUID
        UUID(account_id.strip())
    except ValueError:
        return False, "❌ Invalid account ID format (must be a valid UUID)"
    
    if amount is None or amount == 0:
        return False, "❌ Amount is required"
    
    if amount <= 0:
        return False, "❌ Amount must be greater than 0"
    
    return True, ""


def validate_withdraw_form(account_id: str, amount: float) -> tuple[bool, str]:
    """Validate withdraw form inputs."""
    if not account_id.strip():
        return False, "❌ Account ID is required"
    
    try:
        from uuid import UUID
        UUID(account_id.strip())
    except ValueError:
        return False, "❌ Invalid account ID format (must be a valid UUID)"
    
    if amount is None or amount == 0:
        return False, "❌ Amount is required"
    
    if amount <= 0:
        return False, "❌ Amount must be greater than 0"
    
    return True, ""


def validate_transfer_form(from_id: str, to_id: str, amount: float) -> tuple[bool, str]:
    """Validate transfer form inputs."""
    if not from_id.strip():
        return False, "❌ From Account ID is required"
    
    if not to_id.strip():
        return False, "❌ To Account ID is required"
    
    try:
        from uuid import UUID
        UUID(from_id.strip())
    except ValueError:
        return False, "❌ Invalid From Account ID format (must be a valid UUID)"
    
    try:
        from uuid import UUID
        UUID(to_id.strip())
    except ValueError:
        return False, "❌ Invalid To Account ID format (must be a valid UUID)"
    
    if from_id.strip() == to_id.strip():
        return False, "❌ From and To accounts must be different"
    
    if amount is None or amount == 0:
        return False, "❌ Amount is required"
    
    if amount <= 0:
        return False, "❌ Amount must be greater than 0"
    
    return True, ""


# ==================== API Functions ====================

def create_customer_api(name: str, email: str) -> tuple[bool, dict]:
    """Call POST /customers endpoint."""
    try:
        response = requests.post(
            ENDPOINTS["create_customer"],
            json={"name": name, "email": email},
            timeout=10,
        )
        
        if response.status_code == 201:
            return True, response.json()
        else:
            error_msg = response.json().get("detail", "Unknown error")
            return False, {"error": error_msg}
    
    except requests.exceptions.ConnectionError:
        return False, {"error": f"Cannot connect to API at {API_BASE_URL}. Is the backend running?"}
    except requests.exceptions.Timeout:
        return False, {"error": "Request timeout. Please try again."}
    except Exception as e:
        return False, {"error": str(e)}


def create_account_api(customer_id: str, currency: str) -> tuple[bool, dict]:
    """Call POST /accounts endpoint."""
    try:
        response = requests.post(
            ENDPOINTS["create_account"],
            json={"customer_id": customer_id, "currency": currency},
            timeout=10,
        )
        
        if response.status_code == 201:
            return True, response.json()
        else:
            error_msg = response.json().get("detail", "Unknown error")
            return False, {"error": error_msg}
    
    except requests.exceptions.ConnectionError:
        return False, {"error": f"Cannot connect to API at {API_BASE_URL}. Is the backend running?"}
    except requests.exceptions.Timeout:
        return False, {"error": "Request timeout. Please try again."}
    except Exception as e:
        return False, {"error": str(e)}


def deposit_api(account_id: str, amount: float, description: str = "") -> tuple[bool, dict]:
    """Call POST /transactions/deposit endpoint."""
    try:
        response = requests.post(
            ENDPOINTS["deposit"],
            json={
                "account_id": account_id,
                "amount": str(amount),
                "description": description if description.strip() else None,
            },
            timeout=10,
        )
        
        if response.status_code == 201:
            return True, response.json()
        else:
            error_msg = response.json().get("detail", "Unknown error")
            return False, {"error": error_msg}
    
    except requests.exceptions.ConnectionError:
        return False, {"error": f"Cannot connect to API at {API_BASE_URL}. Is the backend running?"}
    except requests.exceptions.Timeout:
        return False, {"error": "Request timeout. Please try again."}
    except Exception as e:
        return False, {"error": str(e)}


def withdraw_api(account_id: str, amount: float, description: str = "") -> tuple[bool, dict]:
    """Call POST /transactions/withdraw endpoint."""
    try:
        response = requests.post(
            ENDPOINTS["withdraw"],
            json={
                "account_id": account_id,
                "amount": str(amount),
                "description": description if description.strip() else None,
            },
            timeout=10,
        )
        
        if response.status_code == 201:
            return True, response.json()
        else:
            error_msg = response.json().get("detail", "Unknown error")
            return False, {"error": error_msg}
    
    except requests.exceptions.ConnectionError:
        return False, {"error": f"Cannot connect to API at {API_BASE_URL}. Is the backend running?"}
    except requests.exceptions.Timeout:
        return False, {"error": "Request timeout. Please try again."}
    except Exception as e:
        return False, {"error": str(e)}


def transfer_api(from_account_id: str, to_account_id: str, amount: float, description: str = "") -> tuple[bool, dict]:
    """Call POST /transactions/transfer endpoint."""
    try:
        response = requests.post(
            ENDPOINTS["transfer"],
            json={
                "from_account_id": from_account_id,
                "to_account_id": to_account_id,
                "amount": str(amount),
                "description": description if description.strip() else None,
            },
            timeout=10,
        )
        
        if response.status_code == 201:
            return True, response.json()
        else:
            error_msg = response.json().get("detail", "Unknown error")
            return False, {"error": error_msg}
    
    except requests.exceptions.ConnectionError:
        return False, {"error": f"Cannot connect to API at {API_BASE_URL}. Is the backend running?"}
    except requests.exceptions.Timeout:
        return False, {"error": "Request timeout. Please try again."}
    except Exception as e:
        return False, {"error": str(e)}


def get_account_api(account_id: str) -> tuple[bool, dict]:
    """Call GET /accounts/{account_id} endpoint."""
    try:
        response = requests.get(
            f"{ENDPOINTS['get_account']}/{account_id}",
            timeout=10,
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            error_msg = response.json().get("detail", "Unknown error")
            return False, {"error": error_msg}
    
    except requests.exceptions.ConnectionError:
        return False, {"error": f"Cannot connect to API at {API_BASE_URL}. Is the backend running?"}
    except requests.exceptions.Timeout:
        return False, {"error": "Request timeout. Please try again."}
    except Exception as e:
        return False, {"error": str(e)}


def get_transactions_api(account_id: str, limit: int = 100, offset: int = 0) -> tuple[bool, list]:
    """Call GET /accounts/{account_id}/transactions endpoint."""
    try:
        response = requests.get(
            f"{ENDPOINTS['get_transactions']}/{account_id}/transactions",
            params={"limit": limit, "offset": offset},
            timeout=10,
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            error_msg = response.json().get("detail", "Unknown error")
            return False, {"error": error_msg}
    
    except requests.exceptions.ConnectionError:
        return False, {"error": f"Cannot connect to API at {API_BASE_URL}. Is the backend running?"}
    except requests.exceptions.Timeout:
        return False, {"error": "Request timeout. Please try again."}
    except Exception as e:
        return False, {"error": str(e)}


# ==================== UI Components ====================

def render_create_customer_form():
    """Render the create customer form."""
    st.subheader("👤 Create Customer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input(
            "Customer Name",
            placeholder="Enter full name",
            max_chars=255,
            help="Must be between 1 and 255 characters",
        )
    
    with col2:
        email = st.text_input(
            "Email Address",
            placeholder="Enter email address",
            help="Must be a valid email format",
        )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        submit = st.button("Create Customer", key="create_customer_btn", type="primary")
    
    if submit:
        # Validate
        is_valid, error_msg = validate_customer_form(name, email)
        
        if not is_valid:
            st.error(error_msg)
            return
        
        # Call API
        with st.spinner("Creating customer..."):
            success, response = create_customer_api(name.strip(), email.strip())
        
        if success:
            st.success("✅ Customer created successfully!")
            st.json(response)
            st.write(f"**Customer ID:** `{response['id']}`")
            st.write(f"**Name:** {response['name']}")
            st.write(f"**Email:** {response['email']}")
            st.write(f"**Status:** {response['status']}")
            st.write(f"**Created:** {response['created_at']}")
        else:
            st.error(f"Failed to create customer: {response.get('error', 'Unknown error')}")


def render_create_account_form():
    """Render the create account form."""
    st.subheader("💳 Create Account")
    
    col1, col2 = st.columns(2)
    
    with col1:
        customer_id = st.text_input(
            "Customer ID",
            placeholder="Paste the customer UUID",
            help="UUID of an existing customer",
        )
    
    with col2:
        currency = st.selectbox(
            "Currency",
            options=[c.value for c in Currency],
            index=0,
            help="Choose account currency",
        )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        submit = st.button("Create Account", key="create_account_btn", type="primary")
    
    if submit:
        # Validate
        is_valid, error_msg = validate_account_form(customer_id, currency)
        
        if not is_valid:
            st.error(error_msg)
            return
        
        # Call API
        with st.spinner("Creating account..."):
            success, response = create_account_api(customer_id.strip(), currency)
        
        if success:
            st.success("✅ Account created successfully!")
            st.json(response)
            st.write(f"**Account ID:** `{response['id']}`")
            st.write(f"**Customer ID:** `{response['customer_id']}`")
            st.write(f"**Currency:** {response['currency']}")
            st.write(f"**Balance:** {response['balance']} {response['currency']}")
            st.write(f"**Status:** {response['status']}")
            st.write(f"**Created:** {response['created_at']}")
        else:
            st.error(f"Failed to create account: {response.get('error', 'Unknown error')}")


def render_deposit_form():
    """Render the deposit form."""
    st.subheader("💰 Deposit")
    
    col1, col2 = st.columns(2)
    
    with col1:
        account_id = st.text_input(
            "Account ID",
            placeholder="Paste the account UUID",
            help="UUID of the account to deposit to",
            key="deposit_account_id",
        )
    
    with col2:
        amount = st.number_input(
            "Amount",
            min_value=0.01,
            value=100.00,
            step=0.01,
            format="%.2f",
            help="Amount to deposit (must be > 0)",
        )
    
    description = st.text_area(
        "Description (optional)",
        placeholder="e.g., Salary deposit, Gift, etc.",
        max_chars=500,
        height=80,
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        submit = st.button("Deposit", key="deposit_btn", type="primary")
    
    if submit:
        # Validate
        is_valid, error_msg = validate_deposit_form(account_id, amount)
        
        if not is_valid:
            st.error(error_msg)
            return
        
        # Call API
        with st.spinner("Processing deposit..."):
            success, response = deposit_api(account_id.strip(), amount, description)
        
        if success:
            status = response.get("status", "PENDING")
            if status == "COMPLETED":
                st.success("✅ Deposit completed successfully!")
            else:
                st.warning(f"⚠️  Deposit status: {status}")
            
            st.write(f"**Transaction ID:** `{response['id']}`")
            st.write(f"**Account ID:** `{response['from_account_id']}`")
            st.write(f"**Amount:** {response['amount']} {response['currency']}")
            st.write(f"**Fee:** {response['fee']} {response['currency']}")
            st.write(f"**Status:** {response['status']}")
            
            if response.get("rejection_reason"):
                st.error(f"**Rejection Reason:** {response['rejection_reason']}")
            
            st.write(f"**Created:** {response['created_at']}")
        else:
            error_detail = response.get('error', 'Unknown error')
            st.error(f"❌ Deposit failed: {error_detail}")


def render_withdraw_form():
    """Render the withdraw form."""
    st.subheader("💸 Withdraw")
    
    col1, col2 = st.columns(2)
    
    with col1:
        account_id = st.text_input(
            "Account ID",
            placeholder="Paste the account UUID",
            help="UUID of the account to withdraw from",
            key="withdraw_account_id",
        )
    
    with col2:
        amount = st.number_input(
            "Amount",
            min_value=0.01,
            value=50.00,
            step=0.01,
            format="%.2f",
            help="Amount to withdraw (must be > 0)",
            key="withdraw_amount",
        )
    
    description = st.text_area(
        "Description (optional)",
        placeholder="e.g., ATM withdrawal, Bill payment, etc.",
        max_chars=500,
        height=80,
        key="withdraw_description",
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        submit = st.button("Withdraw", key="withdraw_btn", type="primary")
    
    if submit:
        # Validate
        is_valid, error_msg = validate_withdraw_form(account_id, amount)
        
        if not is_valid:
            st.error(error_msg)
            return
        
        # Call API
        with st.spinner("Processing withdrawal..."):
            success, response = withdraw_api(account_id.strip(), amount, description)
        
        if success:
            status = response.get("status", "PENDING")
            if status == "COMPLETED":
                st.success("✅ Withdrawal completed successfully!")
            else:
                st.warning(f"⚠️  Withdrawal status: {status}")
            
            st.write(f"**Transaction ID:** `{response['id']}`")
            st.write(f"**Account ID:** `{response['from_account_id']}`")
            st.write(f"**Amount:** {response['amount']} {response['currency']}")
            st.write(f"**Fee:** {response['fee']} {response['currency']}")
            st.write(f"**Status:** {response['status']}")
            
            if response.get("rejection_reason"):
                st.error(f"**Rejection Reason:** {response['rejection_reason']}")
            
            st.write(f"**Created:** {response['created_at']}")
        else:
            error_detail = response.get('error', 'Unknown error')
            st.error(f"❌ Withdrawal failed: {error_detail}")


def render_transfer_form():
    """Render the transfer form."""
    st.subheader("🔄 Transfer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        from_account_id = st.text_input(
            "From Account ID",
            placeholder="Paste the source account UUID",
            help="UUID of the account to transfer from",
            key="transfer_from_account_id",
        )
    
    with col2:
        to_account_id = st.text_input(
            "To Account ID",
            placeholder="Paste the destination account UUID",
            help="UUID of the account to transfer to",
            key="transfer_to_account_id",
        )
    
    amount = st.number_input(
        "Amount",
        min_value=0.01,
        value=100.00,
        step=0.01,
        format="%.2f",
        help="Amount to transfer (must be > 0)",
        key="transfer_amount",
    )
    
    description = st.text_area(
        "Description (optional)",
        placeholder="e.g., Payment for invoice #123, etc.",
        max_chars=500,
        height=80,
        key="transfer_description",
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        submit = st.button("Transfer", key="transfer_btn", type="primary")
    
    if submit:
        # Validate
        is_valid, error_msg = validate_transfer_form(from_account_id, to_account_id, amount)
        
        if not is_valid:
            st.error(error_msg)
            return
        
        # Call API
        with st.spinner("Processing transfer..."):
            success, response = transfer_api(
                from_account_id.strip(),
                to_account_id.strip(),
                amount,
                description,
            )
        
        if success:
            status = response.get("status", "PENDING")
            if status == "COMPLETED":
                st.success("✅ Transfer completed successfully!")
            else:
                st.warning(f"⚠️  Transfer status: {status}")
            
            st.write(f"**Transaction ID:** `{response['id']}`")
            st.write(f"**From Account:** `{response['from_account_id']}`")
            st.write(f"**To Account:** `{response['to_account_id']}`")
            st.write(f"**Amount:** {response['amount']} {response['currency']}")
            st.write(f"**Fee:** {response['fee']} {response['currency']}")
            st.write(f"**Status:** {response['status']}")
            
            if response.get("rejection_reason"):
                st.error(f"**Rejection Reason:** {response['rejection_reason']}")
            
            st.write(f"**Created:** {response['created_at']}")
        else:
            error_detail = response.get('error', 'Unknown error')
            st.error(f"❌ Transfer failed: {error_detail}")


def render_account_detail():
    """Render the account detail view."""
    st.subheader("📊 Account Details")
    
    account_id = st.text_input(
        "Account ID",
        placeholder="Enter the account UUID",
        help="UUID of the account to view",
        key="detail_account_id",
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        load_btn = st.button("Load Account", key="load_account_btn", type="primary")
    
    if load_btn:
        if not account_id.strip():
            st.error("❌ Account ID is required")
            return
        
        try:
            from uuid import UUID
            UUID(account_id.strip())
        except ValueError:
            st.error("❌ Invalid account ID format (must be a valid UUID)")
            return
        
        # Load account details and transactions
        with st.spinner("Loading account details..."):
            success, account_data = get_account_api(account_id.strip())
        
        if not success:
            st.error(f"Failed to load account: {account_data.get('error', 'Unknown error')}")
            return
        
        # Display account details
        st.success("✅ Account found!")
        
        # Account info in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Balance", f"{account_data['balance']} {account_data['currency']}")
        with col2:
            st.metric("Currency", account_data['currency'])
        with col3:
            st.metric("Status", account_data['status'])
        with col4:
            st.metric("Created", account_data['created_at'][:10])
        
        # Full account details
        with st.expander("📋 Full Account Details"):
            st.write(f"**Account ID:** `{account_data['id']}`")
            st.write(f"**Customer ID:** `{account_data['customer_id']}`")
            st.write(f"**Currency:** {account_data['currency']}")
            st.write(f"**Balance:** {account_data['balance']}")
            st.write(f"**Status:** {account_data['status']}")
            st.write(f"**Created At:** {account_data['created_at']}")
        
        # Load transactions
        st.markdown("---")
        st.subheader("📜 Transaction History")
        
        with st.spinner("Loading transactions..."):
            txn_success, txn_data = get_transactions_api(account_id.strip())
        
        if not txn_success:
            st.error(f"Failed to load transactions: {txn_data.get('error', 'Unknown error')}")
        elif not txn_data:
            st.info("📭 No transactions found for this account.")
        else:
            # Display transactions in a table
            st.write(f"**Total transactions shown:** {len(txn_data)}")
            
            # Format data for display
            transaction_display = []
            for txn in txn_data:
                transaction_display.append({
                    "ID": str(txn['id'])[:8] + "...",
                    "Type": txn['type'],
                    "Amount": f"{txn['amount']} {txn['currency']}",
                    "Fee": f"{txn['fee']} {txn['currency']}",
                    "Status": txn['status'],
                    "Description": txn.get('description', '-')[:30] + ("..." if txn.get('description') and len(txn.get('description', '')) > 30 else ""),
                    "Created": txn['created_at'][:19],
                })
            
            st.dataframe(transaction_display, use_container_width=True, hide_index=True)
            
            # Show detailed transaction info in expander
            with st.expander("📝 View Transaction Details"):
                selected_idx = st.selectbox(
                    "Select a transaction to view details:",
                    range(len(txn_data)),
                    format_func=lambda i: f"{txn_data[i]['type']} - {txn_data[i]['amount']} {txn_data[i]['currency']} - {txn_data[i]['created_at'][:10]}"
                )
                
                if selected_idx is not None:
                    selected_txn = txn_data[selected_idx]
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Transaction ID:** `{selected_txn['id']}`")
                        st.write(f"**Type:** {selected_txn['type']}")
                        st.write(f"**Amount:** {selected_txn['amount']} {selected_txn['currency']}")
                        st.write(f"**Fee:** {selected_txn['fee']} {selected_txn['currency']}")
                    
                    with col2:
                        st.write(f"**Status:** {selected_txn['status']}")
                        st.write(f"**Description:** {selected_txn.get('description', 'N/A')}")
                        st.write(f"**Created:** {selected_txn['created_at']}")
                    
                    if selected_txn.get('from_account_id'):
                        st.write(f"**From Account:** `{selected_txn['from_account_id']}`")
                    if selected_txn.get('to_account_id'):
                        st.write(f"**To Account:** `{selected_txn['to_account_id']}`")
                    
                    if selected_txn.get('rejection_reason'):
                        st.error(f"**Rejection Reason:** {selected_txn['rejection_reason']}")
        
        st.markdown("---")


# ==================== Main App ====================

def main():
    """Main app logic."""
    # Sidebar navigation
    page = st.sidebar.radio(
        "Select Action",
        ["Home", "Create Customer", "Create Account", "Account Details", "Deposit", "Withdraw", "Transfer"],
        index=0,
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "This is a banking system frontend built with Streamlit. "
        "Create customers and accounts, manage funds, and track transactions."
    )
    
    # Render selected page
    if page == "Home":
        render_home()
    elif page == "Create Customer":
        render_create_customer_form()
    elif page == "Create Account":
        render_create_account_form()
    elif page == "Account Details":
        render_account_detail()
    elif page == "Deposit":
        render_deposit_form()
    elif page == "Withdraw":
        render_withdraw_form()
    elif page == "Transfer":
        render_transfer_form()


def render_home():
    """Render home page."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
## Welcome to Banking System 🏦
        
This application provides a simple interface to manage banking operations.
        
### Available Features:
- **Create Customer** 👤: Register new customers with name and email
- **Create Account** 💳: Open new accounts for existing customers
- **Account Details** 📊: View account balance and transaction history
- **Deposit** 💰: Deposit funds into an account
- **Withdraw** 💸: Withdraw funds from an account
- **Transfer** 🔄: Transfer funds between accounts
        
### How to Get Started:
1. Use the sidebar to navigate to "Create Customer"
2. Enter customer details and submit
3. Copy the customer ID from the response
4. Navigate to "Create Account" and create an account for the customer
5. Go to "Account Details" to view the account balance and transactions
6. Use "Deposit", "Withdraw", or "Transfer" to manage funds
        """)
    
    with col2:
        st.markdown("""
### API Status
        """)
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ Backend is running")
                api_info = response.json()
                st.json(api_info)
            else:
                st.error("❌ Backend returned an error")
        except requests.exceptions.ConnectionError:
            st.error(f"❌ Cannot connect to backend at {API_BASE_URL}")
        except Exception as e:
            st.error(f"❌ Error checking backend: {str(e)}")


if __name__ == "__main__":
    main()
