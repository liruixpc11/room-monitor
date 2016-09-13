/**
 * Created by lirui on 16/9/12.
 */

/**
 * PATCH
 */
String.prototype.format = function () {
    var str = this;
    for (var i = 0; i < arguments.length; i++) {
        var reg = new RegExp("\\{" + i + "\\}", "gm");
        str = str.replace(reg, arguments[i]);
    }
    return str;
};

/**
 * CODE
 */
var Chart = require('chart.js');
var $ = require('jquery');

var chartRegion = $('#content');

$.getJSON({
    url: '/logs',
    success: function (data) {
        var temperatureUpdater = renderLineChart(data, chartRegion, 'temperature', '温度');
        var humidityUpdater = renderLineChart(data, chartRegion, 'humidity', '湿度');

        var queryLastId = function (data) {
            var lastId = undefined;
            if (data && data.length) {
                lastId = Math.max.apply(Math, $.map(data, function (v) {
                    return v.id
                }))
            }

            return lastId;
        };

        var shareObject = {
            lastId: queryLastId(data)
        };

        var interval = 2 * 1000; // 2s
        var f = function () {
            var params = {};
            var lastId = shareObject.lastId;
            if (lastId) {
                params.lastId = lastId;
            }

            $.getJSON({
                url: '/logs',
                data: params,
                success: function (data) {
                    temperatureUpdater(data);
                    humidityUpdater(data);
                    var newLastId = queryLastId(data);
                    if (newLastId) {
                        shareObject.lastId = newLastId;
                    }
                }
            }).done(function () {
                setTimeout(f, interval);
            });
        };

        setTimeout(f, interval)
    }
});

function renderLineChart(logs, chartRegion, property, title) {
    var colors = [
        'rgba(255,99,132,1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(153, 102, 255, 1)',
        'rgba(255, 159, 64, 1)'
    ];

    var updateTimes = $.map(logs, function (v) {
        return v.updateTime;
    });
    var labels = $.unique(updateTimes);

    var sensorIds = $.unique($.map(logs, function (v) {
        return v.sensorId;
    }));
    sensorIds.sort();
    var sensorData = {};
    $.each(sensorIds, function (i, sensorId) {
        sensorData[sensorId] = $.map(labels, function () {
            return undefined;
        })
    });

    var updateSensorData = function (logs) {
        $.each(logs, function (i, log) {
            var v = log[property];
            if (!v) {
                v = 0;
            }

            sensorData[log.sensorId][labels.indexOf(log.updateTime)] = v
        });
    };
    updateSensorData(logs);

    var normalizeData = function () {
        $.each(sensorIds, function (i, sensorId) {
            $.each(sensorData[sensorId], function (i, v) {
                if (v == undefined) {
                    if (i == 0) {
                        sensorData[sensorId][i] = 0;
                    } else {
                        sensorData[sensorId][i] = sensorData[sensorId][i - 1];
                    }
                }
            });
        });
    };
    normalizeData();

    var datasets = $.map(sensorIds, function (sensorId, i) {
        return {
            label: sensorId,
            data: sensorData[sensorId],
            borderColor: colors[i % colors.length],
            fill: false
            // lineTension: 0
        }
    });

    var id = 'line-chart-' + property;
    chartRegion.append('<canvas id="{0}" height="100"></canvas>'.format(id));
    var chart = new Chart($('#' + id), {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            scales: {
                xAxes: [{
                    type: 'time',
                    time: {}
                }]
            },
            title: {
                display: true,
                text: title
            }
        }
    });

    return function (newLogs) {
        if (newLogs.length == 0) {
            return;
        }

        var newTimes = $.unique($.map(newLogs, function (v) {
            return v.updateTime
        }));
        newTimes.sort();
        var newLabels = $.grep(newTimes, function (t) {
            return labels.indexOf(t) == -1
        });

        $.merge(labels, newLabels);

        var extendArray = $.map(newLabels, function () {
            return undefined;
        });
        $.each(sensorIds, function (i, sensorId) {
            $.merge(sensorData[sensorId], extendArray);
        });

        updateSensorData(newLogs);
        normalizeData();

        chart.update();
    }
}

