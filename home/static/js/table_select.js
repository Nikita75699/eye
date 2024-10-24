function moveToSelected(row) {
    row.style.display = "none";
    var patientId = row.cells[0].textContent;
    var select = document.getElementById("selectedPatients");
    var option = document.createElement("option");
    option.value = patientId;
    option.text = row.cells[2].textContent+' '+row.cells[3].textContent+' '+row.cells[4].textContent+' '+row.cells[5].textContent;
    select.add(option);
    updateSelectedPatientsInput();
  }

  function moveToTable(select) {
    var selectedPatientId = select.value;
    var table = document.getElementById("patients_with_d");
    var rows = table.getElementsByTagName("tr");
    for (var i = 0; i < rows.length; i++) {
      if (rows[i].cells[0].textContent == selectedPatientId) {
        rows[i].style.display = "";
        break;
      }
    }
    select.remove(select.selectedIndex);
    updateSelectedPatientsInput();
  }

  function updateSelectedPatientsInput() {
    var select = document.getElementById("selectedPatients");
    var selectedPatientsInput = document.getElementById("selectedPatientsInput");

    // Получаем все значения выбранных пациентов
    var selectedPatients = Array.from(select.options).map(option => option.value);

    // Устанавливаем значение скрытого поля
    selectedPatientsInput.value = selectedPatients.join(",");
  }