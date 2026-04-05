import 'package:flutter/foundation.dart';
import '../models/match_model.dart';
import '../services/api_service.dart';

class MatchProvider extends ChangeNotifier {
  final ApiService api;
  bool loading = false;
  List<MatchModel> matches = [];
  MatchModel? selectedMatch;
  List<ParticipantModel> leaderboard = [];
  Map<String, dynamic>? stats;

  MatchProvider(this.api);

  Future<void> loadMatches() async {
    loading = true;
    notifyListeners();
    try {
      final response = await api.get('/matches') as List<dynamic>;
      matches = response
          .map((e) => MatchModel.fromJson({...e as Map<String, dynamic>, 'booked_slots': [], 'participant': null}))
          .toList();
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<void> loadMatchDetails(int matchId) async {
    loading = true;
    notifyListeners();
    try {
      final response = await api.get('/matches/$matchId') as Map<String, dynamic>;
      selectedMatch = MatchModel.fromJson(response);
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<void> joinMatch(int matchId, int slotNumber) async {
    await api.post('/matches/$matchId/join', {'slot_number': slotNumber});
    await loadMatchDetails(matchId);
    await loadMatches();
  }

  Future<void> loadLeaderboard(int matchId) async {
    final response = await api.get('/matches/$matchId/leaderboard') as Map<String, dynamic>;
    leaderboard = (response['leaderboard'] as List)
        .map((e) => ParticipantModel.fromJson(e as Map<String, dynamic>))
        .toList();
    notifyListeners();
  }

  Future<void> loadStats() async {
    stats = await api.get('/my/stats') as Map<String, dynamic>;
    notifyListeners();
  }
}
