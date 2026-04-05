import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../core/constants.dart';

class ApiService {
  String? _token;

  Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('token');
  }

  Future<void> saveToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', token);
  }

  Future<void> clearToken() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
  }

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_token != null) 'Authorization': 'Bearer $_token',
      };

  Future<Map<String, dynamic>> post(String path, Map<String, dynamic> data) async {
    final response = await http.post(
      Uri.parse('${AppConstants.baseUrl}$path'),
      headers: _headers,
      body: jsonEncode(data),
    );
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> put(String path, Map<String, dynamic> data) async {
    final response = await http.put(
      Uri.parse('${AppConstants.baseUrl}$path'),
      headers: _headers,
      body: jsonEncode(data),
    );
    return _handleResponse(response);
  }

  Future<dynamic> get(String path) async {
    final response = await http.get(Uri.parse('${AppConstants.baseUrl}$path'), headers: _headers);
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> multipartPost(String path, Map<String, String> fields, File? file) async {
    final request = http.MultipartRequest('POST', Uri.parse('${AppConstants.baseUrl}$path'));
    if (_token != null) {
      request.headers['Authorization'] = 'Bearer $_token';
    }
    request.fields.addAll(fields);
    if (file != null) {
      request.files.add(await http.MultipartFile.fromPath('photo', file.path));
    }
    final streamed = await request.send();
    final response = await http.Response.fromStream(streamed);
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> multipartPut(String path, Map<String, String> fields, File? file) async {
    final request = http.MultipartRequest('PUT', Uri.parse('${AppConstants.baseUrl}$path'));
    if (_token != null) {
      request.headers['Authorization'] = 'Bearer $_token';
    }
    request.fields.addAll(fields);
    if (file != null) {
      request.files.add(await http.MultipartFile.fromPath('photo', file.path));
    }
    final streamed = await request.send();
    final response = await http.Response.fromStream(streamed);
    return _handleResponse(response);
  }

  dynamic _handleResponse(http.Response response) {
    final decoded = response.body.isEmpty ? {} : jsonDecode(response.body);
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return decoded;
    }
    throw Exception(decoded['message'] ?? 'Request failed');
  }
}
