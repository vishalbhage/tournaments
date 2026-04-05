import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/match_provider.dart';

class LeaderboardScreen extends StatefulWidget {
  final int matchId;
  const LeaderboardScreen({super.key, required this.matchId});

  @override
  State<LeaderboardScreen> createState() => _LeaderboardScreenState();
}

class _LeaderboardScreenState extends State<LeaderboardScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => context.read<MatchProvider>().loadLeaderboard(widget.matchId));
  }

  @override
  Widget build(BuildContext context) {
    final board = context.watch<MatchProvider>().leaderboard;
    return Scaffold(
      appBar: AppBar(title: const Text('Leaderboard')),
      body: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: board.length,
        separatorBuilder: (_, __) => const SizedBox(height: 10),
        itemBuilder: (_, index) {
          final item = board[index];
          return Card(
            child: ListTile(
              leading: CircleAvatar(child: Text('${item.rank ?? '-'}')),
              title: Text(item.username),
              subtitle: Text('Score: ${item.score}'),
              trailing: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text('Reward: ${item.rewardCoins}'),
                  Text('Slot: ${item.slotNumber}'),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
