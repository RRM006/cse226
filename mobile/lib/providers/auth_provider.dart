import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';
import '../services/auth_service.dart';

enum AuthType { none, student, admin }

class AuthProvider extends ChangeNotifier {
  final ApiService _api = ApiService();
  final StorageService _storage = StorageService();
  final AuthService _authService = AuthService();

  AuthType _authType = AuthType.none;
  String? _studentId;
  String? _studentName;
  bool _isLoading = true;

  AuthType get authType => _authType;
  String? get studentId => _studentId;
  String? get studentName => _studentName;
  bool get isLoading => _isLoading;
  bool get isLoggedIn => _authType != AuthType.none;
  bool get isStudent => _authType == AuthType.student;
  bool get isAdmin => _authType == AuthType.admin;

  AuthProvider() {
    _checkExistingAuth();
  }

  Future<void> _checkExistingAuth() async {
    _isLoading = true;
    notifyListeners();

    try {
      final tokenType = await _storage.getTokenType();

      if (tokenType == 'student') {
        final token = await _storage.getToken();
        if (token != null) {
          _api.setAccessToken(token);
          final profile = await _api.getStudentProfile();
          _authType = AuthType.student;
          _studentId = profile['student_id'];
          _studentName = profile['name'] ?? '';
        } else {
          _authType = AuthType.none;
        }
      } else if (tokenType == 'admin') {
        final token = await _storage.getToken();
        if (token != null) {
          _api.setAccessToken(token);
          _authType = AuthType.admin;
        } else {
          _authType = AuthType.none;
        }
      } else {
        _authType = AuthType.none;
      }
    } catch (_) {
      _authType = AuthType.none;
    }

    _isLoading = false;
    notifyListeners();
  }

  Future<Map<String, dynamic>> loginStudent(
      String studentId, String password) async {
    final result = await _api.studentLogin(
      studentId: studentId,
      password: password,
    );

    _authType = AuthType.student;
    _studentId = result['student_id'];
    _studentName = result['name'] ?? '';
    notifyListeners();
    return result;
  }

  Future<void> logout() async {
    await _storage.clearAll();
    _api.clearAccessToken();
    _authType = AuthType.none;
    _studentId = null;
    _studentName = null;
    notifyListeners();
  }

  Future<void> refreshStudentProfile() async {
    if (_authType != AuthType.student) return;
    try {
      final profile = await _api.getStudentProfile();
      _studentId = profile['student_id'];
      _studentName = profile['name'] ?? '';
      notifyListeners();
    } catch (_) {}
  }
}
