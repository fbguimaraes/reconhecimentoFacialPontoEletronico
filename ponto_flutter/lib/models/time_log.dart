class TimeLog {
  final int id;
  final String employeeName;
  final String employeeEmpId;
  final String tipo;
  final DateTime? horario;
  final String horarioFmt;
  final String data;
  final double confidence;

  TimeLog({
    required this.id,
    required this.employeeName,
    required this.employeeEmpId,
    required this.tipo,
    required this.horario,
    required this.horarioFmt,
    required this.data,
    required this.confidence,
  });

  factory TimeLog.fromJson(Map<String, dynamic> json) {
    return TimeLog(
      id: json['id'] as int,
      employeeName: json['employee_name'] as String? ?? '',
      employeeEmpId: json['employee_emp_id'] as String? ?? '',
      tipo: json['tipo'] as String? ?? '',
      horario: json['horario'] != null
          ? DateTime.tryParse(json['horario'] as String)
          : null,
      horarioFmt: json['horario_fmt'] as String? ?? '',
      data: json['data'] as String? ?? '',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
