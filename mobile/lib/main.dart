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
      onResult: _onResult,
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
    );
  }
}

class _HistoryRoute extends StatelessWidget {
  const _HistoryRoute();

  @override
  Widget build(BuildContext context) {
    return HistoryScreen(
      onViewScan: (scanId) {
        // Load scan and show result
      },
      onBack: () => Navigator.pop(context),
    );
  }
}
