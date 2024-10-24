function format(d) {
            let appointments = "";
            for (let i = 0; i < d.appointments.length; i++) {
                appointments += "<li class=\"appointment-row\" onclick=\"moveCheckSelected('" + d.appointments[i].id + "'); return false;\">" + d.appointments[i].date + " - " + d.appointments[i].time + "</li>";
            }
            return (
                '<dl>' +
                '<dt>Appointments:</dt>' +
                '<dd><ul>' +
                appointments +
                '</ul></dd>' +
                '</dl>'
            );
        }
        function moveCheckSelected(key) {
            $.ajax({
            url: '/json_data_appoints'+key,
            type: 'GET',
            data: {'check': true},
            success: function (json) {
                var patientInfo = json;
                var html = '';
                html += '<div class="row">';
                for (var i = 0; i < patientInfo['appointment0'].length; i++) {
                    var appointmentData = patientInfo['appointment0'][i];
                    html += '<div class="col-6 py-2">';
                    html +=     '<div class="card">';
                    html +=         '<div class="card-body text-center">';
                    html +=             '<img id="img' + appointmentData.count + '" class="img1" src="' + appointmentData.image + '" style="width: 100%" data-img-id="' + patientInfo['appointment0'][i].count + '" onclick="openModal(' + patientInfo['appointment0'][i].count + ')">';
                    html +=         '</div>';
                    html +=     '</div>';
                    html += '</div>';
                    html += '<div class="modal fade" id="exampleModalToggle' + patientInfo['appointment0'][i].count + '" tabindex="-1" aria-labelledby="exampleModalToggle' + patientInfo['appointment0'][i].count + '" aria-hidden="true">'
                    html +=   '<div class="modal-dialog modal-fullscreen">'
                    html +=     '<div class="modal-content">'
                    html +=       '<div class="modal-header">'
                    html +=        '<div class="form-check form-switch">'
                    html +=          '<input class="form-check-input" type="checkbox" role="switch" onclick="check(' + patientInfo['appointment0'][i].count + ')">'
                    html +=          '<label class="form-check-label" for="flexSwitchCheckDefault">Переключить режим просмотра</label>'
                    html +=        '</div>'
                    html +=         '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Закрыть"></button>'
                    html +=       '</div>'
                    html +=       '<div class="modal-body">'
                    html +=         '<div id="dinamyc_image' + patientInfo['appointment0'][i].count + '" style="display:none;" class="row">';
                    html +=             '<div class="col-6 py-2">';
                    html +=                 '<h5 class="modal-title" id="exampleModalLabel">' + patientInfo['appointment0'][i].study_date +'</h5>'
                    html +=                 '<img id="img' + patientInfo['appointment0'][i].count + '" class="img1" src="' + patientInfo['appointment0'][i].image + '" style="width: 100%" data-img-id="' + patientInfo['appointment0'][i].count + '">';
                    html +=             '</div>'
                    html +=             '<div class="col-6 py-2">';
                    html +=                '<div id="carousel-img' + patientInfo['appointment0'][i].count + '" class="carousel slide">'
                    html += '<div class="carousel-inner">';
                    var isFirstItem = true;
                        for (var appointment in patientInfo) {
                            if (appointment !== 'appointment0') {
                                console.log(patientInfo[appointment][i]);
                                html += '<div class="carousel-item' + (isFirstItem ? ' active' : '') + '">';
                                html += '<h5 class="modal-title" id="info' + patientInfo[appointment][i].count + '">' + patientInfo[appointment][i].study_date + '</h5>';
                                html += '<img id="img' + patientInfo[appointment][i].count + '" class="img1" src="' + patientInfo[appointment][i].image + '" style="width: 100%">';
                                html += '</div>';
                                isFirstItem = false;
                            }
                        }
                    html += '</div>';
                    html +=                          '<button class="carousel-control-prev" type="button" data-bs-target="#carousel-img' + patientInfo['appointment0'][i].count + '" data-bs-slide="prev">'
                    html +=                            '<span class="carousel-control-prev-icon" aria-hidden="true"></span>'
                    html +=                            '<span class="visually-hidden">Предыдущий</span>'
                    html +=                          '</button>'
                    html +=                          '<button class="carousel-control-next" type="button" data-bs-target="#carousel-img' + patientInfo['appointment0'][i].count + '" data-bs-slide="next">'
                    html +=                             '<span class="carousel-control-next-icon" aria-hidden="true"></span>'
                    html +=                             '<span class="visually-hidden">Следующий</span>'
                    html +=                          '</button>'
                    html +=                 '</div>'
                    html +=             '</div>'
                    html +=          '</div>'
                    html +=         '<div id="no_dinamyc_image' + patientInfo['appointment0'][i].count + '">';
                    html +=             '<div class="col-12 py-2">';
                    html +=                 '<h5 class="modal-title" id="exampleModalLabel">' + patientInfo['appointment0'][i].study_date +'</h5>'
                    html +=                 '<img id="img' + patientInfo['appointment0'][i].count + '" class="img1" src="' + patientInfo['appointment0'][i].image + '" style="width: 100%" data-img-id="' + patientInfo['appointment0'][i].count + '">';
                    html +=             '</div>'
                    html +=          '</div>'
                    html +=       '</div>'
                    html +=       '<div class="modal-footer">'
                    html +=       '</div>'
                    html +=     '</div>'
                    html +=   '</div>'
                    html += '</div>'
                }
                html += '</div>';
                $('#patient-info'+key).empty().append(html);
                $('#modal'+key).modal('show');
            }
            });

        }
        function openModal(imageId) {
            var modal = document.getElementById("exampleModalToggle" + imageId);
            var image = document.getElementById("img" + imageId + "-1");
            var modalToggle = new bootstrap.Modal(modal);
            if (modalToggle.isShown) {
              modalToggle.hide();
            } else {
              modalToggle.show();
            }
        }

