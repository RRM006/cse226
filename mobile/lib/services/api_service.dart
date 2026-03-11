import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  static const String _baseUrl = 'https://nsu-audit-api.railway.app';
  
  String? _accessToken;

  void setAccessToken(String token) {
    _accessToken = token;
  }

  void clearAccessToken() {
    _accessToken = null;
  }

  Map<String, String> get _headers {
    final headers = <String, String>{
      'Accept': 'application/json',
    };
    if (_accessToken != null) {
      headers['Authorization'] = 'Bearer $_accessToken';
    }
    return headers;
  }

  Future<Map<String, dynamic>> uploadCsv({
    required File file,
    required String program,
    required int auditLevel,
    String waivers = '',
  }) async {
    final uri = Uri.parse('$_baseUrl/api/v1/audit/csv');
    final request = http.MultipartRequest('POST', uri);

    request.headers.addAll(_headers);
    request.fields['program'] = program;
    request.fields['audit_level'] = auditLevel.toString();
    if (waivers.isNotEmpty) {
      request.fields['waivers'] = waivers;
    }

    final bytes = await file.readAsBytes();
    final fileName = file.path.split('/').last;
    request.files.add(http.MultipartFile.fromBytes(
      'file',
      bytes,
      filename: fileName,
    ));

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw ApiException(
        response.statusCode,
        response.body,
      );
    }
  }

  Future<Map<String, dynamic>> uploadOcr({
    required File file,
    required String program,
    required int auditLevel,
    String waivers = '',
  }) async {
    final uri = Uri.parse('$_baseUrl/api/v1/audit/ocr');
    final request = http.MultipartRequest('POST', uri);

    request.headers.addAll(_headers);
    request.fields['program'] = program;
    request.fields['audit_level'] = auditLevel.toString();
    if (waivers.isNotEmpty) {
      request.fields['waivers'] = waivers;
    }

    final bytes = await file.readAsBytes();
    final fileName = file.path.split('/').last;
    final mediaType = _getMediaType(fileName);

    request.files.add(http.MultipartFile.fromBytes(
      'file',
      bytes,
      filename: fileName,
      contentType: mediaType,
    ));

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw ApiException(
        response.statusCode,
        response.body,
      );
    }
  }

  MediaType _getMediaType(String fileName) {
    final extension = fileName.split('.').last.toLowerCase();
    switch (extension) {
      case 'png':
        return MediaType('image', 'png');
      case 'jpg':
      case 'jpeg':
        return MediaType('image', 'jpeg');
      case 'pdf':
        return MediaType('application', 'pdf');
      default:
        return MediaType('application', 'octet-stream');
    }
  }

  Future<Map<String, dynamic>> getHistory({
    int limit = 20,
    int offset = 0,
  }) async {
    final uri = Uri.parse(
      '$_baseUrl/api/v1/history?limit=$limit&offset=$offset',
    );
    
    final response = await http.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw ApiException(
        response.statusCode,
        response.body,
      );
    }
  }

  Future<Map<String, dynamic>> getScanById(String scanId) async {
    final uri = Uri.parse('$_baseUrl/api/v1/history/$scanId');
    
    final response = await http.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw ApiException(
        response.statusCode,
        response.body,
      );
    }
  }

  Future<void> deleteScan(String scanId) async {
    final uri = Uri.parse('$_baseUrl/api/v1/history/$scanId');
    
    final response = await http.delete(uri, headers: _headers);

    if (response.statusCode != 200) {
      throw ApiException(
        response.statusCode,
        response.body,
      );
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
    final uri = Uri.parse('$_baseUrl/api/v1/audit/save');
    
    final body = {
      'program': program,
      'input_type': inputType,
      'raw_input': rawInput,
      'waivers': waivers,
      'audit_level': auditLevel,
      'result_json': resultJson,
      'result_text': resultText,
      'student_id': studentId,
    };

    final response = await http.post(
      uri,
      headers: {
        ..._headers,
        'Content-Type': 'application/json',
      },
      body: json.encode(body),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw ApiException(
        response.statusCode,
        response.body,
      );
    }
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException(this.statusCode, String body) 
      : message = _parseError(body);

  static String _parseError(String body) {
    try {
      final data = json.decode(body);
      return data['detail'] ?? body;
    } catch (_) {
      return body;
    }
  }

  @override
  String toString() => 'ApiException: $statusCode - $message';
}
