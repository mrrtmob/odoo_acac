odoo.define('pm_dashboard.registrar_dashboard', function(require){
    'use strict';

    console.log('module loaded');

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');

    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var web_client = require('web.web_client');
    var _t = core._t;
    var QWeb = core.qweb;

    var RegistrarDashboard = AbstractAction.extend({
        template: 'RegistrarDashboard',
        cssLibs: [
        ],
        jsLibs: [
//            '/pm_dashboard/static/lib/chartjs/chartjs.js',
//            '/pm_dashboard/static/lib/chartjs/chartjs-plugin-datalabels.min.js'
        ],

        init: function(){
            this._super.apply(this, arguments);
            console.log('dashboard initialized');

            this.students = {};
            this.currentSemester = {};
            this.alertData = {};
            this.active_terms = [];
        },

        willStart: function() {
            console.log("WILLSTART FUNCTION")
            var self = this;
            //this._super();
            return this.active_terms = self.fetch_active_terms();
            //return  self.fetch_students_by_status();
            
        },

        start: function() {
            console.log("START FUNCTION")
            var self = this;
    //        this.set("title", 'Dashboard');
            return this._super().then(function() {
                self.fetch_student_chart_data();
                self.gradeChart();
                self.absenceChart();
                self.currentSemesterChart();

            });
        },

        fetch_student_chart_data: function() {
            console.log("FETCH_DATE FUNCTION")
            var self = this;
            this._rpc({
                    model: "registrar.dashboard",
                    method: "get_student_enrollment"
                }).then(function(result) {
                    console.log(result)
//                    console.log(result.h_barchart_data)
//                    var students_by_gender = result.students_by_gender;
//                    self.create_pieChat('#male_chart', 'Male', students_by_gender.males);
//                    self.create_pieChat('#female_chart', 'Female', students_by_gender.females);
                    self.barGraph(result.h_barchart_data)

                });
        },
        fetch_active_terms: function(){
            var self = this;
            var def1 = this._rpc({
                    model: "registrar.dashboard",
                    method: "get_active_terms"
                }).then(function(result) {
                    self.active_terms = result;
                });
            return def1;
        },
        fetch_students_by_status: function() {
            console.log("FETCH_DATE FUNCTION WILLSTART")
            var self = this;
            var def1 =  this._rpc({
                model: "registrar.dashboard",
                method: "get_student_graduated"
            }).then(function(result) {
                self.students = result;
            });

            var def2 =  this._rpc({
                model: "registrar.dashboard",
                method: "get_current_semester_students_data"
            }).then(function(result) {
                self.currentSemester = result;
                console.log('====', self.currentSemester);
            });
           
            var def3 =  this._rpc({
                model: "registrar.dashboard",
                method: "get_current_term_alert_data"
            }).then(function(result) {
                self.alertData = result;
            });

            return $.when(def1, def2, def3);
        },

        // student chart (male-chart, female-chart)
        create_pieChat: function(id, label, data){
            var ctx = this.$(id);
            var myChart = new Chart(ctx, {
                type: 'pie',
                data: {
                  labels: [label],
                  datasets: [
                    {
                      backgroundColor: ['#32391C'],
                      borderColor: ['#32391C'],
                      data: [data]
                    }
                  ]
                },
                plugins:[ChartDataLabels],
                options:{
                    responsive: true,
                    legend: {
                        display: false,
                    },
                    plugins: {
                        datalabels: {
                            color: '#fff'
                        },
                   }
                }
            });
        },

        // student nationality chart
        barGraph: function(data){
            var ctx = this.$('#student_horizontal_bar_chart');
            var myChart = new Chart(ctx, {
              type: 'horizontalBar',
              data: {
                datasets: [{
                      label: 'Cambodian',
                      data: [data.cambodian],
                      backgroundColor: [
                        '#E7BC29'
                      ],
                      borderColor: [
                        '#E7BC29'
                      ],
                      borderWidth: 1
                    },
                    {
                      label: 'Foreigners',
                      data: [data.foreigners],
                      backgroundColor: [
                        '#F3A447',
                      ],
                      borderColor: [
                        '#F3A447',
                      ],
                      borderWidth: 1
                    },
                    {
                      label: 'Scholarship',
                      data: [data.scholarship],
                      backgroundColor: [
                        '#A5B592'
                      ],
                      borderColor: [
                        '#A5B592',
                      ],
                      borderWidth: 1
                    }]
              },
              options: {
                  legend: {
                        display: false,
                        position: 'right'
                    },
                    responsive: true,
                    scales: {
                      xAxes: [{
                        display: false,
                        ticks: {
                          beginAtZero: true
                        }
                      },
                      {
                        position: "top",
                        gridLines: {
                        drawBorder: false,
    //                      offsetGridLines: true
                        }
                      }],
                      yAxes: [{
                        ticks: {
                          beginAtZero: true
                        }
                      }]
                    }
              }
            });
            this.$('#js-legend').empty();
            this.$('#js-legend').append(myChart.generateLegend());
            return myChart;
        },

        // student grade chart
        gradeChart: function(){
            var self = this;
            var ctx = this.$('#grade_chard');

            var def1 =  this._rpc({
                model: "registrar.dashboard",
                method: "get_term_grade_data"
            }).then(function(result) {
                var labels = [];
                var datasets = [
                    {
                        label: "Above 80 (%)",
                        backgroundColor: "#A5B592",
                        data: []
                    },
                    {
                        label: "60 - 80 (%)",
                        backgroundColor: "#F3A447",
                        data: []
                    },
                    {
                        label: "Below 60 (%)",
                        backgroundColor: "#E7BC29",
                        data: []
                    }
                ];

                for (var i = 0; i < result['semesters'].length; i++) {
                    labels.push(result['semesters'][i]['name']);

                    datasets[0]['data'].push(result['semesters'][i]['rank_top'].toFixed(2));
                    datasets[1]['data'].push(result['semesters'][i]['rank_middle'].toFixed(2));
                    datasets[2]['data'].push(result['semesters'][i]['rank_low'].toFixed(2));
                }

                var gradeChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                      labels: labels,
                      datasets: datasets
                    },
                    options: {
                        responsive: true,
                        legend: {
                            display: false
                        },
                        plugins: {
                            datalabels: {
                                display: false
                            }
                        },
                        title: {
                            display: true,
                            text: 'Grade'
                        },
                        scales: {
                            xAxes: [{
                                barPercentage: 1.0,
                                categoryPercentage: 0.6,
                                 gridLines: {
                                  color: "rgba(0, 0, 0, 0)",
                                }
                            }]
                        }
                    }
                });

                self.$('#grade_legend').append(gradeChart.generateLegend());
            });
        },

        // absence chart
        absenceChart: function(){
            var self = this;
            var ctx = this.$('#absence_chart');

            var def1 =  this._rpc({
                model: "registrar.dashboard",
                method: "get_term_semesters_absence_data"
            }).then(function(result) {
                var labels = [];
                var datasets = [];
                var numberOfWeeks = 0;

                for (var i = 0; i < result['semesters'].length; i++) {
                    if (result['semesters'][i]['weeks'].length > numberOfWeeks)
                        numberOfWeeks = result['semesters'][i]['weeks'].length;

                    var semesterName = result['semesters'][i]['name'];
                    var color = '#e7bc29';

                    if (i == 0)
                        color = '#b09b53';
                    else if (i == 1)
                        color = '#63744f';
                    else if (i == 2)
                        color = '#9c85c0';
                    else if (i == 3)
                        color = '#a5b592';

                    var dataset = {
                        data: [],
                        label: semesterName,
                        borderColor: color,
                        backgroundColor: color,
                        fill: false,
                        lineTension: 0,
                        pointBackgroundColor: color
                    };

                    for (var j = 0; j < result['semesters'][i]['weeks'].length; j++)
                        dataset['data'].push(result['semesters'][i]['weeks'][j]['absences_count']);

                    datasets.push(dataset);
                }

                for (var w = 1; w <= numberOfWeeks; w++)
                    labels.push('W' + w);

                var absenceChart = new Chart(ctx, {
                  type: 'line',
                  data: {
                    labels: labels,
                    datasets: datasets
                  },
                  options: {
                      plugins: {
                          datalabels: {
                                display: false,
                          },
                      },
                      legend: {
                        display: false
                      },
                      responsive: true,
                      title: {
                          display: true,
                          text: 'Absences'
                      },
                      scales: {
                        xAxes: [{
                            barPercentage: 1.0,
                             gridLines: {
                              color: "rgba(0, 0, 0, 0)",
                            }
                        }]
                    }
                  }
                });
                self.$('#absence_legend').append(absenceChart.generateLegend());
            });

        },

        // current semester enrollment
        currentSemesterChart_old: function(){
            var self = this;
            var ctx = this.$('#current_semester_enrollment');

            var def1 =  this._rpc({
                model: "registrar.dashboard",
                method: "get_current_term_enrollment_data"
            }).then(function(result) {
                var semesterLabels = [];
                var semesterData = [];
                var semesterColors = [];
                var numberOfStudentLabels = [];
                var numberOfStudentData = [];
                var numberOfStudentColors = [];
                var genderAndScholarshipLabels = [];
                var genderAndScholarshipData = [];
                var genderAndScholarshipColors = [];
                var color = '#e7bc29';

                for (var i = 0; i < result['semesters'].length; i++) {
                    if (i == 0)
                        color = '#d092a7'
                    else if (i == 1)
                        color = '#f3a447'
                    else if (i == 2)
                        color = '#e7bc29'
                    else if (i == 3)
                        color = '#a5b592'

                    semesterLabels.push(result['semesters'][i]['name']);
                    semesterData.push(1);
                    semesterColors.push(color);

                    numberOfStudentLabels.push('Students');
                    numberOfStudentData.push(result['semesters'][i]['students_count']);
                    numberOfStudentColors.push(color);

                    genderAndScholarshipLabels.push('Male', 'Female', 'Scholarship');
                    genderAndScholarshipData.push(result['semesters'][i]['male_students_count'], result['semesters'][i]['female_students_count'], result['semesters'][i]['scholarship_students_count']);
                    genderAndScholarshipColors.push(color, color, color);
                }

                var chartData = {
                    datasets: [
                    {
                        data: genderAndScholarshipData,
                        backgroundColor: genderAndScholarshipColors,
                        hoverBackgroundColor: genderAndScholarshipColors,
                        labels: genderAndScholarshipLabels
                    },
                    {
                        data: numberOfStudentData,
                        backgroundColor: numberOfStudentColors,
                        hoverBackgroundColor: numberOfStudentColors,
                        labels: numberOfStudentLabels
                    },
                    {
                        data: semesterData,
                        backgroundColor: semesterColors,
                        hoverBackgroundColor: semesterColors,
                        labels: semesterLabels
                    }]
                };
                var currentSemesterChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: chartData,
                    plugins:[ChartDataLabels],
                    options:{
                        plugins: {
                            datalabels: {
                                display: true
                            }
                        },
                        legend: {
                            display: false
                        },
                        cutoutPercentage: 25,
                        tooltips: {
                            callbacks: {
                                label: function(tooltipItem, data) {
                                    var dataset = data.datasets[tooltipItem.datasetIndex];
                                    var index = tooltipItem.index;
                                    return dataset.labels[index] + ": " + dataset.data[index];
                                }
                            }
                        }
                    }
                });

            });
        },

        // current semester enrollment
        currentSemesterChart: function(){
            var maleStudents = [];
            var femaleStudents = [];
            var scholarshipStudents = [];
            var totalStudent = [];
            var labels = [];
            var self = this;

            this._rpc({
                    model: "registrar.dashboard",
                    method: "get_current_term_enrollment_data"
                }).then(function(result) {

                    console.log('result: ', result)
                    for (var i = 0; i < result['semesters'].length; i++){
                        labels.push(result['semesters'][i]['name'])
                        maleStudents.push(result['semesters'][i]['male_students_count']);
                        femaleStudents.push(result['semesters'][i]['female_students_count']);
                        scholarshipStudents.push(result['semesters'][i]['scholarship_students_count']);
                        totalStudent.push(result['semesters'][i]['students_count'])
                    }

                    var maxValue = Math.max(...totalStudent);

                    var datasets = [
                        {
                          label: "Male",
                          backgroundColor: "#f3a447",
                          data: maleStudents
                        }, {
                          label: "Female",
                          backgroundColor: "#d092a7",
                          data: femaleStudents
                        },
                        {
                          label: "Scholarship",
                          backgroundColor: "#a5b592",
                          data: scholarshipStudents
                        },
                        {
                          label: "Total",
                          backgroundColor: "#ac9969",
                          data: totalStudent
                        }
                    ]

                    console.log('datasets: ', datasets)

                    var ctx = self.$('#current_semester_enrollment');
                    var currentSemesterChart = new Chart(ctx, {
                        type: 'bar',
                        data: {
                          labels: labels,
                          datasets: datasets
                        },
//                        plugins:[ChartDataLabels],
                        options: {
                            responsive: true,
                            legend: {
                                display: false
                            },
                            plugins: {
                                datalabels: {
                                    display: true
                                }
                            },
                            title: {
                                display: false
                            },
                            scales: {
                                xAxes: [{
                                    barPercentage: 1.0,
                                    categoryPercentage: 0.6,
                                     gridLines: {
                                      color: "rgba(0, 0, 0, 0)",
                                    }
                                }],
                                yAxes: [{
                                     display: true,
                                     ticks: {
                                         min: 0,
                                         max: maxValue + 5,
                                         beginAtZero: true
                                     }
                                 }]
                            }
                        }
                    });
    //                self.$('#current_semester_enrollment_legend').append(currentSemesterChart.generateLegend());
                });
            }
    });

    core.action_registry.add('registrar_dashboard', RegistrarDashboard);

    return RegistrarDashboard;
});