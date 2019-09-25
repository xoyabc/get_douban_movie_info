<!--ts-->

   * [get_douban_movie_info](#get_douban_movie_info)
      * [douban_traverse_movies_link.py](#douban_traverse_movies_linkpy)
      * [get_movie_info_from_douban.sh](#get_movie_info_from_doubansh)
      * [get_chn_name_from_eng_movie_name_by_douban.py](#get_chn_name_from_eng_movie_name_by_doubanpy)
         * [使用方法](#使用方法)
      * [get_douban_comment_score_and_number_by_name.py](#get_douban_comment_score_and_number_by_namepy)
         * [使用方法](#使用方法-1)
      * [get_douban_detailed_movie_info_by_requests.py](#get_douban_detailed_movie_info_by_requestspy)
      * [get_douban_detailed_movie_info_using_api.rhilip.info.py](#get_douban_detailed_movie_info_using_apirhilipinfopy)
      * [test_douban_api.py](#test_douban_apipy)
      * [to_do](#to_do)
      * [REF：](#ref)
<!--te-->

# get_douban_movie_info(已失效)

获取豆瓣电影条目信息

搬自：https://github.com/atom210/douban_api_test

## douban_traverse_movies_link.py(已失效)

获取某年某月热门影片，修改`rst_list = movie_links_range(2018, 10);`中的年月即可。
``` bash
[root@host get_douban_movie_info]# python douban_traverse_movies_link.py                
url: https://movie.douban.com/subject/27110363/ title: 名侦探柯南：零的执行人
url: https://movie.douban.com/subject/30290917/ title: 我们无法成为野兽
url: https://movie.douban.com/subject/27140071/ title: 找到你
url: https://movie.douban.com/subject/25812730/ title: 如懿传
url: https://movie.douban.com/subject/26925317/ title: 动物世界
url: https://movie.douban.com/subject/26999424/ title: 我的间谍前男友
url: https://movie.douban.com/subject/30140571/ title: 嗝嗝老师
url: https://movie.douban.com/subject/27039069/ title: 宝贝儿
url: https://movie.douban.com/subject/26725678/ title: 解除好友：暗网
url: https://movie.douban.com/subject/27016554/ title: 鬼入侵
url: https://movie.douban.com/subject/25917789/ title: 铁血战士
url: https://movie.douban.com/subject/26636712/ title: 蚁人2：黄蜂女现身
url: https://movie.douban.com/subject/26996640/ title: 反贪风暴3
url: https://movie.douban.com/subject/26290410/ title: 昨日青空
url: https://movie.douban.com/subject/30122633/ title: 快把我哥带走
url: https://movie.douban.com/subject/30304024/ title: 奇遇人生
url: https://movie.douban.com/subject/26336252/ title: 碟中谍6：全面瓦解
url: https://movie.douban.com/subject/25849049/ title: 超人总动员2
url: https://movie.douban.com/subject/26683421/ title: 特工
url: https://movie.douban.com/subject/26972258/ title: 江湖儿女
```
## get_movie_info_from_douban.sh(已失效)

调用豆瓣v2接口获取影片类别、年份、主演、导演及subject_id。 ~~由于豆瓣v2 API失效，该脚本已不可用2019-07-28~~

// 2019-09-25 换用apikey方式，仍可以使用
```shell
https://api.douban.com/v2/movie/search?apikey=0dad551ec0f84ed02907ff5c42e8ec70&q=%E6%96%AF%E7%A7%91%E6%99%AE%E9%87%8C%E7%9A%84%E8%A7%A3%E6%94%BE
```


## get_chn_name_from_eng_movie_name_by_douban.py

电脑里下载的影片都是英文字幕的，便写了这个脚本，根据文件名中的英文名及年份获取中文名，年份，豆瓣评分及评分人数。

### 使用方法
 - 将文件名贴入movie.name_year
 ```bash
 [root@host get_douban_movie_info]# cat movie.name_year 
Wanted.2008.RERiP.1080p.BluRay.x264.DTS-WiKi
The.Bold.the.Corrupt.and.the.Beautiful.2017.720p.BluRay.x264-WiKi
 ```
 - 运行脚本
 
 由于会拿文件名和豆瓣搜索结果中第一个影片原名作对比，若影片原名不是英文，则获取失败。这里的`血观音`原名是`血觀音`,因此獲取信息失敗。
 
 获取中文片名信息参见下个脚本。
 ```python
 [root@host get_douban_movie_info]# python get_chn_name_from_eng_movie_name_by_douban.py 
Wanted;通缉令;2008;7.4;129782人评价
The.Bold.the.Corrupt.and.the.Beautiful;Not found in douban;N/A;N/A;N/A
 ```
 
 ## get_douban_comment_score_and_number_by_name.py
 
 根据中文或英文片名(不含年份)，取豆瓣电影搜索结果中的第一个条目，获取影片信息，
 
### 使用方法
 - 将文件名贴入movie.name
 ```bash
[root@host get_douban_movie_info]# cat movie.name
Wanted
The.Bold.the.Corrupt.and.the.Beautiful
失速夜狂奔
電影配樂傳奇
我不是药神
 ```
  - 运行脚本
  
  ```python
[root@host get_douban_movie_info]# python get_douban_comment_score_and_number_by_name.py 
Wanted;通缉令;2008;7.4;129782人评价
The.Bold.the.Corrupt.and.the.Beautiful;血观音;2017;8.2;116795人评价
失速夜狂奔;好时光;2017;7.0;7143人评价
電影配樂傳奇;电影配乐传奇;2016;8.0;605人评价
我不是药神;我不是药神;2018;9.0;780276人评价
 ```
 
## get_douban_detailed_movie_info_by_requests.py

根据豆瓣电影条目ID，即subject-id，获取影片详细信息，包括 subject_id,中文名,年份,国家,语言,类型,主演,导演,IMDB编号，最终会以`tab`符号分割，写入到test.txt文件中。

主要使用到了requests, BeautifulSoup模块。在使用`json.loads()`解码json字符串时遇到了`ValueError`异常，报`Invalid control character at: line 85`错误，即非法的控制符号(ACSII前32个字符)，后使用`strict=False`解决。此外，也可将换行符替换为空，`json.loads(script_json.replace('\n', ''))`

 - 将文件名贴入movie.list
```bash
[root@host get_douban_movie_info]# cat movie.list 
1868876
1868933
1872272
1875554
```
  - 运行脚本
  
  ```python
[root@host get_douban_movie_info]# python get_douban_detailed_movie_info_by_requests.py 
[root@host get_douban_movie_info]# 
[root@host get_douban_movie_info]# cat test.txt 
subject_id      中文名  年份    国家    语言    类型    主演    导演    IMDB编号
1868876 旱季    2006    乍得    阿拉伯语        剧情    Ali Barkai      马哈曼特-萨雷·哈隆      tt0825241
1868933 让娜·迪尔曼     1975    法国    法语    剧情    德菲因·塞里格   香特尔·阿克曼   tt0073198
1872272 美国田园下的罪恶        2007    美国    英语    犯罪    艾伦·佩吉       汤米·奥·哈沃    tt0802948
1875554 婚礼之后        2006    丹麦    丹麦语  剧情    麦斯·米科尔森   苏珊娜·比尔     tt0457655
  ```

## get_douban_detailed_movie_info_using_api.rhilip.info.py

调用`R酱`的接口获取，这里就不再说了，接口介绍文档超详细。
https://github.com/Rhilip/PT-help/blob/master/modules/infogen/README.md

## test_douban_api.py(已失效)

```
// 2019-09-25 换用apikey方式，仍可以使用
http://api.douban.com/v2/movie/subject/24751756?apikey=0dad551ec0f84ed02907ff5c42e8ec70
```

搬自：https://github.com/atom210/douban_api_test

使用豆瓣V2版本API`http://api.douban.com/v2/movie/subject/24751756`获取影片信息。
```
[root@host get_douban_movie_info]# python test_douban_api.py 
Hello world
do request: http://api.douban.com/v2/movie/subject/24751756
request.url : http://api.douban.com/v2/movie/subject/24751756    status: 200
id : 24751756
title : 老炮儿
rating : 7.80
ratings_count : 460004
country : 中国大陆
actors : 冯小刚, 许晴, 张涵予, 刘桦
do request: http://api.douban.com/v2/movie/subject/1764796
request.url : http://api.douban.com/v2/movie/subject/1764796     status: 200
id : 1764796
title : 机器人9号
rating : 7.50
ratings_count : 61806
country : 美国
actors : 伊莱贾·伍德, 詹妮弗·康纳利, 约翰·C·赖利, 克里斯托弗·普卢默
```
## to_do

- [x] 获取IMDB评价人数
- [x] 获取IMDB评分
- [ ] 生成excel


## REF：

- [python-json-loads-fails-with-valueerror-invalid-control-character-at-line-1-c](https://stackoverflow.com/questions/9295439/python-json-loads-fails-with-valueerror-invalid-control-character-at-line-1-c)

- [PT-help](https://github.com/Rhilip/PT-help/blob/master/modules/infogen/README.md)

- [Get movie url link](https://gist.github.com/xoyabc/6961eecc7ccf1c481f5cf31b3ec02aa3)
- [豆瓣 v2 API 失效](https://github.com/DIYgod/RSSHub/issues/2221)
