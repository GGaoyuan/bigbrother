import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:card_swiper/card_swiper.dart';

class HomePage extends ConsumerStatefulWidget {
  const HomePage({super.key});

  @override
  ConsumerState<ConsumerStatefulWidget> createState() => _HomePageState();
}

class _HomePageState extends ConsumerState<HomePage> {

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7F7F7),
      body: SafeArea(child: Center(
        child: SizedBox(
          width: 300,
          height: 400,
          child: Swiper(
            itemCount: 9,
            itemBuilder: (context, index) {
              final colors = [
                [Color(0xFFFF5F6D), Color(0xFFFFC371)], // 红色渐变
                [Color(0xFF36D1C4), Color(0xFF5B86E5)], // 蓝绿渐变
                [Color(0xFFee9ca7), Color(0xFFffdde1)], // 粉色渐变
                [Color(0xFFFF5F6D), Color(0xFFFFC371)], // 红色渐变
                [Color(0xFF36D1C4), Color(0xFF5B86E5)], // 蓝绿渐变
                [Color(0xFFee9ca7), Color(0xFFffdde1)], // 粉色渐变
                [Color(0xFFFF5F6D), Color(0xFFFFC371)], // 红色渐变
                [Color(0xFF36D1C4), Color(0xFF5B86E5)], // 蓝绿渐变
                [Color(0xFFee9ca7), Color(0xFFffdde1)], // 粉色渐变
              ];
              return Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(20),
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: colors[index],
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black12,
                      blurRadius: 10,
                      offset: Offset(0, 4),
                    ),
                  ],
                ),
              );
            },
            layout: SwiperLayout.STACK,

            itemWidth: 280,
            itemHeight: 380,
            loop: false,
          ),
        ),
      )),
    );
  }
  
}