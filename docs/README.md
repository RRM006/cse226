# NSU Audit Core

**A Full-Stack Graduation Audit System for North South University**

*Developed by Rafiur Rahman Mashrafi*  
*Course: CSE226.1 — Vibe Coding | Instructor: Dr. Nabeel Mohammed*

---

## Overview

NSU Audit Core is a comprehensive graduation audit system designed for North South University (NSU). It provides multi-platform access to verify student graduation eligibility across three academic programs: **BSCSE** (Computer Science), **BSEEE** (Electrical Engineering), and **LL.B Honors** (Law).

The system evolved from a CLI tool (Phase 1) into a full-stack multi-client service (Phase 2), supporting Web, Mobile, and CLI interfaces with OCR-powered transcript scanning and cloud-based history management.

---

## Features

### Core Functionality
- **Three-Tier Audit System**
  - Level 1: Credit Tally
  - Level 2: CGPA Calculation
  - Level 3: Full Graduation Eligibility Audit

- **Multi-Program Support**
  - BSCSE (Bachelor of Science in Computer Science & Engineering)
  - BSEEE (Bachelor of Science in Electrical & Electronic Engineering)
  - LL.B Honors (Bachelor of Law)

- **OCR Transcript Scanning**
  - Upload transcript images (JPG, PNG, PDF)
  - Automatic data extraction using EasyOCR
  - Confidence-based validation

### Authentication & Authorization
- Google OAuth 2.0 Authentication via Supabase
- Role-based access control (Student / Admin)
- NSU email domain restriction (@northsouth.edu)

### Multi-Platform Access
- **Web App**: React + Vite frontend
- **Mobile App**: Flutter (Android & iOS)
- **CLI**: Python-based command-line tool with offline and remote modes

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend API | FastAPI (Python) |
| Database | PostgreSQL via Supabase |
| Authentication | Supabase Auth (Google OAuth) |
| OCR Engine | EasyOCR |
| Frontend | React + Vite |
| Mobile | Flutter |
| Hosting | Railway (Backend), Vercel (Frontend) |
| CI/CD | GitHub Actions + Pre-commit |
| Load Testing | Locust |

---

## Project Structure

