# Proposal: Refactor to Flask/React Application

This proposal outlines the transition of the Suno Prompter application from a Streamlit-based architecture to a modern web application with a Flask backend and a React/Vite frontend. This change also includes containerizing the application for deployment to Azure.

## 1. Why

The existing Streamlit application is well-suited for rapid prototyping and data-centric applications, but it has limitations for building a robust, scalable, and feature-rich user interface. A separate frontend and backend architecture will provide:

- **Improved User Experience:** A React frontend allows for a more interactive and polished user interface.
- **Scalability:** A stateless Flask API backend is easier to scale independently from the frontend.
- **Maintainability:** Decoupling the frontend and backend clarifies the separation of concerns, making the codebase easier to manage and extend.
- **Simplified Deployment:** A single container deployment to Azure simplifies the release process and environment management.

This change deprecates the `uvx` distribution method in favor of a container-based approach.

## 2. What Changes

This is a significant architectural refactor that will involve the following:

- **Backend:**
    - Replace the Streamlit application with a Flask-based REST API.
    - The API will expose endpoints for the existing functionality (e.g., generating prompts, interacting with agents).
- **Frontend:**
    - Create a new React/Vite frontend application.
    - The frontend will provide the user interface for interacting with the Flask API.
- **Containerization:**
    - Create a `Dockerfile` to build a single container image containing both the Flask backend and the static frontend assets.
- **Deployment:**
    - Provide documentation and scripts for deploying the container to Azure Container Apps (or a similar service).

## 3. Out of Scope

- **Major Feature Changes:** This refactor is focused on the technology stack and architecture. No new user-facing features will be added.
- **Database Integration:** The application will continue to operate without a database for now.
- **Authentication/Authorization:** No user management or security features will be added in this phase.
- **CI/CD Automation:** While the application will be containerized, setting up a full CI/CD pipeline is out of scope.

## 4. Risks

- **Development Time:** This is a complete rewrite of the application, which will require significant development effort.
- **Feature Parity:** Care must be taken to ensure that all existing functionality is ported to the new architecture.
- **New Dependencies:** The new architecture introduces a new set of dependencies (Flask, React, Node.js, etc.) that will need to be managed.
