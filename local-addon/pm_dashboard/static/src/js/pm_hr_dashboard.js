odoo.define('pm_dashboard.pm_hr_dashboard', function(require){
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var web_client = require('web.web_client');
    var _t = core._t;
    var QWeb = core.qweb;

    var PmHRDashboard = AbstractAction.extend({
        template: 'PmHRDashboard',
        cssLibs: [
        ],
        jsLibs: [
//            '/pm_dashboard/static/lib/chartjs/chartjs.js',
//            '/pm_dashboard/static/lib/chartjs/chartjs-plugin-datalabels.min.js'
        ],
        events: {
            'click .leave_request': 'leaves_to_approve',
            'click .leave_request_today':'leaves_request_today',
            'click .leave_request_this_month':'leaves_request_month',
        },

        init: function(){
            this._super.apply(this, arguments);
            console.log('dashboard initialized');
            this.employees = {};
            this.employee_chart = {};
            this.hr_events = {};
        },

        willStart: function() {
            console.log("WILLSTART FUNCTION")
            return this.fetch_initial_data();
        },

        start: function() {
            console.log("START FUNCTION")
            var self = this;
            return this._super().then(function() {
                self.fetch_hr_chart_data();
            });
        },

        fetch_initial_data: function() {

            var self = this;
            // fetch employee data
            var def1 = self._rpc({
                model: "pm.hr.dashboard",
                method: "get_employee_data"
            }).then(function(result){
                self.employees = result;
            });

            var def2 = self._rpc({
                model: "pm.hr.dashboard",
                method: "get_employee_chart_data"
            }).then(function(result){
                self.employee_chart = result;
//                console.log('employee_chart: ', self.employee_chart);
            });

            var def3 = self._rpc({
                model: "pm.hr.dashboard",
                method: "get_hr_events"
            }).then(function(result){
                self.hr_events = result;
//                console.log('get_hr_events: ', result);
            });

            return $.when(def1, def2, def3);
        },

        fetch_hr_chart_data: function() {
            console.log("FETCH_DATE FUNCTION")
            var self = this;
            self._rpc({
                    model: "pm.hr.dashboard",
                    method: "get_department_leave"
                }).then(function(result) {
                    self.initialLeaveChart(result);
                });

           self._rpc({
                    model: "pm.hr.dashboard",
                    method: "get_dept_employee"
                }).then(function(result){
                    self.departmentChart(result);
                });

           self._rpc({
                    model: "pm.hr.dashboard",
                    method: "join_resign_trends"
                }).then(function(result){
                    self.monthlyJoinResignChart(result);
                });

           self._rpc({
                    model: "pm.hr.dashboard",
                    method: "get_attrition_rate"
                }).then(function(result){
                    self.attritionRateChart(result);
                });

           self._rpc({
                    model: "pm.hr.dashboard",
                    method: "get_employee_chart_data"
                }).then(function(result){
                    self.createPieChart('#employee_by_contract_chart', '#employee_contract_legend', result['employee_by_contract']);
                    self.createPieChart('#employee_by_gender_chart', '#employee_gender_legend', result['employee_by_gender']);
                    self.createPieChart('#employee_by_nationality_chart', '#employee_nationality_legend', result['employee_by_nationality']);
//                    self.createPieChart('#employee_turnover_chart', '#employee_turnover_legend', result['turnover_rate']);
                });

           self._rpc({
                    model: "pm.hr.dashboard",
                    method: "get_job_position"
                }).then(function(result){
//                    console.log('get_job_position: ',result)
                    self.jobOpeningChart(result);
                });

           self._rpc({
                    model: "pm.hr.dashboard",
                    method: "get_outstanding_leave"
                }).then(function(result){
//                    console.log('get_outstanding_leave: ',result)
                    self.outstandingChart(result);
                });
        },

        // implementation
        departmentChart: function(data){
            var labels = data.map(d => d.label);
            var values = data.map(d => d.value);
            var ctx = this.$('#department_chart');
            var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337',
            '#fe7139', '#ffa433', '#ffc25b', '#f8e54b'];

            var myChart = new Chart(ctx, {
                type: 'pie',
                data: {
                  labels: labels,
                  datasets: [{
                    labels: labels,
                    backgroundColor: colors,
                    data: values
                  }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        datalabels: {
                            display: false
                        }
                    },
                    legend: {
                        display: false
                    },
                    legendCallback: function(chart) {
                        var text = [];
                        text.push('<ul class="' + chart.id + '-legend">');
                        for (var i = 0; i < chart.data.labels.length; i++) {
                            text.push('<li class="'+ 'd-flex' + ' ' + 'justify-content-between' + '"><div><span style="background-color:' +
                                       chart.data.datasets[0].backgroundColor[i] +
                                       '"></span>');
                            if (chart.data.datasets[0].labels) {
                                text.push(chart.data.datasets[0].labels[i]);
                            }
                            text.push('</div>');
                            text.push('<div>' + chart.data.datasets[0].data[i] +'</div>')
                            text.push('</li>');
                        }
                        text.push('</ul>');
                        return text.join('');
                    },
                }
            });
            this.$('#department_legend').empty();
            this.$('#department_legend').append(myChart.generateLegend());
            return myChart;
        },

        initialLeaveChart: function(result) {
            var months = result.month_list;
            var leaves = result.data;
            var departments = result.department_list;

            var chartData = [];
            for(var i in leaves){
                var monthly_data = [];
                for(var j in months){
                    var leave = leaves[i].leaves_data.filter(l => l.l_month === months[j]);
                    monthly_data.push(leave.length)
                }
                chartData.push({'department': leaves[i]['name'], 'data': monthly_data});
            }

            var bar_data = {
                labels: months,
                data: chartData
            };

            var self = this;
            self.monthlyLeaveBarChart(bar_data);
            self.monthlyLeavePieChart(leaves);
        },

        monthlyLeaveBarChart: function(chart) {
//            console.log('monthlyLeaveBarChart: ', chart);
            var labels = chart.labels;
            var chartData = chart.data;

            var ctx = this.$('#monthly_leave_bar');
            var colors = ['#DAA520', '#FDE39B','#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337',
            '#fe7139', '#ffa433', '#ffc25b', '#f8e54b'];

            var datasets = [];
            for(var i in chartData) {
                datasets.push({
                    label: chart.data[i]['department'],
                    data: chart.data[i]['data'],
                    backgroundColor: [colors[i], colors[i], colors[i], colors[i], colors[i], colors[i]],
                    colors: [colors[i], colors[i], colors[i], colors[i], colors[i], colors[i]]
                })
            }

            var myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                  labels: labels,
                  datasets: datasets
                },
                options: {
                  legend: { display: false },
                  plugins: {
                    datalabels: {
                        display: false
                    }
                  },
                  responsive: true,
                  scales:{
                    xAxes: [{
                        stacked: true,
                        ticks: {
                            beginAtZero: true
                        },
                        barPercentage: 0.4
                    }],
                    yAxes: [{
                        stacked: true
                    }]
                  }
                }
            });
//            this.$('#job_opening_legend').empty();
//            this.$('#job_opening_legend').append(myChart.generateLegend());
            return myChart;
        },
        monthlyLeavePieChart: function(data) {
//            console.log('leaves monthlyLeavePieChart: ', data);
             var labels = data.map(d => d['name']);
             var percentage = data.map(d => d['percentage']);
             var values = data.map(d => d['leaves_data'].length)
            var ctx = this.$('#monthly_leave_pie');
            var colors = ['#DAA520', '#FDE39B','#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337',
            '#fe7139', '#ffa433', '#ffc25b', '#f8e54b'];

            var myChart = new Chart(ctx, {
                type: 'pie',
                data: {
                  labels: labels,
                  datasets: [{
                    labels: labels,
                    backgroundColor: colors,
                    data: values,
                    percentage: percentage
                  }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        datalabels: {
                            display: false
                        }
                    },
                    legend: {
                        display: false
                    },
                    legendCallback: function(chart) {
                        var text = [];
                        text.push('<ul class="' + chart.id + '-legend">');
                        for (var i = 0; i < chart.data.labels.length; i++) {
                            text.push('<li class="'+ 'd-flex' + ' ' + 'justify-content-between' + '"><div><span style="background-color:' +
                                       chart.data.datasets[0].backgroundColor[i] +
                                       '"></span>');
                            if (chart.data.datasets[0].labels) {
                                text.push(chart.data.datasets[0].labels[i]);
                            }
                            text.push('</div>');
                            text.push('<div>' + chart.data.datasets[0].percentage[i] +' %</div>')
                            text.push('</li>');
                        }
                        text.push('</ul>');
                        return text.join('');
                    },
                }
            });
            this.$('#monthly_leave_legend').empty();
            this.$('#monthly_leave_legend').append(myChart.generateLegend());
            return myChart;
        },

        // monthly join/resign
        monthlyJoinResignChart: function(data) {
            var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337',
                          '#fe7139', '#ffa433', '#ffc25b', '#f8e54b'];
            var labels = data[0].values.map(r => r.l_month);
            var datasets = [];
            for(var i = 0; i < 2; i++){
                datasets.push(
                    {
                        data: data[i].values.map(d => d.count),
                        label: data[i].name,
                        borderColor: colors[i],
                        fill: false,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        pointBackgroundColor: "#000",
                        backgroundColor: colors[i],
                        lineTension: 0,
                    }
                  );
            }

            var ctx = this.$('#join_resign_trend');
            var myChart = new Chart(ctx, {
              type: 'line',
              data: {
                labels: labels,
                fill: true,
                datasets: datasets
              },
              options: {
                plugins: {
                    datalabels: {
                        display: false
                    }
                },
                legend: {
                    display: false,
                },
                scales: {
                    yAxes: [{
                      gridLines: {
                        display: false,
                      },
                      ticks: {
                        // test step size (by remove)
                        //stepSize: 10,
                        min: 0
                      }
                    }],
                    xAxes: [{
                      gridLines: {
                        drawBorder: false,
                        display: false,
                      },
                    }],
                },
              }
            });
            this.$('#join_resign_trend_legend').empty();
            this.$('#join_resign_trend_legend').append(myChart.generateLegend());
            return myChart;
        },

        // attrition rate
        attritionRateChart: function(data) {
        var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337',
            '#fe7139', '#ffa433', '#ffc25b', '#f8e54b'];
            var labels = data.map(d => d.month);
            var datasets = [{
                    data: data.map(d => d['attrition_rate']),
                    label: ['Attrition Rate'],
                    borderColor: colors[0],
                    fill: false,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: "#fff",
                    backgroundColor: colors[0],
                    lineTension: 0,
            }];

            var ctx = this.$('#attrition_rate');
            var myChart = new Chart(ctx, {
              type: 'line',
              data: {
                labels: labels,
                fill: true,
                datasets: datasets
              },
              options: {
                plugins: {
                    datalabels: {
                        display: false
                    }
                },
                legend: {
                    display: false,
                },
                scales: {
                    yAxes: [{
                      gridLines: {
                        display: false,
                      },
                      ticks: {
                        stepSize: 10,
                        min: 0
                      }
                    }],
                    xAxes: [{
                      gridLines: {
                        drawBorder: false,
                        display: false,
                      },
                    }],
                },
              }
            });
