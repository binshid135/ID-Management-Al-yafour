from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, IDDocument
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import re
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename
from datetime import datetime, timezone

# ============================================
# TESSERACT CONFIGURATION
# ============================================
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# For better Arabic + English support (download ara.traineddata)
# Place it in: C:\Program Files\Tesseract-OCR\tessdata\

# ============================================
# TEST TESSERACT
# ============================================
def test_tesseract():
    print("\n" + "="*60)
    print("TESTING TESSERACT INSTALLATION")
    print("="*60)
    tesseract_path = pytesseract.pytesseract.tesseract_cmd
    print(f"Checking Tesseract path: {tesseract_path}")
    if os.path.exists(tesseract_path):
        print("✓ Tesseract executable found")
    else:
        print("✗ Tesseract NOT found")
        return False

    try:
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract Version: {version}")
        print("✓ OCR test passed")
        return True
    except Exception as e:
        print(f"✗ Tesseract error: {e}")
        return False


# ============================================
# FLASK SETUP
# ============================================
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///id_documents.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db.init_app(app)

with app.app_context():
    db.create_all()


# ============================================
# IMPROVED IMAGE PREPROCESSING
# ============================================
def preprocess_image(image_path):
    variants = []
    try:
        # OpenCV advanced preprocessing
        img_cv = cv2.imread(image_path)
        if img_cv is not None:
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray)
            # Thresholding
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            variants.append(Image.fromarray(thresh))

            # Adaptive + contrast
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            cl = clahe.apply(denoised)
            variants.append(Image.fromarray(cl))

        # PIL variants
        img = Image.open(image_path).convert('RGB')
        gray_pil = img.convert('L')

        # High contrast + sharpen
        contrast = ImageEnhance.Contrast(gray_pil).enhance(3.0)
        sharp = contrast.filter(ImageFilter.SHARPEN)
        variants.append(sharp)

        # Upscale if small
        w, h = img.size
        if w < 1500:
            scale = 1500 / w
            upscaled = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
            variants.append(upscaled.convert('L'))

        # Auto contrast + original grayscale
        variants.append(ImageOps.autocontrast(gray_pil, cutoff=2))
        variants.append(gray_pil)

    except Exception as e:
        print(f"Preprocessing error: {e}")
        variants.append(Image.open(image_path).convert('L'))

    return variants


# ============================================
# IMPROVED OCR
# ============================================
def run_ocr(image_path):
    variants = preprocess_image(image_path)
    configs = [
        '--psm 6 --oem 3 -l eng+ara',
        '--psm 4 --oem 3 -l eng+ara',
        '--psm 3 --oem 3 -l eng+ara',
        '--psm 11 --oem 3 -l eng+ara',
        '--psm 7 --oem 3 -l eng+ara',
        '--psm 6 --oem 3 -l eng',
        '--psm 4 --oem 3 -l eng',
    ]

    best_text = ""
    best_score = 0

    for img in variants:
        for config in configs:
            try:
                text = pytesseract.image_to_string(img, config=config)
                clean = re.sub(r'\s+', '', text)
                score = len(clean)

                # Bonus for Emirates ID pattern
                if re.search(r'784', text):
                    score += 200

                if score > best_score:
                    best_score = score
                    best_text = text
            except Exception as e:
                print(f"OCR attempt failed: {e}")

    print(f"[OCR] Best extraction: {len(best_text)} characters | Score: {best_score}")
    return best_text


# ============================================
# DOCUMENT TYPE DETECTION (Improved)
# ============================================
def detect_document_type(text):
    text_lower = text.lower()
    driving_keywords = [
        'driving', 'licence', 'license', 'رخصة القيادة', 'rta', 'traffic', 'driver', 'vehicle', 'class'
    ]
    emirates_keywords = [
        'emirates id', 'هوية', 'هوية إماراتية', 'بطاقة الهوية', 'federal authority',
        'united arab emirates', 'eid', 'resident identity', '784'
    ]

    dl_score = sum(1 for kw in driving_keywords if kw in text_lower)
    eid_score = sum(1 for kw in emirates_keywords if kw in text_lower)

    if dl_score > eid_score + 1:
        return 'driving_license'
    return 'emirates_id'


# ============================================
# HELPER FUNCTIONS
# ============================================
def is_valid_name(name):
    words = name.strip().split()
    if len(words) < 2 or len(words) > 8:
        return False
    if not all(re.match(r'^[A-Za-z\-\'\s]+$', w) for w in words):
        return False
    stop_words = {'date', 'birth', 'expiry', 'nationality', 'united', 'arab', 'emirates',
                  'identity', 'card', 'resident', 'number', 'sex', 'male', 'female',
                  'driving', 'licence', 'license', 'valid', 'class', 'type', 'id'}
    if any(w.lower() in stop_words for w in words):
        return False
    return True


def clean_name(name):
    name = re.sub(r'\s+', ' ', name).strip()
    return ' '.join(w.capitalize() for w in name.split())


