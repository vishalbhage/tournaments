import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/api_service.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<dynamic> rows = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    Future.microtask(load);
  }

  Future<void> load() async {
    try {
      final api = context.read<ApiService>();
      final data = await api.get('/my/matches') as List<dynamic>;
      setState(() => rows = data);
    } finally {
      setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (loading) return const Center(child: CircularProgressIndicator());
    return ListView(
      padding: const EdgeInsets.all(16),
      children: rows.map((row) {
        final match = row['match'];
        return Card(
          child: ListTile(
            title: Text(match['title']),
            subtitle: Text('Slot ${row['slot_number']} • Reward ${row['reward_coins']}'),
            trailing: Text(row['rank']?.toString() ?? '-'),
          ),
        );
      }).toList(),
    );
  }
}
