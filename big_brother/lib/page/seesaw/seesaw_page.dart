import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:syncfusion_flutter_datagrid/datagrid.dart';

class Employee {
  Employee(this.id, this.name, this.designation);
  final int id;
  final String name;
  final String designation;
}
typedef OnTapCallback = void Function(String name);
typedef HighlightProvider = String? Function();

class EmployeeDataSource extends DataGridSource {
  EmployeeDataSource(this.employees,
      {required this.onTap, required this.highlightedNameProvider}) {
    buildDataGridRows();
  }

  final List<Employee> employees;
  final OnTapCallback onTap;
  final HighlightProvider highlightedNameProvider;

  List<DataGridRow> _dataGridRows = [];

  void buildDataGridRows() {
    _dataGridRows = employees
        .map((e) => DataGridRow(cells: [
      DataGridCell<int>(columnName: 'id', value: e.id),
      DataGridCell<String>(columnName: 'name', value: e.name),
      DataGridCell<String>(columnName: 'designation', value: e.designation),
    ]))
        .toList();
  }

  @override
  List<DataGridRow> get rows => _dataGridRows;

  @override
  DataGridRowAdapter? buildRow(DataGridRow row) {
    final String name = row.getCells()[1].value;

    final isHighlighted = highlightedNameProvider() != null &&
        highlightedNameProvider() == name;

    return DataGridRowAdapter(
      color: isHighlighted ? Colors.yellow.withOpacity(0.5) : null,
      cells: row.getCells().map((cell) {
        return GestureDetector(
          onTap: () {
            if (cell.columnName == 'name') {
              onTap(name);
            }
          },
          child: Container(
            padding: EdgeInsets.all(8.0),
            alignment: Alignment.center,
            child: Text(cell.value.toString()),
          ),
        );
      }).toList(),
    );
  }
}

class SeesawPage extends ConsumerStatefulWidget {

  const SeesawPage({super.key});

  @override
  SeesawPageState createState() => SeesawPageState();
}

class SeesawPageState extends ConsumerState<SeesawPage> {
  late EmployeeDataSource _employeeDataSource;
  String? _highlightedName;

  final List<Employee> _employees = List.generate(
    10, (index) => Employee(index, '员工${index % 5}', '职位${index % 3}'),
  );

  @override
  void initState() {
    super.initState();

    _employeeDataSource = EmployeeDataSource(_employees, onTap: (name) {
      setState(() {
        _highlightedName = name;
      });
    }, highlightedNameProvider: () => _highlightedName);
  }

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {

    return Center(
      child: GestureDetector(onTap: () {
        print("object");
      },
      child: Container(width: 100, height: 100, color: Colors.red),
      ),
    );

    return Scaffold(
      body: SfDataGrid(
        source: _employeeDataSource,
        columns: [
          GridColumn(
            columnName: 'id',
            label: Center(child: Text('ID')),
          ),
          GridColumn(
            columnName: 'name',
            label: Center(child: Text('姓名')),
          ),
          GridColumn(
            columnName: 'designation',
            label: Center(child: Text('职位')),
          ),
        ],
      ),
    );
  }

}