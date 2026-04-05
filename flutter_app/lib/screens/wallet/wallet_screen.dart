import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/wallet_provider.dart';

class WalletScreen extends StatefulWidget {
  const WalletScreen({super.key});

  @override
  State<WalletScreen> createState() => _WalletScreenState();
}

class _WalletScreenState extends State<WalletScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => context.read<WalletProvider>().loadWallet());
  }

  @override
  Widget build(BuildContext context) {
    final wallet = context.watch<WalletProvider>().wallet;
    if (wallet == null) {
      return const Center(child: CircularProgressIndicator());
    }
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Wallet Balance', style: TextStyle(fontSize: 16)),
                const SizedBox(height: 8),
                Text('${wallet.coins} Coins', style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
        ),
        const SizedBox(height: 14),
        const Text('Transactions', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        ...wallet.transactions.map(
          (txn) => Card(
            child: ListTile(
              title: Text(txn.description),
              subtitle: Text(txn.transactionType.toUpperCase()),
              trailing: Text(
                txn.amount >= 0 ? '+${txn.amount}' : '${txn.amount}',
                style: TextStyle(color: txn.amount >= 0 ? Colors.greenAccent : Colors.redAccent),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
