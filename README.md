# LeetCode Clone

This project is a full-stack application that mimics the functionalities of LeetCode, allowing users to log in, view coding problems, and submit their solutions. The application is built using React with TypeScript for the frontend and Python with Flask for the backend.

## Project Structure

The project is divided into two main parts: the client and the server.

### Client

The client is a React application structured as follows:

- **public/index.html**: The main HTML file that serves as the entry point for the React application.
- **src/components**: Contains reusable components for the application.
  - **CodeEditor.tsx**: A component for writing and testing code.
  - **Navbar.tsx**: A navigation bar for the application.
  - **ProblemDescription.tsx**: Displays the details of a coding problem.
- **src/pages**: Contains the main pages of the application.
  - **Home.tsx**: The landing page of the application.
  - **Login.tsx**: Handles user authentication.
  - **ProblemPage.tsx**: Displays a specific coding problem and its functionalities.
- **src/api/index.ts**: Contains functions for making API calls to the backend.
- **src/App.tsx**: The main application component that sets up routing.
- **src/index.tsx**: The entry point for the React application.

### Server

The server is a Flask application structured as follows:

- **app/__init__.py**: Initializes the Flask application and sets up the application context.
- **app/models**: Contains the data models for the application.
  - **user.py**: Defines the user schema and methods for user-related operations.
  - **problem.py**: Defines the problem schema and methods for problem-related operations.
  - **submission.py**: Defines the submission schema and methods for handling code submissions.
- **app/routes**: Contains the routes for the application.
  - **auth.py**: Routes for user authentication.
  - **problems.py**: Routes for handling problem-related requests.
- **app/services**: Contains services for executing code submissions.
  - **code_execution.py**: Functions for executing code submissions and returning results.
- **app/utils/db.py**: Utility functions for database connection and operations.
- **config.py**: Configuration settings for the Flask application.
- **requirements.txt**: Lists the dependencies required for the Python backend.
- **run.py**: The entry point for running the Flask application.

## Features
- **Authentication**: JWT-based Login and Registration.
- **Problems**: 
    - List all problems.
    - View problem details with examples.
    - Problems are loaded from local JSON files in `server/problems_data/`.
- **Code Execution**: Submit Python code and see the output (mock execution).

## Adding Problems
To add a new problem, create a JSON file in `server/problems_data/` with the following structure:
```json
{
    "title": "Problem Title",
    "description": "Problem Description",
    "difficulty": "Easy",
    "tags": "Tag1, Tag2",
    "test_cases": [
        {
            "input": "arg1, arg2",
            "output": "result"
        }
    ]
}
```
Restart the server to load the new problem.

## Getting Started

### Prerequisites

- Node.js and npm for the client-side application.
- Python and pip for the server-side application.

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd leetcode-clone
   ```

2. Set up the client:
   ```
   cd client
   npm install
   ```

3. Set up the server:
   ```
   cd server
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the server:
   ```
   cd server
   python run.py
   ```

2. Start the client:
   ```
   cd client
   npm start
   ```

The application should now be running on `http://localhost:3000` for the client and `http://localhost:5000` for the server.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.