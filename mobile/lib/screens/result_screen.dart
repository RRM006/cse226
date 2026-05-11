import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

class ResultScreen extends StatefulWidget {
  final Map<String, dynamic> result;
  final VoidCallback onNewAudit;
  final VoidCallback onViewHistory;

  const ResultScreen({
    super.key,
    required this.result,
    required this.onNewAudit,
    required this.onViewHistory,
  });

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  final TextEditingController _studentIdController = TextEditingController();
  bool _idSaved = false;
  bool _savingId = false;
  String? _idError;
  bool _editingId = false;

  bool get _isCancelled => !mounted;

  bool _isValidStudentId(String id) {
    final trimmed = id.trim();
    if (trimmed.isEmpty) return false;
    if (trimmed.length != 10) return false;
    if (!trimmed.startsWith('2')) return false;
    return RegExp(r'^2\d{9}$').hasMatch(trimmed);
  }

  bool get _alreadyValid {
    final detectedId = _studentIdController.text.trim();
    return _isValidStudentId(detectedId) && !_editingId && _idSaved;
  }

  @override
  void initState() {
    super.initState();
    final resultJson = _get(widget.result, 'result_json') ?? widget.result;
    final detectedId = _get(resultJson, 'student_id') ?? '';
    _studentIdController.text = detectedId ?? '';

    if (detectedId != null && _isValidStudentId(detectedId)) {
      _idSaved = true;
    }
  }

  @override
  void dispose() {
    _studentIdController.dispose();
    super.dispose();
  }

  T? _get<T>(Map<String, dynamic>? map, String key, {T? defaultValue}) {
    if (map == null) return defaultValue;
    return map[key] as T? ?? defaultValue;
  }

  Map<String, dynamic> _getMap(Map<String, dynamic>? map, String key) {
    return _get<Map<String, dynamic>>(map, key) ?? {};
  }

