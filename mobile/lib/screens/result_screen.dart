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
    final resultJson = widget.result['result_json'] ?? widget.result;
    final detectedId = resultJson['student_id'] ?? '';
    _studentIdController.text = detectedId;

    if (_isValidStudentId(detectedId)) {
      _idSaved = true;
    }
  }

  @override
  void dispose() {
    _studentIdController.dispose();
    super.dispose();
  }

  Future<void> _handleSaveStudentId() async {
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

      final resultJson = widget.result['result_json'] ?? widget.result;
      final summary = widget.result['summary'] ?? {};

      await apiService.saveAuditWithStudentId(
        studentId: studentId,
        program: widget.result['program'] ?? resultJson['program'] ?? '',
        inputType: widget.result['input_type'] ?? 'csv',
        waivers: List<String>.from(resultJson['waivers_applied'] ?? []),
        auditLevel:
            widget.result['audit_level'] ?? resultJson['audit_level'] ?? 3,
        resultJson: {...resultJson, 'student_id': studentId},
        resultText: widget.result['result_text'] ?? '',
      );

      setState(() {
        _idSaved = true;
        _editingId = false;
      });
    } catch (e) {
      setState(() => _idError = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      setState(() => _savingId = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final summary = widget.result['summary'] ?? {};
    final resultJson = widget.result['result_json'] ?? widget.result;
    final isEligible = summary['eligible'] ?? false;
    final resultText = widget.result['result_text'] ?? '';
    final ocrData = widget.result['ocr_confidence'] != null;

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
            // NSU Student ID Confirmation — always shows until valid ID confirmed
            _buildIdConfirmCard(),

            const SizedBox(height: 16),

            // Summary Card
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
                        widget.result['program'] ??
                            resultJson['program'] ??
                            ''),
                    _buildInfoRow('Level',
                        'Level ${widget.result['audit_level'] ?? resultJson['audit_level'] ?? ''}'),
                    _buildInfoRow(
                        'Student ID', resultJson['student_id'] ?? 'N/A'),
                    const SizedBox(height: 16),
                    _buildInfoRow(
                        'Total Credits', '${summary['total_credits'] ?? 0}'),
                    _buildInfoRow('CGPA',
                        '${summary['cgpa']?.toStringAsFixed(2) ?? '0.00'}'),
                    _buildInfoRow('Standing', summary['standing'] ?? 'N/A'),
                    if (summary['missing_courses'] != null &&
                        (summary['missing_courses'] as List).isNotEmpty)
                      _buildInfoRow('Missing Courses',
                          '${summary['missing_courses'].length}'),
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
                          '${((widget.result['ocr_confidence'] ?? 0) * 100).toStringAsFixed(1)}%'),
                      _buildInfoRow('Extracted Rows',
                          '${widget.result['ocr_extracted_rows'] ?? 0}'),
                      if (widget.result['ocr_warnings'] != null &&
                          (widget.result['ocr_warnings'] as List)
                              .isNotEmpty) ...[
                        const SizedBox(height: 8),
                        const Text(
                          'OCR Warnings:',
                          style: TextStyle(color: Colors.orange),
                        ),
                        ...(widget.result['ocr_warnings'] as List)
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

            // Full Result Text
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
              child: SelectableText(
                resultText,
                style: const TextStyle(
                  fontFamily: 'monospace',
                  fontSize: 12,
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Action Buttons
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
          Text(
            value,
            style: const TextStyle(
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}
