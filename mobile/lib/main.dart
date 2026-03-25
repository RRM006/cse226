import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'screens/login_screen.dart';
import 'screens/upload_screen.dart';
import 'screens/result_screen.dart';
import 'screens/history_screen.dart';
import 'services/auth_service.dart';
import 'services/api_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    await AuthService().initialize();
  } catch (e) {
    debugPrint('AuthService initialization error: $e');
  }
  runApp(const NSUAuditApp());
}

class NSUAuditApp extends StatelessWidget {
  const NSUAuditApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NSU Audit Core',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const AuthWrapper(),
    );
  }
}

class AuthWrapper extends StatefulWidget {
  const AuthWrapper({super.key});

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  final AuthService _authService = AuthService();
  Map<String, dynamic>? _currentResult;
  String? _authError;

  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  bool _isNsuEmail(String? email) {
    return email != null && email.toLowerCase().endsWith('@northsouth.edu');
  }

  void _checkAuth() {
    if (_authService.isLoggedIn()) {
      final session = _authService.getCurrentSession();
      final email = session?.user.email;

      if (!_isNsuEmail(email)) {
        _authError =
            'Only @northsouth.edu accounts are allowed. Please sign in with your NSU email.';
        _onLogout();
        return;
      }

      final token = _authService.getAccessToken();
      if (token != null) {
        ApiService().setAccessToken(token);
      }
      setState(() {});
    }
  }

  void _onLoginSuccess() async {
    final session = _authService.getCurrentSession();
    final email = session?.user.email;

    if (!_isNsuEmail(email)) {
      await _authService.signOut();
      ApiService().clearAccessToken();
      setState(() {
        _authError =
            'Only @northsouth.edu accounts are allowed. Please sign in with your NSU email.';
      });
      return;
    }

    final token = _authService.getAccessToken();
    if (token != null) {
      ApiService().setAccessToken(token);
    }
    setState(() {
      _authError = null;
    });
  }

  void _onLogout() async {
    await _authService.signOut();
    ApiService().clearAccessToken();
    setState(() {});
  }

  void _onResult(Map<String, dynamic> result) {
    setState(() {
      _currentResult = result;
    });
  }

  void _onNewAudit() {
    setState(() {
      _currentResult = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (!_authService.isLoggedIn()) {
      return LoginScreen(
        onLoginSuccess: _onLoginSuccess,
        errorMessage: _authError,
        onClearError: () {
          setState(() {
            _authError = null;
          });
        },
      );
    }

    if (_currentResult != null) {
      return ResultScreen(
        result: _currentResult!,
        onNewAudit: _onNewAudit,
        onViewHistory: () {
          context.push('/history');
        },
      );
    }

    return UploadScreen(
      onResult: _onResult,
      onLogout: _onLogout,
    );
  }
}
