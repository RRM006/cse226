class AuditResult {
  final String id;
  final String studentId;
  final String program;
  final int auditLevel;
  final bool eligible;
  final Map<String, dynamic>? resultJson;
  final String? resultText;
  final String? createdAt;

  AuditResult({
    required this.id,
    required this.studentId,
    required this.program,
    required this.auditLevel,
    required this.eligible,
    this.resultJson,
    this.resultText,
    this.createdAt,
  });

  factory AuditResult.fromJson(Map<String, dynamic> json) {
    return AuditResult(
      id: json['id'] ?? '',
      studentId: json['student_id'] ?? '',
      program: json['program'] ?? '',
      auditLevel: json['audit_level'] ?? 0,
      eligible: json['eligible'] ?? false,
      resultJson: json['result_json'],
      resultText: json['result_text'],
      createdAt: json['created_at'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'student_id': studentId,
      'program': program,
      'audit_level': auditLevel,
      'eligible': eligible,
      'result_json': resultJson,
      'result_text': resultText,
      'created_at': createdAt,
    };
  }
}
