# NOTES WALLAH
Flask-Based File and Music Sharing Platform

Project Description
This Flask-based web application facilitates secure file and music sharing among users. It provides robust features such as user authentication, an admin panel for managing posts and users, and a dashboard for personalized content. Key functionalities include:

User Authentication: 
  Secure login, registration, and logout using hashed passwords.
File and Music Sharing:
  Upload, view, download, and manage files and music posts.
Admin Panel:
  Manage users, posts, and music with privileges for admin users.
User Profile Management:
  Update profiles and manage account settings, including profile pictures.
Responsive Design:  
  Optimized for seamless usage across devices.
  
Technologies Used => 
  Frontend: HTML, CSS, Jinja2 templates for dynamic rendering.
  Backend: Flask framework for routing and server-side logic.
  Database: SQLite for storing user, post, and music data.
  Authentication: Auth0 OAuth integration and password hashing for secure access.
  Utilities: Flask-SQLAlchemy ORM, Flask-Admin for administration, and Werkzeug for file handling.
  
Features Overview => 

Authentication:
  Login, registration, and password management.
  Secure sessions and hashed passwords.
  
File and Music Sharing:
  Upload files and share music links.
  View and download content via personalized dashboards.
  
Admin Panel:
  Manage posts, users, and music as an admin.
  
Profile Management:
  Update user information and profile pictures.
  View other users’ profiles.
  
Custom Content Management:
  Categorized content for easier navigation.
  Responsive and user-friendly design.
  
Setup Instructions => 
  Clone the repository:
  git clone https://github.com/YourUsername/YourRepository.git
  cd YourRepository
  
Install dependencies:
  pip install -r requirements.txt

Create a .env file with the following keys =>

AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
AUTH0_CALLBACK_URL=your_callback_url
AUTH0_DOMAIN=your_auth0_domain

Initialize the database => 
flask db init
flask db migrate
flask db upgrade

Run the application =>
 flask run

Access the app at http://127.0.0.1:5000.

![Screenshot 2024-11-27 214414](https://github.com/user-attachments/assets/7c37e1d0-d4b9-444d-9d7e-30c4c9283ba7)
![Screenshot 2024-11-27 214427](https://github.com/user-attachments/assets/3c9d1b39-f9a4-4980-8bd5-84ca6924407e)
![Screenshot 2024-11-27 214432](https://github.com/user-attachments/assets/1e1d4510-797d-4a62-bd70-fa7e562247a8)


