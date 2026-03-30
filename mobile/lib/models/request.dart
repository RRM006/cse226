class StudentRequest {
  final String id;
  final String message;
  final String status;
  final String? adminNotes;
  final String? createdAt;
  final String? updatedAt;

  StudentRequest({
    required this.id,
    required this.message,
    required this.status,
    this.adminNotes,
    this.createdAt,
    this.updatedAt,
  });

  factory StudentRequest.fromJson(Map<String, dynamic> json) {
    return StudentRequest(
      id: json['id'] ?? '',
      message: json['message'] ?? '',
      status: json['status'] ?? 'pending',
      adminNotes: json['admin_notes'],
      createdAt: json['created_at'],
      updatedAt: json['updated_at'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'message': message,
      'status': status,
      'admin_notes': adminNotes,
      'created_at': createdAt,
      'updated_at': updatedAt,
    };
  }
}
