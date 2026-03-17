import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final Map<String, dynamic>? payload;

  ApiException(this.message, {this.statusCode, this.payload});

  @override
  String toString() => message;
}

class ApiService {
  static Map<String, dynamic> _decodeBody(http.Response response) {
    if (response.body.trim().isEmpty) {
      return {};
    }
    final decoded = jsonDecode(response.body);
    if (decoded is Map<String, dynamic>) {
      return decoded;
    }
    return {'data': decoded};
  }

  static Map<String, dynamic> _readErrorPayload(Map<String, dynamic> body) {
    final detail =
        body['error'] ?? body['message'] ?? body['detail'] ?? 'Erro inesperado';
    return {
      'message': detail.toString(),
      'error_code': body['error_code']?.toString(),
    };
  }

  static Map<String, dynamic> _handleResponse(http.Response response) {
    final body = _decodeBody(response);
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return body;
    }
    final err = _readErrorPayload(body);
    throw ApiException(
      err['message'] as String,
      statusCode: response.statusCode,
      payload: {
        ...body,
        'error_code': err['error_code'],
      },
    );
  }

  static Future<Map<String, dynamic>> recognizeImage(String imageBase64) async {
    final response = await http.post(
      Uri.parse('${Config.apiBaseUrl}/recognize-image/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'image_base64': imageBase64,
        'threshold': Config.recognitionThreshold,
      }),
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> registerLog(
    String empId,
    String tipo,
    double confidence,
  ) async {
    final response = await http.post(
      Uri.parse('${Config.apiBaseUrl}/register-log/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'emp_id': empId,
        'mode': tipo,
        'confidence': confidence,
      }),
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> registerEmployee(
    String name,
    String imageBase64,
  ) async {
    final response = await http.post(
      Uri.parse('${Config.apiBaseUrl}/register-employee-image/'),
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Password': Config.adminPassword,
      },
      body: jsonEncode({
        'name': name,
        'image_base64': imageBase64,
      }),
    );
    return _handleResponse(response);
  }
}
