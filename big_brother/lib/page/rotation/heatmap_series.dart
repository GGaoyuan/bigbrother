

class HeatmapSeries {
  final String name;
  final SeriesPiece pieces;
  const HeatmapSeries(
      this.name,
      this.pieces,
  );
  
  static Set<String> generateDateTime(List<HeatmapSeries> dataSeries) {
    return dataSeries.map((series) => series.pieces.dateTime).toSet();
  }
}

class SeriesPiece {
  final String dateTime;
  final double value;
  const SeriesPiece(
      this.dateTime,
      this.value
      );
}



/*

class _HeatMapData {
  final String percentage;
  final double nancy;
  final double andrew;
  final double janet;
  final double margaret;
  final double steven;
  final double michael;
  final double robert;
  final double laura;
  final double anne;
  final double paul;
  final double mario;

  _HeatMapData(
      this.percentage,
      this.nancy,
      this.andrew,
      this.janet,
      this.margaret,
      this.steven,
      this.michael,
      this.robert,
      this.laura,
      this.anne,
      this.paul,
      this.mario);
}


* */
