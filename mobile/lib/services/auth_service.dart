import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  final SupabaseClient _supabase = Supabase.instance.client;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  static const String _supabaseUrl = 'https://your-project.supabase.co';
  static const String _supabaseAnonKey = 'your-anon-key';

  Future<void> initialize() async {
    await Supabase.initialize(
      url: _supabaseUrl,
      anonKey: _supabaseAnonKey,
    );
  }

  Future<AuthResponse> signInWithGoogle() async {
    return await _supabase.auth.signInWithOAuth(
      OAuthProvider.google,
      redirectTo: 'nsu-audit-mobile://login-callback',
    );
  }

  Future<void> signOut() async {
    await _supabase.auth.signOut();
    await _storage.delete(key: 'session');
  }

  Session? getCurrentSession() {
    return _supabase.auth.currentSession;
  }

  bool isLoggedIn() {
    return _supabase.auth.currentSession != null;
  }

  String? getAccessToken() {
    return _supabase.auth.currentSession?.accessToken;
  }

  Future<bool> isAdmin() async {
    final session = _supabase.auth.currentSession;
    if (session == null) return false;

    final userId = session.user.id;
    
    try {
      final response = await _supabase
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
    final session = _supabase.auth.currentSession;
    if (session == null) return null;

    final user = session.user;
    return {
      'id': user.id,
      'email': user.email,
    };
  }

  Stream<AuthState> get authStateChanges {
    return _supabase.auth.onAuthStateChange;
  }
}
