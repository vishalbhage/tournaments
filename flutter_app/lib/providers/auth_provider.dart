import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:google_sign_in/google_sign_in.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';

class AuthProvider extends ChangeNotifier {
  final ApiService api;
  bool loading = false;
  UserModel? user;

  AuthProvider(this.api);

  bool get isAuthenticated => user != null;

  Future<void> bootstrap() async {
    loading = true;
    notifyListeners();
    await api.loadToken();
    try {
      final response = await api.get('/auth/me');
      user = UserModel.fromJson(response);
    } catch (_) {
      user = null;
    }
    loading = false;
    notifyListeners();
  }

  Future<void> login(String email, String password) async {
    loading = true;
    notifyListeners();
    try {
      final response = await api.post('/auth/login', {'email': email, 'password': password});
      await api.saveToken(response['token']);
      user = UserModel.fromJson(response['user']);
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<void> signup({
    required String email,
    required String password,
    required String username,
    required String fullName,
    String? referralCode,
    File? photo,
  }) async {
    loading = true;
    notifyListeners();
    try {
      final response = await api.multipartPost('/auth/signup', {
        'email': email,
        'password': password,
        'username': username,
        'full_name': fullName,
        if (referralCode != null && referralCode.isNotEmpty) 'referral_code': referralCode,
      }, photo);
      await api.saveToken(response['token']);
      user = UserModel.fromJson(response['user']);
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<void> signInWithGoogle() async {
    loading = true;
    notifyListeners();
    try {
      final googleSignIn = GoogleSignIn.instance;
      await googleSignIn.initialize();
      final account = await googleSignIn.authenticate();
      final response = await api.post('/auth/google', {
        'email': account.email,
        'google_id': account.id,
        'full_name': account.displayName,
        'photo_url': account.photoUrl,
        'username': account.email.split('@').first,
      });
      await api.saveToken(response['token']);
      user = UserModel.fromJson(response['user']);
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<void> updateProfile({String? fullName, String? username, File? photo}) async {
    final response = await api.multipartPut('/auth/profile', {
      if (fullName != null) 'full_name': fullName,
      if (username != null) 'username': username,
    }, photo);
    user = UserModel.fromJson(response);
    notifyListeners();
  }

  Future<void> logout() async {
    await api.clearToken();
    user = null;
    notifyListeners();
  }
}
