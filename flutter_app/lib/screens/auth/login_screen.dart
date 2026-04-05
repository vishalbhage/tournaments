import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import 'signup_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  String? error;

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Spacer(),
              const Text('FF Arena', style: TextStyle(fontSize: 34, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              const Text('Join paid Free Fire tournaments and win coins.'),
              const SizedBox(height: 24),
              TextField(controller: _email, decoration: const InputDecoration(labelText: 'Email')),
              const SizedBox(height: 12),
              TextField(controller: _password, obscureText: true, decoration: const InputDecoration(labelText: 'Password')),
              const SizedBox(height: 12),
              if (error != null) Text(error!, style: const TextStyle(color: Colors.redAccent)),
              const SizedBox(height: 12),
              ElevatedButton(
                onPressed: auth.loading
                    ? null
                    : () async {
                        try {
                          await context.read<AuthProvider>().login(_email.text.trim(), _password.text.trim());
                        } catch (e) {
                          setState(() => error = e.toString().replaceFirst('Exception: ', ''));
                        }
                      },
                child: Text(auth.loading ? 'Please wait...' : 'Login'),
              ),
              const SizedBox(height: 12),
              OutlinedButton(
                onPressed: auth.loading
                    ? null
                    : () async {
                        try {
                          await context.read<AuthProvider>().signInWithGoogle();
                        } catch (e) {
                          setState(() => error = e.toString().replaceFirst('Exception: ', ''));
                        }
                      },
                child: const Text('Continue with Google'),
              ),
              const SizedBox(height: 12),
              TextButton(
                onPressed: () {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => const SignupScreen()));
                },
                child: const Text('Create an account'),
              ),
              const Spacer(),
            ],
          ),
        ),
      ),
    );
  }
}
