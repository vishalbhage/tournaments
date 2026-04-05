import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/api_service.dart';

class AdminDashboardScreen extends StatefulWidget {
  const AdminDashboardScreen({super.key});

  @override
  State<AdminDashboardScreen> createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends State<AdminDashboardScreen> {
  final _title = TextEditingController();
  final _entryFee = TextEditingController(text: '200');
  final _prizePool = TextEditingController(text: '10000');
  final _roomId = TextEditingController();
  final _password = TextEditingController();
  final _startTime = TextEditingController(text: DateTime.now().add(const Duration(hours: 2)).toIso8601String());
  String? info;

  Future<void> createMatch() async {
    final api = context.read<ApiService>();
    await api.post('/admin/matches', {
      'title': _title.text.trim(),
      'entry_fee': int.parse(_entryFee.text),
      'prize_pool': int.parse(_prizePool.text),
      'total_slots': 50,
      'room_id': _roomId.text.trim(),
      'room_password': _password.text.trim(),
      'start_time': _startTime.text.trim(),
    });
    setState(() => info = 'Match created successfully');
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text('Admin Dashboard', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
        const SizedBox(height: 12),
        TextField(controller: _title, decoration: const InputDecoration(labelText: 'Match title')),
        const SizedBox(height: 10),
        TextField(controller: _entryFee, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Entry fee')),
        const SizedBox(height: 10),
        TextField(controller: _prizePool, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Prize pool')),
        const SizedBox(height: 10),
        TextField(controller: _roomId, decoration: const InputDecoration(labelText: 'Room ID')),
        const SizedBox(height: 10),
        TextField(controller: _password, decoration: const InputDecoration(labelText: 'Room password')),
        const SizedBox(height: 10),
        TextField(controller: _startTime, decoration: const InputDecoration(labelText: 'Start time ISO')),
        const SizedBox(height: 12),
        ElevatedButton(onPressed: createMatch, child: const Text('Create Match')),
        if (info != null) ...[
          const SizedBox(height: 12),
          Text(info!),
        ],
        const SizedBox(height: 20),
        const Text('Manual result entry uses POST /api/admin/matches/{id}/results with user_id, score and kills.', style: TextStyle(color: Colors.white70)),
      ],
    );
  }
}
