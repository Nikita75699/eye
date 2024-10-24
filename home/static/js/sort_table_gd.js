var sortOrder = "asc"; // Переменная для отслеживания текущего состояния сортировки

function sortTableByDate() {
  if (document.getElementById("p_without_d").style.display === "none") {
    var table = document.getElementById("p_with_d");
    var rows = Array.from(table.getElementsByTagName("tr"));

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
  } else {
    var table = document.getElementById("p_without_d");
    var rows = Array.from(table.getElementsByTagName("tr"));

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