  Future<void> _handleSaveStudentId() async {
    if (!mounted) return;

    final studentId = _studentIdController.text.trim();
    if (studentId.isEmpty) {
      setState(() => _idError = 'Student ID is required');
      return;
    }
    if (!_isValidStudentId(studentId)) {
      setState(() => _idError =
          'Invalid format. Must be 10 digits starting with 2 (e.g., 2211234567)');
      return;
    }

    setState(() {
      _savingId = true;
      _idError = null;
    });

    try {
      final apiService = ApiService();
      final authService = AuthService();
      final token = authService.getAccessToken();
      if (token != null) {
        apiService.setAccessToken(token);
      }

      final resultJson = _getMap(widget.result, 'result_json');
      final program = _get<String>(widget.result, 'program') ??
          _get<String>(resultJson, 'program') ??
          '';
      final auditLevel = _get<int>(widget.result, 'audit_level') ??
          _get<int>(resultJson, 'audit_level') ??
          3;
      final waivers =
          _get<List>(resultJson, 'waivers_applied')?.cast<String>() ?? [];
      final resultText = _get<String>(widget.result, 'result_text') ?? '';

      await apiService.saveAuditWithStudentId(
        studentId: studentId,
        program: program,
        inputType: _get<String>(widget.result, 'input_type') ?? 'csv',
        waivers: waivers,
        auditLevel: auditLevel,
        resultJson: {...resultJson, 'student_id': studentId},
        resultText: resultText,
      );

      if (!mounted) return;
      setState(() {
        _idSaved = true;
        _editingId = false;
      });
    } catch (e) {
      if (!mounted) return;
      String msg = e.toString();
      if (msg.contains('Exception: '))
        msg = msg.replaceFirst('Exception: ', '');
      if (msg.contains('ApiException: ')) {
        msg = msg.replaceFirst(RegExp(r'ApiException: \d+ - '), '');
      }
      setState(() => _idError = msg);
    } finally {
      if (mounted) setState(() => _savingId = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final summary = _getMap(widget.result, 'summary');
    final resultJson = _getMap(widget.result, 'result_json');

    final eligibleRaw = summary['eligible'] ?? resultJson['eligible'] ?? false;
    final bool isEligible;
    if (eligibleRaw is bool) {
      isEligible = eligibleRaw;
    } else if (eligibleRaw is String) {
      isEligible = eligibleRaw.toString().toLowerCase() == 'true';
    } else {
      isEligible = eligibleRaw == true;
    }

    final resultText = _get<String>(widget.result, 'result_text') ?? '';
    final ocrConfidence = _get<num>(widget.result, 'ocr_confidence');
    final ocrData = ocrConfidence != null;

    if (summary.isEmpty && resultJson.isEmpty && widget.result.isEmpty) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Audit Result'),
          backgroundColor: const Color(0xFF1E3A5F),
          foregroundColor: Colors.white,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: widget.onNewAudit,
          ),
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              const Text('No result data received',
                  style: TextStyle(fontSize: 18)),
              const SizedBox(height: 8),
              ElevatedButton(
                onPressed: widget.onNewAudit,
                child: const Text('Go Back'),
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Audit Result'),
        backgroundColor: const Color(0xFF1E3A5F),
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: widget.onNewAudit,
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: widget.onViewHistory,
            tooltip: 'View History',
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await context.read<AuthProvider>().logout();
              if (mounted) {
                Navigator.pushReplacementNamed(context, '/');
              }
            },
            tooltip: 'Logout',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildIdConfirmCard(),
            const SizedBox(height: 16),
            Card(
              elevation: 4,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          isEligible ? Icons.check_circle : Icons.cancel,
                          color: isEligible ? Colors.green : Colors.red,
                          size: 32,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            isEligible
                                ? 'Eligible for Graduation'
                                : 'Not Eligible',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: isEligible ? Colors.green : Colors.red,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const Divider(height: 24),
                    _buildInfoRow(
                        'Program',
                        _get<String>(widget.result, 'program') ??
                            _get<String>(resultJson, 'program') ??
                            _get<String>(resultJson, 'program_name') ??
                            'N/A'),
                    _buildInfoRow('Level',
                        'Level ${_get<int>(widget.result, 'audit_level') ?? _get<int>(resultJson, 'audit_level') ?? '?'}'),
                    _buildInfoRow(
                        'Student ID',
                        _get<String>(resultJson, 'student_id') ??
                            _get<String>(resultJson, 'studentID') ??
                            'N/A'),
                    const SizedBox(height: 16),
                    _buildInfoRow('Total Credits',
                        '${_get<num>(summary, 'total_credits') ?? _get<num>(resultJson, 'total_credits') ?? 0}'),
                    _buildInfoRow('CGPA',
                        '${((_get<num>(summary, 'cgpa') ?? _get<num>(resultJson, 'cgpa')) ?? 0.0).toStringAsFixed(2)}'),
                    _buildInfoRow(
                        'Standing',
                        _get<String>(summary, 'standing') ??
                            _get<String>(resultJson, 'standing') ??
                            'N/A'),
                    _buildInfoRow('Missing Courses',
                        '${(_get<List>(summary, 'missing_courses') ?? _get<List>(resultJson, 'missing_courses'))?.length ?? 0}'),
                    if (ocrData) ...[
                      const Divider(height: 24),
                      const Text(
                        'OCR Information',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      const SizedBox(height: 8),
                      _buildInfoRow('OCR Confidence',
                          '${((ocrConfidence ?? 0) * 100).toStringAsFixed(1)}%'),
                      _buildInfoRow('Extracted Rows',
                          '${_get<int>(widget.result, 'ocr_extracted_rows') ?? 0}'),
                      if (_get<List>(widget.result, 'ocr_warnings')
                              ?.isNotEmpty ==
                          true) ...[
                        const SizedBox(height: 8),
                        const Text(
                          'OCR Warnings:',
                          style: TextStyle(color: Colors.orange),
                        ),
                        ...(_get<List>(widget.result, 'ocr_warnings') ?? [])
                            .map((w) => Text(
                                  '• $w',
                                  style: const TextStyle(
                                      color: Colors.orange, fontSize: 12),
                                )),
                      ],
                    ],
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'Detailed Report',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.grey[300]!),
              ),
              constraints: const BoxConstraints(maxHeight: 300),
              child: SingleChildScrollView(
                child: SelectableText(
                  resultText.isEmpty
                      ? 'No detailed report available.'
                      : resultText,
                  style: const TextStyle(
                    fontFamily: 'monospace',
                    fontSize: 12,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: widget.onViewHistory,
                    icon: const Icon(Icons.history),
                    label: const Text('History'),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: widget.onNewAudit,
                    icon: const Icon(Icons.add),
                    label: const Text('New Audit'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF1E3A5F),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildIdConfirmCard() {
    final detectedId = _studentIdController.text.trim();
    return Card(
      elevation: 4,
      color: _alreadyValid ? Colors.green.shade50 : Colors.amber.shade50,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: _alreadyValid ? Colors.green.shade300 : Colors.amber.shade300,
          width: 2,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  _alreadyValid ? Icons.check_circle : Icons.warning_amber,
                  color: _alreadyValid ? Colors.green : Colors.amber,
                ),
                const SizedBox(width: 8),
                Text(
                  _alreadyValid
                      ? 'Student ID Confirmed'
                      : 'Confirm NSU Student ID',
                  style: TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 16,
                    color: _alreadyValid
                        ? Colors.green.shade700
                        : Colors.amber.shade700,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (_alreadyValid) ...[
              Text(
                'Audit saved for student $detectedId',
                style: TextStyle(color: Colors.green.shade700),
              ),
              const SizedBox(height: 4),
              Text(
                'Student can now view this result in their portal',
                style: TextStyle(color: Colors.green.shade600, fontSize: 12),
              ),
              const SizedBox(height: 8),
              TextButton.icon(
                onPressed: () => setState(() {
                  _idSaved = false;
                  _editingId = true;
                }),
                icon: const Icon(Icons.edit, size: 16),
                label: const Text('Change ID'),
              ),
            ] else ...[
              Text(
                _editingId || detectedId.isEmpty || detectedId == 'Unknown'
                    ? 'Enter the NSU student ID for this audit:'
                    : 'Auto-detected ID: $detectedId. Confirm or correct it:',
                style: TextStyle(color: Colors.amber.shade700, fontSize: 13),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _studentIdController,
                keyboardType: TextInputType.number,
                maxLength: 10,
                decoration: InputDecoration(
                  hintText: 'e.g., 2211234567',
                  border: const OutlineInputBorder(),
                  errorText: _idError,
                  filled: true,
                  fillColor: Colors.white,
                  counterText: '',
                ),
                onChanged: (_) {
                  if (mounted) setState(() {});
                },
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _savingId ? null : _handleSaveStudentId,
                      icon: _savingId
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(
                                  strokeWidth: 2, color: Colors.white))
                          : const Icon(Icons.save, size: 16),
                      label: Text(_savingId ? 'Saving...' : 'Save & Confirm'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF1E3A5F),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                'Must be 10 digits starting with 2. If the student doesn\'t exist, an account will be auto-created with default password = student ID',
                style: TextStyle(color: Colors.amber.shade600, fontSize: 11),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: Colors.grey,
            ),
          ),
          Flexible(
            child: Text(
              value,
              style: const TextStyle(
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.end,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}