//            this.$('#monthly_leave_legend').empty();
//            this.$('#monthly_leave_legend').append(myChart.generateLegend());
            return myChart;
        },


        // create pie chart
        createPieChart: function(id, legendId, chart){
//            var labels = data.map(d => d.label);
//            var values = data.map(d => d.value);
            var ctx = this.$(id);
            var colors = ['#DAA520', '#FDE39B','#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337',
            '#fe7139', '#ffa433', '#ffc25b', '#f8e54b'];

            var myChart = new Chart(ctx, {
                type: 'pie',
                data: {
                  labels: chart['labels'],
                  datasets: [{
                    labels: chart['labels'],
                    backgroundColor: colors,
                    data: chart['data']
                  }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        datalabels: {
                            display: false
                        }
                    },
                    legend: {
                        display: false
                    },
                    legendCallback: function(chart) {
                        var text = [];
                        text.push('<div class="' + chart.id + '-legend' + ' ' + 'text-center' + ' ' + 'w-100">');
                        for (var i = 0; i < chart.data.labels.length; i++) {
                            text.push('<span class="rounded-legend" style="background-color:' +
                                       chart.data.datasets[0].backgroundColor[i] +
                                       '"></span>');
                            if (chart.data.datasets[0].labels) {
                                text.push(chart.data.datasets[0].labels[i]);
                            }
                            text.push('<span class="mr-4 ml-2">' + chart.data.datasets[0].data[i]);
                            if(chart.data.labels.includes('This Year')) {
                                text.push('%');
                            }
                            text.push('</span>')
                        }
                        text.push('</div>');
                        return text.join('');
                    },
                }
            });
            this.$(legendId).empty();
            this.$(legendId).append(myChart.generateLegend());
            return myChart;
        },

        // create bar chart
        jobOpeningChart: function(data){
            var labels = data.map(d => d.label);
            var values = data.map(d => d.value);
            var ctx = this.$('#job_opening_chart');
            var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337',
            '#fe7139', '#ffa433', '#ffc25b', '#f8e54b'];

            var myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                  labels: labels,
                  datasets: [
                    {
                      backgroundColor: colors,
                      data: values
                    }
                  ]
                },
                options: {
                  legend: { display: false },
                  plugins: {
                    datalabels: {
                        display: false
                    }
                  },
                  responsive: true,
                    scales: {
                        yAxes: [
                            {
                                ticks: {
                                    min: 0,
                                    beginAtZero: true,
                                    stepSize: 5
                                }
                            }
                        ]
                    },
                  legendCallback: function(chart) {
                    var text = [];
                    text.push('<ul class="' + chart.id + '-legend">');
                    for (var i = 0; i < chart.data.labels.length; i++) {
                        text.push('<li class="'+ 'd-flex' + ' ' + 'justify-content-between' + '"><div><span style="background-color:' +
                                   chart.data.datasets[0].backgroundColor[i] +
                                   '"></span>');
                        if (chart.data.labels) {
                            text.push(chart.data.labels[i]);
                        }
                        text.push('</div>');
                        text.push('<div>' + chart.data.datasets[0].data[i] +'</div>')
                        text.push('</li>');
                    }
                    text.push('</ul>');
                    return text.join('');
                },
                }
            });
            this.$('#job_opening_legend').empty();
            this.$('#job_opening_legend').append(myChart.generateLegend());
            return myChart;
        },

        // total outstanding chart
        outstandingChart: function(data){
            var labels = data.map(d => d.department);
            var values = data.map(d => d.count);
            var ctx = this.$('#outstanding_leave_chart');
            var colors = ['#70cac1', '#659d4e', '#208cc2', '#4d6cb1', '#584999', '#8e559e', '#cf3650', '#f65337',
            '#fe7139', '#ffa433', '#ffc25b', '#f8e54b'];

            var myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                  labels: labels,
                  datasets: [
                    {
                      backgroundColor: colors,
                      data: values
                    }
                  ]
                },
                options: {
                  legend: { display: false },
                  plugins: {
                    datalabels: {
                        display: false
                    }
                  },
                  responsive: true,
                    scales: {
                        yAxes: [
                            {
                                ticks: {
                                    min: 0,
                                    beginAtZero: true,
                                    stepSize: 5
                                }
                            }
                        ]
                    },
                  legendCallback: function(chart) {
                    var text = [];
                    text.push('<ul class="' + chart.id + '-legend">');
                    for (var i = 0; i < chart.data.labels.length; i++) {
                        text.push('<li class="'+ 'd-flex' + ' ' + 'justify-content-between' + '"><div><span style="background-color:' +
                                   chart.data.datasets[0].backgroundColor[i] +
                                   '"></span>');
                        if (chart.data.labels) {
                            text.push(chart.data.labels[i]);
                        }
                        text.push('</div>');
                        text.push('<div>' + chart.data.datasets[0].data[i] +'</div>')
                        text.push('</li>');
                    }
                    text.push('</ul>');
                    return text.join('');
                },
                }
            });
            this.$('#outstanding_leave_legend').empty();
            this.$('#outstanding_leave_legend').append(myChart.generateLegend());
            return myChart;
        },

        // event clicked
        on_reverse_breadcrumb: function() {
        console.log("ON_REVERSE_BREADCRUMB")
            var self = this;
            web_client.do_push_state({});
            this.update_cp();
            this.fetch_initial_data().then(function() {
                self.$('.o_hr_dashboard').empty();
//                self.render_dashboards();
//                self.render_graphs();
            });
        },

        update_cp: function() {
            var self = this;
            console.log("UPDATE_CP")
    //        this.update_control_panel(
    //            {breadcrumbs: self.breadcrumbs}, {clear: true}
    //        );
        },

        leaves_to_approve: function(e) {
            console.log('leave approve!!!');
            var self = this;
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            this.do_action({
                name: _t("Leave Request"),
                type: 'ir.actions.act_window',
                res_model: 'hr.leave',
                view_mode: 'tree,form,calendar',
                views: [[false, 'list'],[false, 'form']],
                domain: [['state','in',['confirm','validate1']]],
                target: 'current'
            }, options)
        },

        leaves_request_today: function(e) {
            var self = this;
            var date = new Date();
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            this.do_action({
                name: _t("Leaves Today"),
                type: 'ir.actions.act_window',
                res_model: 'hr.leave',
                view_mode: 'tree,form,calendar',
                views: [[false, 'list'],[false, 'form']],
                domain: [['date_from','<=', date], ['date_to', '>=', date], ['state','=','validate']],
                target: 'current'
            }, options)
        },

        leaves_request_month: function(e) {
            var self = this; 
            e.stopPropagation();
            e.preventDefault();
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            var date = new Date();
            var firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
            var lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0);
            var fday = firstDay.toJSON().slice(0,10).replace(/-/g,'-');
            var lday = lastDay.toJSON().slice(0,10).replace(/-/g,'-');
            this.do_action({
                name: _t("This Month Leaves"),
                type: 'ir.actions.act_window',
                res_model: 'hr.leave',
                view_mode: 'tree,form,calendar',
                views: [[false, 'list'],[false, 'form']],
                domain: [['date_from','>', fday],['state','=','validate'],['date_from','<', lday]],
                target: 'current'
            }, options)
        },

    });

    core.action_registry.add('pm_hr_dashboard', PmHRDashboard);

    return HRDashboard;
});