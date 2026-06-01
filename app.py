from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import os
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

db = SQLAlchemy(app)

# Database Model
class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    subtitle = db.Column(db.String(255))
    language = db.Column(db.String(100))
    editor = db.Column(db.String(255))
    author = db.Column(db.String(255), index=True)
    publisher = db.Column(db.String(255), index=True)
    place = db.Column(db.String(255))
    country = db.Column(db.String(100))
    year = db.Column(db.Integer)
    edition = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'subtitle': self.subtitle,
            'language': self.language,
            'editor': self.editor,
            'author': self.author,
            'publisher': self.publisher,
            'place': self.place,
            'country': self.country,
            'year': self.year,
            'edition': self.edition,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d') if self.updated_at else ''
        }

# Create tables
with app.app_context():
    db.create_all()

# Routes

@app.route('/')
def index():
    """Display all books with search and filter"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'title', type=str)
    sort_order = request.args.get('sort_order', 'asc', type=str)
    
    query = Book.query
    
    # Search functionality
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Book.title.ilike(search_term),
                Book.author.ilike(search_term),
                Book.publisher.ilike(search_term),
                Book.language.ilike(search_term),
                Book.country.ilike(search_term)
            )
        )
    
    # Sorting
    sort_column = getattr(Book, sort_by, Book.title)
    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Pagination
    books = query.paginate(page=page, per_page=10)
    
    return render_template('index.html', 
                         books=books,
                         search=search,
                         sort_by=sort_by,
                         sort_order=sort_order)

@app.route('/book/add', methods=['GET', 'POST'])
def add_book():
    """Add a new book"""
    if request.method == 'POST':
        try:
            data = request.form
            book = Book(
                title=data.get('title'),
                subtitle=data.get('subtitle'),
                language=data.get('language'),
                editor=data.get('editor'),
                author=data.get('author'),
                publisher=data.get('publisher'),
                place=data.get('place'),
                country=data.get('country'),
                year=int(data.get('year')) if data.get('year') else None,
                edition=data.get('edition')
            )
            db.session.add(book)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Book added successfully!', 'id': book.id})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400
    
    return render_template('add_edit_book.html', book=None)

@app.route('/book/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    """Edit a book"""
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        try:
            data = request.form
            book.title = data.get('title')
            book.subtitle = data.get('subtitle')
            book.language = data.get('language')
            book.editor = data.get('editor')
            book.author = data.get('author')
            book.publisher = data.get('publisher')
            book.place = data.get('place')
            book.country = data.get('country')
            book.year = int(data.get('year')) if data.get('year') else None
            book.edition = data.get('edition')
            book.updated_at = datetime.utcnow()
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Book updated successfully!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400
    
    return render_template('add_edit_book.html', book=book)

@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """Delete a book"""
    try:
        book = Book.query.get_or_404(book_id)
        db.session.delete(book)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Book deleted successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/import', methods=['GET', 'POST'])
def import_excel():
    """Import books from Excel file"""
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                return jsonify({'success': False, 'message': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'message': 'No file selected'}), 400
            
            if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
                return jsonify({'success': False, 'message': 'Please upload an Excel or CSV file'}), 400
            
            # Read the Excel file
            df = pd.read_excel(file)
            df.columns = df.columns.str.strip()
            
            imported_count = 0
            errors = []
            
            for idx, row in df.iterrows():
                try:
                    # Check if book already exists
                    existing = Book.query.filter_by(
                        title=str(row.get('Title', '')).strip() if pd.notna(row.get('Title')) else None,
                        author=str(row.get('Author', '')).strip() if pd.notna(row.get('Author')) else None
                    ).first()
                    
                    if not existing:
                        book = Book(
                            title=str(row.get('Title', '')).strip() if pd.notna(row.get('Title')) else '',
                            subtitle=str(row.get('Sub Title', '')).strip() if pd.notna(row.get('Sub Title')) else None,
                            language=str(row.get('Language', '')).strip() if pd.notna(row.get('Language')) else None,
                            editor=str(row.get('Editor', '')).strip() if pd.notna(row.get('Editor')) else None,
                            author=str(row.get('Author', '')).strip() if pd.notna(row.get('Author')) else None,
                            publisher=str(row.get('Publishers', '')).strip() if pd.notna(row.get('Publishers')) else None,
                            place=str(row.get('Place', '')).strip() if pd.notna(row.get('Place')) else None,
                            country=str(row.get('Country', '')).strip() if pd.notna(row.get('Country')) else None,
                            year=int(row.get('Year')) if pd.notna(row.get('Year')) else None,
                            edition=str(row.get('Edition', '')).strip() if pd.notna(row.get('Edition')) else None
                        )
                        db.session.add(book)
                        imported_count += 1
                except Exception as row_error:
                    errors.append(f"Row {idx + 1}: {str(row_error)}")
            
            db.session.commit()
            
            message = f"Imported {imported_count} books successfully!"
            if errors:
                message += f" ({len(errors)} errors encountered)"
            
            return jsonify({
                'success': True,
                'message': message,
                'imported_count': imported_count,
                'errors': errors[:5]
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error importing file: {str(e)}'}), 400
    
    return render_template('import_excel.html')

@app.route('/export')
def export_excel():
    """Export all books to Excel file"""
    try:
        books = Book.query.all()
        
        # Create DataFrame
        data = []
        for book in books:
            data.append({
                'Title': book.title,
                'Sub Title': book.subtitle,
                'Language': book.language,
                'Editor': book.editor,
                'Author': book.author,
                'Publishers': book.publisher,
                'Place': book.place,
                'Country': book.country,
                'Year': book.year,
                'Edition': book.edition
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file with formatting
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Books')
            
            # Format the header row
            worksheet = writer.sheets['Books']
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF")
            
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'library_books_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error exporting file: {str(e)}'}), 400

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('error.html', error='Server error'), 500

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
