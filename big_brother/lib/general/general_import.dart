import 'dart:math';
import 'dart:ui';
import 'package:flutter/material.dart';

Color randomColor() {
  Random random = Random();
  Color color = Color.fromARGB(
    255,
    random.nextInt(256),
    random.nextInt(256),
    random.nextInt(256),
  );
  return color;
}
