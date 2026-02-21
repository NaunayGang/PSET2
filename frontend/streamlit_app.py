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


# ==================== Main App ====================

def main():
    """Main app logic."""
    # Sidebar navigation
    page = st.sidebar.radio(
        "Select Action",
        ["Home", "Create Customer", "Create Account"],
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
        
### How to Get Started:
1. Use the sidebar to navigate to "Create Customer"
2. Enter customer details and submit
3. Copy the customer ID from the response
4. Navigate to "Create Account" and create an account for the customer
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
