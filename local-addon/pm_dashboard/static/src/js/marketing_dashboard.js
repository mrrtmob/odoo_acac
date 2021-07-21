odoo.define('pm_dashboard.marketing_dashboard', function(require){
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var web_client = require('web.web_client');
    var _t = core._t;
    var QWeb = core.qweb;

    var MarketingDashboard = AbstractAction.extend({
        template: 'MarketingDashboard',
        cssLibs: [
        ],
        jsLibs: [
//            '/pm_dashboard/static/lib/chartjs/chartjs.js',
//            '/pm_dashboard/static/lib/chartjs/chartjs-plugin-datalabels.min.js'
        ],

        init: function(){
            this._super.apply(this, arguments);
            console.log('dashboard initialized');

            this.leadConversionTopCampaigns = {};
            this.ytdCampaigns = [];
        },

        willStart: function() {
            console.log("WILLSTART FUNCTION")
            var self = this;
            return this._super()
            .then(function() {
              var def1 = self._rpc({
                model: "marketing.dashboard",
                method: "get_lead_conversion_top_campaigns"
            }).then(function(result) {
                self.leadConversionTopCampaigns = result;
            });

            var def2 = self._rpc({
                model: "marketing.dashboard",
                method: "get_ytd_campaigns"
            }).then(function(result) {
                self.ytdCampaigns = result;
            });

            return $.when(def1, def2);
        });

        },


        start: function() {
            console.log("START FUNCTION")
            var self = this;
    //        this.set("title", 'Dashboard');
            return this._super().then(function() {
                self.lead_conversion_chart();
                self.intake_student_chart();
                self.budget_actual_chart();
            });
        },

        fetch_initial_data: function() {
            var self = this;

            var def1 = self._rpc({
                model: "marketing.dashboard",
                method: "get_lead_conversion_top_campaigns"
            }).then(function(result) {
                self.leadConversionTopCampaigns = result;
            });

            var def2 = self._rpc({
                model: "marketing.dashboard",
                method: "get_ytd_campaigns"
            }).then(function(result) {
                self.ytdCampaigns = result;
            });

            return $.when(def1, def2);
        },


        // lead by conversion
        lead_conversion_chart: function(){
            var ctx = this.$('#lead_conversion_chart');
            var labels = [];
            var datasets = [
                { label: 'Total Cost', backgroundColor: '#ac9969', data: [] },
                { label: 'Conversion', backgroundColor: '#daa520', data: [] },
                { label: 'Cost/Conv.', backgroundColor: '#fde39b', data: [] }
            ];

            for (var i = 0; i < this.leadConversionTopCampaigns.length; i++) {
                labels.push(this.leadConversionTopCampaigns[i]['name']);

                datasets[0]['data'].push(this.leadConversionTopCampaigns[i]['cost']);
                datasets[1]['data'].push(this.leadConversionTopCampaigns[i]['conversions_count']);
                datasets[2]['data'].push(this.leadConversionTopCampaigns[i]['cost_per_conversion']);
            }

            var barChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    title: {
                        display: true,
                        text: 'By Conversion'
                    },
                    legend: {
                        display: false
                    },
                    plugins: {
                        datalabels: {
                            display: false
                        }
                    },
                    scales: {
                        xAxes: [{
                            gridLines: {
                                 display: false
                            },
                        }]
                   }
                }
            });
            this.$('#lead_conversion_chart_legend').empty();
            this.$('#lead_conversion_chart_legend').append(barChart.generateLegend());
        },

        // intake student
        intake_student_chart: function(){
            var ctx = this.$('#intake_student_chart');
            var def1 = this._rpc({
                model: "marketing.dashboard",
                method: "get_student_intake_by_ranks"
            }).then(function(result) {
                var horizontalChart = new Chart(ctx, {
                    type: 'horizontalBar',
                    data: {
                        labels: ['First Contact', 'Potential', 'High Potential'],
                        datasets: [
                            {
                                label: 'Count',
                                backgroundColor: ['#370031', '#4f0147', '#ac9969'],
                                data: [result['first_contact_leads_count'], result['potential_leads_count'], result['high_potential_leads_count']]
                            }
                        ]
                    },
                    plugins:[ChartDataLabels],
                    options: {
                        plugins: {
                            datalabels: {
                                align: 'end',
                                anchor: 'end',
                                color: 'black',
                                offset: 0
                            }
                        },
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Student Intake'
                        },
                        scales: {
                            xAxes: [{
                                display: false,
                                ticks: {
                                    beginAtZero: true
                                },
                                gridLines: {
                                     display: false
                                },
                            }],
                            yAxes: [{
                                ticks: {
                                  beginAtZero: true
                                },
                                gridLines: {
                                     display: false
                                },
                            }]
                        }
                    }
                });
            });
        },

        // budget vs actual
        budget_actual_chart: function(){
            var ctx = this.$('#budget_actual_chart');
            var datasets = [
                {
                    label: "YTD Plan Budget",
                    type: "line",
                    borderColor: "#4f0147",
                    pointBackgroundColor: '#4f0147',
                    data: [],
                    fill: false,
                    lineTension: 0
                },
                {
                    label: "YTD Actual Cost",
                    type: "line",
                    borderColor: "#ac9969",
                    pointBackgroundColor: '#ac9969',
                    data: [],
                    fill: false,
                    lineTension: 0
                }
            ];

            var totalByMonth = {};

            for (var i = 0; i < this.ytdCampaigns.length; i++) {
                var monthNumber = this.ytdCampaigns[i]['month_number'];

                if (totalByMonth[monthNumber] == undefined)
                    totalByMonth[monthNumber] = {
                        total_budget: 0,
                        total_cost: 0
                    };

                totalByMonth[monthNumber]['total_budget'] += this.ytdCampaigns[i]['budget'];
                totalByMonth[monthNumber]['total_cost'] += this.ytdCampaigns[i]['cost'];
            }

            var month = 1;

            while (month <= 12) {
                var monthMatched = false;

                for (monthNumber in totalByMonth) {
                    if (monthNumber == month) {
                        datasets[0]['data'].push(totalByMonth[monthNumber]['total_budget']);
                        datasets[1]['data'].push(totalByMonth[monthNumber]['total_cost']);

                        monthMatched = true;

                        break;
                    }
                }

                if (!monthMatched) {
                    datasets[0]['data'].push(null);
                    datasets[1]['data'].push(null);
                }

                month++;
            }

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
                    datasets: datasets
                },
                options: {
                    plugins:{
                        datalabels: {
                            display: false
                        }
                    },
                    title: {
                        display: true,
                        text: 'Plan Budget vs. Actual Cost'
                    },
                    legend: {
                        display: false
                    },
                    scales: {
                        xAxes: [{
                            ticks: {
                              beginAtZero: true
                            },
                            gridLines: {
                                 display: false
                            },
                        }],
                        yAxes: [{
                            ticks: {
                              beginAtZero: true
                            },
                            gridLines: {
                                 display: false
                            },
                        }]
                    }
                }
            });
        }

    });

    core.action_registry.add('marketing_dashboard', MarketingDashboard);

    return MarketingDashboard;
});