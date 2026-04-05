import 'package:flutter/foundation.dart';
import '../models/wallet_model.dart';
import '../services/api_service.dart';

class WalletProvider extends ChangeNotifier {
  final ApiService api;
  WalletModel? wallet;

  WalletProvider(this.api);

  Future<void> loadWallet() async {
    final response = await api.get('/my/wallet') as Map<String, dynamic>;
    wallet = WalletModel.fromJson(response);
    notifyListeners();
  }
}
