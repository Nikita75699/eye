var sortOrder = {}; // Объект для отслеживания текущего состояния сортировки по каждой таблице

function sortTable(tableId) {

  if (!sortOrder[tableId]) {
    sortOrder[tableId] = "asc";
  }
  if (document.getElementById(tableId).style.display === "none") {
    var table = document.getElementById(tableId);
    var rows = Array.from(table.getElementsByTagName("tr"));
      alert(rows)
      rows.sort(function(a, b) {
        var dateA = new Date(a.cells[5].innerText.split("-").reverse().join("-"));
        var dateB = new Date(b.cells[5].innerText.split("-").reverse().join("-"));
        alert(table)
        if (sortOrder === "asc") {
          return dateA - dateB;
        } else {
          return dateB - dateA;
        }
      });

      rows.forEach(function(row) {
        table.append(row);
      });

      // Изменение состояния сортировки
      if (sortOrder === "asc") {
        sortOrder = "desc";
      } else {
        sortOrder = "asc";
      }
  } else {
    var table = document.getElementById(tableId);
    var rows = Array.from(table.getElementsByTagName("tr"));
        alert(rows)
      rows.sort(function(a, b) {
        var dateA = new Date(a.cells[5].innerText.split("-").reverse().join("-"));
        var dateB = new Date(b.cells[5].innerText.split("-").reverse().join("-"));

        if (sortOrder === "asc") {
          return dateA - dateB;
        } else {
          return dateB - dateA;
        }
      });

      rows.forEach(function(row) {
        table.append(row);
      });

      // Изменение состояния сортировки
      if (sortOrder === "asc") {
        sortOrder = "desc";
      } else {
        sortOrder = "asc";
      }
  }
}
