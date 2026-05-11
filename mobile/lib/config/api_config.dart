class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  static const String supabaseUrl = String.fromEnvironment(
    'SUPABASE_URL',
    defaultValue: 'https://zxzcnpkfabiiecagczao.supabase.co',
  );

  static const String supabaseAnonKey = String.fromEnvironment(
    'SUPABASE_ANON_KEY',
    defaultValue: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4emNucGtmYWJpaWVjYWdjemFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI4MDExNDMsImV4cCI6MjA4ODM3NzE0M30.0Qo8IT6gBIOF3YMlHZm4dnh47lMUW5QesD_f3EVf9tM',
  );

  // Student Endpoints
  static const String studentLogin = '/api/v1/student/login';
  static const String studentChangePassword = '/api/v1/student/change-password';
  static const String studentProfile = '/api/v1/student/me';
  static const String studentAuditResults = '/api/v1/student/audit-results';
  static const String studentRequests = '/api/v1/student/requests';

  // Audit Endpoints
  static const String auditCsv = '/api/v1/audit/csv';
  static const String auditOcr = '/api/v1/audit/ocr';
  static const String auditSave = '/api/v1/audit/save';
  static const String auditSaveWithStudentId =
      '/api/v1/audit/save-with-student-id';

  // History Endpoints
  static const String history = '/api/v1/history';

  // Student Scans
  static const String studentScans = '/api/v1/student/scans';

  // Admin Endpoints
  static const String students = '/api/v1/students';
  static const String auditResults = '/api/v1/audit-results';
  static const String requests = '/api/v1/requests';
}