```
nsu-audit-core/
├── archive
│   ├── scripts
│   │   ├── generate_external_transfer_scripts.py # Script to generate external transfer tests
│   │   ├── generate_test_scripts.py    # Script to generate test scripts
│   │   ├── run_all_tests.py            # Universal test runner
│   │   ├── run_tests.bat               # Windows batch test runner
│   │   └── run_tests.sh                # Shell script test runner
│   ├── src
│   │   ├── external_transfer.py        # Legacy external transfer logic
│   │   ├── level1_credit_tally.py      # Legacy Level 1 credit tally logic
│   │   ├── level2_cgpa_calculator.py   # Legacy Level 2 CGPA calculator
│   │   ├── level3_audit_engine.py      # Legacy Level 3 audit engine
│   │   └── transfer_handler.py         # Legacy transfer handler
│   ├── testbat
│   │   ├── BSCSE
│   │   │   ├── L1
│   │   │   │   ├── L1_BSCSE_001_basic_passing.bat
│   │   │   │   ├── L1_BSCSE_001_basic_passing.sh
│   │   │   │   ├── L1_BSCSE_002_invalid_grades.bat
│   │   │   │   ├── L1_BSCSE_002_invalid_grades.sh
│   │   │   │   ├── L1_BSCSE_003_retakes.bat
│   │   │   │   ├── L1_BSCSE_003_retakes.sh
│   │   │   │   ├── L1_BSCSE_004_all_grades.bat
│   │   │   │   ├── L1_BSCSE_004_all_grades.sh
│   │   │   │   ├── L1_BSCSE_005_zero_credit_labs.bat
│   │   │   │   ├── L1_BSCSE_005_zero_credit_labs.sh
│   │   │   │   ├── L1_BSCSE_006_mixed_grades.bat
│   │   │   │   └── L1_BSCSE_006_mixed_grades.sh
│   │   │   ├── L2
│   │   │   │   ├── L2_BSCSE_001_cgpa_calc.bat
│   │   │   │   ├── L2_BSCSE_001_cgpa_calc.sh
│   │   │   │   ├── L2_BSCSE_002_waiver.bat
│   │   │   │   ├── L2_BSCSE_002_waiver.sh
│   │   │   │   ├── L2_BSCSE_003_retake_improved.bat
│   │   │   │   ├── L2_BSCSE_003_retake_improved.sh
│   │   │   │   ├── L2_BSCSE_004_probation.bat
│   │   │   │   ├── L2_BSCSE_004_probation.sh
│   │   │   │   ├── L2_BSCSE_005_honors.bat
│   │   │   │   ├── L2_BSCSE_005_honors.sh
│   │   │   │   ├── L2_BSCSE_006_mixed_invalid.bat
│   │   │   │   └── L2_BSCSE_006_mixed_invalid.sh
│   │   │   └── L3
│   │   │       ├── L3_BSCSE_001_complete.bat
│   │   │       ├── L3_BSCSE_001_complete.sh
│   │   │       ├── L3_BSCSE_002_deficient.bat
│   │   │       ├── L3_BSCSE_002_deficient.sh
│   │   │       ├── L3_BSCSE_003_retakes.bat
│   │   │       ├── L3_BSCSE_003_retakes.sh
│   │   │       ├── L3_BSCSE_004_prereq_violation.bat
│   │   │       ├── L3_BSCSE_004_prereq_violation.sh
│   │   │       ├── L3_BSCSE_005_probation.bat
│   │   │       ├── L3_BSCSE_005_probation.sh
│   │   │       ├── L3_BSCSE_006_missing_capstone.bat
│   │   │       └── L3_BSCSE_006_missing_capstone.sh
│   │   ├── BSEEE
│   │   │   ├── L1
│   │   │   │   ├── L1_BSEEE_001_basic_passing.bat
│   │   │   │   ├── L1_BSEEE_001_basic_passing.sh
│   │   │   │   ├── L1_BSEEE_002_invalid_grades.bat
│   │   │   │   ├── L1_BSEEE_002_invalid_grades.sh
│   │   │   │   ├── L1_BSEEE_003_retakes.bat
│   │   │   │   ├── L1_BSEEE_003_retakes.sh
│   │   │   │   ├── L1_BSEEE_004_all_grades.bat
│   │   │   │   ├── L1_BSEEE_004_all_grades.sh
│   │   │   │   ├── L1_BSEEE_005_zero_credit_labs.bat
│   │   │   │   ├── L1_BSEEE_005_zero_credit_labs.sh
│   │   │   │   ├── L1_BSEEE_006_mixed_grades.bat
│   │   │   │   └── L1_BSEEE_006_mixed_grades.sh
│   │   │   ├── L2
│   │   │   │   ├── L2_BSEEE_001_cgpa_calc.bat
│   │   │   │   ├── L2_BSEEE_001_cgpa_calc.sh
│   │   │   │   ├── L2_BSEEE_002_waiver.bat
│   │   │   │   ├── L2_BSEEE_002_waiver.sh
│   │   │   │   ├── L2_BSEEE_003_retake_improved.bat
│   │   │   │   ├── L2_BSEEE_003_retake_improved.sh
│   │   │   │   ├── L2_BSEEE_004_probation.bat
│   │   │   │   ├── L2_BSEEE_004_probation.sh
│   │   │   │   ├── L2_BSEEE_005_honors.bat
│   │   │   │   ├── L2_BSEEE_005_honors.sh
│   │   │   │   ├── L2_BSEEE_006_mixed_invalid.bat
│   │   │   │   └── L2_BSEEE_006_mixed_invalid.sh
│   │   │   └── L3
│   │   │       ├── L3_BSEEE_001_complete.bat
│   │   │       ├── L3_BSEEE_001_complete.sh
│   │   │       ├── L3_BSEEE_002_deficient.bat
│   │   │       ├── L3_BSEEE_002_deficient.sh
│   │   │       ├── L3_BSEEE_003_retakes.bat
│   │   │       ├── L3_BSEEE_003_retakes.sh
│   │   │       ├── L3_BSEEE_004_probation.bat
│   │   │       ├── L3_BSEEE_004_probation.sh
│   │   │       ├── L3_BSEEE_005_missing_capstone.bat
│   │   │       ├── L3_BSEEE_005_missing_capstone.sh
│   │   │       ├── L3_BSEEE_006_first_class.bat
│   │   │       └── L3_BSEEE_006_first_class.sh
│   │   ├── external_transfers
│   │   │   ├── BSCSE
│   │   │   │   ├── EXT_BSCSE_001_valid_transfer.bat
│   │   │   │   ├── EXT_BSCSE_001_valid_transfer.sh
│   │   │   │   ├── EXT_BSCSE_002_mixed_grades.bat
│   │   │   │   ├── EXT_BSCSE_002_mixed_grades.sh
│   │   │   │   ├── EXT_BSCSE_003_excessive_transfer.bat
│   │   │   │   └── EXT_BSCSE_003_excessive_transfer.sh
│   │   │   ├── BSEEE
│   │   │   │   ├── EXT_BSEEE_001_valid_transfer.bat
│   │   │   │   ├── EXT_BSEEE_001_valid_transfer.sh
│   │   │   │   ├── EXT_BSEEE_002_poor_grades.bat
│   │   │   │   └── EXT_BSEEE_002_poor_grades.sh
│   │   │   └── LLB
│   │   │       ├── EXT_LLB_001_valid_transfer.bat
│   │   │       ├── EXT_LLB_001_valid_transfer.sh
│   │   │       ├── EXT_LLB_002_poor_grades.bat
│   │   │       └── EXT_LLB_002_poor_grades.sh
│   │   ├── LLB
│   │   │   ├── L1
│   │   │   │   ├── L1_LLB_001_basic_passing.bat
│   │   │   │   ├── L1_LLB_001_basic_passing.sh
│   │   │   │   ├── L1_LLB_002_invalid_grades.bat
│   │   │   │   ├── L1_LLB_002_invalid_grades.sh
│   │   │   │   ├── L1_LLB_003_retakes.bat
│   │   │   │   ├── L1_LLB_003_retakes.sh
│   │   │   │   ├── L1_LLB_004_all_grades.bat
│   │   │   │   ├── L1_LLB_004_all_grades.sh
│   │   │   │   ├── L1_LLB_005_core_courses.bat
│   │   │   │   ├── L1_LLB_005_core_courses.sh
│   │   │   │   ├── L1_LLB_006_mixed_grades.bat
│   │   │   │   └── L1_LLB_006_mixed_grades.sh
│   │   │   ├── L2
│   │   │   │   ├── L2_LLB_001_cgpa_calc.bat
│   │   │   │   ├── L2_LLB_001_cgpa_calc.sh
│   │   │   │   ├── L2_LLB_002_waiver.bat
│   │   │   │   ├── L2_LLB_002_waiver.sh
│   │   │   │   ├── L2_LLB_003_retake_improved.bat
│   │   │   │   ├── L2_LLB_003_retake_improved.sh
│   │   │   │   ├── L2_LLB_004_probation.bat
│   │   │   │   ├── L2_LLB_004_probation.sh
│   │   │   │   ├── L2_LLB_005_honors.bat
│   │   │   │   ├── L2_LLB_005_honors.sh
│   │   │   │   ├── L2_LLB_006_mixed_invalid.bat
│   │   │   │   └── L2_LLB_006_mixed_invalid.sh
│   │   │   └── L3
│   │   │       ├── L3_LLB_001_complete.bat
│   │   │       ├── L3_LLB_001_complete.sh
│   │   │       ├── L3_LLB_002_deficient.bat
│   │   │       ├── L3_LLB_002_deficient.sh
│   │   │       ├── L3_LLB_003_retakes.bat
│   │   │       ├── L3_LLB_003_retakes.sh
│   │   │       ├── L3_LLB_004_probation.bat
│   │   │       ├── L3_LLB_004_probation.sh
│   │   │       ├── L3_LLB_005_missing_electives.bat
│   │   │       ├── L3_LLB_005_missing_electives.sh
│   │   │       ├── L3_LLB_006_first_class.bat
│   │   │       └── L3_LLB_006_first_class.sh
│   │   └── transfers
│   │       ├── TRANSFER_EEE_TO_LLB_001.bat
│   │       ├── TRANSFER_EEE_TO_LLB_001.sh
│   │       ├── TRANSFER_LLB_TO_BSCSE_001.bat
│   │       └── TRANSFER_LLB_TO_BSCSE_001.sh
│   └── test_outputs
│       ├── BSCSE
│       │   ├── L1
│       │   │   ├── L1_BSCSE_001_basic_passing.txt
│       │   │   ├── L1_BSCSE_002_invalid_grades.txt
│       │   │   ├── L1_BSCSE_003_retakes.txt
│       │   │   ├── L1_BSCSE_004_all_grades.txt
│       │   │   ├── L1_BSCSE_005_zero_credit_labs.txt
│       │   │   └── L1_BSCSE_006_mixed_grades.txt
│       │   ├── L2
│       │   │   ├── L2_BSCSE_001_cgpa_calc.txt
│       │   │   ├── L2_BSCSE_002_waiver.txt
│       │   │   ├── L2_BSCSE_003_retake_improved.txt
│       │   │   ├── L2_BSCSE_004_probation.txt
│       │   │   ├── L2_BSCSE_005_honors.txt
│       │   │   └── L2_BSCSE_006_mixed_invalid.txt
│       │   └── L3
│       │       ├── L3_BSCSE_001_complete.txt
│       │       ├── L3_BSCSE_002_deficient.txt
│       │       ├── L3_BSCSE_003_retakes.txt
│       │       ├── L3_BSCSE_004_prereq_violation.txt
│       │       ├── L3_BSCSE_005_probation.txt
│       │       └── L3_BSCSE_006_missing_capstone.txt
│       ├── BSEEE
│       │   ├── L1
│       │   │   ├── L1_BSEEE_001_basic_passing.txt
│       │   │   ├── L1_BSEEE_002_invalid_grades.txt
│       │   │   ├── L1_BSEEE_003_retakes.txt
│       │   │   ├── L1_BSEEE_004_all_grades.txt
│       │   │   ├── L1_BSEEE_005_zero_credit_labs.txt
│       │   │   └── L1_BSEEE_006_mixed_grades.txt
│       │   ├── L2
│       │   │   ├── L2_BSEEE_001_cgpa_calc.txt
│       │   │   ├── L2_BSEEE_002_waiver.txt
│       │   │   ├── L2_BSEEE_003_retake_improved.txt
│       │   │   ├── L2_BSEEE_004_probation.txt
│       │   │   ├── L2_BSEEE_005_honors.txt
│       │   │   └── L2_BSEEE_006_mixed_invalid.txt
│       │   └── L3
│       │       ├── L3_BSEEE_001_complete.txt
│       │       ├── L3_BSEEE_002_deficient.txt
│       │       ├── L3_BSEEE_003_retakes.txt
│       │       ├── L3_BSEEE_004_probation.txt
│       │       ├── L3_BSEEE_005_missing_capstone.txt
│       │       └── L3_BSEEE_006_first_class.txt
│       ├── external_transfers
│       │   ├── BSCSE
│       │   │   ├── EXT_BSCSE_001_valid_transfer.txt
│       │   │   ├── EXT_BSCSE_002_mixed_grades.txt
│       │   │   └── EXT_BSCSE_003_excessive_transfer.txt
│       │   ├── BSEEE
│       │   │   ├── EXT_BSEEE_001_valid_transfer.txt
│       │   │   └── EXT_BSEEE_002_poor_grades.txt
│       │   └── LLB
│       │       ├── EXT_LLB_001_valid_transfer.txt
│       │       └── EXT_LLB_002_poor_grades.txt
│       ├── LLB
│       │   ├── L1
│       │   │   ├── L1_LLB_001_basic_passing.txt
│       │   │   ├── L1_LLB_002_invalid_grades.txt
│       │   │   ├── L1_LLB_003_retakes.txt
│       │   │   ├── L1_LLB_004_all_grades.txt
│       │   │   ├── L1_LLB_005_core_courses.txt
│       │   │   └── L1_LLB_006_mixed_grades.txt
│       │   ├── L2
│       │   │   ├── L2_LLB_001_cgpa_calc.txt
│       │   │   ├── L2_LLB_002_waiver.txt
│       │   │   ├── L2_LLB_003_retake_improved.txt
│       │   │   ├── L2_LLB_004_probation.txt
│       │   │   ├── L2_LLB_005_honors.txt
│       │   │   └── L2_LLB_006_mixed_invalid.txt
│       │   └── L3
│       │       ├── L3_LLB_001_complete.txt
│       │       ├── L3_LLB_002_deficient.txt
│       │       ├── L3_LLB_003_retakes.txt
│       │       ├── L3_LLB_004_probation.txt
│       │       ├── L3_LLB_005_missing_electives.txt
│       │       └── L3_LLB_006_first_class.txt
│       └── transfers
│           ├── TRANSFER_EEE_TO_LLB_001.txt
│           └── TRANSFER_LLB_TO_BSCSE_001.txt
├── backend                             # FastAPI backend
│   ├── apt.txt
│   ├── auth.py                         # Authentication middleware
│   ├── config.py                       # Configuration settings
│   ├── core                            # Phase 1 audit engine
│   │   ├── __init__.py
│   │   ├── level1_credit_tally.py
│   │   ├── level2_cgpa_calculator.py
│   │   └── level3_audit_engine.py
│   ├── database.py                     # Database utilities
│   ├── main.py                         # Application entry point
│   ├── Procfile
│   ├── requirements-dev.txt
│   ├── requirements.txt
│   ├── routers                         # API route handlers
│   │   ├── audit.py                    # Audit endpoints
│   │   ├── history.py                  # History endpoints
│   │   ├── __init__.py
│   │   └── users.py                    # User management
│   ├── runtime.txt
│   ├── services                        # Business logic
│   │   ├── audit_service.py
│   │   ├── __init__.py
│   │   ├── ocr_service.py
│   │   └── scan_service.py
│   └── supabase_schema.sql
├── cli                                 # Python CLI tool
│   ├── audit_cli.py                    # Main CLI application
│   └── credentials.py                  # Token management
├── docs                                # Documentation
│   ├── phase3_prd.md                   # Phase 3 Product Requirements Document
│   ├── prd.md                          # Product Requirements Document
│   ├── prompts.md                      # Development Prompts
│   ├── README.md                       # Project Documentation (this file)
│   ├── testing.md                      # Test Cases and Plan
│   └── tracking.md                     # Project Progress Tracker
├── frontend                            # React web application
│   ├── dist
│   │   ├── assets
│   │   │   ├── index-avivHBry.css
│   │   │   └── index-CzLz6Mpq.js
│   │   ├── index.html
│   │   └── vite.svg
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── postcss.config.js
│   ├── public
│   │   └── vite.svg
│   ├── README.md
│   ├── src
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── assets
│   │   │   └── react.svg
│   │   ├── components                  # Reusable components
│   │   │   ├── AuthGuard.jsx
│   │   │   ├── layout
│   │   │   │   └── DashboardLayout.jsx
│   │   │   └── ui
│   │   │       ├── Button.jsx
│   │   │       ├── Card.jsx
│   │   │       ├── FileUpload.jsx
│   │   │       ├── Input.jsx
│   │   │       ├── Navbar.jsx
│   │   │       └── Select.jsx
│   │   ├── index.css
│   │   ├── lib                         # API and Supabase clients
│   │   │   ├── api.js
│   │   │   ├── supabase.js
│   │   │   └── utils.js
│   │   ├── main.jsx
│   │   └── pages                       # Login, Upload, Result, History, Admin
│   │       ├── AdminPanel.jsx
│   │       ├── AuthCallback.jsx
│   │       ├── History.jsx
│   │       ├── Login.jsx
│   │       ├── Result.jsx
│   │       └── Upload.jsx
│   ├── vercel.json
│   └── vite.config.js
├── mcp
│   ├── auth
│   │   └── google_oauth.py
│   ├── config.py
│   ├── credentials.json
│   ├── credentials.json.example
│   ├── history
│   │   └── local_log.py
│   ├── mcp_script
│   ├── mcp_server.py
│   ├── offline
│   │   └── engine_bridge.py
│   ├── phase3_prd.md
│   ├── README.md
│   ├── requirements.txt
│   ├── TESTING.md
│   └── tools
│       ├── audit_tools.py
│       ├── batch_tools.py
│       ├── drive_tools.py
│       ├── email_tools.py
│       └── history_tools.py
├── mcprun
├── mobile                              # Flutter mobile application
│   ├── analysis_options.yaml
│   ├── lib
│   │   ├── main.dart
│   │   ├── models
│   │   ├── screens                     # App screens
│   │   │   ├── history_screen.dart
│   │   │   ├── login_screen.dart
│   │   │   ├── result_screen.dart
│   │   │   └── upload_screen.dart
│   │   └── services                    # API and auth services
│   │       ├── api_service.dart
│   │       └── auth_service.dart
│   ├── linux
│   │   ├── CMakeLists.txt
│   │   ├── flutter
│   │   │   ├── CMakeLists.txt
│   │   │   ├── ephemeral
│   │   │   │   ├── flutter_linux
│   │   │   │   │   ├── fl_application.h
│   │   │   │   │   ├── fl_basic_message_channel.h
│   │   │   │   │   ├── fl_binary_codec.h
│   │   │   │   │   ├── fl_binary_messenger.h
│   │   │   │   │   ├── fl_dart_project.h
│   │   │   │   │   ├── fl_engine.h
│   │   │   │   │   ├── fl_event_channel.h
│   │   │   │   │   ├── fl_json_message_codec.h
│   │   │   │   │   ├── fl_json_method_codec.h
│   │   │   │   │   ├── fl_message_codec.h
│   │   │   │   │   ├── fl_method_call.h
│   │   │   │   │   ├── fl_method_channel.h
│   │   │   │   │   ├── fl_method_codec.h
│   │   │   │   │   ├── fl_method_response.h
│   │   │   │   │   ├── fl_pixel_buffer_texture.h
│   │   │   │   │   ├── fl_plugin_registrar.h
│   │   │   │   │   ├── fl_plugin_registry.h
│   │   │   │   │   ├── fl_standard_message_codec.h
│   │   │   │   │   ├── fl_standard_method_codec.h
│   │   │   │   │   ├── fl_string_codec.h
│   │   │   │   │   ├── fl_texture_gl.h
│   │   │   │   │   ├── fl_texture.h
│   │   │   │   │   ├── fl_texture_registrar.h
│   │   │   │   │   ├── flutter_linux.h
│   │   │   │   │   ├── fl_value.h
│   │   │   │   │   └── fl_view.h
│   │   │   │   ├── generated_config.cmake
│   │   │   │   ├── icudtl.dat
│   │   │   │   └── libflutter_linux_gtk.so
│   │   │   ├── generated_plugin_registrant.cc
│   │   │   ├── generated_plugin_registrant.h
│   │   │   └── generated_plugins.cmake
│   │   └── runner
│   │       ├── CMakeLists.txt
│   │       ├── main.cc
│   │       ├── my_application.cc
│   │       └── my_application.h
│   ├── nsu_audit_mobile.iml
│   ├── pubspec.lock
│   ├── pubspec.yaml
│   ├── README.md
│   └── test
│       └── widget_test.dart
├── opencode.json
├── pickup_guide.md
├── program_knowledge
│   ├── program_knowledge_BSCSE.md
│   ├── program_knowledge_BSEEE.md
│   └── program_knowledge_LLB.md
└── tests                               # Test files
    ├── BSCSE                           # Test data BSCSE
    │   ├── L1
    │   │   ├── L1_BSCSE_001_basic_passing.csv
    │   │   ├── L1_BSCSE_002_invalid_grades.csv
    │   │   ├── L1_BSCSE_003_retakes.csv
    │   │   ├── L1_BSCSE_004_all_grades.csv
    │   │   ├── L1_BSCSE_005_zero_credit_labs.csv
    │   │   └── L1_BSCSE_006_mixed_grades.csv
    │   ├── L2
    │   │   ├── L2_BSCSE_001_cgpa_calc.csv
    │   │   ├── L2_BSCSE_002_waiver.csv
    │   │   ├── L2_BSCSE_003_retake_improved.csv
    │   │   ├── L2_BSCSE_004_probation.csv
    │   │   ├── L2_BSCSE_005_honors.csv
    │   │   └── L2_BSCSE_006_mixed_invalid.csv
    │   └── L3
    │       ├── L3_BSCSE_001_complete.csv
    │       ├── L3_BSCSE_002_deficient.csv
    │       ├── L3_BSCSE_003_retakes.csv
    │       ├── L3_BSCSE_004_prereq_violation.csv
    │       ├── L3_BSCSE_005_probation.csv
    │       └── L3_BSCSE_006_missing_capstone.csv
    ├── BSEEE                           # Test data BSEEE
    │   ├── L1
    │   │   ├── L1_BSEEE_001_basic_passing.csv
    │   │   ├── L1_BSEEE_002_invalid_grades.csv
    │   │   ├── L1_BSEEE_003_retakes.csv
    │   │   ├── L1_BSEEE_004_all_grades.csv
    │   │   ├── L1_BSEEE_005_zero_credit_labs.csv
    │   │   └── L1_BSEEE_006_mixed_grades.csv
    │   ├── L2
    │   │   ├── L2_BSEEE_001_cgpa_calc.csv
    │   │   ├── L2_BSEEE_002_waiver.csv
    │   │   ├── L2_BSEEE_003_retake_improved.csv
    │   │   ├── L2_BSEEE_004_probation.csv
    │   │   ├── L2_BSEEE_005_honors.csv
    │   │   └── L2_BSEEE_006_mixed_invalid.csv
    │   └── L3
    │       ├── L3_BSEEE_001_complete.csv
    │       ├── L3_BSEEE_002_deficient.csv
    │       ├── L3_BSEEE_003_retakes.csv
    │       ├── L3_BSEEE_004_probation.csv
    │       ├── L3_BSEEE_005_missing_capstone.csv
    │       └── L3_BSEEE_006_first_class.csv
    ├── external_transfers
    │   ├── BSCSE
    │   │   ├── EXT_BSCSE_001_valid_transfer.csv
    │   │   ├── EXT_BSCSE_002_mixed_grades.csv
    │   │   └── EXT_BSCSE_003_excessive_transfer.csv
    │   ├── BSEEE
    │   │   ├── EXT_BSEEE_001_valid_transfer.csv
    │   │   └── EXT_BSEEE_002_poor_grades.csv
    │   └── LLB
    │       ├── EXT_LLB_001_valid_transfer.csv
    │       └── EXT_LLB_002_poor_grades.csv
    ├── LLB                             # Test data LLB
    │   ├── L1
    │   │   ├── L1_LLB_001_basic_passing.csv
    │   │   ├── L1_LLB_002_invalid_grades.csv
    │   │   ├── L1_LLB_003_retakes.csv
    │   │   ├── L1_LLB_004_all_grades.csv
    │   │   ├── L1_LLB_005_core_courses.csv
    │   │   └── L1_LLB_006_mixed_grades.csv
    │   ├── L2
    │   │   ├── L2_LLB_001_cgpa_calc.csv
    │   │   ├── L2_LLB_002_waiver.csv
    │   │   ├── L2_LLB_003_retake_improved.csv
    │   │   ├── L2_LLB_004_probation.csv
    │   │   ├── L2_LLB_005_honors.csv
    │   │   └── L2_LLB_006_mixed_invalid.csv
    │   └── L3
    │       ├── L3_LLB_001_complete.csv
    │       ├── L3_LLB_002_deficient.csv
    │       ├── L3_LLB_003_retakes.csv
    │       ├── L3_LLB_004_probation.csv
    │       ├── L3_LLB_005_missing_electives.csv
    │       └── L3_LLB_006_first_class.csv
    ├── locustfile.py                   # Load testing
    ├── nsu_transcript_ocr              # OCR test samples
    │   ├── 585057865-Riyadh.pdf
    │   ├── 681844277-Transcript.pdf
    │   └── Screenshot_20260309_214956.png
    ├── testclirun.txt
    ├── test_mcp
    ├── test_ocr.py
    └── transfers
        ├── TRANSFER_EEE_TO_LLB_001.csv
        └── TRANSFER_LLB_TO_BSCSE_001.csv
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/audit/csv` | Run audit with CSV upload |
| POST | `/api/v1/audit/ocr` | Run audit with image OCR |
| GET | `/api/v1/history` | Get user's scan history |
| DELETE | `/api/v1/history/{scan_id}` | Delete a scan |
| GET | `/api/v1/users` | List all users (Admin) |
| PATCH | `/api/v1/users/{id}/role` | Change user role (Admin) |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Flutter SDK 3.x
- Supabase account

