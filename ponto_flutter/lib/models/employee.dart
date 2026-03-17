class Employee {
  final int id;
  final String empId;
  final String name;
  final String? department;
  final bool isActive;
  final String todayStatus;

  Employee({
    required this.id,
    required this.empId,
    required this.name,
    required this.department,
    required this.isActive,
    required this.todayStatus,
  });

  factory Employee.fromJson(Map<String, dynamic> json) {
    return Employee(
      id: json['id'] as int,
      empId: json['emp_id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      department: json['department'] as String?,
      isActive: json['is_active'] as bool? ?? true,
      todayStatus: json['today_status'] as String? ?? 'absent',
    );
  }
}
