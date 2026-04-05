class MatchModel {
  final int id;
  final String title;
  final int entryFee;
  final int prizePool;
  final int totalSlots;
  final int spotsLeft;
  final bool isFree;
  final String status;
  final DateTime startTime;
  final String? roomId;
  final String? roomPassword;
  final List<int> bookedSlots;
  final ParticipantModel? participant;

  MatchModel({
    required this.id,
    required this.title,
    required this.entryFee,
    required this.prizePool,
    required this.totalSlots,
    required this.spotsLeft,
    required this.isFree,
    required this.status,
    required this.startTime,
    required this.roomId,
    required this.roomPassword,
    required this.bookedSlots,
    required this.participant,
  });

  factory MatchModel.fromJson(Map<String, dynamic> json) => MatchModel(
        id: json['id'],
        title: json['title'],
        entryFee: json['entry_fee'],
        prizePool: json['prize_pool'],
        totalSlots: json['total_slots'],
        spotsLeft: json['spots_left'] ?? json['available_slots'] ?? 0,
        isFree: json['is_free'],
        status: json['status'],
        startTime: DateTime.parse(json['start_time']),
        roomId: json['room_id'],
        roomPassword: json['room_password'],
        bookedSlots: (json['booked_slots'] as List? ?? []).map((e) => e as int).toList(),
        participant: json['participant'] == null ? null : ParticipantModel.fromJson(json['participant']),
      );
}

class ParticipantModel {
  final int userId;
  final String username;
  final int slotNumber;
  final int score;
  final int? rank;
  final int rewardCoins;

  ParticipantModel({
    required this.userId,
    required this.username,
    required this.slotNumber,
    required this.score,
    required this.rank,
    required this.rewardCoins,
  });

  factory ParticipantModel.fromJson(Map<String, dynamic> json) => ParticipantModel(
        userId: json['user_id'],
        username: json['username'] ?? '',
        slotNumber: json['slot_number'],
        score: json['score'] ?? 0,
        rank: json['rank'],
        rewardCoins: json['reward_coins'] ?? 0,
      );
}
