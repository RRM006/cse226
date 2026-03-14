import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  SupabaseClient? _supabaseClient;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  static const String _supabaseUrl = 'https://zxzcnpkfabiiecagczao.supabase.co';
  static const String _supabaseAnonKey =
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4emNucGtmYWJpaWVjYWdjemFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI4MDExNDMsImV4cCI6MjA4ODM3NzE0M30.0Qo8IT6gBIOF3YMlHZm4dnh47lMUW5QesD_f3EVf9tM';

  SupabaseClient get _client {
    if (_supabaseClient == null) {
      throw Exception('Supabase not initialized. Call initialize() first.');
    }
    return _supabaseClient!;
  }

  Future<void> initialize() async {
    await Supabase.initialize(
      url: _supabaseUrl,
      anonKey: _supabaseAnonKey,
    );
    _supabaseClient = Supabase.instance.client;
  }

  Future<bool> signInWithGoogle() async {
    final result = await _client.auth.signInWithOAuth(
      OAuthProvider.google,
      redirectTo: 'https://zxzcnpkfabiiecagczao.supabase.co/auth/v1/callback',
    );
    return result;
  }

  Future<void> signOut() async {
    await _client.auth.signOut();
    await _storage.delete(key: 'session');
  }

  Session? getCurrentSession() {
    return _client.auth.currentSession;
  }

  bool isLoggedIn() {
    return _client.auth.currentSession != null;
  }

  String? getAccessToken() {
    return _client.auth.currentSession?.accessToken;
  }

  Future<bool> isAdmin() async {
    final session = _client.auth.currentSession;
    if (session == null) return false;

    final userId = session.user.id;

    try {
      final response = await _client
          .from('profiles')
          .select('role')
          .eq('id', userId)
          .single();

      return response['role'] == 'admin';
    } catch (e) {
      return false;
    }
  }

  Future<Map<String, dynamic>?> getCurrentUser() async {
    final session = _client.auth.currentSession;
    if (session == null) return null;

    final user = session.user;
    return {
      'id': user.id,
      'email': user.email,
    };
  }

  Stream<AuthState> get authStateChanges {
    return _client.auth.onAuthStateChange;
  }
}
