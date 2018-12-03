#!/bin/bash
# **********************************************************
# * Author        : xoyabc
# * Email         : lxh1031138448@gmail.com
# * Last modified : 2018-07-01 11:08
# * Filename      : get_douban_hot_movie.sh
# * Description   : 
# **********************************************************
#export PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

mv_info="/tmp/douban_mv_info"
src_file="/data/wwwroot/ys.louxiaohui.com/template/paody/aaaa/sou.js"
ultimate_open_ratio_file="/data/wwwroot/ys.louxiaohui.com/douban.html"

function request_douban()
{
    curl -so ${mv_info} https://movie.douban.com/chart -m 2
}

function get_mv_info()
{
    # movie week
    time_period=$(cat ${mv_info} |pup '#listCont2 [class="box_chart_num color-gray"] text{}')
    mv_name=$(cat ${mv_info} |pup '#listCont2 a text{}'  |sed '/^\s*$/d' |sed -r 's#^(\s*)(.*)$#\2#g'|sed 's# ##g')
    # movie us week
    time_period_us=$(cat ${mv_info} |pup '#listCont1 [class="box_chart_num color-gray"]:contains("美元") text{}')
    mv_name_us=$(cat ${mv_info} |pup '#listCont1 a text{}'  |sed '/^\s*$/d' |sed -r 's#^(\s*)(.*)$#\2#g')
}

function test_ou()
{
    echo ${time_period}
}

function update_mv_info()
{
    #substitute the '\n' to '  '(space)
    js_content=$(echo ${mv_name} |tr '\n' '   ')
    echo ${js_content}
    echo "document.writeln(\"${js_content}\");" > ${src_file}
}

function convert_to_html_format () 
{
# html start
cat > ${ultimate_open_ratio_file} << "EOF"
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- 上述3个meta标签*必须*放在最前面，任何其他内容都*必须*跟随其后！ -->
    <title>豆瓣电影排行榜</title>

    <!-- Bootstrap -->
    <link href="https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">

    <!-- HTML5 shim 和 Respond.js 是为了让 IE8 支持 HTML5 元素和媒体查询（media queries）功能 -->
    <!-- 警告：通过 file:// 协议（就是直接将 html 页面拖拽到浏览器中）访问页面时 Respond.js 不起作用 -->
    <!--[if lt IE 9]>
      <script src="https://cdn.bootcss.com/html5shiv/3.7.3/html5shiv.min.js"></script>
      <script src="https://cdn.bootcss.com/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>

  <!-- table start -->
EOF

# douban weekly top movie
echo -e "<h4 class=\"text-warning\">豆瓣本周口碑榜(${time_period})</h4>" >> ${ultimate_open_ratio_file}
cat >> ${ultimate_open_ratio_file} << EOF
<table class="table table-hover table-condensed">
    <tbody class=" col-xs-12 col-md-18">
        <tr class="success" ><th>Rank</th><th>Movie Name</th></tr>
EOF
    i=1
    for name in ${mv_name}
    do
        echo -e "\t<tr class=\"info\" ><td >${i}</td><td>${name}</td></tr>" >> ${ultimate_open_ratio_file}
        (( ++i ))
    done

cat >> ${ultimate_open_ratio_file} << EOF
    </tbody>
</table>
EOF
# us top movie
cat >> ${ultimate_open_ratio_file} << EOF
  <h4 id="output" class="text-warning"></h4>
  <script type="text/javascript">
      var str="${time_period_us}";
      var time_period_us = str.split(/ /)[0];
      document.getElementById('output').innerHTML = "豆瓣北美票房榜(" + time_period_us + ")";
  </script>
<table class="table table-hover table-condensed">
    <tbody class=" col-xs-12 col-md-18">
        <tr class="success" ><th>Rank</th><th>Movie Name</th></tr>
EOF
    j=1
    for name in ${mv_name_us}
    do
        echo -e "\t<tr class=\"info\" ><td >${j}</td><td>${name}</td></tr>" >> ${ultimate_open_ratio_file}
        (( ++j ))
    done

cat >> ${ultimate_open_ratio_file} << EOF
    </tbody>
</table>
</br>
EOF
# html end
cat >> ${ultimate_open_ratio_file} << EOF
  <!-- table end -->
    <!-- jQuery (Bootstrap 的所有 JavaScript 插件都依赖 jQuery，所以必须放在前边) -->
    <script src="https://cdn.bootcss.com/jquery/1.12.4/jquery.min.js"></script>
    <!-- 加载 Bootstrap 的所有 JavaScript 插件。你也可以根据需要只加载单个插件。 -->
    <script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
  </body>
</html>
EOF
}

request_douban
[ -s ${mv_info} ] && echo "do nothing" >/dev/null || request_douban
get_mv_info
update_mv_info
convert_to_html_format
