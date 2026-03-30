import 'dart:async';
import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../services/auth_service.dart';
import '../services/storage_service.dart';

class LoginScreen extends StatefulWidget {
  final VoidCallback onLoginSuccess;
  final String? errorMessage;
  final VoidCallback? onClearError;

  const LoginScreen({
    super.key,
    required this.onLoginSuccess,
    this.errorMessage,
    this.onClearError,
  });

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  bool _isLoading = false;
  String? _errorMessage;
  final AuthService _authService = AuthService();
  final StorageService _storageService = StorageService();
  StreamSubscription<AuthState>? _authSubscription;

  @override
  void initState() {
    super.initState();
    if (widget.errorMessage != null) {
      _errorMessage = widget.errorMessage;
    }

    // Check if already logged in
    _checkExistingSession();

    // Listen for OAuth callback (when user comes back from browser)
    _authSubscription = _authService.authStateChanges.listen((AuthState state) {
      if (state.event == AuthChangeEvent.signedIn) {
        _handleSuccessfulLogin();
      }
    });
  }

  @override
  void dispose() {
    _authSubscription?.cancel();
    super.dispose();
  }

  void _checkExistingSession() {
    if (_authService.isLoggedIn()) {
      _handleSuccessfulLogin();
    }
  }

  Future<void> _handleSuccessfulLogin() async {
    final token = _authService.getAccessToken();
    if (token != null) {
      await _storageService.saveAdminToken(token);
      if (mounted) {
        widget.onLoginSuccess();
      }
    }
  }

  Future<void> _signInWithGoogle() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await _authService.signInWithGoogle();
      // Auth state listener above will handle the rest after OAuth callback
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = 'Login failed: ${e.toString()}';
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF1E3A5F),
              Color(0xFF0D2137),
            ],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.school,
                    size: 80,
                    color: Colors.white,
                  ),
                  const SizedBox(height: 24),
                  const Text(
                    'NSU Audit Core',
                    style: TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Graduation Audit Made Easy',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.white70,
                    ),
                  ),
                  const SizedBox(height: 48),
                  if (_errorMessage != null) ...[
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.red.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        _errorMessage!,
                        style: const TextStyle(color: Colors.red),
                        textAlign: TextAlign.center,
                      ),
                    ),
                    const SizedBox(height: 24),
                  ],
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton.icon(
                      onPressed: _isLoading ? null : _signInWithGoogle,
                      icon: _isLoading
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Icon(Icons.login),
                      label: Text(
                        _isLoading ? 'Signing in...' : 'Sign in with Google',
                        style: const TextStyle(fontSize: 16),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: const Color(0xFF1E3A5F),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  const Text(
                    'Only @northsouth.edu accounts are permitted',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.white54,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
