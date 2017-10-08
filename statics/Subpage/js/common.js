
var originalStyle = new Array(),
    activate_style = {"background-color":"grey", "opacity":0.4};


function changeTagStyle(ths, attrname) {
    // 根据标签的attrname属性更新样式
    var id = ths.getAttribute("tag_id");
    var bol = int2Bool(ths, attrname);

    ths.style.backgroundColor = bol?activate_style["background-color"]:originalStyle[id]["background-color"];
    ths.style.opacity = bol?activate_style["opacity"]:originalStyle[id]["opacity"];
}


function int2Bool(obj, attrname) {
    /*
    * 把节点属性值转换成boolean类型
    * :obj: 节点对象
    * */
    var num = parseInt(obj.getAttribute(attrname));
    return !isNaN(num)&&Boolean(num);
}


function setAttrBoolean(obj, attrname, bool) {
    /*
    * 根据布尔类型设置节点属性值（设置成数值类型）
    * :obj: 对象节点
    * :attrname: 节点属性名
    * :bool: 要设置的布尔类型值
    * */
    var val = bool ? 1:0;
    obj.setAttribute(attrname, val);
}


function reverseBoolean(obj, attrname) {
    /*
    * 反转节点属性值(要求属性值是数值类型或boolean类型)
    * :obj: 对象节点
    * :attrname: 属性名
    * */
    var bol = int2Bool(obj, attrname);
    setAttrBoolean(obj, attrname, !bol);
}


function str_in_array(arr, str) {
    /*
    * 判断字符串数组中是否存在目标字符串
    * :attr: 字符串数组
    * :str: 目标字符串
    * */
    for(var i=0; i<arr.length; i++){
        if(arr[i].toString().toLowerCase() == str.toString().toLowerCase())
            return true;
    }
    return false;
}


function cleanPreviewData(type) {
    /*
    * 清除预览窗口中sub_type为type的内容
    * :type: 订阅类型
    * */
    parent.PUB.updatePreview(type, "");
}


function dict2LinkArgs(data) {
    /*
    * 把字典类型转换成地址参数
    * :data: 字典类型对象
    * */
    var key_value = new Array();
    for(var key in data){
        key_value.push(key + "=" + argsEncode(data[key]) + "");
    }
    return key_value.join("&");
}


var Ajax={
    /*
    * 实现与后台的数据传输
    * */
    get: function(url, data, fn) {
        var obj = new XMLHttpRequest();  // XMLHttpRequest对象用于在后台与服务器交换数据
        obj.open('GET', url, true);
        obj.onreadystatechange = function() {
            if (obj.readyState == 4 && obj.status == 200 || obj.status == 304) { // readyState == 4说明请求已完成
                fn.call(this, obj.responseText);  //从服务器获得数据
            }
        };
        obj.send(dict2LinkArgs(data));
    },
    post: function (url, data, fn) {         // datat应为'a=a1&b=b1'这种字符串格式，在jq里如果data为对象会自动将对象转成这种字符串格式
        var obj = new XMLHttpRequest();
        obj.open("POST", url, true);
        obj.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  // 添加http头，发送信息至服务器时内容编码类型
        obj.onreadystatechange = function() {
            if (obj.readyState == 4 && (obj.status == 200 || obj.status == 304)) {  // 304未修改
                fn.call(this, obj.responseText);
            }
        };
        obj.send(dict2LinkArgs(data));
    }
};


function autoToolTop() {
    /*
    * 设置订阅工具离页面顶部的距离
    * */
    var container = document.getElementsByClassName("sub_container");
    if(container.length > 0){
        container = container[0];
    }else{
        return;
    }
    var clientHeight = document.body.clientHeight;
    var toolHeight = container.offsetHeight;
    container.style.top = clientHeight/2 - toolHeight/2;
}


function prevent_tag_Click(tag) {
    /*
    * 屏蔽tag标签下所有标签的点击和链接事件， sub_container除外
    * */
    var children = tag.children;
    for(var i=0; i<children.length; i++){
        if(children[i].getAttribute("class") == "sub_container") continue;
        prevent_tag_Click(children[i]);
    }
    tag.addEventListener("click", function (event) {event.preventDefault();}, false);
}


function argsEncode(url) {
    /*
    * 链接特殊字符处理
    * */
    return url.replace(/&/g,"(-)__(-)");
}


window.onresize = function () {
    /*
    * 窗口大小发生变化时，重新设置订阅工具的顶部距离
    * */
        autoToolTop();
    };


function hrefHandler() {
    /*
    * 补全所有缺省href
    * */
    var exclude_nodeName = ["script", "link"];
    var nodes = document.evaluate("//*[@href or @hrefs]", document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
    var p = /(http|https):\/\/([^\/]+)\//i;
    var info = p.exec(document.getElementById("sub_info").getAttribute("website_url"));
    if(!info){
        info = p.exec(document.getElementById("sub_info").getAttribute("content_url"));
    }
    if(!info){
        alert("分析网站Url时出现异常，请联系管理员.");
    }
    var proto = info[1],
        domain = info[2];
    var url = proto + "://" + domain;
    for(var i=0; i<nodes.snapshotLength; i++){
        node = nodes.snapshotItem(i);
        if(str_in_array(exclude_nodeName, node.nodeName)){
            continue
        }
        try {
            var href_v = node.getAttribute("href");
            var href_t = "href";
            if(!href_v){
                href_v = node.getAttribute("hrefs");
                href_t = "hrefs";
            }
            if(href_v.length>0 && href_v[0]=='/'){
                node.setAttribute(href_t, url + href_v);
            }
        }
        catch(e){}
    }
}


function imgSrcHandler() {
    /*
    * （1）把所有data-src转换成src
    * （2）补全所有缺省src
    * */
    nodes = document.evaluate("//img[@src or @data-src]", document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
    var url = document.location.protocol + "//" + document.location.host;
    for(var i=0; i<nodes.snapshotLength; i++){
        node = nodes.snapshotItem(i);
        var src = node.getAttribute("src");
        var data_src = node.getAttribute("data-src");
        if(src && data_src){
            src = data_src;
        }else if(!src && data_src){
            src = data_src;
        }
        if(src[0] == "/"){
            src = url + src;
        }
        node.setAttribute("src", src);
        node.removeAttribute("data-src");
    }
}