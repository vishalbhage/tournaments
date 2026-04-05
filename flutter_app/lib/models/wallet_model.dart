class WalletModel {
  final int coins;
  final List<WalletTransactionModel> transactions;

  WalletModel({required this.coins, required this.transactions});

  factory WalletModel.fromJson(Map<String, dynamic> json) => WalletModel(
        coins: json['coins'],
        transactions: (json['transactions'] as List)
            .map((e) => WalletTransactionModel.fromJson(e))
            .toList(),
      );
}

class WalletTransactionModel {
  final int id;
  final int amount;
  final String transactionType;
  final String description;
  final DateTime createdAt;

  WalletTransactionModel({
    required this.id,
    required this.amount,
    required this.transactionType,
    required this.description,
    required this.createdAt,
  });

  factory WalletTransactionModel.fromJson(Map<String, dynamic> json) => WalletTransactionModel(
        id: json['id'],
        amount: json['amount'],
        transactionType: json['transaction_type'],
        description: json['description'],
        createdAt: DateTime.parse(json['created_at']),
      );
}
