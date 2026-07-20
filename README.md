# Trekky - Design System & Prototypes

> A Flask-based trekking platform featuring a complete design system with a custom color palette, typography, and component library.

## 🚀 Quick Start

### Prerequisites
- Python 3.6+
- pip (Python package installer)

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd Trekky
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Run the app:
    ```bash
    python app.py
    ```

4.  Open [http://localhost:5000](http://localhost:5000) in your browser.

## 🎨 Design System

The design system is implemented in [style.css](static/css/style.css) with all components and color tokens.

### Color Palette

-   **Background**: `#faf9f6` (Warm Off-White)
-   **Text Main**: `#1c1917` (Stone-900)
-   **Accent Rust**: `#c2410c` (Orange-700)

### Typography

-   **Headings**: Fraunces serif font family
-   **Body**: Inter Tight sans-serif font family

### Key Components

-   **Navigation**: Custom Navbar with brand-text and nav-links
-   **Buttons**:
    -   `.btn-solid` - Solid background button
    -   `.btn-outline` - Outlined button
    -   `.btn-accent` - Accent color button
-   **Forms**:
    -   `.form-control-custom` - Custom form inputs
    -   `.form-label-custom` - Custom form labels
-   **Layout**:
    -   `.content-grid` - 2-column grid layout
    -   `.auth-card` - Card-based authentication layout

## 📂 Project Structure

```
Trekky/
├── static/
│   ├── css/
│   │   ├── style.css        # Design system & components
│   │   └── style.scss       # SCSS source (if applicable)
│   ├── js/
│   │   └── main.js          # Client-side scripts
│   └── img/                # Images & assets
├── templates/
│   ├── base.html           # Base layout & navigation
│   ├── index.html          # Home page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── admin/
│   │   └── dashboard.html  # Admin dashboard
│   └── user/
│       └── dashboard.html  # User dashboard
├── app.py                  # Main Flask application
├── models.py               # SQLAlchemy models
├── routes.py               # Flask routes
├── requirements.txt        # Dependencies
└── README.md               # Project documentation
```

## 📋 Pages

### Public Pages

1.  **Home Page** (`/`)
    -   Showcases design system with all components
    -   Design-focused layout with custom typography

2.  **Login** (`/login`)
    -   Email + Password authentication
    -   Option to choose between Trekker and Staff role

3.  **Register** (`/register`)
    -   Create new user account
    -   Role-based registration (Trekker or Staff)
    -   Conditional staff fields

### User Pages

-   **User Dashboard** (`/user/dashboard`)
    -   List of booked treks
    -   Account management

### Staff Pages

-   **Staff Dashboard** (`/staff/dashboard`)
    -   Manage staff profile
    -   View trek information

## 🔐 Authentication & Authorization

The app uses Flask-Login for session management and role-based access control.

### Roles

-   **admin** - Full access to all features
-   **staff** - Staff members managing treks
-   **trekker** - Users booking treks

## 🛠️ Development

### Adding New Features

1.  **Add Models**: Update [models.py](models.py) with new SQLAlchemy models
2.  **Update Routes**: Add new routes to [routes.py](routes.py)
3.  **Create Templates**: Add new HTML templates to [templates/](templates/)
4.  **Design Components**: Create reusable components in [static/css/style.css](static/css/style.css)

## 🧪 Testing

Run the application with debug mode enabled:
```bash
python app.py
```

The server will start on [http://localhost:5000](http://localhost:5000).

## 📚 Additional Resources

-   **Flask Documentation**: [https://flask.palletsprojects.com](https://flask.palletsprojects.com)
-   **SQLAlchemy Documentation**: [https://www.sqlalchemy.org](https://www.sqlalchemy.org)
-   **Bootstrap CDN**: [https://getbootstrap.com](https://getbootstrap.com)
