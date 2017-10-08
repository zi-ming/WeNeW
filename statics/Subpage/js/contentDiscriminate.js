
var activated_tag = null,
    xpaths = {"0":"", "1":"", "2":"", "3":""},
    infos = {'0':"标题", '1':"作者", '2':"时间", '3':"内容"};


function changeTagStyle(ths, attrname) {
    /*
    * 根据attrname更改标签样式
    * */
    var id = ths.getAttribute("tag_id");
    var bol = int2Bool(ths, attrname);
    ths.style.backgroundColor = bol?activate_style["background-color"]:originalStyle[id]["background-color"];
    ths.style.opacity = bol?activate_style["opacity"]:originalStyle[id]["opacity"];
}


function hoverHandler(ths) {
    /*
    * 鼠标掠过标签事件
    * */
    var islocked = int2Bool(ths, "islocked");
    var activated = int2Bool(ths, "activated");
    reverseBoolean(ths, "activated");
    if(islocked == false) {
        if(activated_tag && activated){
            reverseBoolean(activated_tag, "activated");
            changeTagStyle(activated_tag, "activated");
            activated_tag = ths;
        }else if(!activated){
            activated_tag = null;
        }
        changeTagStyle(ths, "activated");
    }
}


function clickHandler(ths) {
    /*
    * 鼠标点击标签事件
    * */
    reverseBoolean(ths, "islocked");
    changeTagStyle(ths, "islocked");

    var sub_content = document.getElementById("sub_content");
    var sub_content_lock = document.getElementById("sub_content_lock");

    var content_confirm = int2Bool(sub_content, "confirm");
    var content_lock_confirm = int2Bool(sub_content_lock, "confirm");
    var islocked = int2Bool(ths, "islocked");
    if(content_confirm && !content_lock_confirm) {
        var type = "3";
        if (islocked) {
            ths.setAttribute("sub_type", type);
        }
        else {
            ths.removeAttribute("sub_type");
            cleanPreviewData(type);
        }
        xpaths[type] = formXpath(type);
    }
}


function initTag(exclusive_tags, tag, id) {
    /*
    * 初始化标签, 为特定标签添加额外的订阅属性
    * :exclusive_tags: 排除的标签名数组
    * :tag: 父节点
    * :id:  起始id值
    * */
    var children = tag.children;
    for(var i=0; i<children.length; i++){
        initTag(exclusive_tags, children[i], id + 1 + i);
    }
    if(!str_in_array(exclusive_tags, tag.tagName)){
        tag.setAttribute("tag_id", id);
        tag.setAttribute("islocked", 0);
        tag.setAttribute("activated", 0);
        tag.setAttribute("onmouseover", "hoverHandler(this);event.cancelBubble = true;");
        tag.setAttribute("onmouseout", "hoverHandler(this);event.cancelBubble = true;");
        tag.setAttribute("onclick", "clickHandler(this);event.cancelBubble = true;");

        var style = Array();
        style['background-color'] = tag.style.background;
        style["opacity"] = tag.style.opacity;
        originalStyle[id] = style;
    }
}


function changeToolTagStyle(obj) {
    /*
    * 根据confirm更新订阅工具样式
    * */
    var confirm = int2Bool(obj, "confirm");
    var cls = obj.className;
    if(cls.indexOf("sub_button_m")!=-1){
        obj.className = confirm ? "sub_button_m active": "sub_button_m unactive";
    }else if(cls.indexOf("sub_button_s")!=-1){
        obj.className = confirm ? "sub_button_s active": "sub_button_s unactive";
    }
}


