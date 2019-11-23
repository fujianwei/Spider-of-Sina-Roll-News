# Spider-of-Sina-Roll-News
## 百万量级文本数据爬虫  
   * 爬取的是新浪的滚动新闻网页，因为爬取量比较大所以选择了比较好爬的滚动网页  
   * 网页本身没什么反爬设置，所以代码也很简单  
   * 爬取内容共分为四组，分别是：finance、sports、technology、entertainment  
   * 每篇文章只爬取了基本信息：标题、URL、文章内容  
   * finance和technology比较好爬，几乎全部都是文本信息  
   * entertainment板块有三种网页：文本网页（域名为ent）、视频网页（域名为video）、图片网页（域名为slid）  
   * sports板块有两种网页：文本网页（域名为ent）、视频网页（域名为video）  
   * 对不同的网页使用不同的request函数  
   * 爬下来的文本内容使用mongodb存储  
   * 数据量为1,000,254篇文本  
   * 其中经济类538,775、体育类283,419，科技类115,631，娱乐类62,429
