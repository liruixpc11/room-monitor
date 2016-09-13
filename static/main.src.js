/**
 * Created by lirui on 16/9/12.
 */

/**
 * UTILS
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
var $ = require('jquery');

var chartRegion = $('#content');

/**
 * draw gauge charts
 */
var echarts = require('echarts');
$.getJSON({
    url: '/status',
    success: function (data) {
        var updaters = {};
        $.each(data, function (i, record) {
            updaters[record.sensorId] = renderGaugeChart(record, chartRegion);
        });

        var f = function () {
            $.getJSON({
                url: '/status',
                success: function (data) {
                    $.each(data, function (i, record) {
                        updaters[record.sensorId](record);
                    });
                }
            }).done(function () {
                setTimeout(f, 2000)
            });
        };

        setTimeout(f, 2000);
    }
});

function renderGaugeChart(record, chartRegion) {
    var chartId = 'status-gauge-' + record.sensorId;
    chartRegion.append("<div id='{0}' style='width: 100%; height: 400px;'></div>".format(chartId));
    var chart = echarts.init($('#' + chartId).get(0));
    var options = {
        title: {
            text: '传感器 {0}'.format(record.sensorId)
        },
        tooltip: {
            formatter: "{a} <br/>{c} {b}"
        },
        toolbox: {
            show: true,
            feature: {
                mark: {show: true},
                restore: {show: true},
                saveAsImage: {show: true}
            }
        },
        series: [
            {
                name: '温度',
                type: 'gauge',
                z: 3,
                min: -10,
                max: 60,
                splitNumber: 14,
                axisLine: {            // 坐标轴线
                    lineStyle: {       // 属性lineStyle控制线条样式
                        width: 10
                    }
                },
                axisTick: {            // 坐标轴小标记
                    length: 15,        // 属性length控制线长
                    lineStyle: {       // 属性lineStyle控制线条样式
                        color: 'auto'
                    }
                },
                splitLine: {           // 分隔线
                    length: 20,         // 属性length控制线长
                    lineStyle: {       // 属性lineStyle（详见lineStyle）控制线条样式
                        color: 'auto'
                    }
                },
                title: {
                    textStyle: {       // 其余属性默认使用全局文本样式，详见TEXTSTYLE
                        fontWeight: 'bolder',
                        fontSize: 20
                    }
                },
                detail: {
                    textStyle: {       // 其余属性默认使用全局文本样式，详见TEXTSTYLE
                        fontWeight: 'bolder'
                    }
                },
                data: [{value: record.temperature, name: '温度(摄氏度)'}]
            },
            {
                name: '湿度',
                type: 'gauge',
                center: ['25%', '55%'],    // 默认全局居中
                radius: '50%',
                min: 0,
                max: 100,
                endAngle: 45,
                splitNumber: 10,
                axisLine: {            // 坐标轴线
                    lineStyle: {       // 属性lineStyle控制线条样式
                        width: 8
                    }
                },
                axisTick: {            // 坐标轴小标记
                    length: 12,        // 属性length控制线长
                    lineStyle: {       // 属性lineStyle控制线条样式
                        color: 'auto'
                    }
                },
                splitLine: {           // 分隔线
                    length: 20,         // 属性length控制线长
                    lineStyle: {       // 属性lineStyle（详见lineStyle）控制线条样式
                        color: 'auto'
                    }
                },
                pointer: {
                    width: 5
                },
                title: {
                    offsetCenter: [0, '-30%']       // x, y，单位px
                },
                detail: {
                    textStyle: {       // 其余属性默认使用全局文本样式，详见TEXTSTYLE
                        fontWeight: 'bolder'
                    }
                },
                data: [{value: record.humidity, name: '湿度(%)'}]
            }
        ]
    };
    chart.setOption(options);

    return function (record) {
        options.series[0].data[0].value = record.temperature;
        options.series[1].data[0].value = record.humidity;
        chart.setOption(options, true);
    }
}

/**
 * draw line charts
 */
var Chart = require('chart.js');
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
    chartRegion.append('<canvas id="{0}" height="100px"></canvas>'.format(id));
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