### Backend Setup

```bash
cd backend
cp .env.example .env
# Edit .env with your Supabase credentials

pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your Supabase credentials

npm run dev
```

### Mobile Setup

```bash
cd mobile
flutter pub get
flutter build apk --release
```

### CLI Setup

```bash
cd cli
pip install -r requirements.txt
python audit_cli.py --help
```

---

## Usage

### CLI Modes

**Offline Mode (Phase 1 behavior):**
```bash
python audit_cli.py l1 tests/BSCSE/L1/L1_BSCSE_001_basic_passing.csv BSCSE
python audit_cli.py l2 tests/BSCSE/L2/L2_BSCSE_001_cgpa_calc.csv BSCSE
python audit_cli.py l3 tests/BSCSE/L3/L3_BSCSE_001_complete.csv BSCSE
```

**Remote Mode (with cloud sync):**
```bash
python audit_cli.py login
python audit_cli.py l3 tests/BSCSE/L3/L3_BSCSE_001_complete.csv BSCSE --remote
python audit_cli.py history
python audit_cli.py logout
```

---

## Running Tests

```bash
# Unit and integration tests
pytest tests/ -v

# Load testing (requires deployed backend)
locust -f tests/locustfile.py --headless -u 20 -r 4 --run-time 60s \
  --host https://nsu-audit-api.railway.app \
  --html tests/load_test_report.html
```

---

## Deployment

### Backend (Railway)
1. Connect repository to Railway
2. Set environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_KEY`
3. Deploy automatically via GitHub Actions

### Frontend (Vercel)
1. Import repository in Vercel
2. Set environment variables:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
   - `VITE_API_URL`
3. Deploy automatically via GitHub Actions

---

## Documentation

Additional documentation available in the `docs/` folder:
---

## License

This project is developed for educational purposes as part of CSE226.1 — Vibe Coding course at North South University.

---

## Author

**Rafiur Rahman Mashrafi**  
North South University  
CSE226.1 — Vibe Coding  
Instructor: Dr. Nabeel Mohammed
