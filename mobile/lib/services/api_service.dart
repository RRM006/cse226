import 'dart:io';
import 'package:dio/dio.dart';
import '../config/api_config.dart';
import 'storage_service.dart';

class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException(this.statusCode, this.message);

  @override
  String toString() => 'ApiException: $statusCode - $message';
}

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;

  late Dio _dio;
  final StorageService _storage = StorageService();
  String? _accessToken;

  ApiService._internal() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConfig.baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 30),
      headers: {'Accept': 'application/json'},
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        if (_accessToken != null) {
          options.headers['Authorization'] = 'Bearer $_accessToken';
        } else {
          final token = await _storage.getToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
        }
        handler.next(options);
      },
      onError: (error, handler) {
        final statusCode = error.response?.statusCode ?? 0;
        final message = _parseError(error.response?.data);
        handler.next(DioException(
          requestOptions: error.requestOptions,
          response: error.response,
          error: ApiException(statusCode, message),
        ));
      },
    ));
  }

  static String _parseError(dynamic data) {
    if (data is Map) {
      return data['detail']?.toString() ?? 'Request failed';
    }
    if (data is String) {
      return data;
    }
    return 'Request failed';
  }

  void setAccessToken(String? token) {
    _accessToken = token;
  }

  void clearAccessToken() {
    _accessToken = null;
  }

  // ─── Student Auth ───

  Future<Map<String, dynamic>> studentLogin({
    required String studentId,
    required String password,
  }) async {
    final response = await _dio.post(
      ApiConfig.studentLogin,
      data: {'student_id': studentId, 'password': password},
    );
    final data = response.data;
    await _storage.saveStudentToken(
      data['access_token'],
      data['student_id'],
      data['name'] ?? '',
    );
    _accessToken = data['access_token'];
    return data;
  }

  Future<void> studentChangePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    await _dio.post(
      ApiConfig.studentChangePassword,
      data: {
        'current_password': currentPassword,
        'new_password': newPassword,
      },
    );
  }

  Future<Map<String, dynamic>> getStudentProfile() async {
    final response = await _dio.get(ApiConfig.studentProfile);
    return response.data;
  }

  // ─── Student Audit Results ───

  Future<Map<String, dynamic>> getStudentAuditResults({
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _dio.get(
      ApiConfig.studentAuditResults,
      queryParameters: {'limit': limit, 'offset': offset},
    );
    return response.data;
  }

  Future<Map<String, dynamic>> getStudentAuditResultById(
      String resultId) async {
    final response = await _dio.get(
      '${ApiConfig.studentAuditResults}/$resultId',
    );
    return response.data;
  }

  // ─── Student Requests ───

  Future<Map<String, dynamic>> submitStudentRequest({
    required String message,
    String? auditResultId,
  }) async {
    final body = {'message': message};
    if (auditResultId != null) {
      body['audit_result_id'] = auditResultId;
    }
    final response = await _dio.post(
      ApiConfig.studentRequests,
      data: body,
    );
    return response.data;
  }

  Future<Map<String, dynamic>> getStudentRequests({
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _dio.get(
      ApiConfig.studentRequests,
      queryParameters: {'limit': limit, 'offset': offset},
    );
    return response.data;
  }

  // ─── Audit (CSV / OCR) ───

  Future<Map<String, dynamic>> uploadCsv({
    required File file,
    required String program,
    required int auditLevel,
    String waivers = '',
  }) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(
        file.path,
        filename: file.path.split('/').last,
      ),
      'program': program,
      'audit_level': auditLevel.toString(),
      if (waivers.isNotEmpty) 'waivers': waivers,
    });

    final response = await _dio.post(
      ApiConfig.auditCsv,
      data: formData,
    );
    return response.data;
  }

  Future<Map<String, dynamic>> uploadOcr({
    required File file,
    required String program,
    required int auditLevel,
    String waivers = '',
  }) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(
        file.path,
        filename: file.path.split('/').last,
      ),
      'program': program,
      'audit_level': auditLevel.toString(),
      if (waivers.isNotEmpty) 'waivers': waivers,
    });

    final response = await _dio.post(
      ApiConfig.auditOcr,
      data: formData,
    );
    return response.data;
  }

  Future<Map<String, dynamic>> saveScan({
    required String program,
    required String inputType,
    required String rawInput,
    required List<String> waivers,
    required int auditLevel,
    required Map<String, dynamic> resultJson,
    required String resultText,
    String studentId = '',
  }) async {
    final response = await _dio.post(
      ApiConfig.auditSave,
      data: {
        'program': program,
        'input_type': inputType,
        'raw_input': rawInput,
        'waivers': waivers,
        'audit_level': auditLevel,
        'result_json': resultJson,
        'result_text': resultText,
        'student_id': studentId,
      },
    );
    return response.data;
  }

  // ─── History ───

  Future<Map<String, dynamic>> getHistory({
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _dio.get(
      ApiConfig.history,
      queryParameters: {'limit': limit, 'offset': offset},
    );
    return response.data;
  }

  Future<Map<String, dynamic>> getScanById(String scanId) async {
    final response = await _dio.get('${ApiConfig.history}/$scanId');
    return response.data;
  }

  Future<void> deleteScan(String scanId) async {
    await _dio.delete('${ApiConfig.history}/$scanId');
  }

  // ─── Admin: Students ───

  Future<Map<String, dynamic>> getAllStudents({
    int limit = 50,
    int offset = 0,
  }) async {
    final response = await _dio.get(
      ApiConfig.students,
      queryParameters: {'limit': limit, 'offset': offset},
    );
    return response.data;
  }

  Future<Map<String, dynamic>> createStudent({
    required String studentId,
    String name = '',
    String email = '',
  }) async {
    final response = await _dio.post(
      ApiConfig.students,
      data: {'student_id': studentId, 'name': name, 'email': email},
    );
    return response.data;
  }

  Future<Map<String, dynamic>> getStudentById(String studentId) async {
    final response = await _dio.get('${ApiConfig.students}/$studentId');
    return response.data;
  }

  Future<void> updateStudent(
      String studentId, Map<String, dynamic> data) async {
    await _dio.patch('${ApiConfig.students}/$studentId', data: data);
  }

  Future<void> adminResetPassword(String studentId, String newPassword) async {
    await _dio.patch(
      '${ApiConfig.students}/$studentId/reset-password',
      data: {'new_password': newPassword},
    );
  }

  Future<void> deleteStudent(String studentId) async {
    await _dio.delete('${ApiConfig.students}/$studentId');
  }

  // ─── Admin: Requests ───

  Future<Map<String, dynamic>> getAllRequests({
    int limit = 50,
    int offset = 0,
  }) async {
    final response = await _dio.get(
      ApiConfig.requests,
      queryParameters: {'limit': limit, 'offset': offset},
    );
    return response.data;
  }

  Future<Map<String, dynamic>> getRequestById(String requestId) async {
    final response = await _dio.get('${ApiConfig.requests}/$requestId');
    return response.data;
  }

  Future<void> updateRequestStatus({
    required String requestId,
    required String status,
    String? adminNotes,
  }) async {
    final body = {'status': status};
    if (adminNotes != null) {
      body['admin_notes'] = adminNotes;
    }
    await _dio.patch('${ApiConfig.requests}/$requestId', data: body);
  }

  // ─── Admin: Audit Results ───

  Future<Map<String, dynamic>> createAuditResult({
    required String studentId,
    required String program,
    required int auditLevel,
    required Map<String, dynamic> resultJson,
    required String resultText,
    required bool eligible,
    String? scanId,
  }) async {
    final data = {
      'student_id': studentId,
      'program': program,
      'audit_level': auditLevel,
      'result_json': resultJson,
      'result_text': resultText,
      'eligible': eligible,
    };
    if (scanId != null) {
      data['scan_id'] = scanId;
    }
    final response = await _dio.post(
      ApiConfig.auditResults,
      data: data,
    );
    return response.data;
  }

  Future<Map<String, dynamic>> getAllAuditResults({
    int limit = 50,
    int offset = 0,
  }) async {
    final response = await _dio.get(
      ApiConfig.auditResults,
      queryParameters: {'limit': limit, 'offset': offset},
    );
    return response.data;
  }
}