function reverse_alltag_attr_and_style(attrname, attrval) {
    /*
    * 翻转所有符合“attrname=attrval”的节点样式
    * */
    var tags = document.evaluate("//*[@"+attrname+"='"+attrval+"']", document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
    for(var i=0; i<tags.snapshotLength; i++){
        var tag = tags.snapshotItem(i);
        reverseBoolean(tag, attrname);
        changeTagStyle(tag, attrname);
    }
}


function cleanLockedTag() {
    /*
    * 清除所有已被locked的标签标记
    * */
    reverse_alltag_attr_and_style("islocked", '1');
}


function cleanActivatedTag() {
    /*
    * 清除所有activated的标签标记
    * */
    reverse_alltag_attr_and_style("activated", '1');
}


function cleanToolTag() {
    /*
    * 重置所有已确认的订阅工具标签
    * */
    var tool_items = document.evaluate("//div[@class='sub_button_m active']", document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
    for(var i=0; i<tool_items.snapshotLength; i++)
        subClick(tool_items.snapshotItem(i));
}


function cleanTagType_with_islocked(type) {
    /*
    * 清除所有locked的标签
    * */
    xpaths[type] = "";
    var tags = document.evaluate("//*[@sub_type='"+type+"']", document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
    for(var i=0; i<tags.snapshotLength; i++){
        var tag = tags.snapshotItem(i);
        tag.removeAttribute("sub_type");
    }
}


function subClick(obj) {
    /*
    * 订阅工具点击事件处理
    * */
    var confirm = int2Bool(obj, "confirm");
    switch(obj.getAttribute("id")){
        case "sub_title": type = 0; break;
        case "sub_author": type = 1; break;
        case "sub_time": type = 2; break;
    }
    if(confirm){     // 之前已经激活，现在取消激活
        cleanTagType_with_islocked(type);
        cleanPreviewData(type);
    }else{      // 之前没有激活，现在激活
        var tags = document.evaluate("//*[@islocked='1']", document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
        if(tags.snapshotLength == 0) return;
        var tag = tags.snapshotItem(0);
        tag.setAttribute("sub_type", type);
        cleanLockedTag();
        xpaths[type] = formXpath(type);
    }
    reverseBoolean(obj, "confirm");
    changeToolTagStyle(obj);                     // 更新订阅菜单显示样式
}


function cleanAllStatus() {
    /*
    * 清除所有操作
    * */
    cleanToolTag();         // 初始化工具栏状态
    cleanLockedTag();       // 初始化所有已被locked的标签
    cleanActivatedTag();    // 清除所有activated的标签
}


function submit() {
    /*
    * 提交订阅信息
    * */
    var title_confirm = int2Bool(document.getElementById("sub_title"), "confirm");
    var content_lock_confirm = int2Bool(document.getElementById("sub_content_lock"), "confirm");
    if(!title_confirm || !content_lock_confirm){
        alert("请补充完整订阅内容信息！");
        return false;
    }

    var sub_info = document.getElementById("sub_info");
    var website_url = sub_info.getAttribute("website_url");
    var content_url = sub_info.getAttribute("content_url");

    var success = function (data) {
        alert("保存成功，点击确定关闭当前窗口", "关闭");
        top.opener = null;
        top.close();
    };

    var data = {
            'website_url': website_url,
            'content_url': content_url,
            'title_xpath': xpaths["0"],
            'author_xpath': xpaths["1"],
            'time_xpath': xpaths["2"],
            'content_xpath': xpaths["3"]};

    Ajax.post("/sub/iframe_contentPage", data, success);
}


function cleanContent() {
    /*
    * 清空内容的所有订阅
    * */
    var type = "3";
    cleanLockedTag();
    cleanTagType_with_islocked(type);
    cleanPreviewData(type);
}


function contentClick() {
    /*
    * 内容订阅工具点击事件
    * */
    var sub_content = document.getElementById("sub_content");
    var content_opera = document.getElementById("content_opera");
    var sub_content_lock = document.getElementById("sub_content_lock");

    var confirm = int2Bool(sub_content,"confirm");
    if(confirm){    // 之前已经激活，现在取消激活
        var content_lock_confirm = int2Bool(sub_content_lock, "confirm");
        if(content_lock_confirm){
            contentLockClick(sub_content_lock);
        }
        sub_content.style.display = "block";
        content_opera.style.display = "none";
        cleanContent();
    }else{          // 之前没有激活，现在激活
        sub_content.style.display = "none";
        content_opera.style.display = "block";
    }
    reverseBoolean(sub_content, "confirm");
    changeToolTagStyle(sub_content);
}


function contentCancelClick() {
    /*
    * 取消内容点击事件
    * */
    contentClick();
}


function contentLockClick(ths) {
    /*
    * 锁定内容点击事件
    * */
    var confirm = int2Bool(ths, "confirm");
    var tags = document.evaluate("//*[@sub_type='3']", document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
    if(confirm){
        for(var i=0; i<tags.snapshotLength; i++){
            reverseBoolean(tags.snapshotItem(i), "islocked");
            changeTagStyle(tags.snapshotItem(i), "islocked");
        }
    }else{
        if(tags.snapshotLength == 0) return;
        cleanLockedTag();
    }
    reverseBoolean(ths, "confirm");
    changeToolTagStyle(ths);
}


function addMenuToolDiv() {
    /*
    * 添加订阅工具
    * */
    sub_tool = "<div class='sub_container'>" +
        "<div class='sub_button_m unactive' confirm='0' id='sub_title' onclick='subClick(this)'>标题</div>"+
        "<div class='sub_button_m unactive' confirm='0' id='sub_author' onclick='subClick(this)'>作者</div>"+
        "<div class='sub_button_m unactive' confirm='0' id='sub_time' onclick='subClick(this)'>时间</div>"+
        "<div class='sub_button_m unactive' confirm='0' id='sub_content' onclick='contentClick(this)'>内容</div>"+
        "<div style='display: none;' id='content_opera'>" +
            "<div class='sub_button_s unactive' confirm='0' id='sub_content_cancel' onclick='contentCancelClick(this)'>取消</div>"+
            "<div class='sub_button_s unactive'confirm='0' id='sub_content_lock' onclick='contentLockClick(this)'>锁定</div>"+
        "</div>" +
        "<div class='sub_button_m red' confirm='0' onclick='cleanAllStatus()'>清除</div>"+
        "<div class='sub_button_m lightBlue' confirm='0' onclick='submit();'>完成</div>"+
        "</div>";
    document.body.innerHTML+=sub_tool;
}


window.onload = function () {
    hrefHandler();
    imgSrcHandler();
    exclusive_tags = ["article", "main", "br", "script", "iframe", "body", "header"];
    initTag(exclusive_tags, document.body, 0);
    addMenuToolDiv();
    prevent_tag_Click(document.body);
};