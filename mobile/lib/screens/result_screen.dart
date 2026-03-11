import 'package:flutter/material.dart';

class ResultScreen extends StatelessWidget {
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
  Widget build(BuildContext context) {
    final summary = result['summary'] ?? {};
    final isEligible = summary['eligible'] ?? false;
    final resultText = result['result_text'] ?? '';
    final ocrData = result['ocr_confidence'] != null;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Audit Result'),
        backgroundColor: const Color(0xFF1E3A5F),
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: onNewAudit,
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: onViewHistory,
            tooltip: 'View History',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
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
                            isEligible ? 'Eligible for Graduation' : 'Not Eligible',
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
                    _buildInfoRow('Program', result['program'] ?? ''),
                    _buildInfoRow('Level', 'Level ${result['audit_level'] ?? ''}'),
                    _buildInfoRow('Student ID', result['student_id'] ?? 'N/A'),
                    const SizedBox(height: 16),
                    _buildInfoRow('Total Credits', '${summary['total_credits'] ?? 0}'),
                    _buildInfoRow('CGPA', '${summary['cgpa']?.toStringAsFixed(2) ?? '0.00'}'),
                    _buildInfoRow('Standing', summary['standing'] ?? 'N/A'),
                    if (summary['missing_courses'] != null && (summary['missing_courses'] as List).isNotEmpty)
                      _buildInfoRow('Missing Courses', '${summary['missing_courses'].length}'),
                    
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
                      _buildInfoRow('OCR Confidence', '${((result['ocr_confidence'] ?? 0) * 100).toStringAsFixed(1)}%'),
                      _buildInfoRow('Extracted Rows', '${result['ocr_extracted_rows'] ?? 0}'),
                      if (result['ocr_warnings'] != null && (result['ocr_warnings'] as List).isNotEmpty) ...[
                        const SizedBox(height: 8),
                        const Text(
                          'OCR Warnings:',
                          style: TextStyle(color: Colors.orange),
                        ),
                        ...(result['ocr_warnings'] as List).map((w) => Text(
                          '• $w',
                          style: const TextStyle(color: Colors.orange, fontSize: 12),
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
                    onPressed: onViewHistory,
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
                    onPressed: onNewAudit,
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
