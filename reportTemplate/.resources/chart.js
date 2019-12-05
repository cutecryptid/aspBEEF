$(document).ready(function(){
    var $xAxisDrop = $("#xAxisSelect");
    var $yAxisDrop = $("#yAxisSelect");

    $.each(chart_data.attributes, function(){
        $xAxisDrop.append($("<option />").val(this).text(this));
        $yAxisDrop.append($("<option />").val(this).text(this));
    });

    $xAxisDrop[0].selectedIndex = 0;
    $yAxisDrop[0].selectedIndex = 1;

    xVal = $xAxisDrop[0].selectedOptions[0].value;
    yVal = $yAxisDrop[0].selectedOptions[0].value;

    chart = echarts.init(document.getElementById("chart"));

    options = {
        grid: {
            left: '3%',
            right: '7%',
            bottom: '3%',
            containLabel: true
        },
        tooltip : {
            // trigger: 'axis',
            showDelay : 0,
            formatter : function (params) {
                if (params.value.length > 1) {
                    return params.seriesName + ' :<br/>'
                    + params.value[0] + 'cm '
                    + params.value[1] + 'cm ';
                }
                else {
                    return params.seriesName + ' :<br/>'
                    + params.name + ' : '
                    + params.value + 'cm ';
                }
            },
            axisPointer:{
                show: true,
                type : 'cross',
                lineStyle: {
                    type : 'dashed',
                    width : 1
                }
            }
        },
        toolbox: {
            feature: {
                dataZoom: {},
                brush: {
                    type: ['rect', 'polygon', 'clear']
                }
            }
        },
        brush: {
        },
        legend: {
            data: [],
            left: 'center'
        },
        xAxis : [
            {
                name: "",
                type : 'value',
                scale:true,
                axisLabel : {
                    formatter: '{value} cm'
                },
                splitLine: {
                    show: false
                }
            }
        ],
        yAxis : [
            {
                name: "",
                type : 'value',
                scale:true,
                axisLabel : {
                    formatter: '{value} cm'
                },
                splitLine: {
                    show: false
                }
            }
        ],
        series : []
    };

    function updatePoints(xVal, yVal, chart, options){
        points = chart_data.points.map(obj => ({
            'cluster' : obj['cluster'],
            [xVal] : obj[xVal],
            [yVal] : obj[yVal]
        }));

        rectangles = chart_data.clusters.map(obj => ({
            'name' : obj.name,
            'x' : obj.dimensions[xVal],
            'y' : obj.dimensions[yVal]
        }));
    
        seriesData = points.reduce(function (acum, point) {
            var cluster = point.cluster;
            if (!acum.hasOwnProperty(cluster)) {
                acum[cluster] = [];
            }
            acum[cluster].push([point[xVal], point[yVal]]);
            return acum;
        }, {});
    
        series = Object.entries(seriesData).map((elem) => ({
            'name' : elem[0],
            'type' : 'scatter',
            'data' : elem[1]
        }));

        rectangles.forEach((elem) => 
            series.push({
                type: 'scatter',
                markArea: {
                        silent: true,
                        itemStyle: {
                            normal: {
                                color: 'transparent',
                                borderWidth: 2,
                                borderType: 'solid'
                            }
                        },
                        data: [[{
                            name: elem.name,
                            xAxis: elem.x[0],
                            yAxis: elem.y[0]
                        }, {
                            xAxis: elem.x[1],
                            yAxis: elem.y[1]
                        }]]
                    }
            })
        );

        classNames = Object.keys(seriesData);

        options.series = series;
        options.xAxis[0].name = xVal;
        options.yAxis[0].name = yVal;
        options.legend.data = classNames;
        
        chart.setOption(options);
    }

    updatePoints(xVal, yVal, chart, options);

    $('select').change(function() { 
        xVal = $xAxisDrop[0].selectedOptions[0].value;
        yVal = $yAxisDrop[0].selectedOptions[0].value;

        updatePoints(xVal, yVal, chart, options);
    }); 
});