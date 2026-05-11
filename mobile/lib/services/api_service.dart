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
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 120),
      sendTimeout: const Duration(seconds: 120),
      headers: {'Accept': 'application/json'},
      validateStatus: (status) => true,
    ));

    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: false,
      error: true,
      logPrint: (o) => print('[API] $o'),
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
          type: error.type,
          message: message,
        ));
      },
    ));
  }

  static String _parseError(dynamic data) {
    if (data is Map) {
      return data['detail']?.toString() ??
          'Request failed (${data.runtimeType})';
    }
    if (data is String) {
      return data;
    }
    return 'Request failed (unknown error)';
  }

  void setAccessToken(String? token) {
    _accessToken = token;
  }

  void clearAccessToken() {
    _accessToken = null;
  }

  Response<T>? _safeResponse<T>(Response<T> response) {
    if (response.statusCode == null) return null;
    if (response.statusCode! >= 200 && response.statusCode! < 300) {
      return response;
    }
    return null;
  }

  void _checkError(Response response) {
    if (response.statusCode == null) {
      throw ApiException(0, 'Network error: No response from server');
    }
    if (response.statusCode! >= 200 && response.statusCode! < 300) {
      return;
    }
    throw ApiException(
      response.statusCode!,
      _parseError(response.data),
    );
  }

  Future<Map<String, dynamic>> _handleResponse(
      Future<Response<dynamic>> Function() request) async {
    try {
      final response = await request();
      _checkError(response);
      if (response.data == null) {
        throw ApiException(
            response.statusCode ?? 0, 'Server returned empty response');
      }
      if (response.data is! Map<String, dynamic>) {
        throw ApiException(
          response.statusCode ?? 0,
          'Unexpected response format: ${response.data.runtimeType}',
        );
      }
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      if (e.error is ApiException) rethrow;
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw ApiException(408, 'Request timed out. Please try again.');
      }
      if (e.type == DioExceptionType.connectionError) {
        throw ApiException(
            0, 'Cannot connect to server. Check your internet connection.');
      }
      if (e.response != null) {
        throw ApiException(
          e.response!.statusCode ?? 0,
          _parseError(e.response!.data),
        );
      }
      throw ApiException(0, 'Network error: ${e.message ?? "Unknown"}');
    }
  }

  Future<Map<String, dynamic>> _handleListResponse(
      Future<Response<dynamic>> Function() request) async {
    return _handleResponse(request);
  }

  Future<Map<String, dynamic>> _post(
    String path, {
    Map<String, dynamic>? data,
    FormData? formData,
  }) =>
      _handleResponse(() => _dio.post(
            path,
            data: formData ?? data,
            options: formData != null
                ? Options(contentType: 'multipart/form-data')
                : null,
          ));

  Future<Map<String, dynamic>> _get(String path,
          {Map<String, dynamic>? queryParameters}) =>
      _handleResponse(() => _dio.get(path, queryParameters: queryParameters));

  Future<void> _patch(String path, {Map<String, dynamic>? data}) =>
      _handleResponse(() => _dio.patch(path, data: data));

  Future<void> _delete(String path) => _handleResponse(() => _dio.delete(path));

  // ─── Student Auth ───

  Future<Map<String, dynamic>> studentLogin({
    required String studentId,
    required String password,
  }) async {
    return _post(
      ApiConfig.studentLogin,
      data: {'student_id': studentId, 'password': password},
    ).then((data) async {
      await _storage.saveStudentToken(
        data['access_token']?.toString() ?? '',
        data['student_id']?.toString() ?? '',
        data['name']?.toString() ?? '',
      );
      _accessToken = data['access_token']?.toString();
      return data;
    });
  }

  Future<void> studentChangePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    await _post(
      ApiConfig.studentChangePassword,
      data: {
        'current_password': currentPassword,
        'new_password': newPassword,
      },
    );
  }

  Future<Map<String, dynamic>> getStudentProfile() async {
    return _get(ApiConfig.studentProfile);
  }

  // ─── Student Audit Results ───

  Future<Map<String, dynamic>> getStudentAuditResults({
    int limit = 20,
    int offset = 0,
  }) async {
    return _get(
      ApiConfig.studentAuditResults,
      queryParameters: {'limit': limit, 'offset': offset},
    );
  }

  Future<Map<String, dynamic>> getStudentAuditResultById(
      String resultId) async {
    return _get('${ApiConfig.studentAuditResults}/$resultId');
  }

  // ─── Student Requests ───

  Future<Map<String, dynamic>> submitStudentRequest({
    required String message,
    String? auditResultId,
  }) async {
    final body = <String, dynamic>{'message': message};
    if (auditResultId != null) body['audit_result_id'] = auditResultId;
    return _post(ApiConfig.studentRequests, data: body);
  }

  Future<Map<String, dynamic>> getStudentRequests({
    int limit = 20,
    int offset = 0,
  }) async {
    return _get(
      ApiConfig.studentRequests,
      queryParameters: {'limit': limit, 'offset': offset},
    );
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
      'audit_level': auditLevel,
      if (waivers.isNotEmpty) 'waivers': waivers,
    });

    return _post(ApiConfig.auditCsv, formData: formData);
  }

  Future<Map<String, dynamic>> uploadOcr({
    required File file,
    required String program,
    required int auditLevel,
    String waivers = '',
  }) async {
    print('[API] OCR upload: program=$program, level=$auditLevel, '
        'file=${file.path.split('/').last}');

    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(
        file.path,
        filename: file.path.split('/').last,
      ),
      'program': program,
      'audit_level': auditLevel,
      if (waivers.isNotEmpty) 'waivers': waivers,
    });

    try {
      final data = await _post(ApiConfig.auditOcr, formData: formData);
      print('[API] OCR response keys: ${data.keys.toList()}');
      return data;
    } catch (e) {
      print('[API] OCR error: $e');
      rethrow;
    }
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
    return _post(
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
  }

  Future<Map<String, dynamic>> saveAuditWithStudentId({
    required String studentId,
    required String program,
    required String inputType,
    required List<String> waivers,
    required int auditLevel,
    required Map<String, dynamic> resultJson,
    required String resultText,
  }) async {
    return _post(
      ApiConfig.auditSaveWithStudentId,
      data: {
        'student_id': studentId,
        'program': program,
        'input_type': inputType,
        'raw_input': '',
        'waivers': waivers,
        'audit_level': auditLevel,
        'result_json': resultJson,
        'result_text': resultText,
      },
    );
  }

  Future<Map<String, dynamic>> getStudentScans({
    int limit = 20,
    int offset = 0,
  }) async {
    return _get(
      ApiConfig.studentScans,
      queryParameters: {'limit': limit, 'offset': offset},
    );
  }

  // ─── History ───

  Future<Map<String, dynamic>> getHistory({
    int limit = 20,
    int offset = 0,
  }) async {
    return _get(
      ApiConfig.history,
      queryParameters: {'limit': limit, 'offset': offset},
    );
  }

  Future<Map<String, dynamic>> getScanById(String scanId) async {
    return _get('${ApiConfig.history}/$scanId');
  }

  Future<void> deleteScan(String scanId) async {
    await _delete('${ApiConfig.history}/$scanId');
  }

  // ─── Admin: Students ───

  Future<Map<String, dynamic>> getAllStudents({
    int limit = 50,
    int offset = 0,
  }) async {
    return _get(
      ApiConfig.students,
      queryParameters: {'limit': limit, 'offset': offset},
    );
  }

  Future<Map<String, dynamic>> createStudent({
    required String studentId,
    String name = '',
    String email = '',
  }) async {
    return _post(
      ApiConfig.students,
      data: {'student_id': studentId, 'name': name, 'email': email},
    );
  }

  Future<Map<String, dynamic>> getStudentById(String studentId) async {
    return _get('${ApiConfig.students}/$studentId');
  }

  Future<void> updateStudent(
      String studentId, Map<String, dynamic> data) async {
    await _patch('${ApiConfig.students}/$studentId', data: data);
  }

  Future<void> adminResetPassword(String studentId, String newPassword) async {
    await _patch(
      '${ApiConfig.students}/$studentId/reset-password',
      data: {'new_password': newPassword},
    );
  }

  Future<void> deleteStudent(String studentId) async {
    await _delete('${ApiConfig.students}/$studentId');
  }

  // ─── Admin: Requests ───

  Future<Map<String, dynamic>> getAllRequests({
    int limit = 50,
    int offset = 0,
  }) async {
    return _get(
      ApiConfig.requests,
      queryParameters: {'limit': limit, 'offset': offset},
    );
  }

  Future<Map<String, dynamic>> getRequestById(String requestId) async {
    return _get('${ApiConfig.requests}/$requestId');
  }

  Future<void> updateRequestStatus({
    required String requestId,
    required String status,
    String? adminNotes,
  }) async {
    final body = <String, dynamic>{'status': status};
    if (adminNotes != null) body['admin_notes'] = adminNotes;
    await _patch('${ApiConfig.requests}/$requestId', data: body);
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
    final data = <String, dynamic>{
      'student_id': studentId,
      'program': program,
      'audit_level': auditLevel,
      'result_json': resultJson,
      'result_text': resultText,
      'eligible': eligible,
    };
    if (scanId != null) data['scan_id'] = scanId;
    return _post(ApiConfig.auditResults, data: data);
  }

  Future<Map<String, dynamic>> getAllAuditResults({
    int limit = 50,
    int offset = 0,
  }) async {
    return _get(
      ApiConfig.auditResults,
      queryParameters: {'limit': limit, 'offset': offset},
    );
  }
}