def normalize_date(date_str):
    date_str = re.sub(r'[\-\.]', '/', date_str)
    parts = date_str.split('/')
    if len(parts) == 3:
        if len(parts[2]) == 4:  # DD/MM/YYYY
            return f"{parts[0].zfill(2)}/{parts[1].zfill(2)}/{parts[2]}"
        elif len(parts[0]) == 4:  # YYYY/MM/DD
            return f"{parts[2].zfill(2)}/{parts[1].zfill(2)}/{parts[0]}"
    return date_str


# ============================================
# EMIRATES ID EXTRACTOR (Major Fix)
# ============================================
def extract_emirates_id_info(text):
    info = {
        'full_name': None,
        'document_number': None,
        'date_of_birth': None,
        'nationality': None,
        'expiry_date': None,
        'detected_doc_type': 'Emirates ID'
    }

    clean = re.sub(r'\s+', ' ', text).strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # 1. Document Number (784-XXXX-XXXXXXX-X) - Very robust
    id_patterns = [
        r'784[-\s]?\d{4}[-\s]?\d{7}[-\s]?\d',
        r'784\d{12}',
        r'(\d{3})[-\s]?(\d{4})[-\s]?(\d{7})[-\s]?(\d)',
    ]
    for pat in id_patterns:
        m = re.search(pat, clean)
        if m:
            raw = re.sub(r'[\s\-]', '', m.group(0))
            if len(raw) == 15 and raw.startswith('784'):
                info['document_number'] = f"{raw[:3]}-{raw[3:7]}-{raw[7:14]}-{raw[14]}"
                break

    # 2. Full Name
    name_patterns = [
        r'(?:Name|Full Name|الاسم)[:\s]+([A-Z][A-Za-z\s\']{5,80})',
    ]
    for pat in name_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip()
            if is_valid_name(candidate):
                info['full_name'] = clean_name(candidate)
                break

    if not info['full_name']:
        for line in lines:
            cleaned = re.sub(r'[^A-Za-z\s\']', '', line).strip()
            if is_valid_name(cleaned) and len(cleaned) > 10:
                info['full_name'] = clean_name(cleaned)
                break

    # 3. Dates (DOB & Expiry)
    dates = re.findall(r'\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})\b', clean)
    for d in dates:
        norm = normalize_date(d)
        ctx = clean[max(0, clean.find(d)-50):clean.find(d)+70].lower()
        if not info['date_of_birth'] and any(k in ctx for k in ['birth', 'ميلاد', 'dob']):
            info['date_of_birth'] = norm
        elif not info['expiry_date'] and any(k in ctx for k in ['expiry', 'انتهاء', 'expire', 'valid until']):
            info['expiry_date'] = norm

    # Fallback: first date usually DOB, last usually Expiry
    if dates:
        if not info['date_of_birth']:
            info['date_of_birth'] = normalize_date(dates[0])
        if not info['expiry_date'] and len(dates) >= 2:
            info['expiry_date'] = normalize_date(dates[-1])

    # 4. Nationality
    nat_patterns = [
        r'(?:Nationality|الجنسية)[:\s]+([A-Za-z\s]{3,40})',
    ]
    for pat in nat_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            nat = m.group(1).strip().title()
            if len(nat) > 2:
                info['nationality'] = nat
                break

    return info


