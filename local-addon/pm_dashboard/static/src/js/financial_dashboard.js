odoo.define('pm_dashboard.financial_dashboard', function(require){
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var web_client = require('web.web_client');
    var _t = core._t;
    var QWeb = core.qweb;

    var FinancialDashboard = AbstractAction.extend({
        template: 'FinancialDashboard',
        cssLibs: [
        ],
        jsLibs: [
//            '/pm_dashboard/static/lib/chartjs/chartjs.js',
//            '/pm_dashboard/static/lib/chartjs/chartjs-plugin-datalabels.min.js'
        ],

        init: function(){
            this._super.apply(this, arguments);
            console.log('dashboard initialized');
            this.finance_data = [];
        },

         willStart: function() {
            console.log("WILLSTART FUNCTION")
            var self = this;
            return this._super()
            .then(function() {
                var def1 = self._rpc({
                    model: "finance.dashboard",
                    method: "get_finance_data"
                }).then(function(result) {
                    self.finance_data = result;
                });
            return $.when(def1);
            });

        },

        start: function() {
            console.log("START FUNCTION")
            var self = this;
    //        this.set("title", 'Dashboard');
            return this._super().then(function() {
                self.payable_by_outstanding();
                self.payable_by_target();
                self.budget_line_chart();
                self.budget_stacked_chart();
                self.ytd_vs_budget_chart();
            });
        },

        // day payable outstanding
        payable_by_outstanding: function(){
            var ctx = this.$('#payable_by_outstanding');
            var myChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    datasets: [
                        {
                            data: [20, 20, 20],
                            backgroundColor: [
                                '#daa520',
                                '#4f0147',
                                '#370031',
                            ],
                            borderWidth    : 0
                        }]
                },
//                plugins:[ChartDataLabels],
                options: {
                    cutoutPercentage: 70,
                    rotation: 1 * Math.PI,/** This is where you need to work out where 89% is */
                    circumference: 1 * Math.PI,/** put in a much smaller amount  so it does not take up an entire semi circle */
                    elements: {
                             center: {
                               text: '90%',
                               sidePadding: 60
                             }
                    },
                    plugins:{
                        datalabels:{
                            color: 'white'
                        }
                    }
                }
            });

            Chart.pluginService.register({
              beforeDraw: function(chart) {
                  if (chart.config.options.elements.center) {
                        var width = chart.chart.width,
                            height = chart.chart.height,
                            ctx = chart.chart.ctx;

                        ctx.restore();
                        var fontSize = (height / 60).toFixed(2);
                        ctx.font = fontSize + "em sans-serif";
                        ctx.textBaseline = "middle";

                        var text = "30",
                            textX = Math.round((width - ctx.measureText(text).width) / 2),
                            textY = height / 1.2;

                        ctx.fillText(text, textX, textY);
                        ctx.save();
                  }
              }
            });
        },

        // payable by payment target
        payable_by_target: function(){
        var ctx = this.$('#payable_by_target');
            var barChart = new Chart(ctx, {
                type: 'bar',
                data: {
                  labels: [ "ACCOUNTS PAYABLE BY PAYMENT TARGET"],
                  datasets: [
                      {
                          label: 'not due',
                          data: [37000],
                          backgroundColor: [
                            '#370031'
                          ],
                          borderColor: [
                            '#370031'
                          ],
                          borderWidth: 1
                      },
                      {
                          label: '<30 Days',
                          data: [29000],
                          backgroundColor: [
                            '#4f0147'
                          ],
                          borderColor: [
                            '#4f0147'
                          ],
                          borderWidth: 1
                      },
                      {
                          label: '<60 Days',
                          data: [18000],
                          backgroundColor: [
                            '#ac9969'
                          ],
                          borderColor: [
                            '#ac9969'
                          ],
                          borderWidth: 1
                      },
                      {
                          label: '<90 Days',
                          data: [10000],
                          backgroundColor: [
                            '#daa520'
                          ],
                          borderColor: [
                            '#daa520'
                          ],
                          borderWidth: 1
                      },
                      {
                          label: '>90 Days',
                          data: [7000],
                          backgroundColor: [
                            '#fde39b'
                          ],
                          borderColor: [
                            '#fde39b'
                          ],
                          borderWidth: 1
                      }
                  ]
                },
//                plugins:[ChartDataLabels],
                options: {
                  legend: {
                        display: false,
                        position: 'right'
                    },
                    responsive: true,
                    scales: {
                        xAxes: [{
                            display: false
                        }],
                        yAxes: [{
                            display: false
                        }]
                    },
                    plugins:{
                        datalabels: {
                            align: 'end',
                            anchor: 'end',
                            color: 'black',
                            offset: 4,
                            padding: 0
                        }
                    }
                }
            });

            this.$('#payable_by_target_legend').append(barChart.generateLegend());
        },

        // budget line chart
        budget_line_chart: function(){
            var ctx = this.$('#budget_line_chart');
            var lineChart = new Chart(ctx, {
                  type: 'line',
                  data: {
                      labels: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
                      datasets: [
                      {
                            data: [0,-1000,-1000,0],
                            label: "Actual",
                            borderColor: "#3e95cd",
                            backgroundColor: "#3e95cd",
                            pointBackgroundColor: '#3e95cd',
                            fill: false,
                            lineTension: 0,
                      },
                      {
                            data: [40000,40000,40000,40000],
                            label: "Budget",
                            borderColor: "#8e5ea2",
                            backgroundColor: "#8e5ea2",
                            pointBackgroundColor: '#8e5ea2',
                            fill: false,
                            lineTension: 0,
                      },
                      {
                            data: [40000,35000,40000,40000],
                            label: "YTD",
                            borderColor: "#3cba9f",
                            backgroundColor: "#3cba9f",
                            pointBackgroundColor: '#3cba9f',
                            fill: false,
                            lineTension: 0,
                      },
                      {
                            data: [40000,70000,110000,150000],
                            label: "Variance",
                            borderColor: "#e8c3b9",
                            backgroundColor: "#e8c3b9",
                            pointBackgroundColor: '#e8c3b9',
                            fill: false,
                            lineTension: 0,
                      }
                    ]
                  },
                  options: {
                       legend: {
                            display: false
                       },
                       plugins: {
                            datalabels: {
                                 display: false,
                            }
                       },
                       responsive: true,
                       title: {
                            display: true,
                            text: 'Actual/YTD/Budget'
                       },
                       scales: {
                            xAxes: [{
                                gridLines: {
                                     display: false
                                },
                            }],
                           yAxes: [{
                                ticks: {
                                    // Include a dollar sign in the ticks
                                     callback: function(value, index, values) {
                                          return value < 0 ? '$(' + value.toFixed(0) + ')' : '$' + value.toFixed(0);
                                     }
                                }
                           }],
                       }
                  }
                });
            this.$('#budget_line_chart_legend').append(lineChart.generateLegend());
        },

        // open stacked chart
        budget_stacked_chart: function(){
            var ctx = this.$('#budget_stacked_chart');
            var stackedChart = new Chart(ctx, {
                  type: 'bar',
                  data: {
                      labels: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
                      datasets: [
                      {
                            data: [100],
                            label: "Actual",
                            backgroundColor: '#3e95cd'
                      },
                      {
                            data: [50],
                            label: "Budget",
                            backgroundColor: '#8e5ea2'
                      },
                      {
                            data: [10],
                            label: "YTD",
                            backgroundColor: '#3cba9f'
                      },
                      {
                            data: [50],
                            label: "Variance",
                            backgroundColor: '#e8ddb9'
                      },
                      {
                            data: [50],
                            label: "Variance",
                            backgroundColor: '#ccc3b9'
                      }
                    ]
                  },
                  options: {
                       legend: {
                            display: false
                       },
                       plugins: {
                            datalabels: {
                                 display: false,
                            }
                       },
                       responsive: true,
                       title: {
                            display: true,
                            text: 'Opex '
                       },
                       scales: {
                            xAxes: [{
                                stacked: true,
                                gridLines: {
                                     display: false
                                },
                            }],
                           yAxes: [{
                                stacked: true,
                                ticks: {
                                    // Include a dollar sign in the ticks
                                     callback: function(value, index, values) {
                                          return value < 0 ? '$(' + value.toFixed(0) + ')' : '$' + value.toFixed(0);
                                     }
                                }
                           }],
                       }
                  }
                });
            this.$('#budget_stacked_chart_legend').append(stackedChart.generateLegend());
        },

        // YTD vs budget
        ytd_vs_budget_chart: function(){
            console.log("FETCH_DATE FUNCTION")
            var self = this;
            this._rpc({
                model: "finance.dashboard",
                method: "get_ytd_vs_budget"
            }).then(function(result) {
                console.log('ddd', result)
                var ctx = self.$('#ytd_vs_budget');
                var doughnutChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                    labels: ["YTD%", "Budget%"],
                    datasets: [
                        {
                            label: "YTD VS BUDGET",
                            backgroundColor: ["#96761e", "#4f0147"],
                            data: result
                        }
                    ]
                    },
                    plugins:[ChartDataLabels],
                    options: {
                        legend: {
                            display: true
                        },
                        title: {
                            display: true,
                            text: 'YTD vs. Budget'
                        },
                        cutoutPercentage: 70,
                        plugins:{
                            datalabels: {
                                color: 'white'
                            }
                        }
                    }
                });
                //self.$('#ytd_vs_budget_legend').append(doughnutChart.generateLegend());
            })

        },
        fetch_finance_data: function(){
            var self = this;
            var def1 = this._rpc({
                    model: "finance.dashboard",
                    method: "get_finance_data"
                }).then(function(result) {
                    self.finance_data = result;
                });
            return def1;
        }
    });

    core.action_registry.add('financial_dashboard', FinancialDashboard);

    return FinancialDashboard;
});