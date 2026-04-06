# ID Document Management System

A full-stack web application for uploading, extracting, and managing ID documents with OCR technology. The system supports multiple ID types including UAE ID, driving license, Passports, and more.

## Features

- **Multi-ID Support**: Upload and manage two different ID documents
- **Automatic Text Extraction**: Uses Tesseract OCR to extract text from ID images
- **ID Type Detection**: Automatically detects UAE ID, driving license, Passport, and other document types
- **CRUD Operations**: Complete Create, Read, Update, Delete functionality
- **Modern UI**: Responsive design with Tailwind CSS
- **Real-time Updates**: Instant feedback on uploads and edits
- **Document Storage**: Saves uploaded images and extracted data

## Tech Stack

### Backend
- **Python 3.12+**
- **Flask** - Web framework
- **Flask-SQLAlchemy** - ORM for database operations
- **Flask-CORS** - Cross-origin resource sharing
- **Tesseract OCR** - Text extraction from images
- **Pillow** - Image processing
- **SQLite** - Lightweight database

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Dropzone** - File upload handling

## 📋 Prerequisites

Before running this project, make sure you have:

- **Python 3.12 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **Tesseract OCR** - [Download Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

## 🔧 Installation

### 1. Clone the Repository

git clone <your-repository-url>
cd id-management-al-yafour


# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

Install Tesseract OCR
Windows:
Download installer from UB-Mannheim/tesseract

Run installer and check "Add Tesseract to system PATH"

# Navigate to frontend directory (from project root)
cd frontend

# Install Node dependencies
npm install

# Install additional packages
npm install axios react-dropzone

# In backend directory with virtual environment activated
python app.py

The backend will run on http://localhost:5000

# Open a new terminal, navigate to frontend directory
cd frontend

# Start Vite dev server
npm run dev
The frontend will run on http://localhost:3000

Usage Guide
Uploading Documents
Click on the upload area

Select the document type (First ID or Second ID)

Click "Upload Documents" button

Wait for OCR processing and auto-detection

Managing Documents
View Details: Click "View" button to see all extracted information

Edit Data: Click "Edit" button to manually correct extracted information

Delete Document: Click "Delete" button to remove a document

video Waltkthrough Link Google drive : https://drive.google.com/file/d/1R9pX-jNlySE8owNIcTgWdoC1hNVwvI6Q/view?usp=sharing
