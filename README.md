# Library Management Application

A simple, web-based Library Management System built with Python Flask and SQLite. Perfect for managing your book collection with easy import/export from Excel.

## Features

- 📚 **Book Management** - Add, edit, delete, and view books
- 🔍 **Search & Filter** - Find books by title, author, language, publisher, year
- 📥 **Excel Import** - Upload your Excel sheet to populate the database
- 📤 **Excel Export** - Download book data back to Excel format
- 📱 **User-Friendly Interface** - Beautiful, responsive web interface
- 💾 **Persistent Storage** - SQLite database for data persistence

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. Clone the repository:
```bash
git clone https://github.com/abhiramraom/library-management.git
cd library-management
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and go to:
```
http://localhost:5000
```

## Usage

### Dashboard
- View all books in your library
- Books are displayed with pagination (10 per page)
- Sort by title, language, publisher, or year

### Add a Book
1. Click "Add New Book" in the navigation
2. Fill in book details (Title is required)
3. Click "Add Book"

### Edit a Book
1. Find the book in the list
2. Click the "Edit" button
3. Update the details
4. Click "Update Book"

### Delete a Book
1. Find the book in the list
2. Click the "Delete" button
3. Confirm deletion

### Search Books
- Use the search bar to find books by:
  - Title
  - Author
  - Publisher
  - Language
  - Country

### Import Excel
1. Click "Import Excel" from the navigation
2. Upload your Excel file (.xlsx, .xls, or .csv)
3. The application will add all books to the database
4. Duplicate books (same title and author) are skipped

### Export to Excel
1. Click "Export to Excel" from the navigation
2. All books are downloaded as a formatted Excel file

## Excel Format

Your Excel file should have these columns:
- **Title** (required)
- **Sub Title**
- **Language**
- **Editor**
- **Author**
- **Publishers**
- **Place**
- **Country**
- **Year**
- **Edition**

## Database Schema

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Unique book ID |
| title | Text | Book title |
| subtitle | Text | Book subtitle |
| language | Text | Language of the book |
| editor | Text | Book editor |
| author | Text | Book author(s) |
| publisher | Text | Publisher name |
| place | Text | Publication place |
| country | Text | Publication country |
| year | Integer | Publication year |
| edition | Text | Edition number |
| created_at | DateTime | When book was added |
| updated_at | DateTime | Last update time |

## Project Structure

```
library-management/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore file
├── templates/
│   ├── base.html              # Base HTML template
│   ├── index.html             # Dashboard/Book listing
│   ├── add_edit_book.html     # Add/Edit book form
│   ├── import_excel.html      # Excel import page
│   └── error.html             # Error page
├── static/
│   └── style.css              # Application styling
└── data/
    └── books.db               # SQLite database (auto-created)
```

## Technologies Used

- **Backend**: Python 3.8+
- **Framework**: Flask 2.3.0
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3
- **Data Handling**: Pandas 2.0.0
- **Excel Support**: openpyxl 3.10.0

## Future Enhancements

- [ ] User authentication and multi-user support
- [ ] Book categories/genres
- [ ] Borrowing and return tracking
- [ ] Advanced analytics and statistics
- [ ] API for programmatic access
- [ ] Mobile app integration

## License

MIT License - Feel free to use this project for any purpose.

## Support

If you encounter any issues or have suggestions, please create an issue on GitHub.
