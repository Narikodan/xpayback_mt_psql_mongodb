# User Registration and Profile Picture Storage with FastAPI, PostgreSQL, and MongoDB

This is a FastAPI application that allows users to register with PostgreSQL for user details (First Name, Email, Password, Phone) and MongoDB for profile pictures. It also provides a GET method to retrieve user details, including the user's profile picture.

## Prerequisites

Before you can run this application, you need to set up your own PostgreSQL and MongoDB databases. Make sure you have the following prerequisites installed:

- Python 3.7+
- PostgreSQL
- MongoDB
- pip (Python package manager)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/fastapi-registration.git
   cd fastapi-registration

    1. Install the required Python packages using pip:

            pip install -r requirements.txt

    2. Set up your database configurations in the application:

    PostgreSQL: Modify the DATABASE_URL in the main.py file to include your PostgreSQL database credentials.

            DATABASE_URL = "postgresql://yourusername:yourpassword@localhost/yourdatabase"

            MongoDB: Ensure that you have a running MongoDB instance on mongodb://localhost:27017.


## Running the Application

--Start the FastAPI application:

    uvicorn main:app --reload

The application will be running on http://127.0.0.1:8000. You can access the API at this address.
