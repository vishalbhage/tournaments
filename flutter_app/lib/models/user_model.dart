class UserModel {
  final int id;
  final String email;
  final String username;
  final String fullName;
  final String? photoUrl;
  final String role;
  final int coins;
  final bool usernameLocked;
  final String referralCode;

  UserModel({
    required this.id,
    required this.email,
    required this.username,
    required this.fullName,
    required this.photoUrl,
    required this.role,
    required this.coins,
    required this.usernameLocked,
    required this.referralCode,
  });

  bool get isAdmin => role == 'admin';

  factory UserModel.fromJson(Map<String, dynamic> json) => UserModel(
        id: json['id'],
        email: json['email'],
        username: json['username'],
        fullName: json['full_name'],
        photoUrl: json['photo_url'],
        role: json['role'],
        coins: json['coins'],
        usernameLocked: json['username_locked'],
        referralCode: json['referral_code'],
      );
}
