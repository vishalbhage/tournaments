import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/match_provider.dart';
import '../../providers/wallet_provider.dart';
import '../../widgets/slot_grid.dart';
import 'leaderboard_screen.dart';

class MatchDetailScreen extends StatefulWidget {
  final int matchId;
  const MatchDetailScreen({super.key, required this.matchId});

  @override
  State<MatchDetailScreen> createState() => _MatchDetailScreenState();
}

class _MatchDetailScreenState extends State<MatchDetailScreen> {
  int? selectedSlot;
  String? error;
  Timer? timer;
  Duration remaining = Duration.zero;

  @override
  void initState() {
    super.initState();
    Future.microtask(() => context.read<MatchProvider>().loadMatchDetails(widget.matchId));
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  void startCountdown(DateTime startTime) {
    timer?.cancel();
    timer = Timer.periodic(const Duration(seconds: 1), (_) {
      final diff = startTime.difference(DateTime.now());
      setState(() => remaining = diff.isNegative ? Duration.zero : diff);
    });
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<MatchProvider>();
    final match = provider.selectedMatch;
    if (provider.loading && match == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    if (match == null) {
      return const Scaffold(body: Center(child: Text('Match not found')));
    }
    startCountdown(match.startTime.toLocal());

    return Scaffold(
      appBar: AppBar(title: Text(match.title)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Entry Fee: ${match.isFree ? 'Free' : '${match.entryFee} Coins'}'),
                  Text('Prize Pool: ${match.prizePool}'),
                  Text('Spots Left: ${match.spotsLeft}'),
                  Text('Countdown: ${remaining.inHours.toString().padLeft(2, '0')}:${(remaining.inMinutes % 60).toString().padLeft(2, '0')}:${(remaining.inSeconds % 60).toString().padLeft(2, '0')}'),
                  if (match.participant != null) ...[
                    const SizedBox(height: 10),
                    Text('Your Slot: ${match.participant!.slotNumber}', style: const TextStyle(fontWeight: FontWeight.bold)),
                  ],
                  if (match.roomId != null && match.roomPassword != null) ...[
                    const Divider(height: 28),
                    Text('Room ID: ${match.roomId}', style: const TextStyle(fontWeight: FontWeight.bold)),
                    Text('Password: ${match.roomPassword}', style: const TextStyle(fontWeight: FontWeight.bold)),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          const Text('Choose Your Slot', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          SlotGrid(
            totalSlots: match.totalSlots,
            bookedSlots: match.bookedSlots,
            selectedSlot: selectedSlot,
            userLockedSlot: match.participant?.slotNumber,
            onSelect: (slot) => setState(() => selectedSlot = slot),
          ),
          const SizedBox(height: 12),
          if (error != null) Text(error!, style: const TextStyle(color: Colors.redAccent)),
          const SizedBox(height: 12),
          if (match.participant == null)
            ElevatedButton(
              onPressed: selectedSlot == null
                  ? null
                  : () async {
                      try {
                        await context.read<MatchProvider>().joinMatch(match.id, selectedSlot!);
                        await context.read<WalletProvider>().loadWallet();
                      } catch (e) {
                        setState(() => error = e.toString().replaceFirst('Exception: ', ''));
                      }
                    },
              child: const Text('Confirm Booking'),
            ),
          const SizedBox(height: 8),
          OutlinedButton(
            onPressed: () {
              Navigator.push(context, MaterialPageRoute(builder: (_) => LeaderboardScreen(matchId: match.id)));
            },
            child: const Text('View Leaderboard'),
          ),
        ],
      ),
    );
  }
}
