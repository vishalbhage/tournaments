import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});

  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _username = TextEditingController();
  final _fullName = TextEditingController();
  final _referral = TextEditingController();
  File? photo;
  String? error;

  Future<void> pickPhoto() async {
    final picked = await ImagePicker().pickImage(source: ImageSource.gallery, imageQuality: 80);
    if (picked != null) {
      setState(() => photo = File(picked.path));
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    return Scaffold(
      appBar: AppBar(title: const Text('Create account')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            GestureDetector(
              onTap: pickPhoto,
              child: CircleAvatar(
                radius: 42,
                backgroundImage: photo != null ? FileImage(photo!) : null,
                child: photo == null ? const Icon(Icons.person, size: 36) : null,
              ),
            ),
            const SizedBox(height: 18),
            TextField(controller: _fullName, decoration: const InputDecoration(labelText: 'Full name')),
            const SizedBox(height: 12),
            TextField(controller: _username, decoration: const InputDecoration(labelText: 'Username')),
            const SizedBox(height: 12),
            TextField(controller: _email, decoration: const InputDecoration(labelText: 'Email')),
            const SizedBox(height: 12),
            TextField(controller: _password, obscureText: true, decoration: const InputDecoration(labelText: 'Password')),
            const SizedBox(height: 12),
            TextField(controller: _referral, decoration: const InputDecoration(labelText: 'Referral code (optional)')),
            const SizedBox(height: 12),
            if (error != null) Text(error!, style: const TextStyle(color: Colors.redAccent)),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: auth.loading
                  ? null
                  : () async {
                      try {
                        await context.read<AuthProvider>().signup(
                              email: _email.text.trim(),
                              password: _password.text.trim(),
                              username: _username.text.trim(),
                              fullName: _fullName.text.trim(),
                              referralCode: _referral.text.trim(),
                              photo: photo,
                            );
                        if (mounted) Navigator.pop(context);
                      } catch (e) {
                        setState(() => error = e.toString().replaceFirst('Exception: ', ''));
                      }
                    },
              child: Text(auth.loading ? 'Please wait...' : 'Create account'),
            ),
          ],
        ),
      ),
    );
  }
}
