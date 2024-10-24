var sortOrder = "asc"; // Переменная для отслеживания текущего состояния сортировки

function sortTableByDate1() {

  var table = document.getElementById("p_with_d_check");
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