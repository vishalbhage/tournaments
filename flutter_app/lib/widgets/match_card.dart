import 'package:flutter/material.dart';
import '../models/match_model.dart';
import 'package:intl/intl.dart';

class MatchCard extends StatelessWidget {
  final MatchModel match;
  final VoidCallback onTap;

  const MatchCard({super.key, required this.match, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(child: Text(match.title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold))),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: match.isFree ? Colors.green.withOpacity(.18) : Colors.orange.withOpacity(.15),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(match.isFree ? 'FREE' : '${match.entryFee} Coins'),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text('Prize Pool: ${match.prizePool}'),
              Text('Slots: ${match.totalSlots}'),
              Text('Spots Left: ${match.spotsLeft}'),
              const SizedBox(height: 8),
              Text('Starts: ${DateFormat('dd MMM, hh:mm a').format(match.startTime.toLocal())}'),
            ],
          ),
        ),
      ),
    );
  }
}
