# Client-side LeetCode Clone

This is the client-side application of the LeetCode-like platform built using React and TypeScript. The application allows users to log in, view coding problems, and submit their solutions.

## Project Structure

- **public/index.html**: The main HTML file that serves as the entry point for the React application.
- **src/components**: Contains reusable components for the application.
  - **CodeEditor.tsx**: A component for writing and testing code.
  - **Navbar.tsx**: A navigation bar for the application.
  - **ProblemDescription.tsx**: Displays the details of a coding problem.
- **src/pages**: Contains the main pages of the application.
  - **Home.tsx**: The landing page of the application.
  - **Login.tsx**: Handles user authentication.
  - **ProblemPage.tsx**: Displays a specific coding problem and its functionalities.
- **src/api/index.ts**: Functions for making API calls to the backend, including user login and problem submission.
- **src/App.tsx**: The main application component that sets up routing and renders necessary components.
- **src/index.tsx**: The entry point for the React application.

## Getting Started

1. **Install Dependencies**: Run `npm install` in the client directory to install the required packages.
2. **Start the Application**: Use `npm start` to run the application in development mode. Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

## Features

- User authentication (login).
- View and solve coding problems.
- Submit solutions and receive feedback.

## Contributing

Feel free to submit issues or pull requests for improvements and new features.