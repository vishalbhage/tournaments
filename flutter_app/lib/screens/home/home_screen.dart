import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/match_provider.dart';
import '../../providers/wallet_provider.dart';
import '../../widgets/match_card.dart';
import '../admin/admin_dashboard_screen.dart';
import '../matches/match_detail_screen.dart';
import '../wallet/wallet_screen.dart';
import '../matches/history_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int currentIndex = 0;

  @override
  void initState() {
    super.initState();
    Future.microtask(() async {
      await context.read<MatchProvider>().loadMatches();
      await context.read<WalletProvider>().loadWallet();
      await context.read<MatchProvider>().loadStats();
    });
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final pages = [
      _buildHomeTab(context),
      const WalletScreen(),
      const HistoryScreen(),
      if (auth.user?.isAdmin ?? false) const AdminDashboardScreen(),
    ];
    return Scaffold(
      appBar: AppBar(
        title: const Text('FF Arena'),
        actions: [
          IconButton(onPressed: () => context.read<AuthProvider>().logout(), icon: const Icon(Icons.logout)),
        ],
      ),
      body: pages[currentIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: currentIndex,
        onDestinationSelected: (value) => setState(() => currentIndex = value),
        destinations: [
          const NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
          const NavigationDestination(icon: Icon(Icons.account_balance_wallet), label: 'Wallet'),
          const NavigationDestination(icon: Icon(Icons.history), label: 'History'),
          if (auth.user?.isAdmin ?? false)
            const NavigationDestination(icon: Icon(Icons.admin_panel_settings), label: 'Admin'),
        ],
      ),
    );
  }

  Widget _buildHomeTab(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final wallet = context.watch<WalletProvider>().wallet;
    final matchProvider = context.watch<MatchProvider>();
    return RefreshIndicator(
      onRefresh: () async {
        await context.read<MatchProvider>().loadMatches();
        await context.read<WalletProvider>().loadWallet();
        await context.read<MatchProvider>().loadStats();
      },
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundImage: auth.user?.photoUrl != null ? NetworkImage(auth.user!.photoUrl!) : null,
                    child: auth.user?.photoUrl == null ? const Icon(Icons.person) : null,
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(auth.user?.username ?? '', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        Text('Coins: ${wallet?.coins ?? auth.user?.coins ?? 0}'),
                        Text('Referral: ${auth.user?.referralCode ?? '-'}'),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          const Text('Available Matches', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          ...matchProvider.matches.map(
            (match) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: MatchCard(
                match: match,
                onTap: () {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => MatchDetailScreen(matchId: match.id)));
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}
