const ctx1 = document.getElementById('myChart1');
var ctx2 = document.getElementById("myChart2").getContext('2d');
const ctx3 = document.getElementById('myChart3');
const ctx4 = document.getElementById('myChart4');

new Chart(ctx1, {
  plugins: [ChartDataLabels],
  type: 'doughnut',
    data: {
      labels: ['Женщины', 'Мужчины'],
      datasets: [
        {
          data: [{{inform_list_f}}, {{inform_list_m}}],
        },
      ],
    },
    options: {
        scales: {
          y: {
            beginAtZero: true
          },
        },
    plugins: {
        datalabels: {
          display: true,
          align: 'center',
          backgroundColor: '#ccc',
          borderRadius: 3,
          font: {
            size: 18,
          },
        },
      },
    },
});
  var myChart = new Chart(ctx2, {
    plugins: [ChartDataLabels],
    type: 'bar',
    data: {
      labels: ["до 18","от 18 до 30","от 30 до 45","от 45 до 60","старше 60"],
      datasets: [{
        label: 'С паталогией',
        backgroundColor: '#6495ed',
        data: [{{inform_list_18_t}}, {{inform_list_30_t}}, {{inform_list_45_t}}, {{inform_list_60_t}}, {{inform_list_70_t}}],
      }, {
        label: 'Без патологии',
        backgroundColor: '#20b2aa',
        data: [{{inform_list_18_f}}, {{inform_list_30_f}}, {{inform_list_45_f}}, {{inform_list_60_f}}, {{inform_list_70_f}}],
      }],
    },
      options: {

        plugins: {
            datalabels: {
              display: true,
              align: 'top',
              backgroundColor: '#ccc',
              borderRadius: 3,
              font: {
                size: 12,
              },
            },
          },
    }
  });

  var labels_ = [
      {% for item in inform_list_l %}
        "{{ item.key }}",
      {% endfor %}
    ]
  var value_ = [
      {% for item in inform_list_l %}
        {{ item.value }},
      {% endfor %}
    ]
  new Chart(ctx3, {
      plugins: [ChartDataLabels],
      type: 'doughnut',
      data: {
        labels: labels_,
        datasets: [{
          label: 'человек',
          data: value_,
          borderWidth: 1
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true
          }
        },
        plugins: {
            datalabels: {
              display: true,
              align: 'top',
              backgroundColor: '#ccc',
              borderRadius: 3,
              font: {
                size: 12,
              },
            },
          },
      }
    });
new Chart(ctx4, {
  plugins: [ChartDataLabels],
  type: 'doughnut',
  data: {
    labels: ['Норма мужчины', 'Патология мужчины', 'Норма женщины', 'Патология женщины'],
      datasets: [
        {
          data: [{{inform_list_p1}}, {{inform_list_p2}}, {{inform_list_p3}}, {{inform_list_p4}}],
              backgroundColor: [
                '#ff6425',
                '#cf3500',
                '#20b2aa',
                '#6495ed',
              ],
        },
      ],
  },
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    },
    plugins: {
        datalabels: {
          display: true,
          align: 'center',
          backgroundColor: '#ccc',
          borderRadius: 3,
          font: {
            size: 16,
          },
        },
      },
  }
});