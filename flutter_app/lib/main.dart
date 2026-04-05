import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/app_theme.dart';
import 'providers/auth_provider.dart';
import 'providers/match_provider.dart';
import 'providers/wallet_provider.dart';
import 'screens/auth/login_screen.dart';
import 'screens/home/home_screen.dart';
import 'services/api_service.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const FfTournamentApp());
}

class FfTournamentApp extends StatelessWidget {
  const FfTournamentApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider(create: (_) => ApiService()),
        ChangeNotifierProxyProvider<ApiService, AuthProvider>(
          create: (context) => AuthProvider(context.read<ApiService>()),
          update: (context, api, previous) => previous ?? AuthProvider(api),
        ),
        ChangeNotifierProxyProvider<ApiService, MatchProvider>(
          create: (context) => MatchProvider(context.read<ApiService>()),
          update: (context, api, previous) => previous ?? MatchProvider(api),
        ),
        ChangeNotifierProxyProvider<ApiService, WalletProvider>(
          create: (context) => WalletProvider(context.read<ApiService>()),
          update: (context, api, previous) => previous ?? WalletProvider(api),
        ),
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'FF Arena',
        theme: AppTheme.darkTheme,
        home: const AppEntryPoint(),
      ),
    );
  }
}

class AppEntryPoint extends StatefulWidget {
  const AppEntryPoint({super.key});

  @override
  State<AppEntryPoint> createState() => _AppEntryPointState();
}

class _AppEntryPointState extends State<AppEntryPoint> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => context.read<AuthProvider>().bootstrap());
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (_, auth, __) {
        if (auth.loading) {
          return const Scaffold(body: Center(child: CircularProgressIndicator()));
        }
        return auth.isAuthenticated ? const HomeScreen() : const LoginScreen();
      },
    );
  }
}
