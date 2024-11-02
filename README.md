# **Rafeek SMMA**

**Rafeek SMMA** is a project management application designed for social media marketing agencies. It helps manage client relationships, track tasks, and streamline the workflow with a focus on role-based access, dashboards, and Kanban boards.

## **Features**

- **Role-based Access**: Supports managers and workers, each with different levels of access and features.
  - Managers can assign tasks, track progress, manage clients, and view submitted tasks.
  - Workers can view tasks assigned to them, update their progress, and submit completed work.

- **Kanban Board**: Visual task management system to track tasks through different stages of completion.

- **Client Management**: Add and manage client information, including contact details, business category, social media handles, and specific goals.

- **Task Tracking**: Create and assign tasks with deadlines and manage their lifecycle from assignment to completion.

- **Notifications**: Integrated notification system to keep users informed of new assignments, updates, and client activity.

- **Dashboard**: Overview of active clients, tasks in progress, and general project status for managers and workers.

## **Technologies Used**

- **Backend**: Python, Flask, SQLAlchemy, Flask-WTF
- **Frontend**: Jinja2, Bootstrap, HTML, CSS
- **Database**: PostgreSQL, SQLAlchemy
- **Tools**: Docker, Git, AWS (RDS, S3, Lambda)
- **Other**: Font Awesome for icons, CSRF protection

## **Setup Instructions**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/iRAFEEK/Rafeek-SMMA.git
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory and add the necessary configuration for the database, secret keys, etc.

5. **Run the Application**:
   ```bash
   flask run
   ```

6. **Access the App**:
   - Open your browser and go to `http://127.0.0.1:5000`.

## **Usage**

- **Managers** can access the dashboard, assign tasks, view the Kanban board, and manage client information.
- **Workers** can view their tasks, update their progress, and mark tasks as completed.
- **Forms** are available for adding clients, onboarding tasks, content ideas, and metrics.

## **Project Structure**

- **`app`**: Contains the main application code, including blueprints for different modules.
- **`templates`**: HTML templates for rendering pages.
- **`static`**: CSS and JavaScript files for styling and interactivity.
- **`models.py`**: Defines the database models.
- **`forms.py`**: Contains the form definitions using Flask-WTF.
- **`views.py`**: Handles routes and logic for various features.

## **Contributing**

Feel free to open issues or submit pull requests to improve the functionality or add new features. Contributions are always welcome!

## **License**

This project is licensed under the MIT License. See the `LICENSE` file for more details.



