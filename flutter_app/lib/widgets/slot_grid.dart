import 'package:flutter/material.dart';

class SlotGrid extends StatelessWidget {
  final int totalSlots;
  final List<int> bookedSlots;
  final int? selectedSlot;
  final int? userLockedSlot;
  final ValueChanged<int> onSelect;

  const SlotGrid({
    super.key,
    required this.totalSlots,
    required this.bookedSlots,
    required this.selectedSlot,
    required this.userLockedSlot,
    required this.onSelect,
  });

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: totalSlots,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 5,
        crossAxisSpacing: 8,
        mainAxisSpacing: 8,
      ),
      itemBuilder: (_, index) {
        final slot = index + 1;
        final isBooked = bookedSlots.contains(slot);
        final isMine = userLockedSlot == slot;
        final isSelected = selectedSlot == slot;
        Color color = Colors.green.withOpacity(.2);
        if (isBooked) color = Colors.red.withOpacity(.28);
        if (isSelected) color = Colors.orange.withOpacity(.28);
        if (isMine) color = Colors.blue.withOpacity(.35);

        return InkWell(
          onTap: isBooked || userLockedSlot != null ? null : () => onSelect(slot),
          borderRadius: BorderRadius.circular(12),
          child: Container(
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.white12),
            ),
            alignment: Alignment.center,
            child: Text('$slot', style: const TextStyle(fontWeight: FontWeight.bold)),
          ),
        );
      },
    );
  }
}
