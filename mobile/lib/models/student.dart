class Student {
  final String id;
  final String studentId;
  final String name;
  final String email;
  final bool isFirstLogin;
  final String? createdAt;

  Student({
    required this.id,
    required this.studentId,
    required this.name,
    required this.email,
    required this.isFirstLogin,
    this.createdAt,
  });

  factory Student.fromJson(Map<String, dynamic> json) {
    return Student(
      id: json['id'] ?? '',
      studentId: json['student_id'] ?? '',
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      isFirstLogin: json['is_first_login'] ?? false,
      createdAt: json['created_at'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'student_id': studentId,
      'name': name,
      'email': email,
      'is_first_login': isFirstLogin,
      'created_at': createdAt,
    };
  }
}
