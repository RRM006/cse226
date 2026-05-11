import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/auth_provider.dart';
import 'services/auth_service.dart';
import 'services/api_service.dart';
import 'screens/auth/login_gate.dart';
import 'screens/auth/student_login.dart';
import 'screens/login_screen.dart';
import 'screens/upload_screen.dart';
import 'screens/result_screen.dart';
import 'screens/history_screen.dart';
import 'screens/student/student_dashboard.dart';
import 'screens/student/student_audit_results.dart';
import 'screens/student/student_requests.dart';
import 'screens/student/change_password.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AuthService().initialize();
  runApp(
    ChangeNotifierProvider(
      create: (_) => AuthProvider(),
      child: const NSUAuditApp(),
    ),
  );
}

class NSUAuditApp extends StatelessWidget {
  const NSUAuditApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NSU Audit Core',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1E3A5F)),
      ),
      home: const AuthWrapper(),
      routes: {
        '/student/dashboard': (_) => const StudentDashboard(),
        '/student/audit-results': (_) => const StudentAuditResults(),
        '/student/requests': (_) => const StudentRequests(),
        '/student/change-password': (_) => const ChangePassword(),
        '/history': (_) => const _HistoryRoute(),
      },
    );
  }
}

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, auth, _) {
        if (auth.isLoading) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        if (auth.isStudent) {
          return const StudentDashboard();
        }

        if (auth.isAdmin) {
          return const AdminHome();
        }

        return LoginGate(
          onStudentLoginSuccess: () {
            Navigator.pushReplacementNamed(context, '/student/dashboard');
          },
          onAdminLoginSuccess: () {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (_) => const AdminHome()),
            );
          },
        );
      },
    );
  }
}

class AdminHome extends StatefulWidget {
  const AdminHome({super.key});

  @override
  State<AdminHome> createState() => _AdminHomeState();
}

class _AdminHomeState extends State<AdminHome> {
  Map<String, dynamic>? _currentResult;

  void _onResult(Map<String, dynamic> result, BuildContext context) {
    print('[DEBUG] _onResult called with keys: ${result.keys.toList()}');

    if (!mounted) {
      print('[WARN] _onResult: widget already unmounted, ignoring');
      return;
    }

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) {
        print('[WARN] _onResult: widget unmounted after postFrameCallback');
        return;
      }
      try {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => ResultScreen(
              result: result,
              onNewAudit: () {
                Navigator.pop(context);
              },
              onViewHistory: () {
                Navigator.pop(context);
                Navigator.pushNamed(context, '/history');
              },
            ),
          ),
        ).catchError((e) {
          print('[ERROR] Navigation error: $e');
        });
      } catch (e, stack) {
        print('[ERROR] _onResult error: $e');
        print('[ERROR] Stack: $stack');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Navigation error: $e')),
        );
      }
    });
  }

  void _onNewAudit() {
    setState(() {
      _currentResult = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_currentResult != null) {
      return ResultScreen(
        result: _currentResult!,
        onNewAudit: _onNewAudit,
        onViewHistory: () {
          Navigator.pushNamed(context, '/history');
        },
      );
    }

    return UploadScreen(
      onResult: (result) => _onResult(result, context),
      onLogout: () async {
        final auth = context.read<AuthProvider>();
        await auth.logout();
        if (mounted) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (_) => const AuthWrapper()),
          );
        }
      },
      onViewHistory: () {
        Navigator.pushNamed(context, '/history');
      },
    );
  }
}

class _HistoryRoute extends StatefulWidget {
  const _HistoryRoute();

  @override
  State<_HistoryRoute> createState() => _HistoryRouteState();
}

class _HistoryRouteState extends State<_HistoryRoute> {
  Map<String, dynamic>? _selectedScan;
  bool _isLoading = false;

  Future<void> _loadScan(String scanId) async {
    setState(() {
      _isLoading = true;
    });

    try {
      final apiService = ApiService();
      final authService = AuthService();
      final token = authService.getAccessToken();
      if (token != null) {
        apiService.setAccessToken(token);
      }

      final scanData = await apiService.getScanById(scanId);

      if (mounted) {
        setState(() {
          _selectedScan = scanData;
          _isLoading = false;
        });

        // Show result screen
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => ResultScreen(
              result: scanData,
              onNewAudit: () {
                Navigator.pop(context);
              },
              onViewHistory: () {
                Navigator.pop(context);
                Navigator.pushNamed(context, '/history');
              },
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading scan: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return HistoryScreen(
      onViewScan: _loadScan,
      onBack: () => Navigator.pop(context),
    );
  }
}
