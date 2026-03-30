import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class StorageService {
  static final StorageService _instance = StorageService._internal();
  factory StorageService() => _instance;
  StorageService._internal();

  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  static const String _tokenKey = 'auth_token';
  static const String _tokenTypeKey = 'token_type';
  static const String _studentIdKey = 'student_id';
  static const String _studentNameKey = 'student_name';

  Future<void> saveStudentToken(
      String token, String studentId, String name) async {
    await _storage.write(key: _tokenKey, value: token);
    await _storage.write(key: _tokenTypeKey, value: 'student');
    await _storage.write(key: _studentIdKey, value: studentId);
    await _storage.write(key: _studentNameKey, value: name);
  }

  Future<void> saveAdminToken(String token) async {
    await _storage.write(key: _tokenKey, value: token);
    await _storage.write(key: _tokenTypeKey, value: 'admin');
  }

  Future<String?> getToken() async {
    return await _storage.read(key: _tokenKey);
  }

  Future<String?> getTokenType() async {
    return await _storage.read(key: _tokenTypeKey);
  }

  Future<String?> getStudentId() async {
    return await _storage.read(key: _studentIdKey);
  }

  Future<String?> getStudentName() async {
    return await _storage.read(key: _studentNameKey);
  }

  Future<bool> isStudentToken() async {
    final type = await getTokenType();
    return type == 'student';
  }

  Future<bool> isAdminToken() async {
    final type = await getTokenType();
    return type == 'admin';
  }

  Future<void> clearAll() async {
    await _storage.delete(key: _tokenKey);
    await _storage.delete(key: _tokenTypeKey);
    await _storage.delete(key: _studentIdKey);
    await _storage.delete(key: _studentNameKey);
  }

  Future<void> clearStudentData() async {
    await _storage.delete(key: _tokenKey);
    await _storage.delete(key: _tokenTypeKey);
    await _storage.delete(key: _studentIdKey);
    await _storage.delete(key: _studentNameKey);
  }
}
