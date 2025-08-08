
class HeatmapRowData {
  final List<HeatmapData> row;
  const HeatmapRowData(
      this.row
  );
}


class HeatmapData {
  final String name;
  final String dateTime;
  final double value;
  const HeatmapData(
      this.name,
      this.dateTime,
      this.value
      );
}



class HeatmapSeries {
  final List<SeriesPiece> pieces;
  const HeatmapSeries(
      this.pieces,
  );
  
  static Set<String> generateDateTime(List<HeatmapSeries> dataSeries) {
    Set<String> dateTimes = {};
    for (HeatmapSeries series in dataSeries) {
      for (SeriesPiece piece in series.pieces) {
        dateTimes.add(piece.dateTime);
      }
    }
    
    return dateTimes;
  }
}

class SeriesPiece {
  final String name;
  final String dateTime;
  final double value;
  const SeriesPiece(
      this.name,
      this.dateTime,
      this.value
      );
}