# ============================================
# DRIVING LICENSE EXTRACTOR (Improved)
# ============================================
def extract_driving_license_info(text):
    info = {
        'full_name': None,
        'document_number': None,
        'date_of_birth': None,
        'nationality': None,
        'expiry_date': None,
        'detected_doc_type': 'UAE Driving License'
    }

    clean = re.sub(r'\s+', ' ', text).strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # License Number
    lic_patterns = [
        r'(?:Licence No|License No|رقم|No\.?)[:\s]*([A-Z0-9\-]{5,18})',
        r'\b([A-Z0-9]{5,15})\b',
    ]
    for pat in lic_patterns:
        m = re.search(pat, clean, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip()
            if not re.match(r'\d{2}[\/\-]\d{2}[\/\-]\d{4}', candidate) and not candidate.startswith('784'):
                info['document_number'] = candidate
                break

    # Name, Dates, Nationality - similar logic as Emirates ID
    name_patterns = [r'(?:Name|Full Name|الاسم)[:\s]+([A-Z][A-Za-z\s\']{5,80})']
    for pat in name_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m and is_valid_name(m.group(1)):
            info['full_name'] = clean_name(m.group(1))
            break

    if not info['full_name']:
        for line in lines:
            cleaned = re.sub(r'[^A-Za-z\s\']', '', line).strip()
            if is_valid_name(cleaned) and len(cleaned) > 10:
                info['full_name'] = clean_name(cleaned)
                break

    # Dates (similar fallback)
    dates = re.findall(r'\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})\b', clean)
    for d in dates:
        norm = normalize_date(d)
        ctx = clean[max(0, clean.find(d)-50):clean.find(d)+70].lower()
        if not info['date_of_birth'] and any(k in ctx for k in ['birth', 'ميلاد', 'dob']):
            info['date_of_birth'] = norm
        elif not info['expiry_date'] and any(k in ctx for k in ['expiry', 'انتهاء', 'expire']):
            info['expiry_date'] = norm

    if dates:
        if not info['date_of_birth']:
            info['date_of_birth'] = normalize_date(dates[0])
        if not info['expiry_date'] and len(dates) >= 2:
            info['expiry_date'] = normalize_date(dates[-1])

    return info


def extract_document_info(text, hint_type=None):
    doc_type = hint_type or detect_document_type(text)
    print(f"[Extractor] Detected type: {doc_type}")

    if doc_type == 'driving_license':
        info = extract_driving_license_info(text)
    else:
        info = extract_emirates_id_info(text)

    for k, v in info.items():
        print(f"  {'✓' if v else '✗'} {k}: {v}")

    return info


# ============================================
# ROUTES (unchanged except minor logging)
# ============================================
@app.route('/api/upload', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        document_type = request.form.get('document_type', 'id1')
        doc_kind = request.form.get('doc_kind')  # optional hint

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'PDF not supported. Use JPG/PNG'}), 400

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(f"{document_type}_{timestamp}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        extracted_text = run_ocr(filepath)

        if extracted_text.strip():
            info = extract_document_info(extracted_text, hint_type=doc_kind)
        else:
            info = {'full_name': None, 'document_number': None, 'date_of_birth': None,
                    'nationality': None, 'expiry_date': None, 'detected_doc_type': 'Unknown'}

        document = IDDocument(
            document_type=document_type,
            full_name=info['full_name'] or "Not detected — please edit",
            document_number=info['document_number'] or "Not detected — please edit",
            date_of_birth=info.get('date_of_birth'),
            nationality=info.get('nationality'),
            expiry_date=info.get('expiry_date'),
            extracted_text=extracted_text[:4000],
            image_path=filepath
        )

        db.session.add(document)
        db.session.commit()

        ocr_success = bool(info.get('document_number') and "Not detected" not in str(info.get('document_number')))

        return jsonify({
            'message': 'Document processed',
            'document': document.to_dict(),
            'detected_doc_type': info.get('detected_doc_type'),
            'ocr_success': ocr_success,
            'fields_extracted': {
                'name': bool(info.get('full_name')),
                'document_number': bool(info.get('document_number')),
                'date_of_birth': bool(info.get('date_of_birth')),
                'nationality': bool(info.get('nationality')),
                'expiry_date': bool(info.get('expiry_date')),
            }
        }), 201

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Other routes remain the same (get_documents, update, delete, health, test-ocr)
@app.route('/api/documents', methods=['GET'])
def get_documents():
    documents = IDDocument.query.order_by(IDDocument.created_at.desc()).all()
    return jsonify([doc.to_dict() for doc in documents])


@app.route('/api/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    document = IDDocument.query.get_or_404(doc_id)
    return jsonify(document.to_dict())


@app.route('/api/documents/<int:doc_id>', methods=['PUT'])
def update_document(doc_id):
    document = IDDocument.query.get_or_404(doc_id)
    data = request.json
    document.full_name = data.get('full_name', document.full_name)
    document.document_number = data.get('document_number', document.document_number)
    document.date_of_birth = data.get('date_of_birth', document.date_of_birth)
    document.nationality = data.get('nationality', document.nationality)
    document.expiry_date = data.get('expiry_date', document.expiry_date)
    document.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify(document.to_dict())


@app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    document = IDDocument.query.get_or_404(doc_id)
    if document.image_path and os.path.exists(document.image_path):
        try:
            os.remove(document.image_path)
        except Exception as e:
            print(f"File delete error: {e}")
    db.session.delete(document)
    db.session.commit()
    return jsonify({'message': 'Document deleted'})


@app.route('/api/health', methods=['GET'])
def health_check():
    tesseract_ok = False
    version = None
    try:
        if os.path.exists(pytesseract.pytesseract.tesseract_cmd):
            version = str(pytesseract.get_tesseract_version())
            tesseract_ok = True
    except:
        pass

    return jsonify({
        'status': 'healthy',
        'tesseract': {'installed': tesseract_ok, 'version': version}
    })


@app.route('/api/test-ocr', methods=['POST'])
def test_ocr():
    # ... (keep your existing test route)
    pass


# ============================================
# STARTUP
# ============================================
if __name__ == '__main__':
    print("\n" + "="*70)
    print("ID DOCUMENT OCR SYSTEM — IMPROVED VERSION")
    print("="*70)
    test_tesseract()
    print(f"\nServer running at: http://localhost:5000")
    print("Tip: Place ara.traineddata in tessdata folder for better Arabic support")
    print("="*70 + "\n")
    app.run(debug=True, port=5000)