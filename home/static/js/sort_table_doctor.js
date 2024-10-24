var sortOrder1 = "asc"; // Переменная для отслеживания текущего состояния сортировки

function sortTableByDate1() {
  if (document.getElementById("p_without_dy").style.display === "none") {
    var table = document.getElementById("p_with_dy");
    var rows = Array.from(table.getElementsByTagName("tr"));

      rows.sort(function(a, b) {
        var dateA = new Date(a.cells[4].innerText.split("-").reverse().join("-"));
        var dateB = new Date(b.cells[4].innerText.split("-").reverse().join("-"));

        if (sortOrder1 === "asc") {
          return dateA - dateB;
        } else {
          return dateB - dateA;
        }
      });

      rows.forEach(function(row) {
        table.append(row);
      });

      // Изменение состояния сортировки
      if (sortOrder1 === "asc") {
        sortOrder1 = "desc";
      } else {
        sortOrder1 = "asc";
      }
  } else {
    var table = document.getElementById("p_without_dy");
    var rows = Array.from(table.getElementsByTagName("tr"));

      rows.sort(function(a, b) {
        var dateA = new Date(a.cells[5].innerText.split("-").reverse().join("-"));
        var dateB = new Date(b.cells[5].innerText.split("-").reverse().join("-"));

        if (sortOrder1 === "asc") {
          return dateA - dateB;
        } else {
          return dateB - dateA;
        }
      });

      rows.forEach(function(row) {
        table.append(row);
      });

      // Изменение состояния сортировки
      if (sortOrder1 === "asc") {
        sortOrder1 = "desc";
      } else {
        sortOrder1 = "asc";
      }
  }
}

var sortOrder2 = "asc"; // Переменная для отслеживания текущего состояния сортировки

function sortTableByDate2() {

  if (document.getElementById("p_without_dg").style.display === "none") {
    var table = document.getElementById("p_with_dg");
    var rows = Array.from(table.getElementsByTagName("tr"));

      rows.sort(function(a, b) {
        var dateA = new Date(a.cells[5].innerText.split("-").reverse().join("-"));
        var dateB = new Date(b.cells[5].innerText.split("-").reverse().join("-"));

        if (sortOrder2 === "asc") {
          return dateA - dateB;
        } else {
          return dateB - dateA;
        }
      });

      rows.forEach(function(row) {
        table.append(row);
      });

      // Изменение состояния сортировки
      if (sortOrder2 === "asc") {
        sortOrder2 = "desc";
      } else {
        sortOrder2 = "asc";
      }
  } else {
    var table = document.getElementById("p_with_dg");
    var rows = Array.from(table.getElementsByTagName("tr"));

      rows.sort(function(a, b) {
        var dateA = new Date(a.cells[5].innerText.split("-").reverse().join("-"));
        var dateB = new Date(b.cells[5].innerText.split("-").reverse().join("-"));

        if (sortOrder2 === "asc") {
          return dateA - dateB;
        } else {
          return dateB - dateA;
        }
      });

      rows.forEach(function(row) {
        table.append(row);
      });

      // Изменение состояния сортировки
      if (sortOrder2 === "asc") {
        sortOrder2 = "desc";
      } else {
        sortOrder2 = "asc";
      }
  }
}
